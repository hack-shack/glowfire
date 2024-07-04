"""
tracstar: music player for snakeware
(c) 2023 Asa Durkee. MIT License.
"""
import datetime
from math import ceil
import os
from os import path
import pygame
import pygame_gui
from pygame_gui.elements.ui_image import UIImage as UIImage
from pygame_gui.elements.ui_label import UILabel as UILabel
from pygame_gui.elements.ui_panel import UIPanel as UIPanel
import time

import sys


BLACK = ((0,)*3)
WHITE = ((255,)*3)
CWD       = path.dirname(__file__)
FONTDIR   = path.join(CWD,"../../../data/fonts")
LIBDIR    = path.join(CWD,"../../../data/lib")
MUSIC_DIR = path.join(CWD,"music")
TEXTUREDIR= path.join(CWD,"data/textures")

sys.path.append(LIBDIR)
import bmpfont


class Tracstar(UIPanel):
    """ Create a panel with the tracstar music player interface. """
    DIMS = (200,240)

    def __init__(self, position, manager):
        super().__init__(
            pygame.Rect(position, (self.DIMS[0], self.DIMS[1])),
            manager=manager,
            object_id="#tracstar"
        )



        self.display_album_name = UILabel(
            relative_rect=pygame.Rect(0,0,200,25),
            text="Album Name",
            manager=manager,
            container=self,
            parent_element=self,
            object_id=ObjectID(class_id="@tracstar_label",
                               object_id="#display_album_name"
            )
        )
        self.display_artist_name = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(0,0,200,25),
            text="Artist Name",
            manager=manager,
            container=self,
            parent_element=self,
            object_id=ObjectID(class_id="@tracstar_label",
                               object_id="#display_artist_name"
            )
            
        self.display_track_name = UILabel(
            relative_rect=pygame.Rect(0,0,200,25),
            text="Track Name",
            manager=manager,
            container=self,
            parent_element=self,
            object_id="#display_track_name"
        )



        self.dsurf = UIImage(
            pygame.Rect((0, 0),self.DIMS),
            pygame.Surface(self.DIMS).convert(),
            manager = manager,
            container = self,
            parent_element = self,
        )

        self.btn_playpause = pygame_gui.elements.UIButton(
            relative_rect = pygame.Rect(0,0,120,25),
            text = 'playpause',
            manager = manager,
            container = self,
            object_id = '#btn_playpause',
        )

        self.IMAGES_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)),"data/images")
        print(str(self.IMAGES_PATH))

    # VARIABLES
    # -----------------------------------------------------------------
    current_track_marquee = 'Test Track'
    x = 20

    # BITMAPPED FONTS - PNG font image, column/row indexed
    # The "PNG fonts" use the bmpfont module and are imple-
    # mented completely differently from TrueType fonts.
    # -----------------------------------------------------
    bmpfont_dans_sans = bmpfont.BmpFont(os.path.join(FONTDIR,"DansSans/DansSans.idx"))
    bmpfont_exupery   = bmpfont.BmpFont(os.path.join(FONTDIR,"Exupery/Exupery.idx"))
    all_glyphs = " !\"#$%&\'()*+,-./0123456789:;<=>?"\
                    "@ABCDEFGHIJKLMNOPQRSTUVWXYZ[\\\]^"\
                        "`abcdefghijklmnopqrstuvwxyz\{|\}~©"

    # TRUETYPE FONTS - crisp at certain predefined sizes
    # -----------------------------------------------------
    pygame.font.init()
    font_profont14 = pygame.font.Font(os.path.join(FONTDIR,'ProFontIIx/ProFontIIx.ttf'),14)  # crisp sizes are 24,18,14, and 12,10,9 at tiny sizes

    def draw_music_controls(self):
        """ Draw a cluster of music playback controls. """
        cluster_width = 200
        # Fetch button images from disk. pygame stores each as a Surface.
        i_playpause = pygame.image.load(os.path.join(self.IMAGES_PATH,"playpause.png"))
        i_next = pygame.image.load(os.path.join(self.IMAGES_PATH,"next.png"))
        i_last = pygame.image.load(os.path.join(self.IMAGES_PATH,"last.png"))
        # Get the dimensions of those surfaces. Store into pygame rect coordinates.
        r_playpause = i_playpause.get_rect()
        r_next = i_next.get_rect()
        r_last = i_last.get_rect()

        minimum_width = 0
        for image in (r_playpause, r_next, r_last):
            minimum_width += image.width
        if minimum_width < cluster_width:
            print('WARN : music_controls cluster_width is too narrow to hold all images.')
            print('DEBUG: minimum_width: ' + str(minimum_width))
            print('DEBUG: cluster_width: ' + str(cluster_width))

        # Create output surface to hold the button images.
        surf = pygame.Surface((cluster_width,48))
        surf.fill((255,255,255,0))

        # Arrange the button images on the output surface.
        surf.blit(i_last,(0,0))  # left edge of surface
        surf.blit(i_playpause,((surf.get_rect().width / 2) - (i_playpause.get_rect().width / 2),0))  # middle
        surf.blit(i_next,((surf.get_rect().width - i_next.get_rect().width),0))  # right edge of surface
        return surf

    def draw_playbar(self,x,width,direction,offset_counter=0,
    height=16):
        """ Draw a magnetic tape inspired 'playbar.' """
        velocity  = 1
        texture = pygame.image.load(os.path.join(TEXTUREDIR,"stripes.png"))
        rect = pygame.Rect(0,0,width,height)
        surf = pygame.Surface((rect.w, rect.h))

        # fill the entire width of the playbar surface
        for t in range(ceil(rect.w / texture.get_width())):
            surf.blit(texture,(ceil(t * texture.get_width()),0))
        if direction == 'Left':
            offset_counter -= velocity
            surf.scroll(velocity,0)
        if direction == 'Right':
            offset_counter += velocity

        surf.blit(texture, (offset_counter + width, 0))
        #lcd.blit(surf,(x,y))

        if x < 0:
            direction = 'Right'
        elif x > (self.DIMS[0] - width):
            direction = 'Left'
        if direction == 'Right':
            x += velocity
        if direction == 'Left':
            x -= velocity

        #lcd.blit(surf, (x,y))
        #return offset_counter
        return surf

    def draw_track_status(self, surface, status):
        """ Draw a four-character track status in dot matrix font. """
        font_title  = bmpfont.BmpFont(os.path.join(FONTDIR,"Exupery/Exupery.idx"))
        font_status = bmpfont.BmpFont(os.path.join(FONTDIR,"Prescott/Prescott.idx"))
        surf_temp = pygame.Surface((154,63))
        surf_temp.fill(WHITE)
        font_title.blit("playback status",surf_temp,(2,0),usetextxy=0)
        font_status.blit(status, surf_temp,(0,14),usetextxy=0)
        surf_status = pygame.Surface.copy(surf_temp)
        return surf_status

    def process_event(self, event):
        super().process_event(event)


    def update(self, delta):
        super().update(delta)

        self.dsurf.image.fill(WHITE)

        self.display_album_name.text = 'Album'
        self.display_artist_name.text = 'Artist'
        self.display_track_name.text = 'Track'
        """
        self.display_album_name.text.rebuild()
        self.display_artist_name.text.rebuild()
        self.display_track_name.text.rebuild()
        """




        #self.draw_track_status(surface=self.dsurf.image,status="stop")

        """ Draw name of currently playing track. """
        #x, direction = self.scroll_track_text(self.current_track_marquee,x,137,direction)
        #self.dsurf.image.blit(self.scroll_track_text(self.current_track_marquee, 'Left'),(0,20))




        # test
        #track_status = 'list'

        """ Draw a four-character track status in dot matrix font. """
        # TODO: 40 fps performance impact.
        """
        track_status_position = (0,(self.DIMS[1] - 48 - 72))
        if track_status == 'stop':
            self.dsurf.image.blit(self.draw_track_status("stop"),track_status_position)
        elif track_status == 'list':
            self.dsurf.image.blit(self.draw_track_status("list"),track_status_position)
        elif track_status == 'scan':
            self.dsurf.image.blit(self.draw_track_status("scan"),track_status_position)
        elif track_status == 'load':
            self.dsurf.image.blit(self.draw_track_status("load"),track_status_position)
        elif track_status == 'play':
            self.dsurf.image.blit(self.draw_track_status("Play"),track_status_position)
            draw_track_time(datetime.datetime.now().strftime('%M:%S'))
        elif track_status == 'pause':
            #self.draw_track_status("PaUS")
            self.dsurf.image.blit(self.draw_track_status("PaUS"),(0,124))
        """

        """ Draw a five-character track time counter in dot matrix font. """
        # TODO: 20-30 fps performance impact.
        #self.dsurf.image.blit(draw_track_time(datetime.datetime.now().strftime('%M:%S')),(173,124))

        """ Draw magnetic-tape 'playbar.' """
        #self.dsurf.image.blit(self.draw_playbar(3,(self.DIMS[0]-6),'Left'),(3,100))

        """ Place music controls. """
        #self.dsurf.image.blit(self.draw_music_controls(),(0,self.DIMS[1] - 48))

        """ Draw 1px vertical line border on the panel's right edge. """
        #pygame.draw.line(surface=self.dsurf, color='black', start_pos=(self.DIMS[0],0),end_pos=self.DIMS)


# FUNCTIONS - SOFTWARE
# =========================================================

def draw_track_time(time):
        font_title  = bmpfont.BmpFont(os.path.join(FONTDIR,"Exupery/Exupery.idx"))
        font_time = bmpfont.BmpFont(os.path.join(FONTDIR,"Prescott/Prescott.idx"))
        #surf_temp = pygame.Surface((len(time) + 1) * font_time.width, font_time.height)  # +1 for the colon
        surf_temp = pygame.Surface((200,240))
        surf_temp.fill(WHITE)
        font_title.blit("time remaining", surf_temp,(54,0),usetextxy=0)
        font_time.blit(time, surf_temp,(0,14), usetextxy=0)
        surf_time = pygame.Surface.copy(surf_temp)
        return surf_time

# MAIN
# =========================================================
def main():
    volume = 0.1
    volume_levels = [0.0, 0.02, 0.05, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 1.0]  # nonlinear volume control
    volume_index = 2  # volume_levels index number for the volume level you want to start with
    draw_snapper = False
    track_list  = []
    track_list_move = ''
    selected_track = 0
    #track_status = 'pause' #'stop'
    current_track = ""

    draw_track_list = False
    draw_track = False
    x = 20
    direction = 'Right'
    offset2   = 0
    mouse_rel = (0,0)  # mouse relative movement
    click = False  # status of our internal 'mouse button'

    """
    def draw_track_time(time):
        font_title  = bmpfont.BmpFont(os.path.join(FONTDIR,"Exupery/Exupery.idx"))
        font_time = bmpfont.BmpFont(os.path.join(FONTDIR,"Prescott/Prescott.idx"))
        #surf_temp = pygame.Surface((len(time) + 1) * font_time.width, font_time.height)  # +1 for the colon
        surf_temp = pygame.Surface((50,120))
        #surf_temp.fill(WHITE)
        font_title.blit("time remaining", surf_temp,(54,0),usetextxy=0)
        font_time.blit(time, surf_temp,(0,14), usetextxy=0)
        surf_time = pygame.Surface.copy(surf_temp)
        surf_outp = pygame.Surface((400,240))
        surf_time.blit(surf_outp,(204,174))
        return(surf_outp)
    """
    
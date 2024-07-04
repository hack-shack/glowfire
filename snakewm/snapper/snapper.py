import datetime
import os
import platform
import pygame
import pygame_gui
from pygame_gui.core import ObjectID
from pygame_gui.elements import UILabel
from pygame_gui.elements import UIPanel
from pygame_gui.elements import UIStatusBar
from pygame_gui.elements import UIHorizontalSlider
from pygame_gui.elements.ui_image import UIImage
import re
import time
import subprocess

class Snapper(UIPanel):
    """ A widget panel that snaps out from the edge of the screen. """
    manager = None
    SCREENSIZE = (400,240)
    DIMS = (87,120)
    path = None

    BLACK = ((0,)*3)
    WHITE = ((255,)*3)

    def __init__(self,
                position,
                manager=manager,
                element_id="#pn_snapper"
                ):
        super().__init__(
            pygame.Rect(self.SCREENSIZE[0]-self.DIMS[0], 0, self.DIMS[0], self.DIMS[1]),
            object_id=ObjectID(class_id="@snapper_panel",
                               object_id="#snapper"
            ),
        )

        if platform.system() == 'Darwin':
            self.PLATFORM = 'Darwin'
        if platform.system() == 'Linux':
            self.PLATFORM = 'Linux'

        # Initialize main display surface to contain entire app UI.
        self.display_surf = UIImage(
            relative_rect=pygame.Rect((0, 0), self.DIMS),
            image_surface=pygame.Surface(self.DIMS).convert(),
            manager=manager,
            container=self,
            parent_element=self,
            object_id=ObjectID(class_id="@snapper_image",
                               object_id="#snapper_display_surface"
            )
        )

        # Initialize counter for framerate limiting.
        self.last_time = 0

        # Initialize text label for clock.
        self.time_label = UILabel(
            relative_rect=pygame.Rect(5,0,self.DIMS[0],32),
            text='00:00',
            manager=manager,
            container=self,
            parent_element=self,
            object_id=ObjectID(class_id="@snapper_clock_label",
                               object_id="#snapper_time_label"
            )
        )

        # Initialize text label for date.
        self.date_label = UILabel(
            relative_rect=pygame.Rect(5,27,self.DIMS[0],32),
            text='00-00',
            manager=manager,
            container=self,
            parent_element=self,
            object_id=ObjectID(class_id="@snapper_clock_label",
                               object_id="#snapper_date_label"
            )
        )

        # Initialize status bar to represent battery charge.
        batt_x = 4
        batt_y = 54
        batt_w = 69
        batt_h = 23
        self.battery_icon = UIStatusBar(
            relative_rect=pygame.Rect(batt_x,batt_y,batt_w,batt_h),
            manager=manager,
            container=self,
            parent_element=self,
            object_id=ObjectID(class_id="@snapper_statusbar",
                               object_id="#snapper_battery_statusbar"
            ),
            percent_method=self.get_battery_status
        )

        # Draw status glyph on battery's right side.
        self.battery_glyph = UILabel(
            relative_rect=pygame.Rect(batt_w+5,batt_y+2,20,20),
            text="+",
            manager=manager,
            container=self,
            parent_element=self,
            object_id=ObjectID(class_id="@snapper_label",
                               object_id="#snapper_battery_glyph"
            )
        )

        # Initialize status bar to represent wifi strength.
        wifi_x = 4
        wifi_y = 80
        wifi_w = 69
        wifi_h = 23
        self.battery_icon = UIStatusBar(
            relative_rect=pygame.Rect(wifi_x,wifi_y,wifi_w,wifi_h),
            manager=manager,
            container=self,
            parent_element=self,
            object_id=ObjectID(class_id="@snapper_statusbar",
                               object_id="#snapper_wifi_statusbar"
            ),
            percent_method=self.get_wifi_status
        )

        # Draw status glyph on wifi bar's right side.
        self.battery_glyph = UILabel(
            relative_rect=pygame.Rect(wifi_w+5,wifi_y+1,20,20),
            text="w",
            manager=manager,
            container=self,
            parent_element=self,
            object_id=ObjectID(class_id="@snapper_label",
                               object_id="#snapper_wifi_glyph"
            )
        )

    def update(self, delta):
        """ Every frame, do the following. """
        super().update(delta)
         # limit frame rate to 4 FPS
        if time.time() - self.last_time > 0.25:
            self.display_surf.image.blit(self.draw_widgets(),(0,0))
            self.last_time = time.time()

    def get_battery_status(self):
        if self.PLATFORM == 'Darwin':
            output = subprocess.run(['pmset','-g','batt'],capture_output=True)
            regex = re.compile('([0-9]{1,3})%;.*?$')
            for match in re.findall(regex, str(output.stdout)):
                output_int = int(match)
            return output_int
        if self.PLATFORM == 'Linux':
            output = subprocess.run(["cat","/sys/firmware/beepy/battery_percent"],capture_output=True)
            output_int = int(output.stdout)
            return output_int

    def get_wifi_status(self):
        # TODO: Get working.
        output_int = [100,100]
        if self.PLATFORM == 'Darwin':
            # TODO: wdutil works, but needs sudo
            output_int[0] = 100  # percentage; currently we substitute 100%
            output_int[1] = 100
            return(output_int[0])
        if self.PLATFORM == 'Linux':
            return(20)
            """
            try:
                regex = re.compile("^.*Quality=([0-9]{1,3})/([0-9]{1,3})\s")
                output = subprocess.run(["iwlist","scan"])
                matches = re.findall(regex, str(output.stdout))
                #print(matches[0])
                #print(matches[1])
                #return(matches[0])
                print('match')
                return(0)
            except:
                return(0)  # default to 0% if iwlist fails
            """

    def draw_widgets(self):
        """ Draw widget cluster. """
        widget_surface = pygame.Surface(self.DIMS)
        widget_surface.fill(self.WHITE)

        # Clock
        # --------------------------
        dt = datetime.datetime.now()
        short_time = dt.strftime("%H:%M")
        short_date = dt.strftime("%m-%d")
        self.time_label.set_text(short_time)
        self.date_label.set_text(short_date)

        # Load widget icons for snapper.
        """
        i_bluetooth = pygame.image.load(os.path.join(self.images_path,'bluetooth.png'))
        i_lora = pygame.image.load(os.path.join(self.images_path,'lora.png'))
        i_satellite = pygame.image.load(os.path.join(self.images_path,'satellite.png'))
        i_wifi = pygame.image.load(os.path.join(self.images_path,'wifi.png'))
        """

        # Arrange widget icons.
        """
        i_bluetooth.blit(surf,(40,40))
        i_wifi.blit(surf,(0,40))
        i_lora.blit(surf,(0,60))
        i_satellite.blit(surf,(40,60))
        """

        # Draw left and bottom frames for the snapper panel.
        pygame.draw.lines(surface  = widget_surface,
                          color    = 'black',
                          closed   = False,
                          points   = [(0,0),(0,self.DIMS[1]-1),
                                      (0,self.DIMS[1]-1),(self.DIMS[0],self.DIMS[1]-1)]
                          )

        return widget_surface

    def destroy(self):
        """ Kill the snapper panel. """
        self.visible=0
        self.kill()

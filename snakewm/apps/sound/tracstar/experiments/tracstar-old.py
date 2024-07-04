#!/usr/bin/python3
"""
Copyright (c) 2023 Asa Durkee. MIT License.
Demonstrates pygame on beepy. Runs as simulator when launched from desktop computer.
This was made after porting pygame to the beepy, but before porting snakeware.
Provided as an example of "bare metal" pygame programming,
without the overhead of snakeware and pygame_gui.
"""
# Prerequisites for Mac:
# $ /usr/bin/pip3 install pygame pendulum 

# IMPORTS 1 - These modules work on simulator and hardware
# =========================================================
import io    # talks to tty1 (on the memory lcd), the RP2040 devfs, and devtree model
import datetime
from math import ceil
import os
from os import listdir
from os import path
from os.path import isfile
import platform
import pygame
import subprocess
import bmpfont  # in lib folder
import audio_metadata  # in lib folder
import tbm_utils  # in lib folder

def is_raspi():
# Determine if we're on Raspi hardware, or a desktop computer (simulator).
# Disable certain hardware-related functions if in simulator.
    try:
        with io.open('/sys/firmware/devicetree/base/model', 'r') as m:
            if "raspberry pi" in m.read().lower():
                print("INFO : Firmware detected as raspi.")
                SYSTEM = "raspi"
                return True
    except Exception:
        print(Exception)
    return False

# GLOBAL VARIABLES
# =========================================================
BLACK = ((0,)*3)
WHITE = ((255,)*3)
LCDWIDTH  = 400
LCDHEIGHT = 240
REAL_PI   = is_raspi()
CWD       = path.dirname(__file__)
FONTDIR   = path.join(CWD,"data/fonts")
TEXTUREDIR= path.join(CWD,"data/textures")
MUSIC_DIR = path.join(CWD,"music")

# IMPORTS 2 - These modules require actual hardware
# =========================================================
if REAL_PI == True:
    print("INFO : Running on raspi hardware.")
    from gpiozero import Button    # for beepy sidebutton (GPIO 17 -> GND)
    #from lib import beepyled

# SETUP - SIDE BUTTON HANDLERS
# ==================================================
"""
How we trigger a pygame draw call with a GPIO button
----------------------------------------------------
The beepy side button is connected to Raspi Zero GPIO 17.
When you press the side button, it shorts to GND, going from HIGH to LOW.
gpiozero's when_pressed() watches for this HIGH->LOW transition.
When you release the side button, it is pulled up, going from LOW to HIGH.
gpiozero's when_released() watches for this LOW->HIGH transition.
gpiozero's when_pressed() and when_released() trigger a sort of "interrupt
    service routine" - the pressed() and released() functions.
We keep these functions simple and fast, and simply post an event to pygame.
"""
if REAL_PI == True:
    side_button = Button(17)

    SIDEBUTTON_PRESS = pygame.USEREVENT+0
    evt_sidebutton_press = pygame.event.Event(SIDEBUTTON_PRESS, message="Side button pressed.")

    SIDEBUTTON_RELEASE = pygame.USEREVENT+1
    evt_sidebutton_release = pygame.event.Event(SIDEBUTTON_RELEASE, message="Side button released.")

    def pressed():
        print("DEBUG: Side button pressed.")
        pygame.event.post(evt_sidebutton_press)

    def released():
        print("DEBUG: Side button released.")
        pygame.event.post(evt_sidebutton_release)

    side_button.when_pressed = pressed
    side_button.when_released = released


# FUNCTIONS - HARDWARE
# =========================================================
def get_audio_devices():
    devices = tuple(sdl2_audio.get_audio_device_names(capture_devices))
    return devices

# FUNCTIONS - SOFTWARE
# =========================================================
def list_music_folder(dirname):
    extensions_to_match = ['flac','m4a','mp3','wav']
    matching_files = []
    dict_file = {'abspath':0, 'name':0, 'extension':0, 'mtime':0}
    if os.path.isdir(dirname):
        for root,dirs,files in os.walk(dirname):
            for filename in files:
                for extension in extensions_to_match:
                    if os.path.splitext(filename)[1] == ("." + extension):
                        #matching_files.append({'abspath'    :   os.path.abspath(filename),
                        matching_files.append({'abspath'    :   os.path.abspath(os.path.join(dirname,filename)),
                                               'filename'   :   filename,
                                               'extension'  :   extension,
                                               'mtime'      :   os.path.getmtime(os.path.join(dirname,filename))})
                        print(os.path.abspath(filename))
        return(matching_files)
    if not os.path.isdir(dirname):
        os.mkdir(dirname)
        raise OSError("ERROR: Music directory does not exist. Created empty directory.")

def get_md_tags(file):
    print("INFO : Attempting to get metadata tags for file: " + file)
    md = audio_metadata.load(file)
    md_tags = {}
    md_tags['album'] = md['tags']['album'][0]
    md_tags['artist'] = md['tags']['artist'][0]
    md_tags['duration'] = md['tags']['duration'][0]
    md_tags['title'] = md['tags']['title'][0]
    md_tags['track_num'] = md['tags']['tracknumber'][0]
    print('Artist: ', md_tags['artist'])
    print('Title : ', md_tags['title'])
    print('Album : ', md_tags['album'])
    print('Track#: ', str(md_tags['track_num']))
    print('Duration: ', str(md_tags('duration')))
    return

def play_audio_file(file):
    try:
        pygame.mixer.init()
    except:
        print("ERROR: Unable to do pygame.mixer.init. Do you have a sound device connected?")
    try:
        pygame.mixer.music.load(file)
        #track_text = get_md_tags(file)
        pygame.mixer.music.set_volume(0.1)
        pygame.mixer.music.play()
        #current_track_marquee = track_text
        track_status = 'play'
        draw_track_list = False
    except:
        print("Couldn't open music.")
        track_status = 'stop'


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
    track_status = 'stop'
    current_track = ""
    current_track_marquee = ''
    draw_track_list = False
    draw_track = False
    x = 20
    direction = 'Right'
    offset2   = 0
    mouse_rel = (0,0)  # mouse relative movement
    click = False  # status of our internal 'mouse button'

    #if REAL_PI == True:
    #    bpy_led = beepyled.BeepyLed()
    pygame.init()
    running = True
    pygame.display.set_caption('Beepy Simulator')
    lcd = pygame.display.set_mode((400,240),depth=1)

    # can't have a mouse cursor visible if you need infinite relative mode
    # reference: https://www.pygame.org/ftp/contrib/input.html
    #pygame.mouse.set_cursor(*pygame.cursors.arrow)
    #cursor = pygame.SYSTEM_CURSOR_HAND
    #pygame.mouse.set_cursor(cursor)
    pygame.event.set_grab(1)

    # BITMAPPED FONTS - PNG font image, column/row indexed.
    # -----------------------------------------------------
    # The "PNG fonts" use the bmpfont module and are imple-
    # mented completely differently from TrueType fonts.
    # These fonts are easy to modify and are pixel-precise,
    # but they are best for simple text (gauges, displays).
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

    # SNAPPER WIDGETS
    # -----------------------------------------------------
    i_snapper = pygame.image.load("data/snapper.png")
    r_snapper = i_snapper.get_rect()
    s_snapper = pygame.Surface((r_snapper.w,r_snapper.h))

    i_battery = pygame.image.load("data/battery.png")
    i_volume = pygame.image.load("data/volume.png")
    i_satellite = pygame.image.load("data/satellite.png")
    i_lora = pygame.image.load("data/lora.png")
    i_wifi = pygame.image.load("data/wifi.png")
    i_bluetooth = pygame.image.load("data/bluetooth.png")

    clock = pygame.time.Clock()

    def draw_track_status(status):
        font_title  = bmpfont.BmpFont(os.path.join(FONTDIR,"Exupery/Exupery.idx"))
        font_status = bmpfont.BmpFont(os.path.join(FONTDIR,"Prescott/Prescott.idx"))
        surf_temp = pygame.Surface((154,63))
        surf_temp.fill(WHITE)
        font_title.blit("playback status",surf_temp,(2,0),usetextxy=0)
        font_status.blit(status, surf_temp,(0,14),usetextxy=0)
        surf_status = pygame.Surface.copy(surf_temp)
        lcd.blit(surf_status,(1,174))

    def draw_track_time(time):
        font_title  = bmpfont.BmpFont(os.path.join(FONTDIR,"Exupery/Exupery.idx"))
        font_time = bmpfont.BmpFont(os.path.join(FONTDIR,"Prescott/Prescott.idx"))
        #surf_temp = pygame.Surface((len(time) + 1) * font_time.width, font_time.height)  # +1 for the colon
        surf_temp = pygame.Surface((400,240))
        surf_temp.fill(WHITE)
        font_title.blit("time remaining", surf_temp,(54,0),usetextxy=0)
        font_time.blit(time, surf_temp,(0,14), usetextxy=0)
        surf_time = pygame.Surface.copy(surf_temp)
        lcd.blit(surf_time,(204,174))

    def scroll_track_text(text,x,y,direction,fontface=font_profont14):
        # render text to a surface using specified font
        surf_text = font_profont14.render(text, False, BLACK)
        # is the text surface wider than the scrollbox?
        """
        # This commented-out section will scroll the track text, using the BmpFont class instead. ("PNG fonts")
        temp_surf = pygame.Surface(([len(text) * bmpfont_exupery.width,bmpfont_exupery.height]))
        temp_surf.fill(WHITE)
        bmpfont_exupery.blit(text,temp_surf)
        surf_text = pygame.Surface.copy(temp_surf)
        """
        width  = pygame.Surface.get_width(surf_text)
        velocity  = 0.8
        if x < 0:
            direction = 'Right'
        elif x > (LCDWIDTH - width):
            direction = 'Left'
        if direction == 'Right':
            x += velocity
        if direction == 'Left':
            x -= velocity
        lcd.blit(surf_text, (x,y))
        return x, direction


    def draw_playbar(x,y,width,direction,offset_counter,height=16):
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
        lcd.blit(surf,(x,y))

        if x < 0:
            direction = 'Right'
        elif x > (LCDWIDTH - width):
            direction = 'Left'
        if direction == 'Right':
            x += velocity
        if direction == 'Left':
            x -= velocity

        #lcd.blit(surf, (x,y))
        return offset_counter

    def draw_music_controls(x,y,width,height):
        border  = 0
        padding = 5
        scrubber_height = 15
        bounding_box = pygame.Rect((x,y),width,height)
        scrubber = pygame.Rect((bounding_box.padding,(bounding_box.height / 2)),bounding_box.width - (padding * 2),scrubber_height)
        pass

    def draw_snapper_widgets():
        r_snapper.topright = 400,0
        pygame.draw.rect(lcd,WHITE,r_snapper)
        lcd.blit(i_snapper,r_snapper)
        snapper_clock_text = datetime.datetime.now().strftime('%H:%M:%S')
        bmpfont_dans_sans.blit(snapper_clock_text,lcd,(17,0))
        draw_help_panel()

    def draw_help_panel():
        help = ["Press Q to quit.",
                    "L to list music files;",
                    "O to open one."]
        pygame.draw.rect(lcd, BLACK,(0,0,270,130))
        pygame.draw.rect(lcd, WHITE,(0,0,270,128))
        for count, line in enumerate(help):
            bmpfont_exupery.blit(line, lcd, (1,1 + count))

    i_playpause = pygame.image.load("data/playpause.png")
    i_next = pygame.image.load("data/next.png")
    i_last = pygame.image.load("data/last.png")
    r_playpause = i_playpause.get_rect()
    r_next = i_next.get_rect()
    r_last = i_last.get_rect()

# MAIN LOOP
# =========================================================
    while running:
        lcd.fill(WHITE)

        for event in pygame.event.get():
            print(event)
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.MOUSEMOTION:
                mouse_rel = (event.rel[0],event.rel[1])
            if event.type == pygame.MOUSEBUTTONDOWN:
                click = True
            if event.type == pygame.KEYDOWN:
                # pygame key reference: https://www.pygame.org/docs/ref/key.html#key-constants-label

                # Quit Key
                # -----------------------------------------
                if event.key == pygame.K_q:
                    running = False  # quit

                # Movement and Selection Keys
                # -----------------------------------------
                elif event.key == pygame.K_y:
                    click = True  # "select" key
                # Up/Down - Beepy Keyboard
                elif event.key == pygame.K_h:
                    track_list_move = 'Up'
                elif event.key == pygame.K_b:
                    track_list_move = 'Down'
                # Up/Down - PC Keyboard, and Beepy Fallback (for firmware setting touchpad as arrow keys)
                elif event.key == pygame.K_UP:
                    track_list_move = 'Up'
                elif event.key == pygame.K_DOWN:
                    track_list_move = 'Down'

                # Function Keys
                # -----------------------------------------
                # L : List music files
                elif event.key == pygame.K_l:
                    if track_status == 'list':
                        pass
                    elif track_status != 'list':
                        track_status = 'list'
                        draw_track_list = True
                        try:
                            track_list = list_music_folder(MUSIC_DIR)
                        except OSError as error:
                            print("ERROR: " + str(error))

                # P: Playpause
                elif event.key == pygame.K_p:
                    if track_status == 'play':
                        if pygame.mixer.get_init() != None:      # mixer is running
                            pygame.mixer.music.pause()
                            track_status = 'pause'
                    elif track_status != 'play':
                        if pygame.mixer.get_init() != None:   # mixer is running
                            pygame.mixer.music.unpause()
                            track_status = 'play'
                elif event.key == pygame.K_r:  # R : resume play
                    pygame.mixer.music.unpause()
                    track_status = 'play'
                    draw_track_list = False

                # Volume Keys
                # --------------------------------------------------
                elif event.key == pygame.K_m:  # M : volume increase
                    if (volume_index + 1) < len(volume_levels):
                        volume_index += 1
                        volume = volume_levels[volume_index]
                    pygame.mixer.music.set_volume(volume)
                    print("DEBUG : Volume : " + str(volume))
                elif event.key == pygame.K_n:  # N : volume decrease
                    if (volume_index - 1) >= 0:  # start of index
                        volume_index -= 1
                        volume = volume_levels[volume_index]
                    pygame.mixer.music.set_volume(volume)
                    print("DEBUG : Volume : " + str(volume))

            # Front Buttons (Q20 keyboard, w4ilun firmware)
            #  ------------------------------------------------
            # | Call Start |  Logo  | [ ] |  Back  |  Call End |
            #  ------------------------------------------------
            # Call Start button on beepy / Left Ctrl on PC
            if event.type == pygame.KEYUP:
                if event.key == pygame.K_LCTRL:
                    draw_snapper=False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LCTRL:
                    draw_snapper=True

            # Logo button on beepy
            if event.type == pygame.KEYUP:
                if event.key == pygame.K_PAGEDOWN:
                    draw_snapper=False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_PAGEDOWN:
                    draw_snapper=True

            # Back button on beepy
            if event.type == pygame.K_PAGEUP:
                pass

            # Call End button on beepy
            if event.type == pygame.K_MENU:
                pass


            # Side Button (when running on beepy hardware)
            # --------------------------------------------
            if REAL_PI == True:
                if event.type == SIDEBUTTON_PRESS:
                    print(event.message)
                    draw_snapper = True
                if event.type == SIDEBUTTON_RELEASE:
                    print(event.message)
                    draw_snapper = False
            if not REAL_PI == True:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:  # spacebar on desktop opens the Snapper
                        draw_snapper = True
                if event.type == pygame.KEYUP:
                    if event.key == pygame.K_SPACE:
                        draw_snapper = False

        # Select current track in list, based on mouse movement
        # -----------------------------------------------------
        y_sensitivity = 5  # integer, min 1, lower is higher sensitivity
        if mouse_rel[1] < -(y_sensitivity):  # up
            print("UP")
            track_list_move = 'Up'
        if mouse_rel[1] > y_sensitivity:  # down
            print("DOWN")
            track_list_move = 'Down'

        # Draw track list, with header and items
        # --------------------------------------
        #if draw_track_list == True:
        if track_status == 'list':
            lcd.blit(font_profont14.render('Track List', False, BLACK),(0,0))
            if any(track_list):
                for index, track_file_md in enumerate(track_list):
                    #print("Track metadata: " + track_file_md['abspath'])
                    #print("Track filename: " + track_file_md['filename'])
                    track_text = font_profont14.render(str(track_file_md['filename']), False, BLACK)
                    lcd.blit(track_text, (14,(24 + (index * 24))))
        #elif draw_track_list == False:
        elif track_status == 'play':
            # TODO: clean up drawn items
            pass

        # Select track based on mouse movement
        # ------------------------------------
        if draw_track_list == True:
            if any(track_list):
                if track_list_move == 'Up':
                    if selected_track == 0:
                        selected_track = (len(track_list)-1)
                        print(selected_track)
                    else:
                        selected_track -= 1
                        print(selected_track)
                if track_list_move == 'Down':
                    if selected_track == (len(track_list)-1):
                        selected_track = 0
                        print(selected_track)
                    else:
                        selected_track += 1
                        print(selected_track)
                else:
                    pass
            track_list_move = ''
        else:
            pass

        # Hilite selected track
        # ---------------------
        if track_status == 'list':
            if any(track_list):
                pygame.draw.rect(lcd,BLACK,(0,(26 + (selected_track * 24)),13,14))
        else:
            pass

        # Play selected track
        # -------------------
        if any(track_list):
            if click == True:
                print("Click")
                click = False
                filename = [d.get('filename') for d in track_list][selected_track]
                print(filename)
                abspath = [d.get('abspath') for d in track_list][selected_track]
                file_to_play = abspath
                print("INFO : Playing: " + file_to_play)
                current_track_marquee = filename
                play_audio_file(file_to_play)
            else:
                pass


        # Draw name of currently playing track
        # ------------------------------------
        x, direction = scroll_track_text(current_track_marquee,x,137,direction)

        # Draw track status
        # -----------------
        if track_status == 'stop':
            draw_track_status("stop")
        elif track_status == 'list':
            draw_track_status("list")
        elif track_status == 'scan':
            draw_track_status("scan")
        elif track_status == 'load':
            draw_track_status("load")
        elif track_status == 'play':
            draw_track_status("Play")
            draw_track_time(datetime.datetime.now().strftime('%M:%S'))
        elif track_status == 'pause':
            draw_track_status("PaUS")

        # Draw magnetic-tape "playbar"
        # ----------------------------
        offset2 = draw_playbar(3,156,394,'Left',offset2)

        # Draw mouse input widget
        # -----------------------
        """
        mouse_scale = 2  # integer; how much to scale input relative values
        mouse_abs[0] += (mouse_rel[0] * mouse_scale)
        mouse_abs[1] += (mouse_rel[1] * mouse_scale)
        if mouse_abs[0] < 0:  # runs off left of screen
            mouse_abs[0] = 0
        if mouse_abs[1] < 0:  # runs off top of screen
            mouse_abs[1] = 0
        if mouse_abs[0] > LCDWIDTH:
            mouse_abs[0] = LCDWIDTH  # clamp to screen right
        if mouse_abs[1] > LCDHEIGHT:
            mouse_abs[1] = LCDHEIGHT  # clamp to screen bottom
        """
    

        # Draw snapper
        # ------------
        if draw_snapper == True:
            draw_snapper_widgets()

        pygame.display.update()
        #clock.tick(60) # framerate
        pygame.time.wait(100)
        mouse_rel = (0,0)
    pygame.quit()
    subprocess.run(['chvt','1'])    # Change beepy virtual terminal to tty1 at quit

# ENTRY POINT
# =============================================================================
if REAL_PI == True:
    uid = os.geteuid()
    print("INFO : UID is: " + str(uid))
    if os.geteuid() == 0:
        print("INFO : Running as root user. This is expected behavior.")
    if os.geteuid() != 0:
        exit("ERROR: You must run this script as a root user, or with sudo.")

    """
    # DirectFB arguments: 'DFBARGS=system=fbdev,fbdev=/dev/fb1,graphics-vt,no-cursor;export DFBARGS'
    os.environ['DFBARGS'] = 'system=fbdev,fbdev=/dev/fb1,graphics-vt,no-cursor'
    # TODO: if arch is arm64: 'LD_LIBRARY_PATH=/usr/local/lib/aarch64-linux-gnu/;export LD_LIBRARY_PATH'
    os.environ['LD_LIBRARY_PATH'] = '/usr/local/lib/aarch64-linux-gnu/'
    # TODO: if arch is arm32: 'LD_LIBRARY_PATH=/usr/local/lib/arm-linux-gnueabihf/;export LD_LIBRARY_PATH'
    #os.environ['LD_LIBRARY_PATH'] = '/usr/local/lib/arm-linux-gnueabihf/'
    """


if __name__=="__main__":
   main()

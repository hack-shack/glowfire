"""
candLED: LED controller for SQFMI beepy
(c) 2024 Asa Durkee. MIT License.
"""
import os
import i18n
import pygame
import pygame_gui
from pygame_gui.core import ObjectID
from pygame_gui.elements import UIButton
from pygame_gui.elements import UIHorizontalSlider
from pygame_gui.elements import UILabel
from pygame_gui.elements import UIWindow

class CandLED(UIWindow):
    def __init__(self, position, manager):
        super().__init__(
            pygame.Rect(position, (332,232)),
            manager=manager,
            window_display_title="candLED",
            object_id="#candled",
            resizable=False
        )

        i18n.load_path.append(os.path.join(os.path.dirname(__file__),"data/translations"))

        self.SLEFT=55    # slider pixels from left side
        self.SHEIGHT=26  # slider height
        self.SWIDTH=100  # slider width
        self.SDIMS=(self.SWIDTH,self.SHEIGHT)  # slider dimensions
        self.R_Y=30   # red slider Y coord
        self.G_Y=60  # green slider Y coord
        self.B_Y=90  # blue slider Y coord
        self.W_Y=120  # white slider Y coord (keyboard backlight)
        self.Z_Y=150  # zero button Y coord (raspi zero ACT LED)
        self.LDIMS=(50,30)  # label dimensions
        self.L_Y_OFFSET=3  # number of pixels up Y to move label

        self.COL2X=180  # x offset for column 2 (right side widgets)

        try:
            with open('/sys/class/leds/ACT/brightness') as f: b=f.read()
        except:
            print('DEBUG: Could not open Raspi Zero LED sysfs file.')
            print('DEBUG: Substituting LED value of OFF.')
            b=0
        self.PI_LIT = False
        if b==0:
            self.PI_LIT = False
        if b==255:
            self.PI_LIT = True


        # COLUMN 1: Left widgets with RGBW color controls
        # ===================================================
        # RED SLIDER
        self.r_slider = UIHorizontalSlider(
            relative_rect = pygame.Rect((self.SLEFT,self.R_Y),self.SDIMS),
            start_value=0,
            value_range=(0,255),
            manager=manager,
            container=self,
            object_id=ObjectID(class_id="@candled_slider",
                               object_id="#candled_r_slider"
            ),
            click_increment=10
        )

        # GREEN SLIDER
        self.g_slider = UIHorizontalSlider(
            relative_rect = pygame.Rect((self.SLEFT,self.G_Y),self.SDIMS),
            start_value=0,
            value_range=(0,255),
            manager=manager,
            container=self,
            object_id=ObjectID(class_id="@candled_slider",
                               object_id="#candled_g_slider"
            ),
            click_increment=10
        )

        # BLUE SLIDER
        self.b_slider = UIHorizontalSlider(
            relative_rect = pygame.Rect((self.SLEFT,self.B_Y),self.SDIMS),
            start_value=0,
            value_range=(0,255),
            manager=manager,
            container=self,
            object_id=ObjectID(class_id="@candled_slider",
                               object_id="#candled_b_slider"
            ),
            click_increment=10
        )

        # WHITE SLIDER (KEYBOARD BACKLIGHT LEDS)
        self.w_slider = UIHorizontalSlider(
            relative_rect = pygame.Rect((self.SLEFT,self.W_Y),self.SDIMS),
            start_value=0,
            value_range=(0,255),
            manager=manager,
            container=self,
            object_id=ObjectID(class_id="@candled_slider",
                               object_id="#candled_w_slider"
            ),
            click_increment=10
        )

        # ZERO BUTTON (RASPBERRY PI ONBOARD LED)
        self.z_button = UIButton(
            relative_rect = pygame.Rect((self.SLEFT+1,self.Z_Y),(98,24)),
            text=i18n.t('toggle'),
            manager=manager,
            container=self,
            tool_tip_text=i18n.t('tooltip_pi_led'),
            tool_tip_object_id="#tooltop_pi_led",
            object_id=ObjectID(class_id="@candled_button",
                               object_id="#candled_z_button"
            )
        )

        # SLIDER LABEL
        self.slider_label = UILabel(relative_rect=pygame.Rect((self.SLEFT-self.LDIMS[0],self.R_Y-30),(130,30)),
            text=i18n.t('led_brightness'),
            manager=manager,
            container=self,
            object_id=ObjectID(class_id="@candled_label",
                               object_id="#candled_header_label")
        )

        # RED LABEL
        self.r_label = UILabel(relative_rect=pygame.Rect((self.SLEFT-self.LDIMS[0],self.R_Y-self.L_Y_OFFSET),self.LDIMS),
            text=i18n.t('red'),
            manager=manager,
            container=self,
            object_id=ObjectID(class_id="@candled_label",
                               object_id="#candled_led_label")
        )

        # GREEN LABEL
        self.g_label = UILabel(relative_rect=pygame.Rect((self.SLEFT-self.LDIMS[0],self.G_Y-self.L_Y_OFFSET),self.LDIMS),
            text=i18n.t('green'),
            manager=manager,
            container=self,
            object_id=ObjectID(class_id="@candled_label",
                               object_id="#candled_led_label")
        )

        # BLUE LABEL
        self.b_label = UILabel(relative_rect=pygame.Rect((self.SLEFT-self.LDIMS[0],self.B_Y-self.L_Y_OFFSET),self.LDIMS),
            text=i18n.t('blue'),
            manager=manager,
            container=self,
            object_id=ObjectID(class_id="@candled_label",
                               object_id="#candled_led_label")
        )

        # KEYBOARD LABEL
        self.w_label = UILabel(relative_rect=pygame.Rect((self.SLEFT-self.LDIMS[0],self.W_Y-self.L_Y_OFFSET),self.LDIMS),
            text=i18n.t('kbd'),
            manager=manager,
            container=self,
            object_id=ObjectID(class_id="@candled_label",
                               object_id="#candled_led_label")
        )

        # PI LABEL
        self.w_label = UILabel(relative_rect=pygame.Rect((self.SLEFT-self.LDIMS[0],self.Z_Y-self.L_Y_OFFSET),self.LDIMS),
            text=i18n.t('pi'),
            manager=manager,
            container=self,
            object_id=ObjectID(class_id="@candled_label",
                               object_id="#candled_led_label")
        )

        # COLUMN 2: Right column with presets
        # =======================================================

        # PRESETS LABEL
        self.presets_label = UILabel(relative_rect=pygame.Rect((self.COL2X,self.R_Y-30),(130,30)),
            text=i18n.t('presets'),
            manager=manager,
            container=self,
            object_id=ObjectID(class_id="@candled_label",
                               object_id="#candled_header_label")
        )

        self.candle_button = UIButton(
            relative_rect=pygame.Rect((self.COL2X,31),(110,24)),
            text=i18n.t('candlite'),
            manager=manager,
            container=self,
            tool_tip_text=i18n.t('tooltip_candle'),
            tool_tip_object_id="#candled_tooltip",
            object_id=ObjectID(class_id='@candled_button',
                               object_id='#candled_button_candle')
        )

        self.frontlite_button = UIButton(
            relative_rect=pygame.Rect((self.COL2X,61),(110,24)),
            text=i18n.t('frontlite'),
            manager=manager,
            container=self,
            tool_tip_text=i18n.t('tooltip_front'),
            object_id=ObjectID(class_id='@candled_button',
                               object_id='#candled_button_frontlite')
        )

        self.all_off_button = UIButton(
            relative_rect=pygame.Rect((self.COL2X,self.Z_Y),(110,24)),
            text=i18n.t('leds_off'),
            manager=manager,
            container=self,
            tool_tip_text=i18n.t('tooltip_leds_off'),
            object_id=ObjectID(class_id='@candled_button',
                               object_id='#candled_button_off')
        )

    # FUNCTIONS
    # =======================================================

    def set_rled(self,red):
        rled_sysfs = '/sys/firmware/beepy/led_red'
        led_power_sysfs = '/sys/firmware/beepy/led'
        r = open(rled_sysfs,'a')
        r.write(str(red))
        r.close()
        p = open(led_power_sysfs,'a')
        p.write(str(1))
        p.close()

    def set_gled(self,green):
        gled_sysfs = '/sys/firmware/beepy/led_green'
        led_power_sysfs = '/sys/firmware/beepy/led'
        r = open(gled_sysfs,'a')
        r.write(str(green))
        r.close()
        p = open(led_power_sysfs,'a')
        p.write(str(1))
        p.close()

    def set_bled(self,blue):
        bled_sysfs = '/sys/firmware/beepy/led_blue'
        led_power_sysfs = '/sys/firmware/beepy/led'
        r = open(bled_sysfs,'a')
        r.write(str(blue))
        r.close()
        p = open(led_power_sysfs,'a')
        p.write(str(1))
        p.close()

    def set_wled(self,white):
        wled_sysfs = '/sys/firmware/beepy/keyboard_backlight'
        led_power_sysfs = '/sys/firmware/beepy/led'
        f = open(wled_sysfs,'a')
        f.write(str(white))
        f.close()
        p = open(led_power_sysfs,'a')
        p.write(str(1))
        p.close()

    def turn_off_zled(self):
        zled_sysfs = '/sys/class/leds/ACT/brightness'
        f = open(zled_sysfs,'a')
        f.write(str(0))
        f.close()

    def toggle_zled(self):
        """ Raspberry Pi Zero 2W 'ACT' LED.
            0 = off. All other ints set full brightness. """
        zled_sysfs = '/sys/class/leds/ACT/brightness'
        if self.PI_LIT == False:
            try:
                f = open(zled_sysfs,'a')
                f.write(str(255))
                f.close()
                self.PI_LIT = True
            except:
                print('ERROR: unable to turn on Pi Zero LED.')
        elif self.PI_LIT == True:
            try:
                f = open(zled_sysfs,'a')
                f.write(str(0))
                f.close()
                self.PI_LIT = False
            except:
                print('ERROR: unable to turn off Pi Zero LED.')

    def process_event(self, event):
        super().process_event(event)

        if event.type == pygame.USEREVENT:
            if event.user_type == pygame_gui.UI_HORIZONTAL_SLIDER_MOVED:
                if event.ui_object_id == '#candled.#candled_r_slider':
                    self.set_rled(event.value)
            if event.user_type == pygame_gui.UI_HORIZONTAL_SLIDER_MOVED:
                if event.ui_object_id == '#candled.#candled_g_slider':
                    self.set_gled(event.value)
            if event.user_type == pygame_gui.UI_HORIZONTAL_SLIDER_MOVED:
                if event.ui_object_id == '#candled.#candled_b_slider':
                    self.set_bled(event.value)
            if event.user_type == pygame_gui.UI_HORIZONTAL_SLIDER_MOVED:
                if event.ui_object_id == '#candled.#candled_w_slider':
                    self.set_wled(event.value)
            if event.user_type == pygame_gui.UI_BUTTON_PRESSED:
                    if event.ui_object_id == "#candled.#candled_z_button":
                        self.toggle_zled()
                    if event.ui_object_id == "#candled.#candled_button_candle":
                        self.set_rled(30)
                        self.set_gled(8)
                        self.set_bled(0)
                        self.set_wled(0)
                    if event.ui_object_id == "#candled.#candled_button_frontlite":
                        self.set_rled(200)
                        self.set_gled(200)
                        self.set_bled(200)
                        self.set_wled(0)
                    if event.ui_object_id == "#candled.#candled_button_off":
                        self.set_rled(0)
                        self.set_gled(0)
                        self.set_bled(0)
                        self.set_wled(0)
                        self.turn_off_zled()
                        self.PI_LIT = False
                        self.r_slider.set_current_value(0)
                        self.g_slider.set_current_value(0)
                        self.b_slider.set_current_value(0)
                        self.w_slider.set_current_value(0)

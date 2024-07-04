"""
Takes an input image, scales it to no larger than the beepy screen,
and converts it to black-and-white (1-bit) with several diffusion methods.

Requires https://github.com/hbldh/hitherdither
pip install git+https://www.github.com/hbldh/hitherdither
"""

import os
import i18n
import pygame
from pygame import event
import pygame_gui
from pygame_gui.core import ObjectID
from pygame_gui.elements.ui_button import UIButton
from pygame_gui.elements.ui_image import UIImage
from pygame_gui.elements.ui_window import UIWindow
import time

from PIL import Image

class DitherBox(UIWindow):
    app_dimensions = (370,210)

    def __init__(self, position, manager):
        super().__init__(
            rect=pygame.Rect(position, self.app_dimensions),
            manager=manager,
            window_display_title='ditherbox',
            object_id=ObjectID(class_id="@ditherbox_window",
                               object_id="#ditherbox"
            )
        )
        self.btn_load_image = UIButton(
            relative_rect = pygame.Rect((0,0),(160,25)),
            text='load image',
            manager=manager,
            container=self,
            parent_element=self,
            object_id=ObjectID(class_id="@ditherbox_button",
                               object_id="#ditherbox_btn_load_image"
            )
        )
        self.btn_dither_stucki = UIButton(
            relative_rect = pygame.Rect((0,50),(160,25)),
            text='stucki',
            manager=manager,
            container=self,
            parent_element=self,
            object_id=ObjectID(class_id="@ditherbox_button",
                               object_id="#btn_dither_stucki"
            ),
            tool_tip_text=i18n.t("desc_stucki"),
        )

        self.btn_dither_floyd_steinberg = UIButton(
            relative_rect = pygame.Rect((0,78),(160,25)),
            text='floyd-steinberg',
            manager=manager,
            container=self,
            parent_element=self,
            object_id=ObjectID(class_id="@ditherbox_button",
                               object_id="#btn_dither_floyd_steinberg"
            ),
            tool_tip_text=i18n.t("desc_floyd_steinberg"),
        )

        self.btn_dither_atkinson = UIButton(
            relative_rect = pygame.Rect((0,105),(160,25)),
            text='atkinson',
            manager=manager,
            container=self,
            parent_element=self,
            object_id=ObjectID(class_id="@ditherbox_button",
                               object_id="#btn_dither_atkinson"
            ),
            tool_tip_text=i18n.t("desc_atkinson")
        )

        self.source_image_dir = os.path.join("")
        self.dest_image_dir = os.path.join("")

        i18n.load_path.append(os.path.join(os.path.dirname(__file__),"data/translations"))



        self.last_time = 0

    def open_image(self):
        """ Display a file open dialog box. """
        self.open_image = pygame_gui.windows.UIFileDialog(
            rect=pygame.Rect(0,0, 300, 180),
            manager=manager,
            window_title=i18n.t("select_source_image"),
            allowed_suffixes=["gif","jpg","png"],
            initial_file_path=self.source_image_dir,
            allow_picking_directories=True,
            object_id=ObjectID(class_id="@ditherbox_filedialog",
                                object_id="#souce_image_picker"
            )
        )

    def process_event(self, event):
        super().process_event(event)
        if event.type == pygame.USEREVENT:
                if event.user_type == pygame_gui.UI_BUTTON_PRESSED:
                    if event.ui_object_id == "#ditherbox.#ditherbox_btn_load_image":
                        open_image()
                        #self.kill()

    def update(self, delta):
        try:
            super().update(delta)
            # limit frame rate to 4 FPS
            if time.time() - self.last_time > 0.25:
                #self.draw_ram()
                #self.last_time = time.time()
                pass
            #self.dsurf.image.blit(self.ram, (0, 0))
        except:
            raise
    
    def quit():
        self.kill()
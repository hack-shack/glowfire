""" Documentation browser for snakeware. """

import os
import re
import pygame
import pygame_gui
from pygame_gui.core import ObjectID
from pygame_gui.elements.ui_button import UIButton
from pygame_gui.elements.ui_drop_down_menu import UIDropDownMenu
from pygame_gui.elements.ui_panel import UIPanel

path = os.path.dirname(os.path.abspath(__file__))

def appname(x):
    l = x.split("/")
    return l[-2]

class Docs(pygame_gui.elements.UIPanel):
    def __init__(self, pos, manager):
        super().__init__(
            pygame.Rect(0,0,400,240),
            manager=manager,
            object_id=ObjectID(class_id="@docs_window",object_id="#docs")
        )
        self.DIMS = 400,240
        self.langcode = self.ui_manager.get_locale()

        self.files = self.getdocs()
        self.last = self.files[0][0]

        self.menu = UIDropDownMenu(
            options_list=[p for p, q in self.files],
            starting_option=self.last,
            relative_rect=pygame.Rect(self.DIMS[0]-130-24,0,130,24),
            manager=manager,
            container=self,
        )

        self.menu.current_state.should_transition = True

        self.textbox = pygame_gui.elements.UITextBox(
            "",
            relative_rect=pygame.Rect(0, 24, 400, 240-24),
            manager=manager,
            object_id=ObjectID(class_id="@docs_textbox",object_id="#docs_textbox_main_content"),
            container=self,
            anchors={
                "left": "left",
                "right": "right",
                "top": "top",
                "bottom": "bottom",
            },
            allow_split_dashes=True
        )
        self.last = 0
        if self.langcode == "ja":
            self.textbox.allow_split_dashes=False
            self.textbox.line_spacing=1.3

        self.button_close = UIButton(
            relative_rect=pygame.Rect(376,0,24,24),
            text='',
            manager=manager,
            container=self,
            parent_element=self,
            object_id=ObjectID(class_id="@docs_button",
                               object_id="#docs_button_close"
            )
        )

    def getdocs(self):
        apps_dir = os.path.abspath(os.path.join(path,'../..'))
        regex = re.compile(r"README_{0,1}([a-z]{0,2}).md",flags=re.IGNORECASE)
        readmes = []
        for root, dirs, files in os.walk(apps_dir, topdown=False):
            localized_readme = None
            english_readme = None

            for filename in files:
                if filename.lower() == f"readme_{self.langcode}.md":
                    localized_readme = filename
                elif filename.lower() == "readme.md":
                    english_readme = filename

            if localized_readme:
                readmes.append((appname(os.path.join(root,localized_readme)), os.path.join(root,localized_readme)))
            elif english_readme:
                readmes.append((appname(os.path.join(root,english_readme)), os.path.join(root,english_readme)))

        readmes.sort(key=lambda r: r[0])
        return readmes

    def process_event(self, event):
        super().process_event(event)
        if event.type == pygame.USEREVENT:
            if event.user_type == pygame_gui.UI_BUTTON_PRESSED:
                if event.ui_object_id == "#docs.#docs_button_close":
                    self.kill()

    def update(self, time_delta):
        super().update(time_delta)

        n = self.menu.selected_option
        if n == self.last:
            return
        self.last = n
        s = ""

        locale = self.ui_manager.get_locale()
        #print('DEBUG: locale: ' + locale)
        for i in range(len(self.files)):
            if self.files[i][0] == n:
                for l in open(self.files[i][1]):
                    x = l.strip()
                    if len(x) > 1 and x[0] == "#":
                        #x = "<b><u>" + x[1:] + " </u></b>"
                        if locale in ['en','fr']:
                            x = "<font face=ComputerModern><font pixel_size=32><b>" + x[2:] + "</b></font></font>"
                        elif locale == "ja":
                            x = "<font face=KH-Dot-Hibiya-32><font pixel_size=32>" + x[2:] + "</font></font>"
                    if locale in ['en','fr']:
                        s += "<font face=ComputerModern><font pixel_size=20>" + x + "</font></font><br>"
                    elif locale == "ja":
                        s += "<font face=KH-Dot-Hibiya-24><font pixel_size=24>" + x + "</font></font><br>"


        self.set_text(s)

    def set_text(self, text):
        self.textbox.html_text = text
        #self.textbox.html_text = "<font face=ComputerModern><font pixel_size=12>" + text + "</font></font>"
        self.textbox.rebuild()

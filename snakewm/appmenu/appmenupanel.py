"""
App menu panel containing a list of all apps or subdirectories in the
current directory.
"""
import i18n
import os
import pygame
import pygame_gui
from pygame_gui.core import ObjectID

from pygame_gui.elements import UIPanel
from pygame_gui.elements import UIButton

# button dimensions
BUTTON_DIMS = (125, 25) # 104,25

class AppMenuPanel(UIPanel):
    manager = None
    pos = None
    path = None

    # the elements field is a dict object containing the structure of
    # the current directory and all subdirectories. If a value is None,
    # that means its corresponding key represents an app.
    elements = None

    # sub panel created when a directory button is hovered
    sub = None

    def __init__(self, manager, pos, path, elements, loadfunc):
        """
        manager - UIManager to manage this panel
        pos - position indices to start drawing this panel at
        path - the directory this panel represents
        elements - list of elements in this directory
        """
        super().__init__(
            relative_rect = pygame.Rect(
                (pos[0] * BUTTON_DIMS[0], pos[1] * BUTTON_DIMS[1]),
                (BUTTON_DIMS[0] + 0, BUTTON_DIMS[1] * len(elements.keys()) + 0),
            ),
            starting_height=100,  # floats at this level in the element stack
            object_id=ObjectID(class_id="@appmenupanel_panel",
                                object_id="#appmenupanel"
            )
        )
        #print('DEBUG: starting language: ' + str(manager._locale))
        self.pos = pos
        self.path = path
        self.elements = elements
        self.loadfunc = loadfunc

        # sorted list of element keys to generate the panel from
        self.element_keys = sorted(list(elements.keys()))

        # Load dictionary with language translations.
        i18n.load_path.append('snakewm/appmenu/data/translations/')
        i18n.set('filename_format','{locale}.{format}')

        # Generate buttons.
        for i in range(len(self.element_keys)):
            UIButton(
                pygame.Rect((0, i * BUTTON_DIMS[1]), BUTTON_DIMS),
                text=self.element_keys[i],
                manager=manager,
                container=self,
                object_id=ObjectID(class_id="@appmenupanel_button",
                                   object_id="#menu-" + self.path.replace(".", "-"))
            )

    def process_event(self, event):
        if event.type != pygame.USEREVENT:
            return

        if event.user_type == pygame_gui.UI_BUTTON_PRESSED and event.ui_object_id == (
            "#appmenupanel.#menu-" + self.path.replace(".", "-")
        ):
            # open clicked app
            uitext = event.ui_element.text

            if self.elements[uitext] == None:
                self.loadfunc(self.path + "." + uitext)
                #print("DEBUG: App opened.")
                appmenuclose_event = pygame.event.Event(pygame.USEREVENT,
                                        ui_element="appmenupanel",
                                        ui_object_id="#appmenupanel",
                                        user_type="APPMENU_PANEL_CLOSED",
                                        message="AppMenuPanel_closed.")
                pygame.event.post(appmenuclose_event)

        if (
            event.user_type == pygame_gui.UI_BUTTON_ON_HOVERED
            and event.ui_object_id == ("#appmenupanel.#menu-" + self.path.replace(".", "-"))
        ):
            uitext = event.ui_element.text

            if self.elements[uitext] != None:
                # first destroy the active sub panel
                if self.sub is not None:
                    self.sub.destroy()

                # next open a new sub panel
                self.sub = AppMenuPanel(
                    self.ui_manager,
                    (self.pos[0] + 1, self.pos[1] + self.element_keys.index(uitext)),
                    self.path + "." + uitext,
                    self.elements[uitext],
                    self.loadfunc,
                )

    def destroy(self):
        """
        Recursively kill this panel and all sub panels.
        """
        if self.sub is not None:
            self.sub.destroy()
            self.sub = None
        self.kill()

"""
appmenuclose_event = pygame.event.Event(pygame.USEREVENT,
                                                ui_element="appmenupanel",
                                                ui_object_id="appmenu",
                                                user_type="APPMENU_PANEL_CLOSED",
                                                message="AppMenuPanel_closed.")
pygame.event.post(appmenuclose_event)
"""
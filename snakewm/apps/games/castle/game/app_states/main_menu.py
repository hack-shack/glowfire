import os
from pathlib import Path
from pathlib import PurePath
import pygame
from pygame.locals import *
import pygame_gui
from pygame_gui.core import ObjectID
from pygame_gui.elements import UIButton
from pygame_gui.elements import UILabel

from .base_app_state import BaseAppState


class MainMenu(BaseAppState):
    """ Main menu class for Castle. """

    def __init__(self, ui_manager: pygame_gui.UIManager, state_manager):
        super().__init__('main_menu', 'select_level', state_manager)

        self.ui_manager = ui_manager
        image_dir = PurePath(Path(os.path.dirname(__file__)).parent.parent, Path("images"))
        self.background_image = pygame.image.load(PurePath(Path(image_dir),Path("bg_title_screen.png"))).convert()

        self.title_label = None
        self.play_game_button = None

    def start(self):
        self.title_label = UILabel(pygame.Rect((0, 0, 400, 50)),
                                   text="Castle.",
                                   manager=self.ui_manager,
                                   object_id=ObjectID(class_id="@castle_label",
                                                      object_id="#castle_label_title")
        )

        #screensize = pygame.display.get_window_size()
        screensize = 400,240
        screenwidth = screensize[0]
        screenheight = screensize[1]

        self.play_game_button = UIButton(pygame.Rect((125 , 200), (150, 35)),
                                         text="Start Game",
                                         manager=self.ui_manager,
                                         tool_tip_text="<b>Click to Start.</b>")


    def end(self):
        self.title_label.kill()
        self.play_game_button.kill()

    def run(self, surface, time_delta):
        for event in pygame.event.get():
            if event.type == QUIT:
                self.set_target_state_name('quit')
                self.trigger_transition()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.set_target_state_name('quit')
                    self.trigger_transition()

            self.ui_manager.process_events(event)

            if event.type == pygame_gui.UI_BUTTON_PRESSED:
                if event.ui_element == self.play_game_button:
                    self.set_target_state_name('select_level')
                    self.trigger_transition()

                if event.ui_object_id == "#castle_rect.#castle_button_quit":
                    print('hi')
                    self.set_target_state_name('quit')
                    self.trigger_transition()

        self.ui_manager.update(time_delta)

        surface.blit(self.background_image, (0, 0))  # draw the background

        self.ui_manager.draw_ui(surface)

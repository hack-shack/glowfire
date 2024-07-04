import os
from pathlib import Path
from pathlib import PurePath
import pygame
from pygame.locals import *
import pygame_gui
from pygame_gui.elements.ui_button import UIButton
from pygame_gui.elements.ui_label import UILabel


from .base_app_state import BaseAppState


class LevelUIData:
    def __init__(self, level_path):
        self.path = level_path
        self.display_name = level_path.split('/')[-1].split('.')[0].replace('_', ' ').capitalize()


class SelectLevelMenu(BaseAppState):
    def __init__(self, ui_manager: pygame_gui.UIManager, state_manager):
        super().__init__('select_level', 'game', state_manager)
        self.ui_manager = ui_manager
        self.all_level_paths = []
        self.selected_level_path = None
        self.background_image = None
        self.title_label = None
        self.play_game_button = None
        self.edit_map_button = None
        self.level_button_group = []
        self.level_group_y_start = 150
        self.reload_levels()

    def start(self):
        self.level_group_y_start = 150
        self.selected_level_path = self.all_level_paths[0].path

        self.background_image = pygame.image.load("images/bg_select_level.png").convert()

        self.title_label = UILabel(pygame.Rect((0, 0), (230, 62)), "Select Level",
                                   self.ui_manager, object_id="#game_sub_title")

        self.play_game_button = UIButton(pygame.Rect((10, 70), (100, 30)),
                                         "Play Game", self.ui_manager,
                                         tool_tip_text="<b>Click to start.</b>")

        self.edit_map_button = UIButton(pygame.Rect((10, 100), (100, 30)),
                                        "Edit Map", self.ui_manager,
                                        tool_tip_text="<b>Click to enter the level editor.</b>")

        for level_data in self.all_level_paths:
            self.level_button_group.append(UIButton(pygame.Rect((10, self.level_group_y_start),
                                                                (100, 20)),
                                                    level_data.display_name,
                                                    self.ui_manager,
                                                    tool_tip_text="<b>Select this level.</b>",
                                                    object_id="#choose_level_button"))
            self.level_group_y_start += 24
            
        if len(self.level_button_group) > 0:
            self.ui_manager.set_focus_set(self.level_button_group[0])

    def end(self):
        self.title_label.kill()
        self.play_game_button.kill()
        self.edit_map_button.kill()
        for button in self.level_button_group:
            button.kill()
        self.level_button_group.clear()

    def reload_levels(self):
        self.all_level_paths[:] = []
        levels_dir = PurePath(Path(os.path.dirname(__file__)).parent.parent, Path("data/levels"))
        for level_file in os.listdir(levels_dir):
            full_file_name = str(PurePath(levels_dir, Path(level_file)))
            level_data = LevelUIData(full_file_name)
            self.all_level_paths.append(level_data)
              
    def run(self, surface, time_delta):
        for event in pygame.event.get():
            if event.type == QUIT:
                self.set_target_state_name('quit')
                self.trigger_transition()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.trigger_transition()

            self.ui_manager.process_events(event)

            if event.type == pygame_gui.UI_BUTTON_PRESSED:
                if event.ui_element == self.play_game_button:
                    self.set_target_state_name('game')
                    self.outgoing_transition_data['selected_level_path'] = self.selected_level_path
                    self.trigger_transition()

                if event.ui_element == self.edit_map_button:
                    self.set_target_state_name('editor')
                    self.outgoing_transition_data['selected_level_path'] = self.selected_level_path
                    self.trigger_transition()

                if event.ui_object_id == "#choose_level_button":
                    self.ui_manager.set_focus_set(event.ui_element)
                    for level_data in self.all_level_paths:
                        if level_data.display_name == event.ui_element.text:
                            self.selected_level_path = level_data.path

        self.ui_manager.update(time_delta)

        surface.blit(self.background_image, (0, 0))  # draw the background
        self.ui_manager.draw_ui(surface)

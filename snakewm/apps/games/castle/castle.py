import os

import pygame
import pygame_gui
from pygame_gui import UIManager
from pygame_gui.core.object_id import ObjectID
from pygame_gui.elements.ui_button import UIButton
from pygame_gui.elements.ui_panel import UIPanel

#import .game.app_states.app_state_manager.AppStateManager
from .game.app_states.app_state_manager import AppStateManager
from .game.app_states.main_menu import MainMenu
from .game.app_states.select_level import SelectLevelMenu
from .game.app_states.quit_state import QuitState
from .game.app_states.game_state import GameState
from .game.app_states.editor_state import EditorState

class ScreenData:
    def __init__(self, hud_size, editor_hud_size, screen_size):
        self.screen_size = screen_size
        self.hud_dimensions = hud_size
        self.editor_hud_dimensions = editor_hud_size
        self.play_area = [screen_size[0], screen_size[1] - self.hud_dimensions[1]]

    def set_editor_active(self):
        self.play_area = [self.screen_size[0], self.screen_size[1] - self.editor_hud_dimensions[1]]

    def set_editor_inactive(self):
        self.play_area = [self.screen_size[0], self.screen_size[1] - self.hud_dimensions[1]]

class Castle(UIPanel):
    """ Draw a panel to contain the Castle game UI. """
    manager = None
    RESOLUTION = (400,240)
    def __init__(self,
        position=(0,0),
        starting_height=1,
        manager=manager,
        size=RESOLUTION,
        element_id="#castle"
        ):
        super().__init__(
            pygame.Rect(position,size),
            manager=manager,
            object_id="#castle_rect"
        )

        x_screen_size = 400
        y_screen_size = 240
        screen_data = ScreenData([x_screen_size, 128], [x_screen_size, 184], [x_screen_size, y_screen_size])

        ui_manager = manager
        #manager(screen.get_size(), ".data/ui_theme.json")
        print("CWD:")
        print(os.getcwd())
        #ui_manager.get_theme().load_theme("snakewm/apps/games/towerdef/data/ui_theme.json")
        #manager((400,240),".data/ui_theme.json")
        app_state_manager = AppStateManager()
        MainMenu(ui_manager, app_state_manager)
        SelectLevelMenu(ui_manager, app_state_manager)
        GameState(ui_manager, self, screen_data, app_state_manager)
        EditorState(ui_manager, self, screen_data, app_state_manager)
        QuitState(app_state_manager)
        app_state_manager.set_initial_state('main_menu')

        clock = pygame.time.Clock()
        running = True

        self.button_quit = UIButton(
            relative_rect=pygame.Rect(376,0,24,24),
            text='',
            manager=manager,
            container=self,
            parent_element=self,
            object_id=ObjectID(class_id="@castle_button",
                               object_id="#castle_button_quit"
            )
        )

    def process_event(self, event):
        super().process_event(event)

    def update(self, delta):
        super().update(delta)

def main():
    #pygame.init()
    #os.environ['SDL_VIDEO_CENTERED'] = '1'
    #pygame.key.set_repeat()
    #x_screen_size = 400
    #y_screen_size = 240
    #x_screen_size = 800
    #y_screen_size = 480
    #pygame.display.set_caption('Castle')
    #screen = pygame.display.set_mode(((x_screen_size, y_screen_size)))
    #screen.fill((255,255,255))
    #screen_data = ScreenData([x_screen_size, 128], [x_screen_size, 184], [x_screen_size, y_screen_size])
    """
    ui_manager = UIManager(screen.get_size(), "data/ui_theme.json")
    ui_manager.preload_fonts([{'name': 'fira_code', 'point_size': 10, 'style': 'bold'},
                              {'name': 'fira_code', 'point_size': 10, 'style': 'regular'},
                              {'name': 'fira_code', 'point_size': 14, 'style': 'bold'}])
    """
    app_state_manager = AppStateManager()
    app_state_manager.set_initial_state('main_menu')
    MainMenu(ui_manager=super.manager, state_manager=app_state_manager)
    """
    SelectLevelMenu(ui_manager, app_state_manager)
    GameState(ui_manager, screen, screen_data, app_state_manager)
    EditorState(ui_manager, screen, screen_data, app_state_manager)
    QuitState(app_state_manager)
    """
    clock = pygame.time.Clock()
    running = True
    while running:
        frame_time = clock.tick(60)
        time_delta = min(frame_time/1000.0, 0.1)

        running = app_state_manager.run(screen, time_delta)

        pygame.display.flip()  # flip all our drawn stuff onto the screen

    pygame.quit()  # exited game loop so quit pygame


if __name__ == '__main__':
    main()

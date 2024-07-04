from collections import deque

import pygame
import pygame_gui

from pygame_gui.elements import UIPanel
from pygame_gui.elements import UILabel
from pygame_gui.elements import UIButton

from .base_app_state import BaseAppState
from ...collision.collision_grid import CollisionGrid
from ...tiled_levels.tiled_level import TiledLevel
from ..monster_wave_spawner import MonsterWaveSpawner
from ..splat import SplatLoader
from ..player_resources import PlayerResources

from ..gun_turret import GunTurret
from ..flame_turret import FlameTurret
from ..missile_turret import MissileTurret
from ..slow_turret import SlowTurret
from ..laser_turret import LaserTurret

BLACK = (0,0,0)
WHITE = (255,255,255)


class TurretCosts:
    def __init__(self):
        self.gun = 150
        self.flamer = 250
        self.missile = 400
        self.slow = 700
        self.laser = 500


class HUDPanel(UIPanel):
    def __init__(self, rect: pygame.Rect, manager: 'pygame_gui.ui_manager.UIManager',
                 player_resources: PlayerResources, turret_costs: TurretCosts):
        super().__init__(rect, 1, manager, element_id='hud_panel')
        self.player_resources = player_resources
        self.turret_costs = turret_costs

        # create top edge shadow
        top_edge_shadow_size = 4
        border_size = 1
        background_surface = pygame.Surface((self.rect.width,
                                             self.rect.height - top_edge_shadow_size))
        background_surface.fill(pygame.Color(BLACK))
        background_surface.fill(pygame.Color(WHITE),
                                pygame.Rect((border_size, border_size),
                                            (self.rect.width - (border_size * 2),
                                             self.rect.height - (border_size * 2) - top_edge_shadow_size)))
        shadow = self.ui_manager.get_shadow((self.rect.width + 48, self.rect.height))
        self.image = pygame.Surface(self.rect.size, flags=pygame.SRCALPHA)
        self.image.blit(shadow, (0, 0), area=pygame.Rect((24, 0), self.rect.size))
        self.image.blit(background_surface, (0, top_edge_shadow_size))

        self.get_container().relative_rect.width = self.rect.width
        self.get_container().relative_rect.height = self.rect.height - top_edge_shadow_size
        self.get_container().relative_rect.x = self.get_container().relative_rect.x
        self.get_container().relative_rect.y = self.get_container().relative_rect.y + top_edge_shadow_size
        self.get_container().update_containing_rect_position()

        self.health_label = UILabel(pygame.Rect((0,0), (150, 40)),
                                    "Health: " + "{:,}".format(self.player_resources.current_base_health),
                                    manager=self.ui_manager,
                                    container=self.get_container(),
                                    object_id="#screen_text")

        self.cash_label = UILabel(pygame.Rect((100, 0), (100, 40)),
                                  "£" + "{:,}".format(self.player_resources.current_cash),
                                  manager=self.ui_manager,
                                  container=self.get_container(),
                                  object_id="#screen_text")

        self.clearable_hud_elements = []

    def update(self, time_delta: float):
        self.cash_label.set_text("£" + "{:,}".format(self.player_resources.current_cash))
        self.health_label.set_text("Health: " + "{:,}".format(self.player_resources.current_base_health))

    def display_normal_hud(self):

        for element in self.clearable_hud_elements:
            element.kill()

        self.clearable_hud_elements.clear()

        self.clearable_hud_elements.append(
            UIButton(pygame.Rect(32, 32, 66, 66), "",
                     manager=self.ui_manager, container=self.get_container(), object_id="#gun_turret_button",
                     tool_tip_text="<font size=2><b>Gun Turret</b><br><br>"
                                   "A turret that fires a pair of low damage bullets at enemies in range. Has a"
                                   " fairly rapid rate of fire.</font>"))
        self.clearable_hud_elements.append(
            UIButton(pygame.Rect(128, 32, 66, 66), "",
                     manager=self.ui_manager, container=self.get_container(), object_id="#missile_turret_button",
                     tool_tip_text="<font size=2><b>Missile Turret</b><br><br>"
                                   "A slow firing, large range turret that launches homing missiles. Missiles do high "
                                   "damage.</font>"))
        self.clearable_hud_elements.append(
            UIButton(pygame.Rect(224, 32, 66, 66), "",
                     manager=self.ui_manager, container=self.get_container(), object_id="#flame_turret_button",
                     tool_tip_text="<font size=2><b>Flame Turret</b><br><br>"
                                   "Short range turret that fires a continuous cone of flame."
                                   " The flames do damage while an enemy is within the cone. "
                                   "Works well when enemies have to walk directly at the "
                                   "turret.</font>"))
        self.clearable_hud_elements.append(
            UIButton(pygame.Rect(320, 32, 66, 66), "",
                     manager=self.ui_manager, container=self.get_container(), object_id="#slow_turret_button",
                     tool_tip_text="<font size=2><b>Slow Turret</b><br><br>"
                                   "This turret uses time warping fields to slow down"
                                   " all enemies within its radius. Works "
                                   "well to multiply the damage done by nearby turrets.</font>"))
        self.clearable_hud_elements.append(
            UIButton(pygame.Rect(416, 32, 66, 66), "",
                     manager=self.ui_manager, container=self.get_container(), object_id="#laser_turret_button",
                     tool_tip_text="<font size=2><b>Laser Turret</b><br><br>"
                                   "This turret fires a continuous laser beam at a single target."
                                   " Useful for dealing with armoured targets that resist other "
                                   "types of damage.</font>"))
        self.clearable_hud_elements.append(
            UILabel(pygame.Rect((32, 64), (64, 32)),
                    "£ " + str(self.turret_costs.gun),
                    manager=self.ui_manager, container=self.get_container(), object_id="#small_screen_text"))
        self.clearable_hud_elements.append(
            UILabel(pygame.Rect((128, 64), (64, 32)),
                    "£ " + str(self.turret_costs.missile),
                    manager=self.ui_manager, container=self.get_container(), object_id="#small_screen_text"))
        self.clearable_hud_elements.append(
            UILabel(pygame.Rect((224, 64), (64, 32)),
                    "£ " + str(self.turret_costs.flamer),
                    manager=self.ui_manager, container=self.get_container(), object_id="#small_screen_text"))
        self.clearable_hud_elements.append(
            UILabel(pygame.Rect((320, 64), (64, 32)),
                    "£ " + str(self.turret_costs.slow),
                    manager=self.ui_manager, container=self.get_container(), object_id="#small_screen_text"))
        self.clearable_hud_elements.append(
            UILabel(pygame.Rect((416, 64), (64, 32)),
                    "£ " + str(self.turret_costs.laser),
                    manager=self.ui_manager, container=self.get_container(), object_id="#small_screen_text"))

    def display_upgrade_hud(self, upgrade_turret):

        for element in self.clearable_hud_elements:
            element.kill()

        self.clearable_hud_elements.clear()

        self.clearable_hud_elements.append(
            UIButton(pygame.Rect(32, 32, 66, 66), "",
                     manager=self.ui_manager, container=self.get_container(), object_id="#upgrade_button",
                     tool_tip_text="<font size=2><b>Upgrade Turret</b><br><br>"
                                   "Upgrades the selected turret to the next level."
                                   " Turrets have three levels.</font>"))
        self.clearable_hud_elements.append(
            UIButton(pygame.Rect(128, 32, 66, 66), "",
                     manager=self.ui_manager, container=self.get_container(), object_id="#sell_button",
                     tool_tip_text="<font size=2><b>Sell Turret</b><br><br>"
                                   "Sells the selected turret for half of the cost of building it.</font>"))
        self.clearable_hud_elements.append(
            UILabel(pygame.Rect((32, 96), (64, 32)),
                    "£ " + str(upgrade_turret.get_upgrade_cost()),
                    manager=self.ui_manager, container=self.get_container(), object_id="#small_screen_text"))
        self.clearable_hud_elements.append(
            UILabel(pygame.Rect((128, 96), (64, 32)),
                    "£ " + str(upgrade_turret.get_sell_value()),
                    manager=self.ui_manager, container=self.get_container(), object_id="#small_screen_text"))


class GameState(BaseAppState):

    def __init__(self, ui_manager: pygame_gui.UIManager, screen_surface, screen_data, state_manager):
        super().__init__('game', 'main_menu', state_manager)

        self.ui_manager = ui_manager
        self.screen_surface = screen_surface
        self.screen_data = screen_data

        self.background = None

        self.level_to_load_path = None
        self.level_to_load = None

        # objects that do stuff
        self.collision_grid = None
        self.tiled_level = None
        self.monster_wave_spawner = None
        self.splat_loader = None
        self.player_resources = None

        self.should_redraw_static_sprites = False

        # game sub state booleans
        self.is_play_game = False
        self.restart_game = False
        self.is_setup = False
        self.is_game_over = False
        self.should_show_count_down_message = False
        self.upgrade_hud_active = False

        self.hud_panel = None

        # labels
        self.fps_counter_label = None
        self.wave_display_label = None
        self.count_down_message_label = None
        self.health_label = None
        self.cash_label = None
        self.win_message_label = None
        self.play_again_message_label = None

        self.frame_rates = deque([])

        # turrets
        self.active_upgrade_turret = None
        self.mouse_active_turret = None

        # lists of things
        self.explosions = []
        self.new_explosions = []
        self.bullets = []
        self.turrets = []
        self.monsters = []
        self.hud_buttons = []

        # sprite groups
        self.static_sprite_surface = None
        self.all_tile_sprites = None
        self.all_square_sprites = None
        self.all_monster_sprites = None
        self.all_turret_sprites = None
        self.all_bullet_sprites = None
        self.all_explosion_sprites = None
        self.splat_sprites = None

        # images
        self.explosions_sprite_sheet = None
        self.image_atlas = None

        self.turret_costs = TurretCosts()

        self.count_down_message = ""
        self.win_message = ""

        # timer
        self.setup_time = 10.0
        self.setup_accumulator = 0.0

        self.hud_rect = None

    def start(self):
        self.hud_rect = pygame.Rect(0, self.screen_data.screen_size[1] - 128,
                                    self.screen_data.screen_size[0], 128)

        self.player_resources = PlayerResources()

        self.background = pygame.Surface(self.screen_surface.get_size())
        self.background = self.background.convert(self.screen_surface)
        self.background.fill((95, 140, 95))

        self.should_redraw_static_sprites = True
        self.static_sprite_surface = pygame.Surface(self.screen_surface.get_size())
        self.all_tile_sprites = pygame.sprite.Group()
        self.all_square_sprites = pygame.sprite.Group()
        self.all_monster_sprites = pygame.sprite.Group()
        self.all_turret_sprites = pygame.sprite.Group()
        self.all_bullet_sprites = pygame.sprite.Group()
        self.all_explosion_sprites = pygame.sprite.Group()
        self.splat_sprites = pygame.sprite.Group()

        self.explosions_sprite_sheet = pygame.image.load("images/explosions.png").convert_alpha()
        self.image_atlas = pygame.image.load("images/image_atlas.png").convert_alpha()
        self.splat_loader = SplatLoader()

        self.level_to_load_path = self.incoming_transition_data['selected_level_path']

        self.fps_counter_label = UILabel(pygame.Rect((0, 10), (100, 40)),
                                         "0 FPS", manager=self.ui_manager, object_id="#screen_text")

        self.wave_display_label = None

        grid_size = 64
        screen_filling_number_of_grid_squares = [int(self.screen_data.screen_size[0] / grid_size),
                                                 int(self.screen_data.screen_size[1] / grid_size)]
        self.collision_grid = CollisionGrid(screen_filling_number_of_grid_squares, grid_size)

        # clear level
        self.tiled_level = TiledLevel(self.level_to_load_path, [40, 21], self.all_tile_sprites,
                                      self.all_monster_sprites, self.all_square_sprites,
                                      self.image_atlas, self.monsters,
                                      self.screen_data, self.explosions_sprite_sheet)
        self.tiled_level.load_tiles()
        self.tiled_level.update_offset_position(self.tiled_level.find_player_start(), self.all_tile_sprites)
        self.monster_wave_spawner = MonsterWaveSpawner(self.monsters, self.tiled_level.monster_walk_path,
                                                       10, self.all_monster_sprites,
                                                       self.image_atlas, self.collision_grid,
                                                       self.splat_loader, self.ui_manager)

        self.is_play_game = True
        self.restart_game = True
        self.should_redraw_static_sprites = True

        self.hud_panel = HUDPanel(self.hud_rect, self.ui_manager,
                                  self.player_resources, self.turret_costs)

    def end(self):
        if self.fps_counter_label is not None:
            self.fps_counter_label.kill()
            self.fps_counter_label = None

        if self.count_down_message_label is not None:
            self.count_down_message_label.kill()
            self.count_down_message_label = None

        if self.wave_display_label is not None:
            self.wave_display_label.kill()
            self.wave_display_label = None

        if self.hud_panel is not None:
            self.hud_panel.kill()
            self.hud_panel = None

        if self.win_message_label is not None:
            self.win_message_label.kill()
            self.win_message_label = None

        if self.play_again_message_label is not None:
            self.play_again_message_label.kill()
            self.play_again_message_label = None

        for sprite in self.all_monster_sprites.sprites():
            sprite.kill()

        self.all_monster_sprites.empty()
        self.all_turret_sprites.empty()
        self.all_bullet_sprites.empty()
        self.all_explosion_sprites.empty()

    def run(self, surface, time_delta):

        if not self.restart_game and self.is_setup:
            if self.setup_accumulator >= self.setup_time:
                self.is_setup = False
                self.setup_accumulator = 0.0
            elif self.setup_accumulator >= (self.setup_time - 6.0):
                seconds_string = str(int(self.setup_time - self.setup_accumulator))
                self.count_down_message = "First wave in " + seconds_string + " seconds"
                self.should_show_count_down_message = True
                self.setup_accumulator += time_delta

                if self.count_down_message_label is None:
                    count_down_message_label_rect = pygame.Rect((400, 10), (250, 40))
                    count_down_message_label_rect.centerx = self.screen_data.screen_size[0] / 2
                    count_down_message_label_rect.centery = 24
                    self.count_down_message_label = UILabel(count_down_message_label_rect,
                                                            self.count_down_message, manager=self.ui_manager,
                                                            object_id="#screen_text")
            else:
                self.setup_accumulator += time_delta
                remaining_time = str(int(self.setup_time - self.setup_accumulator))
                self.count_down_message = "Setup Time remaining: " + remaining_time + " seconds"
                self.should_show_count_down_message = True

                if self.count_down_message_label is None:
                    count_down_message_label_rect = pygame.Rect((400, 10), (250, 40))
                    count_down_message_label_rect.centerx = self.screen_data.screen_size[0] / 2
                    count_down_message_label_rect.centery = 24
                    self.count_down_message_label = UILabel(count_down_message_label_rect,
                                                            self.count_down_message, manager=self.ui_manager,
                                                            object_id="#screen_text")
        elif self.restart_game:
            self.restart_game = False

            # clear all stuff
            self.explosions[:] = []
            self.new_explosions[:] = []
            self.bullets[:] = []
            self.turrets[:] = []
            self.monsters[:] = []
            self.hud_buttons[:] = []

            self.all_monster_sprites.empty()
            self.all_turret_sprites.empty()
            self.all_bullet_sprites.empty()
            self.all_explosion_sprites.empty()

            self.tiled_level.reset_squares()

            # reset player resources
            self.player_resources = PlayerResources()
            self.hud_panel.player_resources = self.player_resources

            self.is_game_over = False
            self.is_setup = True
            self.setup_accumulator = 0.0
            self.monster_wave_spawner = MonsterWaveSpawner(self.monsters, self.tiled_level.monster_walk_path, 10,
                                                           self.all_monster_sprites, self.image_atlas,
                                                           self.collision_grid, self.splat_loader, self.ui_manager)
            self.mouse_active_turret = None
            self.active_upgrade_turret = None
            self.upgrade_hud_active = False
            self.should_show_count_down_message = False
            if self.count_down_message_label is not None:
                self.count_down_message_label.kill()
                self.count_down_message_label = None

            if self.wave_display_label is not None:
                self.wave_display_label.kill()
                self.wave_display_label = None

            if self.win_message_label is not None:
                self.win_message_label.kill()
                self.win_message_label = None

            if self.play_again_message_label is not None:
                self.play_again_message_label.kill()
                self.play_again_message_label = None

            self.hud_panel.display_normal_hud()

        elif self.is_game_over:
            self.should_show_count_down_message = False
            if self.count_down_message_label is not None:
                self.count_down_message_label.kill()
                self.count_down_message_label = None
        else:
            self.monster_wave_spawner.update(time_delta, self.tiled_level.position_offset)
            if self.wave_display_label is not None:
                self.wave_display_label.kill()
                self.wave_display_label = None

            if self.monster_wave_spawner.should_show_wave_countdown:
                self.should_show_count_down_message = True
                self.count_down_message = self.monster_wave_spawner.count_down_message

                if self.count_down_message_label is None:
                    count_down_message_label_rect = pygame.Rect((400, 10), (250, 40))
                    count_down_message_label_rect.centerx = self.screen_data.screen_size[0] / 2
                    count_down_message_label_rect.centery = 24
                    self.count_down_message_label = UILabel(count_down_message_label_rect,
                                                            self.count_down_message, manager=self.ui_manager,
                                                            object_id="#screen_text")
            else:
                self.should_show_count_down_message = False
                if self.count_down_message_label is not None:
                    self.count_down_message_label.kill()
                    self.count_down_message_label = None

                if self.wave_display_label is None:
                    current_wave = str(self.monster_wave_spawner.current_wave_number)
                    max_wave = str(self.monster_wave_spawner.maximum_wave_number)
                    wave_display_label_rect = pygame.Rect((400, 10), (100, 40))
                    wave_display_label_rect.centerx = self.screen_data.screen_size[0] / 2
                    wave_display_label_rect.centery = 24
                    self.wave_display_label = UILabel(wave_display_label_rect,
                                                      "Wave " + current_wave + "/" + max_wave,
                                                      manager=self.ui_manager, object_id="#screen_text")

        if not self.is_game_over and self.player_resources.current_base_health <= 0:
            self.is_game_over = True
            self.win_message = "You have been defeated!"
            self.win_message_label = UILabel(pygame.Rect((347, 200), (330, 70)),
                                             self.win_message,
                                             manager=self.ui_manager,
                                             object_id="#win_message_text")

            self.play_again_message_label = UILabel(pygame.Rect((362, 250), (300, 70)),
                                                    "Play Again? Press 'Y' to restart",
                                                    manager=self.ui_manager,
                                                    object_id="#screen_text")

        on_final_wave = self.monster_wave_spawner.current_wave_number == self.monster_wave_spawner.maximum_wave_number
        if not self.is_game_over and on_final_wave and len(self.monsters) == 0:
            self.is_game_over = True
            self.win_message = "You are victorious!"
            self.win_message_label = UILabel(pygame.Rect((347, 200), (330, 70)),
                                             self.win_message,
                                             manager=self.ui_manager,
                                             object_id="#win_message_text")

            self.play_again_message_label = UILabel(pygame.Rect((362, 250), (300, 70)),
                                                    "Play Again? Press 'Y' to restart",
                                                    manager=self.ui_manager,
                                                    object_id="#screen_text")

        self.all_turret_sprites.empty()
        self.all_bullet_sprites.empty()
        self.all_explosion_sprites.empty()

        # handle UI and inout events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.trigger_transition()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.trigger_transition()
                if event.key == pygame.K_g:
                    self.monster_wave_spawner.wave_points = 1000
                    self.monster_wave_spawner.wave_time_accumulator = 5.0
                if event.key == pygame.K_y:
                    if self.is_game_over:
                        self.restart_game = True

            self.ui_manager.process_events(event)

            if event.type == pygame_gui.UI_BUTTON_PRESSED:
                if "#gun_turret_button" in event.ui_object_id:
                    if self.turret_costs.gun <= self.player_resources.current_cash:
                        new_turret = GunTurret(pygame.mouse.get_pos(), self.turret_costs.gun,
                                               self.explosions_sprite_sheet,
                                               self.image_atlas, self.collision_grid)
                        self.mouse_active_turret = new_turret
                        self.turrets.append(new_turret)
                elif "#flame_turret_button" in event.ui_object_id:
                    if self.turret_costs.flamer <= self.player_resources.current_cash:
                        new_turret = FlameTurret(pygame.mouse.get_pos(), self.turret_costs.flamer,
                                                 self.explosions_sprite_sheet, self.image_atlas,
                                                 self.collision_grid)
                        self.mouse_active_turret = new_turret
                        self.turrets.append(new_turret)
                elif "#missile_turret_button" in event.ui_object_id:
                    if self.turret_costs.missile <= self.player_resources.current_cash:
                        new_turret = MissileTurret(pygame.mouse.get_pos(), self.turret_costs.missile,
                                                   self.explosions_sprite_sheet, self.image_atlas,
                                                   self.collision_grid)
                        self.mouse_active_turret = new_turret
                        self.turrets.append(new_turret)
                elif "#slow_turret_button" in event.ui_object_id:
                    if self.turret_costs.slow <= self.player_resources.current_cash:
                        new_turret = SlowTurret(pygame.mouse.get_pos(), self.turret_costs.slow,
                                                self.image_atlas)
                        self.mouse_active_turret = new_turret
                        self.turrets.append(new_turret)
                elif "#laser_turret_button" in event.ui_object_id:
                    if self.turret_costs.laser <= self.player_resources.current_cash:
                        new_turret = LaserTurret(pygame.mouse.get_pos(), self.turret_costs.laser,
                                                 self.image_atlas)
                        self.mouse_active_turret = new_turret
                        self.turrets.append(new_turret)
                elif "#upgrade_button" in event.ui_object_id:
                    if self.active_upgrade_turret is not None:
                        if self.player_resources.current_cash >= self.active_upgrade_turret.get_upgrade_cost():
                            self.player_resources.current_cash -= self.active_upgrade_turret.get_upgrade_cost()
                            self.active_upgrade_turret.upgrade()
                            self.upgrade_hud_active = False
                            self.active_upgrade_turret = None
                            self.hud_panel.display_normal_hud()
                elif "#sell_button" in event.ui_object_id:
                    if self.active_upgrade_turret is not None:
                        self.player_resources.current_cash += self.active_upgrade_turret.get_sell_value()
                        for square in self.tiled_level.turret_squares:
                            if square.rect.collidepoint(self.active_upgrade_turret.position):
                                square.occupied = False
                        self.turrets.remove(self.active_upgrade_turret)
                        self.upgrade_hud_active = False
                        self.active_upgrade_turret = None
                        self.hud_panel.display_normal_hud()

            if not self.is_game_over and event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 3:
                    if self.mouse_active_turret is not None:
                        self.turrets[:] = [turret for turret in self.turrets if turret is not self.mouse_active_turret]
                        self.mouse_active_turret = None
                    if self.upgrade_hud_active:
                        self.upgrade_hud_active = False
                        self.hud_panel.display_normal_hud()
                if event.button == 1:
                    if self.mouse_active_turret is not None:
                        placed_turret = False
                        for square in self.tiled_level.turret_squares:
                            if self.mouse_active_turret is not None:
                                if square.rect.collidepoint(pygame.mouse.get_pos()) and not square.occupied:
                                    self.mouse_active_turret.set_position(square.position)
                                    placed_turret = True
                                    square.occupied = True
                                    self.player_resources.current_cash -= self.mouse_active_turret.build_cost
                                    self.mouse_active_turret.placed = True
                                    self.mouse_active_turret = None
                        if not placed_turret:
                            self.turrets[:] = [turret for turret in self.turrets
                                               if turret is not self.mouse_active_turret]
                            self.mouse_active_turret = None
                    else:
                        for turret in self.turrets:
                            if turret.rect.collidepoint(pygame.mouse.get_pos()):
                                if turret.get_level() < turret.get_max_level():
                                    self.upgrade_hud_active = True
                                    self.active_upgrade_turret = turret
                                    self.hud_panel.display_upgrade_hud(self.active_upgrade_turret)

        if not self.is_game_over and self.mouse_active_turret is not None:
            is_over_square = False
            for square in self.tiled_level.turret_squares:
                if square.rect.collidepoint(pygame.mouse.get_pos()) and not square.occupied:
                    self.mouse_active_turret.set_position(square.position)
                    self.mouse_active_turret.show_radius = True
                    is_over_square = True
            if not is_over_square:
                self.mouse_active_turret.set_position(pygame.mouse.get_pos())
                self.mouse_active_turret.show_radius = False

        for bullet in self.bullets:
            self.all_bullet_sprites = bullet.update_sprite(self.all_bullet_sprites)
            bullet.update_movement_and_collision(self.monsters, time_delta, self.new_explosions, self.explosions)
        self.bullets[:] = [bullet for bullet in self.bullets if not bullet.should_die]

        for monster in self.monsters:
            monster.update_movement_and_collision(time_delta, self.player_resources,
                                                  self.tiled_level.position_offset, self.splat_sprites)
            monster.update_sprite()
        self.monsters[:] = [monster for monster in self.monsters if not monster.should_die]
        self.new_explosions[:] = []

        for turret in self.turrets:
            turret.update_movement_and_collision(time_delta, self.monsters, self.bullets, pygame.mouse.get_pos())
            self.all_turret_sprites = turret.update_sprite(self.all_turret_sprites)

        for explosion in self.explosions:
            self.all_explosion_sprites = explosion.update_sprite(self.all_explosion_sprites, time_delta)
        self.explosions[:] = [explosion for explosion in self.explosions if not explosion.should_die]

        self.splat_sprites.update(time_delta)

        self.collision_grid.update_shape_grid_positions()
        self.collision_grid.check_collisions()

        self.ui_manager.update(time_delta)

        for collided_shape in self.collision_grid.shapes_collided_this_frame:
            if collided_shape.owner is not None:
                collided_shape.owner.react_to_collision()

        if self.should_redraw_static_sprites:
            self.should_redraw_static_sprites = False
            self.static_sprite_surface.blit(self.background, (0, 0))  # draw the background
            self.all_tile_sprites.draw(self.static_sprite_surface)

        surface.blit(self.static_sprite_surface, (0, 0))
        self.splat_sprites.draw(surface)
        if self.mouse_active_turret is not None:
            self.all_square_sprites.draw(surface)
        self.all_monster_sprites.draw(surface)
        self.all_turret_sprites.draw(surface)
        self.all_bullet_sprites.draw(surface)
        self.all_explosion_sprites.draw(surface)

        # collision debug
        # for monster in monsters:
        #     monster.draw_collision_circle(screen)
        # for bullet in bullets:
        #     bullet.draw_collision_rect(screen)

        for turret in self.turrets:
            if turret.show_radius:
                turret.draw_radius_circle(surface)

        if time_delta > 0.0 and self.fps_counter_label is not None:
            if len(self.frame_rates) < 300:
                self.frame_rates.append(1.0 / time_delta)
            else:
                self.frame_rates.popleft()
                self.frame_rates.append(1.0 / time_delta)

            fps = sum(self.frame_rates) / len(self.frame_rates)

            self.fps_counter_label.set_text("FPS: {:.2f}".format(fps))

        if self.should_show_count_down_message and self.count_down_message_label is not None:
            self.count_down_message_label.set_text(self.count_down_message)

        if self.wave_display_label is not None and self.monster_wave_spawner.has_changed_wave:
            current_wave = str(self.monster_wave_spawner.current_wave_number)
            max_wave = str(self.monster_wave_spawner.maximum_wave_number)
            self.wave_display_label.set_text("Wave " + current_wave + "/" + max_wave)

        self.ui_manager.draw_ui(surface)

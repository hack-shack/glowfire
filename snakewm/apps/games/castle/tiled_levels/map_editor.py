import os
import math

import pygame
import pygame_gui
from pygame.locals import *
from pygame_gui.windows import UIMessageWindow
from pygame_gui.elements import UIButton, UILabel

from .tile import Tile


class DrawableWaypointCircle:
    def __init__(self, radius, position, ui_manager, order):
        self.ui_manager = ui_manager
        self.traversal_order = order
        self.radius = radius
        self.colour = pygame.Color("#FF6464")
        self.rectangle_colour = pygame.Color("#646464")
        self.color_key = (127, 33, 33)
        self.world_position = [int(position[0]-self.radius), int(position[1]-self.radius)]
        self.surface = pygame.Surface((self.radius*2, self.radius*2))
        self.surface.fill(self.color_key)
        self.surface.set_colorkey(self.color_key)
        pygame.draw.circle(self.surface, self.colour, (self.radius, self.radius), self.radius)
        self.surface.set_alpha(100)

        self.rectangle_surface = pygame.Surface((32, 32))
        self.rectangle_surface.fill(self.color_key)
        self.rectangle_surface.set_colorkey(self.color_key)
        pygame.draw.rect(self.rectangle_surface, self.rectangle_colour, pygame.Rect(0, 0, 32, 32))
        self.rectangle_surface.set_alpha(100)
        self.position = [self.world_position[0], self.world_position[1]]
        # self.id_text = fonts[6].render(str(self.traversal_order), True, pygame.Color("#FFFFFF"))

        self.id_text_label = UILabel(pygame.Rect(self.position, (32, 32)), str(self.traversal_order),
                                     manager=self.ui_manager, object_id="#small_screen_text")

    def kill(self):
        self.id_text_label.kill()

    def update_offset_position(self, offset):
        self.position = [self.world_position[0]-offset[0], self.world_position[1]-offset[1]]
        self.id_text_label.rect.x = self.position[0] + 16
        self.id_text_label.rect.y = self.position[1] + 16

    def draw(self, screen):
        screen.blit(self.rectangle_surface, [self.position[0] + 16, self.position[1] + 16])
        screen.blit(self.surface, self.position)
        # screen.blit(self.id_text, self.id_text.get_rect(centerx=self.position[0] + 32, centery=self.position[1] + 32))


class RemoveTurretSquareIcon(pygame.sprite.Sprite):
    def __init__(self, position, *groups):
        super().__init__(*groups)
        self.position = position
        self.image = pygame.image.load("images/remove_turret_square_icon.png").convert_alpha()
        self.rect = self.image.get_rect()
        self.rect.center = self.position

    def is_inside(self, pos):
        if self.rect[0] <= pos[0] < self.rect[0] + self.rect[2]:
            if self.rect[1] <= pos[1] < self.rect[1] + self.rect[3]:
                return True
        return False


class PlaceTurretSquareIcon(pygame.sprite.Sprite):
    def __init__(self, position, *groups):
        super().__init__(*groups)
        self.position = position
        self.image = pygame.image.load("images/place_turret_square_icon.png").convert_alpha()
        self.rect = self.image.get_rect()
        self.rect.center = self.position

    def is_inside(self, pos):
        if self.rect[0] <= pos[0] < self.rect[0] + self.rect[2]:
            if self.rect[1] <= pos[1] < self.rect[1] + self.rect[3]:
                return True
        return False


class RemoveWaypointIcon(pygame.sprite.Sprite):
    def __init__(self, position, *groups):
        super().__init__(*groups)
        self.position = position
        self.sprite = pygame.sprite.Sprite()
        self.image = pygame.image.load("images/remove_waypoint_icon.png").convert_alpha()
        self.rect = self.image.get_rect()
        self.rect.center = self.position

    def is_inside(self, pos):
        if self.rect[0] <= pos[0] < self.rect[0] + self.rect[2]:
            if self.rect[1] <= pos[1] < self.rect[1] + self.rect[3]:
                return True
        return False


class PlaceWaypointIcon(pygame.sprite.Sprite):
    def __init__(self, position, *groups):
        super().__init__(*groups)
        self.position = position
        self.image = pygame.image.load("images/place_waypoint_icon.png").convert_alpha()
        self.rect = self.image.get_rect()
        self.rect.center = self.position

    def is_inside(self, pos):
        if self.rect[0] <= pos[0] < self.rect[0] + self.rect[2]:
            if self.rect[1] <= pos[1] < self.rect[1] + self.rect[3]:
                return True
        return False


class PlayableAreaDisplay:
    def __init__(self):
        self.dimensions = [128, 104, 1152, 576]

    def draw(self, screen, offset):
        # draw 4 lines bounding the playable area
        pygame.draw.line(screen, pygame.Color("#C83232"), [self.dimensions[0]-offset[0], self.dimensions[1]-offset[1]],
                         [self.dimensions[0]-offset[0], self.dimensions[3]-offset[1]], 3)
        pygame.draw.line(screen, pygame.Color("#C83232"), [self.dimensions[0]-offset[0], self.dimensions[1]-offset[1]],
                         [self.dimensions[2]-offset[0], self.dimensions[1]-offset[1]], 3)
        pygame.draw.line(screen, pygame.Color("#C83232"), [self.dimensions[2]-offset[0], self.dimensions[1]-offset[1]],
                         [self.dimensions[2]-offset[0], self.dimensions[3]-offset[1]], 3)
        pygame.draw.line(screen, pygame.Color("#C83232"), [self.dimensions[0]-offset[0], self.dimensions[3]-offset[1]],
                         [self.dimensions[2]-offset[0], self.dimensions[3]-offset[1]], 3)


class MapEditor:
    def __init__(self, tiled_level, hud_rect, all_square_sprites, ui_manager):
        self.editing_layer = 0
        self.tiled_level = tiled_level
        self.hud_rect = hud_rect
        self.all_square_sprites = all_square_sprites
        self.ui_manager = ui_manager

        self.current_levels = [file for file in os.listdir("data/levels/")
                               if os.path.isfile(os.path.join("data/levels/", file))]
        
        self.left_mouse_held = False
        self.right_mouse_held = False

        self.need_to_refresh_tiles = True

        self.default_tile = [pygame.Rect(0, 0, 0, 0), self.tiled_level.tile_map[0][0], "grass_tile", True, None]
        self.held_tile_data = self.default_tile

        self.held_ai_spawn = None
        self.held_turret_square = None

        self.rect_of_tile = None
        self.hovered_rec = None

        self.rotate_selected_tile_left = False
        self.rotate_selected_tile_right = False

        self.all_palette_tile_sprites = pygame.sprite.Group()
        self.all_ai_spawn_sprites = pygame.sprite.Group()

        self.palette_page = 0
        self.should_increase_palette_page = False
        self.should_decrease_palette_page = False

        self.remove_turret_square_icon = None
        self.place_turret_square_icon = None
        self.remove_waypoint_icon = None
        self.place_waypoint_icon = None
        self.right_click_mode = "place_tile"
        
        self.palette_tiles = []
        self.palette_ai_spawns = []
        self.num_ai_spawns = 3
        self.tiles_per_page = 26
        all_tiles_and_ai = len(self.tiled_level.all_tile_data.keys()) + self.num_ai_spawns
        self.max_pages = int(math.ceil(all_tiles_and_ai / self.tiles_per_page))

        self.refresh_palette_tiles()

        self.left_scroll_held = False
        self.right_scroll_held = False
        self.up_scroll_held = False
        self.down_scroll_held = False

        self.map_scroll_speed = 256.0

        self.map_start_pos = self.tiled_level.find_player_start()
        self.map_position = [self.map_start_pos[0], self.map_start_pos[1]]

        # self.map_editor_instructions = MapEditorInstructionsWindow([362, 100, 300, 250], fonts)
        instructions_message = ("Arrow keys to scroll map <br>"
                                "Left mouse click to select tile from palette<br>"
                                "Right mouse click to place tile<br>"
                                "'>' and '<' to rotate selected tile<br>"
                                "F5 or quit to save map<br>")
        self.instruction_message_window = UIMessageWindow(pygame.Rect((312, 100), (400, 250)),
                                                          instructions_message,
                                                          self.ui_manager,
                                                          window_title="Instructions")

        self.level_name_label = UILabel(pygame.Rect((462, 8), (100, 34)),
                                        self.tiled_level.level_name,
                                        self.ui_manager, object_id="#screen_text")

        self.make_new_button = UIButton(pygame.Rect(870, self.hud_rect[1] + 24, 150, 20),
                                        "Make New", self.ui_manager)

        self.tile_set_button = UIButton(pygame.Rect(870, self.hud_rect[1] + 49, 150, 20),
                                        "Switch Tiles", self.ui_manager)

        self.playable_area_display = PlayableAreaDisplay()

        self.visible_way_point_circles = []
        self.refresh_visible_waypoint_circles()

    def end(self):
        if self.tile_set_button is not None:
            self.tile_set_button.kill()
            self.tile_set_button = None

        if self.make_new_button is not None:
            self.make_new_button.kill()
            self.make_new_button = None

        if self.level_name_label is not None:
            self.level_name_label.kill()
            self.level_name_label = None

        if self.instruction_message_window is not None:
            self.instruction_message_window.kill()
            self.instruction_message_window = None

        for circle in self.visible_way_point_circles:
            circle.kill()

    def refresh_visible_waypoint_circles(self):
        for circle in self.visible_way_point_circles:
            circle.kill()
            del circle
        self.visible_way_point_circles[:] = []
        traversal_order = 1
        if self.tiled_level.monster_walk_path.start_waypoint is not None:
            self.visible_way_point_circles.append(
                DrawableWaypointCircle(self.tiled_level.monster_walk_path.waypoint_radius,
                                       self.tiled_level.monster_walk_path.start_waypoint,
                                       self.ui_manager, traversal_order))
            traversal_order += 1
        for waypoint in self.tiled_level.monster_walk_path.waypoints:
            self.visible_way_point_circles.append(
                DrawableWaypointCircle(self.tiled_level.monster_walk_path.waypoint_radius,
                                       waypoint, self.ui_manager, traversal_order))
            traversal_order += 1
        
    def display_turret_placement_squares(self, screen):
        self.all_square_sprites.draw(screen)
        
    def increase_palette_pos(self, x_pos, y_pos):
        x_pos += self.tiled_level.tile_size[0] + 8
        if x_pos > 800:
            x_pos = 40
            y_pos += self.tiled_level.tile_size[1] + 8
        return x_pos, y_pos
    
    def refresh_palette_tiles(self):
        self.all_palette_tile_sprites.empty()
        self.palette_tiles[:] = []
        self.palette_ai_spawns[:] = []
        x_pos = 40
        y_pos = 40

        sorted_tile_keys = sorted(self.tiled_level.all_tile_data.keys())
        display_tile = self.palette_page * self.tiles_per_page

        max_tile = (self.palette_page * self.tiles_per_page) + self.tiles_per_page
        min_tile = len(sorted_tile_keys) + self.num_ai_spawns
        while display_tile < min_tile and display_tile < max_tile:
            if display_tile < len(sorted_tile_keys):
                tile_data = sorted_tile_keys[display_tile]
                self.palette_tiles.append(Tile([self.hud_rect[0] + x_pos, self.hud_rect[1] + y_pos],
                                               0, self.tiled_level.all_tile_data[tile_data], self.editing_layer))
                display_tile += 1
            else:  
                self.remove_turret_square_icon = RemoveTurretSquareIcon([self.hud_rect[0] + x_pos,
                                                                         self.hud_rect[1] + y_pos],
                                                                        self.all_palette_tile_sprites)
                x_pos, y_pos = self.increase_palette_pos(x_pos, y_pos)
                display_tile += 1

                self.place_turret_square_icon = PlaceTurretSquareIcon([self.hud_rect[0] + x_pos,
                                                                       self.hud_rect[1] + y_pos],
                                                                      self.all_palette_tile_sprites)
                x_pos, y_pos = self.increase_palette_pos(x_pos, y_pos)
                display_tile += 1

                self.remove_waypoint_icon = RemoveWaypointIcon([self.hud_rect[0] + x_pos,
                                                                self.hud_rect[1] + y_pos],
                                                               self.all_palette_tile_sprites)
                x_pos, y_pos = self.increase_palette_pos(x_pos, y_pos)
                display_tile += 1

                self.place_waypoint_icon = PlaceWaypointIcon([self.hud_rect[0] + x_pos,
                                                              self.hud_rect[1] + y_pos],
                                                             self.all_palette_tile_sprites)
                x_pos, y_pos = self.increase_palette_pos(x_pos, y_pos)
                display_tile += 1
                
                display_tile += self.num_ai_spawns
                
            x_pos, y_pos = self.increase_palette_pos(x_pos, y_pos)

        for tile in self.palette_tiles:
            self.all_palette_tile_sprites.add(tile)

        # for aiSpawn in self.paletteAISpawns:
        #    self.allPaletteTileSprites.add(aiSpawn.sprite)

    def run(self, screen, background, all_tile_sprites, hud_rect, time_delta):
        running = True
        for event in pygame.event.get():
            self.ui_manager.process_events(event)

            if event.type == pygame_gui.UI_BUTTON_PRESSED:
                if event.ui_element == self.make_new_button:
                    new_level_num = len(self.current_levels) + 1
                    new_level_name = "Level " + str(new_level_num)
                    self.tiled_level.change_level_name_and_save(new_level_name)
                    self.level_name_label.set_text(self.tiled_level.level_name)
                elif event.ui_element == self.tile_set_button:
                    self.tiled_level.toggle_tile_map()
                    for tile in self.palette_tiles:
                        tile.reload_tile_image_from_data(self.tiled_level.all_tile_data)

            if event.type == QUIT:
                self.tiled_level.save_tiles()
                running = False
            if event.type == MOUSEBUTTONDOWN:
                if event.button == 1:
                    self.left_mouse_held = True
                if event.button == 3:
                    self.right_mouse_held = True
            if event.type == MOUSEBUTTONUP:
                if event.button == 1:
                    self.left_mouse_held = False
                if event.button == 3:
                    self.right_mouse_held = False
            if event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    self.tiled_level.save_tiles()
                    running = False
                if event.key == K_F5:
                    self.tiled_level.save_tiles()
                if event.key == K_PERIOD:
                    self.rotate_selected_tile_right = True
                if event.key == K_COMMA:
                    self.rotate_selected_tile_left = True
                if event.key == K_UP:
                    self.up_scroll_held = True
                if event.key == K_DOWN:
                    self.down_scroll_held = True
                if event.key == K_LEFT:
                    self.left_scroll_held = True
                if event.key == K_RIGHT:
                    self.right_scroll_held = True
                if event.key == K_1:
                    self.editing_layer = 1
                if event.key == K_0:
                    self.editing_layer = 0
                if event.key == K_RIGHTBRACKET:
                    self.should_increase_palette_page = True
                if event.key == K_LEFTBRACKET:
                    self.should_decrease_palette_page = True
            if event.type == KEYUP:
                if event.key == K_UP:
                    self.up_scroll_held = False
                if event.key == K_DOWN:
                    self.down_scroll_held = False
                if event.key == K_LEFT:
                    self.left_scroll_held = False
                if event.key == K_RIGHT:
                    self.right_scroll_held = False
            
        self.ui_manager.update(time_delta)

        if self.should_increase_palette_page:
            self.should_increase_palette_page = False
            if self.palette_page < self.max_pages - 1:
                self.palette_page += 1
            else:
                self.palette_page = 0  # loop back round
            self.refresh_palette_tiles()

        if self.should_decrease_palette_page:
            self.should_decrease_palette_page = False
            if self.palette_page > 0:
                self.palette_page -= 1
            else:
                self.palette_page = self.max_pages - 1  # loop back round
            self.refresh_palette_tiles()

        if self.up_scroll_held:
            self.map_position[1] -= self.map_scroll_speed * time_delta
            if self.map_position[1] < self.tiled_level.initial_screen_offset[1]:
                self.map_position[1] = self.tiled_level.initial_screen_offset[1]
        if self.down_scroll_held:
            self.map_position[1] += self.map_scroll_speed * time_delta
            y_limit = self.tiled_level.level_pixel_size[1]-self.tiled_level.initial_screen_offset[1] + self.hud_rect[1]
            if self.map_position[1] > y_limit:
                self.map_position[1] = y_limit

        if self.left_scroll_held:
            self.map_position[0] -= self.map_scroll_speed * time_delta
            if self.map_position[0] < self.tiled_level.initial_screen_offset[0]:
                self.map_position[0] = self.tiled_level.initial_screen_offset[0]
        if self.right_scroll_held:
            self.map_position[0] += self.map_scroll_speed * time_delta
            max_x = self.tiled_level.level_pixel_size[0] - self.tiled_level.initial_screen_offset[0]
            if self.map_position[0] > max_x:
                self.map_position[0] = max_x
                
        if self.rotate_selected_tile_right and self.held_tile_data[4] is not None:
            self.rotate_selected_tile_right = False
            self.held_tile_data[4].rotate_tile_right()
            self.need_to_refresh_tiles = True

        if self.rotate_selected_tile_left and self.held_tile_data[4] is not None:
            self.rotate_selected_tile_left = False
            self.held_tile_data[4].rotate_tile_left()
            self.need_to_refresh_tiles = True
        
        if self.left_mouse_held:
            click_pos = pygame.mouse.get_pos()
            if self.is_inside_hud(click_pos, hud_rect):
                self.held_tile_data = self.get_palette_tile_data_at_pos(click_pos)
                if self.held_tile_data is None:
                    if self.remove_turret_square_icon.is_inside(click_pos):
                        self.right_click_mode = "remove_turret_square"
                    elif self.place_turret_square_icon.is_inside(click_pos):
                        self.right_click_mode = "place_turret_square"
                    elif self.remove_waypoint_icon.is_inside(click_pos):
                        self.right_click_mode = "remove_waypoint"
                    elif self.place_waypoint_icon.is_inside(click_pos):
                        self.right_click_mode = "place_waypoint"
                else:
                    self.right_click_mode = "place_tile"
                    
            else:
                self.held_tile_data = self.tiled_level.get_tile_data_at_pos(click_pos, self.editing_layer)

        if self.right_mouse_held:
            click_pos = pygame.mouse.get_pos()
            
            if self.is_inside_hud(click_pos, hud_rect):
                pass
            else:
                angle = 0
                if self.right_click_mode == "place_tile" and self.held_tile_data is not None:
                    if self.held_tile_data[4] is not None:
                        angle = self.held_tile_data[4].angle
                    self.rect_of_tile = self.tiled_level.set_tile_at_pos(click_pos, self.held_tile_data[2],
                                                                         angle, self.editing_layer)
                elif self.right_click_mode == "place_ai" and self.held_ai_spawn is not None:
                    self.tiled_level.add_ai_spawn_at_pos(click_pos, self.held_ai_spawn)
                elif self.right_click_mode == "remove_ai":
                    self.tiled_level.remove_ai_spawn_at_pos(click_pos)
                elif self.right_click_mode == "remove_turret_square":
                    self.tiled_level.remove_turret_square_at_pos(click_pos)
                elif self.right_click_mode == "place_turret_square":
                    self.tiled_level.place_turret_square_at_pos(click_pos)
                elif self.right_click_mode == "remove_waypoint":
                    self.tiled_level.remove_waypoint_at_pos(click_pos)
                    self.refresh_visible_waypoint_circles()
                elif self.right_click_mode == "place_waypoint":
                    if self.tiled_level.place_waypoint_at_pos(click_pos):
                        self.refresh_visible_waypoint_circles()

        if self.tiled_level.update_offset_position(self.map_position, all_tile_sprites):
            self.need_to_refresh_tiles = True
                
        self.all_ai_spawn_sprites.empty()
        for ai_spawn in self.tiled_level.ai_spawns:
            self.all_ai_spawn_sprites.add(ai_spawn)

        self.hovered_rec = self.tiled_level.get_tile_data_at_pos(pygame.mouse.get_pos(), self.editing_layer)[0]

        screen.blit(background, (0, 0))  # draw the background
        all_tile_sprites.draw(screen)
        self.all_ai_spawn_sprites.draw(screen)

        self.playable_area_display.draw(screen, self.tiled_level.position_offset)

        self.display_turret_placement_squares(screen)

        for waypoint_circles in self.visible_way_point_circles:
            waypoint_circles.update_offset_position(self.tiled_level.position_offset)
            waypoint_circles.draw(screen)

        if self.held_tile_data is not None:
            if not self.held_tile_data[3]:
                pygame.draw.rect(screen, pygame.Color("#FF6464"), self.held_tile_data[0], 1)
        if self.hovered_rec is not None:
            pygame.draw.rect(screen, pygame.Color("#FFE164"), self.hovered_rec, 1)
        # draw the hud
        pygame.draw.rect(screen, pygame.Color("#3C3C3C"), hud_rect, 0)
        self.all_palette_tile_sprites.draw(screen)
        if self.held_tile_data is not None:
            if self.held_tile_data[3]:
                pygame.draw.rect(screen, pygame.Color("#FF6464"), self.held_tile_data[0], 1)

        self.ui_manager.draw_ui(screen)

        return running

    @staticmethod
    def is_inside_hud(pos, hud_rect):
        if hud_rect[0] <= pos[0] and hud_rect[1] <= pos[1]:
            if hud_rect[0] + hud_rect[2] > pos[0] and hud_rect[1] + hud_rect[3] > pos[1]:
                return True
        return False

    def get_palette_tile_data_at_pos(self, click_pos):
        for tile in self.palette_tiles:
            x_min = tile.rect[0]
            x_max = tile.rect[0] + tile.rect[2]
            y_min = tile.rect[1]
            y_max = tile.rect[1] + tile.rect[3]
            if x_min <= click_pos[0] < x_max:
                if y_min <= click_pos[1] < y_max:
                    return [tile.rect, tile.image, tile.tile_id, True, None]
        return None

    def get_ai_spawn_data_at_pos(self, click_pos):
        for ai_spawn in self.palette_ai_spawns:
            x_min = ai_spawn.rect[0]
            x_max = ai_spawn.rect[0] + ai_spawn.rect[2]
            y_min = ai_spawn.rect[1]
            y_max = ai_spawn.rect[1] + ai_spawn.rect[3]
            if x_min <= click_pos[0] < x_max:
                if y_min <= click_pos[1] < y_max:
                    return ai_spawn
        return None

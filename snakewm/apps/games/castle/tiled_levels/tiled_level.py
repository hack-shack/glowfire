import pygame
import csv
import os

from typing import List
from .tile import Tile, TileData, AISpawn
from ..game.base_monster import MonsterPath
from ..game.place_square import PlaceSquare


class TiledLevel:
    def __init__(self, file_name, level_tile_size, all_tile_sprites, all_monster_sprites, all_square_sprites,
                 entity_image_atlas, monsters, screen_data, explosions_sprite_sheet):

        self.tile_size = [32, 32]
        self.initial_screen_offset = [0, 0]
        self.position_offset = [0, 0]
        self.current_centre_position = [100000000, 111111111111]
        self.explosions_sprite_sheet = explosions_sprite_sheet
        self.guards_sprite_map = None

        self.file_name = file_name
        self.level_name = "Untitled"
        self.screen_data = screen_data

        self.all_tile_sprites = all_tile_sprites
        self.all_top_tile_sprites = pygame.sprite.Group()
        self.all_tile_map_paths = ["images/tiles/" + file for file in os.listdir("images/tiles/")
                                   if os.path.isfile(os.path.join("images/tiles/", file))]
        
        self.tile_map_path = self.all_tile_map_paths[0]
        
        if os.path.isfile(self.file_name):
            with open(self.file_name, "r") as tileFile:
                reader = csv.reader(tileFile)
                found_level_name = False
                found_tile_map = False
                for line in reader:
                    line_type = line[0]
                    if line_type == "level_name":
                        self.level_name = line[1]
                        found_level_name = True
                    if line_type == "tile_map":
                        self.tile_map_path = str(line[1])
                        found_tile_map = True
                   
                    if found_level_name and found_tile_map:
                        break                   
        
        self.tile_map = self.load_tile_table(self.tile_map_path, self.tile_size[0],
                                             self.tile_size[1], False)

        self.all_square_sprites = all_square_sprites
        self.all_square_sprites.empty()
        self.entity_image_atlas = entity_image_atlas
        self.all_monster_sprites = all_monster_sprites
        self.monsters = monsters
        self.monster_walk_path = MonsterPath()

        self.zero_tile_x = 0
        self.zero_tile_y = 0
        self.end_tile_x = 0
        self.end_tile_y = 0

        self.player_start = [0.0, 0.0]

        self.tile_grid = []  # type: List[List]
        self.top_tile_grid = []  # type: List[List]
        self.tiles = []
        self.collidable_tiles = []
        self.walkable_tiles = []

        self.ai_spawns = []

        self.turret_squares = []

        self.level_tile_size = level_tile_size
        self.level_pixel_size = [self.level_tile_size[0] * self.tile_size[0],
                                 self.level_tile_size[1] * self.tile_size[1]]

        for tile_x in range(0, self.level_tile_size[0]):
            column = []
            top_column = []
            for tile_y in range(0, self.level_tile_size[1]):
                column.append(None)
                top_column.append(None)
            self.tile_grid.append(column)
            self.top_tile_grid.append(top_column)
            
        self.initial_offset = True

        self.all_tile_data = {}
        tile_data_files = [file for file in os.listdir("data/tiles/")
                           if os.path.isfile(os.path.join("data/tiles/", file))]

        self.default_tile = None
        for file_name in tile_data_files:
            new_tile_data = TileData(os.path.join("data/tiles/", file_name), self.tile_map)
            new_tile_data.load_tile_data()
            self.all_tile_data[new_tile_data.tile_id] = new_tile_data
            if self.default_tile is None:
                self.default_tile = new_tile_data

    def clear(self):
        for tile in self.tiles:
            tile.kill()

    def toggle_tile_map(self):
        current_tile_map_index = 0
        all_maps_index = 0
        for tileMap in self.all_tile_map_paths:
            if tileMap == self.tile_map_path:
                current_tile_map_index = all_maps_index
            all_maps_index += 1

        if current_tile_map_index+1 < len(self.all_tile_map_paths):
            current_tile_map_index += 1
        else:
            current_tile_map_index = 0

        self.tile_map_path = self.all_tile_map_paths[current_tile_map_index]
        self.tile_map = self.load_tile_table(self.tile_map_path, self.tile_size[0],
                                             self.tile_size[1], False)

        for tile_name, tile_data in self.all_tile_data.items():
            tile_data.update_tile_map(self.tile_map)

        for tile in self.tiles:
            tile.reload_tile_image_from_data(self.all_tile_data)

    def change_level_name_and_save(self, new_name):
        self.level_name = new_name
        self.file_name = "data/levels/" + self.level_name.lower().replace(' ', '_') + ".csv"
        self.save_tiles()

    def reset_squares(self):
        for square in self.turret_squares:
            square.occupied = False

    def clear_level_to_default_tile(self):
        for x in range(0, self.level_tile_size[0]):
            for y in range(0, self.level_tile_size[1]):
                self.make_empty_tile_default(x, y)

    def make_empty_tile_default(self, tile_x: int, tile_y: int):
        x_centre = self.tile_size[0] / 2 + (tile_x * self.tile_size[0])
        y_centre = self.tile_size[1] / 2 + (tile_y * self.tile_size[1])
        default_tile = Tile([x_centre, y_centre], 0, self.default_tile, 0)
        self.tiles.append(default_tile)
        self.walkable_tiles.append(default_tile)
        self.tile_grid[tile_x][tile_y] = default_tile
        
    def update_offset_position(self, centre_position, all_tile_sprites):
        should_update = False
        self.current_centre_position = centre_position
        x_offset = int(self.current_centre_position[0] - self.initial_screen_offset[0])
        y_offset = int(self.current_centre_position[1] - self.initial_screen_offset[1])

        if x_offset <= 0:
            x_offset = 0
        if x_offset >= int(self.level_pixel_size[0] - self.screen_data.play_area[0]):
            x_offset = int(self.level_pixel_size[0] - self.screen_data.play_area[0])

        if y_offset <= 0:
            y_offset = 0
        if y_offset >= int(self.level_pixel_size[1] - self.screen_data.play_area[1]):
            y_offset = int(self.level_pixel_size[1] - self.screen_data.play_area[1])

        if self.initial_offset or not (x_offset == self.position_offset[0] and y_offset == self.position_offset[1]):
            if self.initial_offset:
                self.initial_offset = False
            self.position_offset = [x_offset, y_offset]

            screen_tile_width = int(self.screen_data.play_area[0] / self.tile_size[0]) + 1
            screen_tile_height = int(self.screen_data.play_area[1] / self.tile_size[1]) + 2

            old_zero_tile_x = self.zero_tile_x
            old_zero_tile_y = self.zero_tile_y

            self.zero_tile_x = int(x_offset / self.tile_size[0])
            self.zero_tile_y = int(y_offset / self.tile_size[1])

            if self.zero_tile_x != old_zero_tile_x or self.zero_tile_y != old_zero_tile_y:
                all_tile_sprites.empty()
                self.end_tile_x = self.zero_tile_x + screen_tile_width
                self.end_tile_y = self.zero_tile_y + screen_tile_height

                if self.zero_tile_x >= len(self.tile_grid):
                    self.zero_tile_x = len(self.tile_grid) - screen_tile_width
                if self.zero_tile_y >= len(self.tile_grid[0]):
                    self.zero_tile_y = len(self.tile_grid[0]) - screen_tile_height

                if self.end_tile_x >= len(self.tile_grid):
                    self.end_tile_x = len(self.tile_grid)
                if self.end_tile_y >= len(self.tile_grid[0]):
                    self.end_tile_y = len(self.tile_grid[0])
                
                for tileX in range(self.zero_tile_x, self.end_tile_x):
                    for tileY in range(self.zero_tile_y, self.end_tile_y):
                        tile = self.tile_grid[tileX][tileY]
                        if tile is None:
                            print("No tile at grid: " + str(tileX) + ", " + str(tileY) + ": clearing to default")
                            self.make_empty_tile_default(tileX, tileY)
                        else:
                            tile.update_offset_position(self.position_offset, self.screen_data)
                            all_tile_sprites.add(tile)
            else:
                for tileX in range(self.zero_tile_x, self.end_tile_x):
                    for tileY in range(self.zero_tile_y, self.end_tile_y):
                        tile = self.tile_grid[tileX][tileY]
                        if tile is None:
                            print("No tile at grid: " + str(tileX) + ", " + str(tileY) + ": clearing to default")
                            self.make_empty_tile_default(tileX, tileY)
                        else:
                            tile.update_offset_position(self.position_offset, self.screen_data)

            for spawn in self.ai_spawns:
                spawn.update_offset_position(self.position_offset)

            for square in self.turret_squares:
                square.update_offset_position(self.position_offset)

        return should_update
    
    def draw_tile_collision_shapes(self, screen):
        for tile_x in range(self.zero_tile_x, self.end_tile_x):
            for tile_y in range(self.zero_tile_y, self.end_tile_y):
                tile = self.tile_grid[tile_x][tile_y]
                if tile is not None:
                    tile.draw_collision_shapes(screen)
    
    def find_player_start(self):
        screen_centre = [self.screen_data.play_area[0] / 2, self.screen_data.play_area[1] / 2]
        self.player_start = [640, 332]
        
        self.initial_screen_offset[0] = screen_centre[0]
        self.initial_screen_offset[1] = screen_centre[1]
        
        self.current_centre_position = self.player_start
        x_offset = int(self.current_centre_position[0] - self.initial_screen_offset[0])
        y_offset = int(self.current_centre_position[1] - self.initial_screen_offset[1])

        if x_offset <= 0:
            x_offset = 0
        if x_offset >= int(self.level_pixel_size[0] - self.screen_data.play_area[0]):
            x_offset = int(self.level_pixel_size[0] - self.screen_data.play_area[0])

        if y_offset <= 0:
            y_offset = 0
        if y_offset >= int(self.level_pixel_size[1] - self.screen_data.play_area[1]):
            y_offset = int(self.level_pixel_size[1] - self.screen_data.play_area[1])
            
        self.position_offset = [x_offset, y_offset]
        self.initial_offset = True
        return self.player_start

    @staticmethod
    def load_tile_table(filename, width, height, use_transparency):
        if use_transparency:
            image = pygame.image.load(filename).convert_alpha()
        else:
            image = pygame.image.load(filename).convert()
        image_width, image_height = image.get_size()
        tile_table = []
        for tile_x in range(0, int(image_width/width)):
            line = []
            tile_table.append(line)
            for tile_y in range(0, int(image_height/height)):
                rect = (tile_x*width, tile_y*height, width, height)
                line.append(image.subsurface(rect))
        return tile_table

    def get_tile_data_at_pos(self, click_pos, layer):
        for tile_x in range(self.zero_tile_x, self.end_tile_x):
            for tile_y in range(self.zero_tile_y, self.end_tile_y):
                if layer == 0:
                    tile = self.tile_grid[tile_x][tile_y]
                    tile_screen_min = [(tile_x * self.tile_size[0]) - self.position_offset[0],
                                       (tile_y * self.tile_size[1]) - self.position_offset[1]]
                    tile_screen_max = [(tile_x * self.tile_size[0]) + self.tile_size[0] - self.position_offset[0],
                                       (tile_y * self.tile_size[1]) + self.tile_size[1] - self.position_offset[1]]
                    if tile_screen_min[0] <= click_pos[0] and tile_screen_min[1] <= click_pos[1]:
                        if tile_screen_max[0] > click_pos[0] and tile_screen_max[1] > click_pos[1]:
                            if tile is not None:
                                return [tile.rect, tile.image, tile.tile_id, False, tile]
                            else:
                                return [pygame.Rect(tile_screen_min[0], tile_screen_min[1], 64, 64),
                                        None, "", False, None]
                if layer == 1:
                    tile = self.top_tile_grid[tile_x][tile_y]
                    tile_screen_min = [(tile_x * self.tile_size[0]) - self.position_offset[0],
                                       (tile_y * self.tile_size[1]) - self.position_offset[1]]
                    tile_screen_max = [(tile_x * self.tile_size[0]) + self.tile_size[0] - self.position_offset[0],
                                       (tile_y * self.tile_size[1]) + self.tile_size[1] - self.position_offset[1]]
                    if tile_screen_min[0] <= click_pos[0] and tile_screen_min[1] <= click_pos[1]:
                        if tile_screen_max[0] > click_pos[0] and tile_screen_max[1] > click_pos[1]:
                            if tile is not None:
                                return [tile.rect, tile.image, tile.tile_id, False, tile]
                            else:
                                return [pygame.Rect(tile_screen_min[0], tile_screen_min[1], self.tile_size[0],
                                                    self.tile_size[1]), None, "", False, None]
                    
        return [pygame.Rect(0, 0, 0, 0), None, "", False, None]

    def set_tile_at_pos(self, click_pos, tile_id, tile_angle, layer):
        tile_to_set = None
        tile_click_x = 0
        tile_click_y = 0
        for tile_x in range(self.zero_tile_x, self.end_tile_x):
            for tile_y in range(self.zero_tile_y, self.end_tile_y):
                if layer == 0:
                    tile = self.tile_grid[tile_x][tile_y]
                    tile_screen_min = [(tile_x * self.tile_size[0]) - self.position_offset[0],
                                       (tile_y * self.tile_size[1]) - self.position_offset[1]]
                    tile_screen_max = [(tile_x * self.tile_size[0]) + self.tile_size[0] - self.position_offset[0],
                                       (tile_y * self.tile_size[1]) + self.tile_size[1] - self.position_offset[1]]
                    if tile_screen_min[0] <= click_pos[0] and tile_screen_min[1] <= click_pos[1]:
                        if tile_screen_max[0] > click_pos[0] and tile_screen_max[1] > click_pos[1]:
                            tile_to_set = tile
                            tile_click_x = tile_x
                            tile_click_y = tile_y
                            break
                if layer == 1:
                    tile = self.top_tile_grid[tile_x][tile_y]
                    tile_screen_min = [(tile_x * self.tile_size[0]) - self.position_offset[0],
                                       (tile_y * self.tile_size[1]) - self.position_offset[1]]
                    tile_screen_max = [(tile_x * self.tile_size[0]) + self.tile_size[0] - self.position_offset[0],
                                       (tile_y * self.tile_size[1]) + self.tile_size[1] - self.position_offset[1]]
                    if tile_screen_min[0] <= click_pos[0] and tile_screen_min[1] <= click_pos[1]:
                        if tile_screen_max[0] > click_pos[0] and tile_screen_max[1] > click_pos[1]:
                            tile_to_set = tile
                            tile_click_x = tile_x
                            tile_click_y = tile_y
                            break
                        
        if tile_to_set is not None:
            if layer == 0:
                if tile_to_set.collidable:
                    self.collidable_tiles.remove(tile_to_set)
                else:
                    self.walkable_tiles.remove(tile_to_set)
            
            self.tiles.remove(tile_to_set)

            new_tile = Tile(tile_to_set.world_position, tile_angle, self.all_tile_data[tile_id], layer)
            self.tiles.append(new_tile)

            new_x_grid_pos = int((new_tile.world_position[0] - (self.tile_size[0] / 2)) / self.tile_size[0])
            new_y_grid_pos = int((new_tile.world_position[1] - (self.tile_size[1] / 2)) / self.tile_size[1])
            if layer == 0:
                self.tile_grid[new_x_grid_pos][new_y_grid_pos] = new_tile
                if new_tile.collidable:
                    self.collidable_tiles.append(new_tile)
                else:
                    self.walkable_tiles.append(new_tile)
            if layer == 1:
                self.top_tile_grid[new_x_grid_pos][new_y_grid_pos] = new_tile
        else:
            new_tile_world_position = [int((tile_click_x * self.tile_size[0]) + (self.tile_size[0] / 2)),
                                       int((tile_click_y * self.tile_size[1]) + (self.tile_size[1] / 2))]
            new_tile = Tile(new_tile_world_position, tile_angle, self.all_tile_data[tile_id], layer)
            self.tiles.append(new_tile)

            new_x_grid_pos = int((new_tile.world_position[0] - (self.tile_size[0] / 2)) / self.tile_size[0])
            new_y_grid_pos = int((new_tile.world_position[1] - (self.tile_size[1] / 2)) / self.tile_size[1])
            if layer == 0:
                self.tile_grid[new_x_grid_pos][new_y_grid_pos] = new_tile
                if new_tile.collidable:
                    self.collidable_tiles.append(new_tile)
                else:
                    self.walkable_tiles.append(new_tile)
            if layer == 1:
                self.top_tile_grid[new_x_grid_pos][new_y_grid_pos] = new_tile

        self.all_tile_sprites.empty()
        for tile_x in range(self.zero_tile_x, self.end_tile_x):
            for tile_y in range(self.zero_tile_y, self.end_tile_y):
                tile = self.tile_grid[tile_x][tile_y]
                if tile is None:
                    print("No tile at grid: " + str(tile_x) + ", " + str(tile_y))
                else:
                    tile.update_offset_position(self.position_offset, self.screen_data)
                    self.all_tile_sprites.add(tile)

                top_tile = self.top_tile_grid[tile_x][tile_y]
                if top_tile is not None:
                    top_tile.update_offset_position(self.position_offset, self.screen_data)
                    self.all_top_tile_sprites.add(top_tile)

    def save_tiles(self):
        with open(self.file_name, "w", newline='') as tileFile:
            writer = csv.writer(tileFile, quotechar='"', quoting=csv.QUOTE_NONNUMERIC)
            writer.writerow(["level_name", self.level_name])
            writer.writerow(["tile_map", self.tile_map_path])
            for tile in self.tiles:
                writer.writerow(["tile", tile.tile_id, int(tile.world_position[0]),
                                 int(tile.world_position[1]), int(tile.angle)])
            for ai_spawn in self.ai_spawns:
                writer.writerow(["ai_spawn", ai_spawn.type_id, str(int(ai_spawn.world_position[0])),
                                 str(int(ai_spawn.world_position[1]))])
            for square in self.turret_squares:
                writer.writerow(["placement_square", int(square.world_position[0]), int(square.world_position[1])])

            if self.monster_walk_path.start_waypoint is not None:
                writer.writerow(["monster_waypoint_start", self.monster_walk_path.start_waypoint[0],
                                 self.monster_walk_path.start_waypoint[1]])

            for waypoint in self.monster_walk_path.waypoints:
                writer.writerow(["monster_waypoint", waypoint[0], waypoint[1]])
                
    def load_tiles(self):
        if os.path.isfile(self.file_name):
            self.tiles[:] = []
            self.collidable_tiles[:] = []
            self.walkable_tiles[:] = []
            
            with open(self.file_name, "r") as tileFile:
                reader = csv.reader(tileFile)
                for line in reader:
                    line_type = line[0]
                    
                    if line_type == "tile":
                        tile_id = line[1]
                        tile_x_pos = int(line[2])
                        tile_y_pos = int(line[3])
                        tile_angle = int(line[4])
                        tile_layer = 0
                        if len(line) == 6:
                            tile_layer = int(line[5])
                            
                        loaded_tile = Tile([tile_x_pos, tile_y_pos], tile_angle,
                                           self.all_tile_data[tile_id], tile_layer)
                        self.tiles.append(loaded_tile)
                        tile_x_grid_pos = int((tile_x_pos - (self.tile_size[0] / 2)) / self.tile_size[0])
                        tile_y_grid_pos = int((tile_y_pos - (self.tile_size[1] / 2)) / self.tile_size[1])
                        self.tile_grid[tile_x_grid_pos][tile_y_grid_pos] = loaded_tile

                        if loaded_tile.collidable:
                            self.collidable_tiles.append(loaded_tile)
                        else:
                            self.walkable_tiles.append(loaded_tile)
                            
                    elif line_type == "aiSpawn":
                        type_id = line[1]
                        tile_x_pos = int(line[2])
                        tile_y_pos = int(line[3])
                        new_ai_spawn = AISpawn(self.guards_sprite_map[0][1], [tile_x_pos, tile_y_pos], type_id)
                        self.ai_spawns.append(new_ai_spawn)

                    elif line_type == "placement_square":
                        self.turret_squares.append(PlaceSquare([int(line[1]), int(line[2])],
                                                               self.all_square_sprites, self.entity_image_atlas))
                    elif line_type == "monster_waypoint_start":
                        self.monster_walk_path.start_waypoint = [int(line[1]), int(line[2])]
                    elif line_type == "monster_waypoint":
                        self.monster_walk_path.waypoints.append([int(line[1]), int(line[2])])
        else:
            self.clear_level_to_default_tile()

    def place_waypoint_at_pos(self, click_pos):
        tile_to_set = None
        for tile in self.tiles:
            x_min = tile.rect[0]
            x_max = tile.rect[0] + tile.rect[2]
            y_min = tile.rect[1]
            y_max = tile.rect[1] + tile.rect[3]
            if x_min <= click_pos[0] < x_max:
                if y_min <= click_pos[1] < y_max:
                    tile_to_set = tile
                    
        already_placed = False
        for waypoint in self.monster_walk_path.waypoints:
            if waypoint[0] == tile_to_set.world_position[0] and waypoint[1] == tile_to_set.world_position[1]:
                already_placed = True

        if self.monster_walk_path.start_waypoint is not None:
            x_equal = self.monster_walk_path.start_waypoint[0] == tile_to_set.world_position[0]
            y_equal = self.monster_walk_path.start_waypoint[1] == tile_to_set.world_position[1]
            if x_equal and y_equal:
                already_placed = True

        if not already_placed:
            new_waypoint = [tile_to_set.world_position[0], tile_to_set.world_position[1]]
            if self.monster_walk_path.start_waypoint is None:
                self.monster_walk_path.start_waypoint = new_waypoint
            else:
                self.monster_walk_path.waypoints.append(new_waypoint)

        return not already_placed

    def remove_waypoint_at_pos(self, click_pos):
        tile_to_set = None
        for tile in self.tiles:
            x_min = tile.rect[0]
            x_max = tile.rect[0] + tile.rect[2]
            y_min = tile.rect[1]
            y_max = tile.rect[1] + tile.rect[3]
            if x_min <= click_pos[0] < x_max:
                if y_min <= click_pos[1] < y_max:
                    tile_to_set = tile
                    
        waypoint_to_remove = None
        for waypoint in self.monster_walk_path.waypoints:
            if waypoint[0] == tile_to_set.world_position[0] and waypoint[1] == tile_to_set.world_position[1]:
                waypoint_to_remove = waypoint

        if self.monster_walk_path.start_waypoint is not None:
            x_equal = self.monster_walk_path.start_waypoint[0] == tile_to_set.world_position[0]
            y_equal = self.monster_walk_path.start_waypoint[1] == tile_to_set.world_position[1]
            if x_equal and y_equal:
                waypoint_to_remove = self.monster_walk_path.start_waypoint

        if waypoint_to_remove is not None:
            if waypoint_to_remove == self.monster_walk_path.start_waypoint:
                if len(self.monster_walk_path.waypoints) == 0:
                    self.monster_walk_path.start_waypoint = None
            else:
                self.monster_walk_path.waypoints.remove(waypoint_to_remove)

        # TODO: sort out re-ordering next?

    def place_turret_square_at_pos(self, click_pos):
        tile_to_set = None
        for tile in self.tiles:
            x_min = tile.rect[0]
            x_max = tile.rect[0] + tile.rect[2]
            y_min = tile.rect[1]
            y_max = tile.rect[1] + tile.rect[3]
            if x_min <= click_pos[0] < x_max:
                if y_min <= click_pos[1] < y_max:
                    tile_to_set = tile
                    
        already_placed = False
        for square in self.turret_squares:
            x_equal = square.world_position[0] == tile_to_set.world_position[0]
            y_equal = square.world_position[1] == tile_to_set.world_position[1]
            if x_equal and y_equal:
                already_placed = True

        if not already_placed:
            new_square = PlaceSquare([tile_to_set.world_position[0], tile_to_set.world_position[1]],
                                     self.all_square_sprites, self.entity_image_atlas)
            new_square.update_offset_position(self.position_offset)
            self.turret_squares.append(new_square)

    def remove_turret_square_at_pos(self, click_pos):
        tile_to_set = None
        for tile in self.tiles:
            x_min = tile.rect[0]
            x_max = tile.rect[0] + tile.rect[2]
            y_min = tile.rect[1]
            y_max = tile.rect[1] + tile.rect[3]
            if x_min <= click_pos[0] < x_max:
                if y_min <= click_pos[1] < y_max:
                    tile_to_set = tile
        turret_square_to_remove = None
        for square in self.turret_squares:
            x_equal = square.world_position[0] == tile_to_set.world_position[0]
            y_equal = square.world_position[1] == tile_to_set.world_position[1]
            if x_equal and y_equal:
                turret_square_to_remove = square

        if turret_square_to_remove is not None:
            self.all_square_sprites.remove(turret_square_to_remove)
            self.turret_squares.remove(turret_square_to_remove)
    
    def add_ai_spawn_at_pos(self, click_pos, ai_spawn):
        tile_to_set = None
        for tile in self.tiles:
            x_min = tile.rect[0]
            x_max = tile.rect[0] + tile.rect[2]
            y_min = tile.rect[1]
            y_max = tile.rect[1] + tile.rect[3]
            if x_min <= click_pos[0] < x_max:
                if y_min <= click_pos[1] < y_max:
                    tile_to_set = tile
        already_placed = False
        for spawn in self.ai_spawns:
            x_equal = spawn.world_position[0] == tile_to_set.world_position[0]
            y_equal = spawn.world_position[1] == tile_to_set.world_position[1]
            if x_equal and y_equal:
                already_placed = True

        if not already_placed:
            new_ai_spawn = AISpawn(ai_spawn.tile_image, tile_to_set.world_position, ai_spawn.type_id)
            new_ai_spawn.update_offset_position(self.position_offset)
            self.ai_spawns.append(new_ai_spawn)

    def remove_ai_spawn_at_pos(self, click_pos):
        tile_to_set = None
        for tile in self.tiles:
            x_min = tile.rect[0]
            x_max = tile.rect[0] + tile.rect[2]
            y_min = tile.rect[1]
            y_max = tile.rect[1] + tile.rect[3]
            if x_min <= click_pos[0] < x_max:
                if y_min <= click_pos[1] < y_max:
                    tile_to_set = tile
        spawn_to_remove = None
        for spawn in self.ai_spawns:
            x_equal = spawn.world_position[0] == tile_to_set.world_position[0]
            y_equal = spawn.world_position[1] == tile_to_set.world_position[1]
            if x_equal and y_equal:
                spawn_to_remove = spawn

        if spawn_to_remove is not None:
            self.ai_spawns.remove(spawn_to_remove)

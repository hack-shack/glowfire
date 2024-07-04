import pygame
import copy
import csv
import os


class AISpawn(pygame.sprite.Sprite):
    def __init__(self, image, position, type_id, *groups):
        super().__init__(*groups)
        self.type_id = type_id
        self.position = [0, 0]
        self.position[0] = position[0]
        self.position[1] = position[1]

        self.world_position = [0, 0]
        self.world_position[0] = position[0]
        self.world_position[1] = position[1]
        self.image = image
        self.rect = self.image.get_rect()
        self.rect.center = self.position

    def update_offset_position(self, offset):
        self.position[0] = self.world_position[0] - offset[0]
        self.position[1] = self.world_position[1] - offset[1]
        self.rect.center = self.position


class TileData:
    def __init__(self, file_path, tile_map):
        self.file_path = file_path
        self.tile_map = tile_map
        self.tile_id = os.path.splitext(os.path.basename(file_path))[0]
        self.collidable = False
        self.collide_radius = 26
        self.collision_shapes = []
        self.tile_image = None
        self.image_coords = [0, 0]

    def update_tile_map(self, tile_map):
        self.tile_map = tile_map
        self.tile_image = self.tile_map[self.image_coords[0]][self.image_coords[1]]

    def load_tile_data(self):
        if os.path.isfile(self.file_path):
            with open(self.file_path, "r") as tile_file:
                reader = csv.reader(tile_file)
                for line in reader:
                    data_type = line[0]
                    if data_type == "isCollidable":
                        self.collidable = bool(int(line[1]))
                    elif data_type == "tileImageCoords":
                        self.image_coords[0] = int(line[1])
                        self.image_coords[1] = int(line[2])
                        self.tile_image = self.tile_map[self.image_coords[0]][self.image_coords[1]]
                    elif data_type == "rect":
                        top_left_tile_offset = [int(line[1]), int(line[2])]
                        self.collision_shapes.append(["rect", top_left_tile_offset,
                                                      pygame.Rect(int(line[1]), int(line[2]),
                                                                  int(line[3]) - int(line[1]),
                                                                  int(line[4]) - int(line[2]))])
                    elif data_type == "circle":
                        self.collision_shapes.append(["circle", [int(line[1]), int(line[2])],
                                                      [int(line[1]), int(line[2])], int(line[3])])
                        self.collide_radius = int(line[3])

    def copy(self):
        tile_data_copy = TileData(self.file_path, self.tile_map)
        tile_data_copy.tile_id = copy.deepcopy(self.tile_id)
        tile_data_copy.collidable = copy.deepcopy(self.collidable)
        tile_data_copy.collide_radius = copy.deepcopy(self.collide_radius)
        tile_data_copy.collision_shapes = copy.deepcopy(self.collision_shapes)
        self.tile_image = self.tile_map[self.image_coords[0]][self.image_coords[1]]
        return tile_data_copy
                       

class Tile(pygame.sprite.Sprite):
    def __init__(self, position, tile_angle, tile_data, layer, *groups):
        super().__init__(*groups)
        self.group_tile_data = tile_data
        self.tile_data = tile_data.copy()
        self.world_position = [position[0], position[1]]
        self.position = [position[0], position[1]]
        self.angle = tile_angle
        self.collide_radius = self.group_tile_data.collide_radius
        self.collidable = self.group_tile_data.collidable
        self.tile_id = self.group_tile_data.tile_id

        self.image = pygame.transform.rotate(self.group_tile_data.tile_image, self.angle)
        self.rect = self.image.get_rect()
        self.rect.center = self.position
        self.is_visible = False
        self.layer = layer

    def reload_tile_image_from_data(self, all_tile_data):
        self.group_tile_data = all_tile_data[self.tile_id]
        self.image = pygame.transform.rotate(self.group_tile_data.tile_image, self.angle)

    def update_collision_shapes_position(self):
        for shape in self.tile_data.collision_shapes:
            if shape[0] == "rect":
                shape[2].left = self.rect.left + shape[1][0]
                shape[2].top = self.rect.top + shape[1][1]
            if shape[0] == "circle":
                shape[2][0] = self.rect.left + shape[1][0]
                shape[2][1] = self.rect.top + shape[1][1]

    def update_offset_position(self, offset, screen_data):
        should_update = False
        should_add_to_visible_tiles = False
        should_add_to_visible_collidable_tiles = False
        self.position[0] = self.world_position[0] - offset[0]
        self.position[1] = self.world_position[1] - offset[1]
        self.rect.center = self.position
        self.update_collision_shapes_position()
        if -32 <= self.position[0] <= screen_data.screen_size[0] + 32:
                if -32 <= self.position[1] <= screen_data.screen_size[1] + 32:
                    if not self.is_visible:
                        should_update = True
                    self.is_visible = True
                    should_add_to_visible_tiles = True
                    if self.collidable:
                        should_add_to_visible_collidable_tiles = True
                else:
                    self.is_visible = False
        else:
            self.is_visible = False
        return should_update, should_add_to_visible_tiles, should_add_to_visible_collidable_tiles
            
    def draw_collision_shapes(self, screen):
        for shape in self.tile_data.collision_shapes:
            if shape[0] == "circle":
                self.draw_radius_circle(screen, shape[2], shape[3])
            elif shape[0] == "rect":
                self.draw_collision_rect(screen, shape[2])
                
    @staticmethod
    def draw_collision_rect(screen, rect):
        ck = (180, 100, 100)
        s = pygame.Surface((rect.width, rect.height))
        s.fill(ck)
        s.set_alpha(75)
        screen.blit(s, rect)
        
    @staticmethod
    def draw_radius_circle(screen, centre, radius):
        ck = (127, 33, 33)
        int_position = [0, 0]
        int_position[0] = int(centre[0]-radius)
        int_position[1] = int(centre[1]-radius)
        s = pygame.Surface((radius*2, radius*2))

        # first, "erase" the surface by filling it with a color and
        # setting this color as colorkey, so the surface is empty
        s.fill(ck)
        s.set_colorkey(ck)

        pygame.draw.circle(s, pygame.Color("#B46464"), (radius, radius), radius)

        # after drawing the circle, we can set the 
        # alpha value (transparency) of the surface
        s.set_alpha(75)
        screen.blit(s, int_position)

    def test_projectile_collision(self, projectile_rect):
        collided = False
        if self.rect.colliderect(projectile_rect):
            for collision_shape in self.tile_data.collisionShapes:
                if collision_shape[0] == "circle":
                    if self.test_rect_in_circle(projectile_rect, collision_shape[2], collision_shape[3]):
                        collided = True
                elif collision_shape[0] == "rect":
                    if collision_shape[2].colliderect(projectile_rect):
                        collided = True  

        return collided

    @staticmethod
    def test_point_in_circle(point, circle_pos, circle_radius):
        return (point[0] - circle_pos[0]) ** 2 + (point[1] - circle_pos[1]) ** 2 < circle_radius ** 2

    def test_rect_in_circle(self, rect, circle_centre, circle_radius):
        tl_in = self.test_point_in_circle(rect.topleft, circle_centre, circle_radius)
        tr_in = self.test_point_in_circle(rect.topright, circle_centre, circle_radius)
        bl_in = self.test_point_in_circle(rect.bottomleft, circle_centre, circle_radius)
        br_in = self.test_point_in_circle(rect.bottomright, circle_centre, circle_radius)
        return tl_in or tr_in or bl_in or br_in

    def rotate_tile_right(self):
        self.angle -= 90
        if self.angle < 0:
            self.angle = 270
        self.image = pygame.transform.rotate(self.image, -90)

    def rotate_tile_left(self):
        self.angle += 90
        if self.angle > 270:
            self.angle = 0
        self.image = pygame.transform.rotate(self.image, 90)

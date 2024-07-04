import pygame
import math

from .collision_shapes import BaseCollisionShape

# --------------------------------------------------------------------------------------------------------------
# This file contains some helper classes to assist in visualising the collision library's shapes, either in game
# programs, or in example programs where these are the only visuals.
# --------------------------------------------------------------------------------------------------------------


class DrawableCollisionCircle:
    def __init__(self, collision_circle):
        self.collision_circle = collision_circle

        # noinspection PyArgumentList
        self.colour = pygame.Color(50, 255, 50)
        self.color_key = (127, 33, 33)
        self.draw_surface = pygame.Surface((self.collision_circle.radius * 2, self.collision_circle.radius * 2))
        self.draw_surface.fill(self.color_key)
        self.draw_surface.set_colorkey(self.color_key)
        pygame.draw.circle(self.draw_surface,
                           self.colour,
                           (self.collision_circle.radius, self.collision_circle.radius),
                           self.collision_circle.radius)
        self.draw_surface.set_alpha(100)

        self.move_vec = [0.0, 0.0]
        
        self.last_collide_state = False

        self.error = False

    def set_error(self):
        self.error = True 

    def set_move_vector(self, vec):
        self.move_vec[0] = vec[0]
        self.move_vec[1] = vec[1]

    def update_movement(self, dt, screen_size):
        new_pos = [self.collision_circle.x + (self.move_vec[0] * dt), self.collision_circle.y + self.move_vec[1] * dt]
        if new_pos[0] > screen_size[0]:
            new_pos[0] = 0.0
        if new_pos[0] < 0.0:
            new_pos[0] = float(screen_size[0])

        if new_pos[1] > screen_size[1]:
            new_pos[1] = 0.0
        if new_pos[1] < 0.0:
            new_pos[1] = float(screen_size[1])

        self.collision_circle.set_position(new_pos)

    def update_collided_colours(self):
        collided = len(self.collision_circle.collided_shapes_this_frame) > 0
        if self.last_collide_state != collided:
            self.last_collide_state = collided
            if self.error:
                # noinspection PyArgumentList
                self.set_color(pygame.Color(50, 50, 255))
            else:
                if collided:
                    # noinspection PyArgumentList
                    self.set_color(pygame.Color(255, 50, 50))
                else:
                    # noinspection PyArgumentList
                    self.set_color(pygame.Color(50, 255, 50))

    def on_change_radius(self):
        self.draw_surface = pygame.Surface((self.collision_circle.radius * 2, self.collision_circle.radius * 2))
        self.draw_surface.fill(self.color_key)
        self.draw_surface.set_colorkey(self.color_key)
        pygame.draw.circle(self.draw_surface,
                           self.colour,
                           (self.collision_circle.radius, self.collision_circle.radius),
                           self.collision_circle.radius)
        self.draw_surface.set_alpha(100)

    def set_color(self, colour):
        self.colour = colour

        self.draw_surface.fill(self.color_key)
        self.draw_surface.set_colorkey(self.color_key)
        pygame.draw.circle(self.draw_surface,
                           self.colour,
                           (self.collision_circle.radius, self.collision_circle.radius),
                           self.collision_circle.radius)
        self.draw_surface.set_alpha(100)

    def draw(self, surface, camera_position=(0.0, 0.0), camera_half_dimensions=(0.0, 0.0)):
        view_top_left_position = (camera_position[0] - camera_half_dimensions[0],
                                  camera_position[1] - camera_half_dimensions[1])
        surface.blit(self.draw_surface,
                     [int(self.collision_circle.x - self.collision_circle.radius) - view_top_left_position[0],
                      int(self.collision_circle.y - self.collision_circle.radius) - view_top_left_position[1]])
        pygame.draw.circle(surface,
                           self.colour,
                           [int(self.collision_circle.x - view_top_left_position[0]),
                            int(self.collision_circle.y - view_top_left_position[1])],
                           self.collision_circle.radius, 1)

        self.draw_normals(surface, view_top_left_position)

    def draw_normals(self, surface, view_top_left_position):
        length_of_normals = 5.0 + self.collision_circle.radius

        normal_start_point = [self.collision_circle.x - view_top_left_position[0],
                              self.collision_circle.y - view_top_left_position[1]]
        normal_end_point = [self.collision_circle.x + (self.collision_circle.collision_normal[0] * length_of_normals),
                            self.collision_circle.y + (self.collision_circle.collision_normal[1] * length_of_normals)]

        normal_end_point = [normal_end_point[0] - view_top_left_position[0],
                            normal_end_point[1] - view_top_left_position[1]]
        pygame.draw.line(surface, self.colour, normal_start_point, normal_end_point, 1)


class DrawableCollisionRect:
    def __init__(self, collision_rect, text_to_draw=None):

        self.collision_rect = collision_rect
        self.text_to_draw = text_to_draw
        if self.text_to_draw is not None:
            self.font = pygame.font.Font(None, int(self.collision_rect.width/2))
        # noinspection PyArgumentList
        self.colour = pygame.Color(50, 255, 50)
        self.color_key = (127, 33, 33)
        self.draw_surface = pygame.Surface((self.collision_rect.width, self.collision_rect.height))
        self.final_draw_surface = pygame.Surface((self.collision_rect.width, self.collision_rect.height))
        self.outline_draw_surface = pygame.Surface((self.collision_rect.width, self.collision_rect.height))
        self.final_outline_draw_surface = pygame.Surface((self.collision_rect.width, self.collision_rect.height))
        
        self.draw_surface.fill(self.color_key)
        self.draw_surface.set_colorkey(self.color_key)
        pygame.draw.rect(self.draw_surface,
                         self.colour,
                         pygame.Rect(0,
                                     0,
                                     self.collision_rect.width,
                                     self.collision_rect.height))
        self.draw_surface.set_alpha(100)
        self.final_draw_surface = pygame.transform.rotate(self.draw_surface,
                                                          (self.collision_rect.rotation * 180 / math.pi))

        self.outline_draw_surface.fill(self.color_key)
        self.outline_draw_surface.set_colorkey(self.color_key)
        pygame.draw.rect(self.outline_draw_surface,
                         self.colour,
                         pygame.Rect(0,
                                     0,
                                     self.collision_rect.width,
                                     self.collision_rect.height),
                         1)
        self.final_outline_draw_surface = pygame.transform.rotate(self.outline_draw_surface,
                                                                  (self.collision_rect.rotation * 180 / math.pi))

        self.move_vec = [0.0, 0.0]
        self.spin_vec = 0.0

        self.last_collide_state = False

        self.error = False

    def set_error(self):
        self.error = True        

    def set_move_vector(self, vec):
        self.move_vec[0] = vec[0]
        self.move_vec[1] = vec[1]

    def set_spin_vector(self, vec):
        self.spin_vec = vec

    def update_movement(self, dt, screen_size):
        new_pos = [self.collision_rect.x + (self.move_vec[0] * dt), self.collision_rect.y + self.move_vec[1] * dt]
        if new_pos[0] > screen_size[0]:
            new_pos[0] = 0.0
        if new_pos[0] < 0.0:
            new_pos[0] = float(screen_size[0])

        if new_pos[1] > screen_size[1]:
            new_pos[1] = 0.0
        if new_pos[1] < 0.0:
            new_pos[1] = float(screen_size[1])

        self.collision_rect.set_position(new_pos)

        self.collision_rect.rotate(self.spin_vec * dt)
        self.on_rotation()

    def on_rotation(self):
        self.final_draw_surface = pygame.transform.rotate(self.draw_surface,
                                                          (self.collision_rect.rotation * 180 / math.pi))
        self.final_outline_draw_surface = pygame.transform.rotate(self.outline_draw_surface,
                                                                  (self.collision_rect.rotation * 180 / math.pi))

    def on_change_dimensions(self):
        self.draw_surface = pygame.Surface((self.collision_rect.width, self.collision_rect.height))
        self.final_draw_surface = pygame.Surface((self.collision_rect.width, self.collision_rect.height))
        self.outline_draw_surface = pygame.Surface((self.collision_rect.width, self.collision_rect.height))
        self.final_outline_draw_surface = pygame.Surface((self.collision_rect.width, self.collision_rect.height))

        self.draw_surface.fill(self.color_key)
        self.draw_surface.set_colorkey(self.color_key)
        pygame.draw.rect(self.draw_surface,
                         self.colour,
                         pygame.Rect(0,
                                     0,
                                     self.collision_rect.width,
                                     self.collision_rect.height))
        self.draw_surface.set_alpha(100)
        self.final_draw_surface = pygame.transform.rotate(self.draw_surface,
                                                          (self.collision_rect.rotation * 180 / math.pi))

        self.outline_draw_surface.fill(self.color_key)
        self.outline_draw_surface.set_colorkey(self.color_key)
        pygame.draw.rect(self.outline_draw_surface,
                         self.colour,
                         pygame.Rect(0,
                                     0,
                                     self.collision_rect.width,
                                     self.collision_rect.height),
                         1)
        self.final_outline_draw_surface = pygame.transform.rotate(self.outline_draw_surface,
                                                                  (self.collision_rect.rotation * 180 / math.pi))

    def update_collided_colours(self):
        collided = len(self.collision_rect.collided_shapes_this_frame) > 0
        if self.last_collide_state != collided:
            self.last_collide_state = collided

            if self.error:
                # noinspection PyArgumentList
                self.set_color(pygame.Color(50, 50, 255))
            else:
                if collided:
                    # noinspection PyArgumentList
                    self.set_color(pygame.Color(255, 50, 50))
                else:
                    # noinspection PyArgumentList
                    self.set_color(pygame.Color(50, 255, 50))

    def set_color(self, colour):
        self.colour = colour
        self.draw_surface.fill(self.color_key)
        self.draw_surface.set_colorkey(self.color_key)
        pygame.draw.rect(self.draw_surface,
                         self.colour,
                         pygame.Rect(0,
                                     0,
                                     self.collision_rect.width,
                                     self.collision_rect.height))
        self.draw_surface.set_alpha(100)
        self.final_draw_surface = pygame.transform.rotate(self.draw_surface,
                                                          (self.collision_rect.rotation * 180 / math.pi))

        pygame.draw.rect(self.outline_draw_surface,
                         self.colour,
                         pygame.Rect(0,
                                     0,
                                     self.collision_rect.width,
                                     self.collision_rect.height),
                         1)
        self.final_outline_draw_surface = pygame.transform.rotate(self.outline_draw_surface,
                                                                  (self.collision_rect.rotation * 180 / math.pi))

    def draw_nearby_grid(self, surface):
        squares = []
        for x in range(self.collision_rect.nearbyGridRangeX[0], self.collision_rect.nearbyGridRangeX[1] + 1):
            for y in range(self.collision_rect.nearbyGridRangeY[0], self.collision_rect.nearbyGridRangeY[1] + 1):
                x_pos = x*64
                y_pos = y*64
                square_points = [[x_pos, y_pos], [x_pos+64, y_pos], [x_pos+64, y_pos+64], [x_pos, y_pos+64]]
                squares.append(square_points)
            
        for square in squares:
            pygame.draw.lines(surface, (0, 0, 0), True, square, 1)
        
    def draw(self, surface, camera_position=(0.0, 0.0), camera_half_dimensions=(0.0, 0.0)):
        view_top_left_position = (camera_position[0] - camera_half_dimensions[0],
                                  camera_position[1] - camera_half_dimensions[1])
        # self.draw_nearby_grid(surface)

        surface_half_width = (self.final_outline_draw_surface.get_width() / 2)
        surface_half_height = (self.final_outline_draw_surface.get_height() / 2)

        surface.blit(self.final_draw_surface,
                     [self.collision_rect.x - surface_half_width - view_top_left_position[0],
                      self.collision_rect.y - surface_half_height - view_top_left_position[1]])

        surface.blit(self.final_outline_draw_surface,
                     [self.collision_rect.x - surface_half_width - view_top_left_position[0],
                      self.collision_rect.y - surface_half_height - view_top_left_position[1]])

        self.draw_normals(surface, view_top_left_position)

        if self.text_to_draw is not None:
            fps_text_render = self.font.render(self.text_to_draw, True, self.colour)
            surface.blit(fps_text_render,
                         fps_text_render.get_rect(centerx=self.collision_rect.x - view_top_left_position[0],
                                                  centery=self.collision_rect.y - view_top_left_position[1]))

    def draw_normals(self, surface, view_top_left_position):
        length_of_normals = 5.0
        for edge_id in self.collision_rect.edges:
            edge = self.collision_rect.edges[edge_id]
            normal = self.collision_rect.normals[edge_id]

            edge_centre_point = [(edge.value[0][0] + edge.value[1][0])/2, (edge.value[0][1] + edge.value[1][1])/2]
            normal_end_point = [edge_centre_point[0] + normal.value[0] * length_of_normals,
                                edge_centre_point[1] + normal.value[1] * length_of_normals]

            edge_centre_point = [edge_centre_point[0] - view_top_left_position[0],
                                 edge_centre_point[1] - view_top_left_position[1]]
            normal_end_point = [normal_end_point[0] - view_top_left_position[0],
                                normal_end_point[1] - view_top_left_position[1]]

            if normal.should_skip:
                pygame.draw.line(surface, pygame.Color("#0000FF"), edge_centre_point, normal_end_point, 1)
            else:
                pygame.draw.line(surface, self.colour, edge_centre_point, normal_end_point, 1)


class DrawableCompositeShape:
    def __init__(self, composite_shape):
        self.composite_shape = composite_shape
        self.drawable_composite_shapes = []
        self.last_collide_state = False

        for shape in composite_shape.collision_shapes:
            if shape.type == BaseCollisionShape.RECT:
                self.drawable_composite_shapes.append(DrawableCollisionRect(shape))
            elif shape.type == BaseCollisionShape.CIRCLE:
                self.drawable_composite_shapes.append(DrawableCollisionCircle(shape))

    def draw(self, surface, camera_position=(0.0, 0.0), camera_half_dimensions=(0.0, 0.0)):
        for shape in self.drawable_composite_shapes:
            shape.draw(surface, camera_position, camera_half_dimensions)

    def update_collided_colours(self):
        collided = len(self.composite_shape.collided_shapes_this_frame) > 0
        if self.last_collide_state != collided:
            self.last_collide_state = collided

            for shape in self.drawable_composite_shapes:
                if collided:
                    # noinspection PyArgumentList
                    shape.set_color(pygame.Color(255, 50, 50))
                else:
                    # noinspection PyArgumentList
                    shape.set_color(pygame.Color(50, 255, 50))

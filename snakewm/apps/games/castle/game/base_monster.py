import math
import random

import pygame
from pygame_gui.elements import UIWorldSpaceHealthBar

from .splat import Splat
from ..collision.collision_shapes import CollisionCircle
from ..collision.drawable_collision_shapes import DrawableCollisionCircle
from .game_collision_types import GameCollisionType


class MonsterPath:
    def __init__(self):
        self.start_waypoint = None
        self.waypoints = []
        self.waypoint_radius = 32


class BaseMonster(pygame.sprite.Sprite):

    def __init__(self, monster_path, monster_id, loaded_image, point_cost, all_monster_sprites, offset, collision_grid,
                 splat_loader, ui_manager, *groups):
        super().__init__(*groups)
        self.id = monster_id
        self.point_cost = point_cost
        self.cash_value = 0
        self.move_speed = 0.0
        self.monster_path = monster_path
        self.collision_grid = collision_grid
        self.splat_loader = splat_loader
        self.ui_manager = ui_manager
        self.splat_image = None
        self.original_image = loaded_image
        self.image = self.original_image.copy()

        self.rect = self.image.get_rect()
        self.collide_radius = int(self.rect[2] / 2.0)

        self.position = [0.0, 0.0]
        int_position = self.get_random_point_in_radius_of_point(self.monster_path.start_waypoint,
                                                                self.monster_path.waypoint_radius)
        self.position[0] = float(int_position[0])
        self.position[1] = float(int_position[1])
        self.position[0] -= offset[0]
        self.position[1] -= offset[1]

        self.collision_grid = collision_grid
        handlers_by_type = {GameCollisionType.TURRET_PROJECTILE: self.collision_grid.no_handler}
        self.collision_shape = CollisionCircle(self.position[0], self.position[1],
                                               self.collide_radius,
                                               handlers_by_type,
                                               GameCollisionType.MONSTER,
                                               [GameCollisionType.TURRET_PROJECTILE])
        self.collision_shape.set_owner(self)
        self.collision_grid.add_new_shape_to_grid(self.collision_shape)

        self.drawable_collision_circle = DrawableCollisionCircle(self.collision_shape)

        self.rect.centerx = self.position[0]
        self.rect.centery = self.position[1]

        self.change_direction_time = 5.0
        self.change_direction_accumulator = 0.0

        self.next_way_point_index = 0
        next_way_point_centre = self.monster_path.waypoints[self.next_way_point_index]
        self.next_way_point = self.get_random_point_in_radius_of_point(next_way_point_centre,
                                                                       self.monster_path.waypoint_radius)
        # apply screen position offset
        self.next_way_point[0] -= offset[0]
        self.next_way_point[1] -= offset[1]
        x_dist = float(self.next_way_point[0]) - float(self.position[0])
        y_dist = float(self.next_way_point[1]) - float(self.position[1])
        self.distance_to_next_way_point = math.sqrt((x_dist * x_dist) + (y_dist * y_dist))
        self.current_vector = [x_dist / self.distance_to_next_way_point, y_dist / self.distance_to_next_way_point]

        direction_magnitude = math.sqrt(self.current_vector[0] ** 2 + self.current_vector[1] ** 2)
        if direction_magnitude > 0.0:
            unit_dir_vector = [self.current_vector[0] / direction_magnitude,
                               self.current_vector[1] / direction_magnitude]
            self.oldFacingAngle = math.atan2(-unit_dir_vector[0], -unit_dir_vector[1])*180/math.pi
            monster_centre_position = self.rect.center
            self.image = pygame.transform.rotate(self.original_image, self.oldFacingAngle)
            self.rect = self.image.get_rect()
            self.rect.center = monster_centre_position
    
        self.should_die = False
        
        self.sprite_needs_update = True
        self.all_monster_sprites = all_monster_sprites
        self.all_monster_sprites.add(self)

        self.health_capacity = 100
        self.current_health = self.health_capacity

        self.slow_down_percentage = 1.0

        self.health_bar = UIWorldSpaceHealthBar(pygame.Rect((0, 0), (self.rect.width+4, 8)), self, self.ui_manager)

    def set_starting_health(self, value):
        self.health_capacity = value
        self.current_health = self.health_capacity

    def kill(self):
        self.health_bar.kill()
        super().kill()

    def setup_splat(self, colour):
        self.splat_image = self.splat_loader.create_random_coloured_splat(colour)

    def draw_collision_circle(self, screen):
        self.drawable_collision_circle.update_collided_colours()
        self.drawable_collision_circle.draw(screen)

    def update_sprite(self):
        if self.sprite_needs_update:
            self.sprite_needs_update = False

    def react_to_collision(self):
        for shape in self.collision_shape.collided_shapes_this_frame:
            if shape.game_type == GameCollisionType.EXPLOSION:
                explosion = shape.owner
                self.take_damage(explosion.damage)

    def update_movement_and_collision(self, time_delta, player_resources, offset, splat_sprites):
        if self.current_health <= 0:
            self.should_die = True
            player_resources.current_cash += self.cash_value
       
        if self.distance_to_next_way_point <= 0.0:
            if self.next_way_point_index < (len(self.monster_path.waypoints) - 1):
                self.next_way_point_index += 1
                next_way_point_centre = self.monster_path.waypoints[self.next_way_point_index]
                self.next_way_point = self.get_random_point_in_radius_of_point(next_way_point_centre,
                                                                               self.monster_path.waypoint_radius)
                # apply screen position offset
                self.next_way_point[0] -= offset[0]
                self.next_way_point[1] -= offset[1]
                x_dist = float(self.next_way_point[0]) - float(self.position[0])
                y_dist = float(self.next_way_point[1]) - float(self.position[1])
                self.distance_to_next_way_point = math.sqrt((x_dist * x_dist) + (y_dist * y_dist))
                self.current_vector = [x_dist / self.distance_to_next_way_point,
                                       y_dist / self.distance_to_next_way_point]

                # calc facing angle
                direction_magnitude = math.sqrt(self.current_vector[0] ** 2 + self.current_vector[1] ** 2)
                if direction_magnitude > 0.0:
                    unit_dir_vector = [self.current_vector[0] / direction_magnitude,
                                       self.current_vector[1] / direction_magnitude]
                    facing_angle = math.atan2(-unit_dir_vector[0], -unit_dir_vector[1])*180/math.pi

                    if facing_angle != self.oldFacingAngle:
                        self.sprite_needs_update = True
                        self.oldFacingAngle = facing_angle
                        monster_centre_position = self.rect.center
                        self.image = pygame.transform.rotate(self.original_image, facing_angle)
                        self.rect = self.image.get_rect()
                        self.rect.center = monster_centre_position
            else:
                # monster has reached base
                player_resources.current_base_health -= 10
                self.should_die = True

        # move
        self.position[0] += (self.current_vector[0] * time_delta * self.move_speed * self.slow_down_percentage)
        self.position[1] += (self.current_vector[1] * time_delta * self.move_speed * self.slow_down_percentage)
        self.distance_to_next_way_point -= time_delta * self.move_speed * self.slow_down_percentage

        # reset any slowdown from turrets
        self.slow_down_percentage = 1.0
        # set sprite & collision shape positions
        self.rect.center = self.position
        self.collision_shape.set_position(self.position)

        if self.should_die:
            self.collision_grid.remove_shape_from_grid(self.collision_shape)
            self.all_monster_sprites.remove(self)
            self.kill()
            if self.splat_image is not None:
                Splat(self.position, self.splat_image, splat_sprites)
            
    @staticmethod
    def get_random_point_in_radius_of_point(point, radius):
        t = 2*math.pi*random.random()
        u = random.random() + random.random()
        if u > 1:
            r = 2-u
        else:
            r = u
        return [point[0] + radius*r*math.cos(t), point[1] + radius*r*math.sin(t)]

    def guess_position_at_time(self, time):
        guess_position = [0.0, 0.0]
        # make sure we don't overshoot monster waypoints with our guesses, or turrets
        # will aim at impossible positions for monsters inside walls.
        if (time * self.move_speed * self.slow_down_percentage) > self.distance_to_next_way_point:
            guess_position[0] = self.next_way_point[0]
            guess_position[1] = self.next_way_point[1]
        else:
            x_move = self.current_vector[0] * time * self.move_speed * self.slow_down_percentage
            y_move = self.current_vector[1] * time * self.move_speed * self.slow_down_percentage
            guess_position[0] = self.position[0] + x_move
            guess_position[1] = self.position[1] + y_move
        return guess_position

    def set_average_speed(self, average_speed):
        self.move_speed = random.randint(int(average_speed * 0.75), int(average_speed * 1.25))
        return self.move_speed

    def take_damage(self, damage):
        self.current_health -= damage.amount

    def set_slowdown(self, percentage):
        self.slow_down_percentage = percentage

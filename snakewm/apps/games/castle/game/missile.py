import math
import pygame
from .projectile import Projectile
from .explosion import Explosion
from .damage import DamageType
from ..collision.collision_shapes import CollisionRect
from ..collision.drawable_collision_shapes import DrawableCollisionRect
from .game_collision_types import GameCollisionType


class Missile(Projectile):
    def __init__(self, start_pos, initial_heading_vector, current_target, target_position, damage, speed,
                 explosions_sprite_sheet, image_atlas, homing_radius, collision_grid, *groups):

        super().__init__(*groups)
        self.explosions_sprite_sheet = explosions_sprite_sheet
        self.original_image = image_atlas.subsurface((0, 256, 6, 12))

        self.current_vector = [initial_heading_vector[0], initial_heading_vector[1]]
        self.target_vector = self.current_vector
        self.position = [float(start_pos[0]), float(start_pos[1])]
        
        facing_angle = math.atan2(-self.current_vector[0], -self.current_vector[1]) * 180 / math.pi
        self.image = pygame.transform.rotate(self.original_image, facing_angle)

        self.rect = self.image.get_rect()
        self.rect.center = start_pos

        self.collision_grid = collision_grid
        handlers_by_type = {GameCollisionType.MONSTER: self.collision_grid.no_handler}
        self.collision_shape = CollisionRect(self.original_image.get_rect(), math.atan2(-self.current_vector[0],
                                                                                        -self.current_vector[1]),
                                             handlers_by_type,
                                             GameCollisionType.TURRET_PROJECTILE, [GameCollisionType.MONSTER])
        self.collision_shape.set_owner(self)
        self.collision_grid.add_new_shape_to_grid(self.collision_shape)

        self.drawable_collision_rect = DrawableCollisionRect(self.collision_shape)

        self.should_die = False

        self.projectile_speed = speed
        self.damage = damage

        self.target_position = target_position
        x_diff = self.target_position[0] - self.position[0]
        y_diff = self.target_position[1] - self.position[1]
        total_target_dist = math.sqrt(x_diff ** 2 + y_diff ** 2)
        self.target_distance = total_target_dist + 16.0
        self.shot_range = 600.0

        self.rotate_speed = 10.0

        self.time_to_home_in = False
        self.homing_time_acc = 0.0
        self.homing_time = 0.2
        self.homing_radius = homing_radius

        self.current_target = current_target

    def update_sprite(self, all_bullet_sprites):
        all_bullet_sprites.add(self)
        return all_bullet_sprites

    def draw_collision_rect(self, screen):
        self.drawable_collision_rect.update_collided_colours()
        self.drawable_collision_rect.draw(screen)

    def react_to_collision(self):
        for shape in self.collision_shape.collided_shapes_this_frame:
            if shape.game_type == GameCollisionType.MONSTER:
                self.should_die = True

    def update_movement_and_collision(self, monsters, time_delta, new_explosions, explosions):
        if self.homing_time_acc < self.homing_time:
            self.homing_time_acc += time_delta
        else:
            self.time_to_home_in = True
            
        if self.time_to_home_in:
            self.homing_time_acc = 0.0
            self.time_to_home_in = False
            if self.current_target is None or self.current_target.should_die:
                self.current_target, self.target_distance = self.get_closest_monster_in_radius(monsters)
            if self.current_target is not None:
                self.target_distance = self.calc_distance_to_target(self.current_target)
                self.target_vector = self.calculate_aiming_vector(self.current_target, self.target_distance)

        relative_angle = self.rotate_current_angle_to_target(time_delta)

        self.shot_range -= time_delta * self.projectile_speed
        self.position[0] += (self.current_vector[0] * time_delta * self.projectile_speed)
        self.position[1] += (self.current_vector[1] * time_delta * self.projectile_speed)
        self.rect.center = (int(self.position[0]), int(self.position[1]))

        self.collision_shape.set_position(self.position)

        if self.shot_range <= 0.0:
            self.should_die = True

        if relative_angle != 0.0:
            direction_magnitude = math.sqrt(self.current_vector[0] ** 2 + self.current_vector[1] ** 2)
            unit_dir_vector = [0, 0]
            if direction_magnitude > 0.0:
                unit_dir_vector = [self.current_vector[0] / direction_magnitude,
                                   self.current_vector[1] / direction_magnitude]
            facing_angle = math.atan2(-unit_dir_vector[0], -unit_dir_vector[1])*180/math.pi

            bullet_centre_position = self.rect.center
            self.image = pygame.transform.rotate(self.original_image, facing_angle)
            self.rect = self.image.get_rect()
            self.rect.center = bullet_centre_position
            
            self.collision_shape.set_rotation(math.atan2(-unit_dir_vector[0], -unit_dir_vector[1]))

        if self.should_die:
            self.collision_grid.remove_shape_from_grid(self.collision_shape)
            # explode at front of missile
            explosion_pos = [0.0, 0.0]
            explosion_pos[0] = self.position[0] + (self.current_vector[0] * 7.0)
            explosion_pos[1] = self.position[1] + (self.current_vector[1] * 7.0)
            new_explosion = Explosion(self.position, self.explosions_sprite_sheet, 12,
                                      self.damage, DamageType.MISSILE, self.collision_grid)
            new_explosions.append(new_explosion)
            explosions.append(new_explosion)

    def calc_distance_to_target(self, target):
        x_dist = self.position[0] - target.position[0]
        y_dist = self.position[1] - target.position[1]
        current_dist = math.sqrt((x_dist ** 2) + (y_dist ** 2))
        # re-adjust distance to our anticipated position when projectiles reach target
        time_to_reach_target = current_dist/self.projectile_speed
        guess_position = target.guess_position_at_time(time_to_reach_target)
        x_dist = guess_position[0] - self.position[0]
        y_dist = guess_position[1] - self.position[1]
        guess_dist = math.sqrt((x_dist ** 2) + (y_dist ** 2))
        return guess_dist
    
    def get_closest_monster_in_radius(self, monsters):
        closest_monster_distance = 100000.0
        closest_monster_in_radius = None
        for monster in monsters:
            guess_dist = self.calc_distance_to_target(monster)
            if guess_dist < self.homing_radius:
                if guess_dist < closest_monster_distance:
                    closest_monster_distance = guess_dist
                    closest_monster_in_radius = monster
        return closest_monster_in_radius, closest_monster_distance

    def calculate_aiming_vector(self, target, distance):
        time_to_reach_target = distance/self.projectile_speed
        guess_position = target.guess_position_at_time(time_to_reach_target)
        x_direction = guess_position[0] - self.position[0]
        y_direction = guess_position[1] - self.position[1]
        distance = math.sqrt((x_direction ** 2) + (y_direction ** 2))
        return [x_direction/distance, y_direction/distance]

    def rotate_current_angle_to_target(self, time_delta):
        relative_angle = 0.0
        if self.target_vector[0] != self.current_vector[0] or self.target_vector[0] != self.current_vector[0]:
            current_angle = math.atan2(self.current_vector[1], self.current_vector[0])
            target_angle = math.atan2(self.target_vector[1], self.target_vector[0])
            relative_angle = target_angle - current_angle

            if abs(relative_angle) < 0.01:
                self.current_vector[0] = self.target_vector[0]
                self.current_vector[1] = self.target_vector[1]
            else:   
                if relative_angle > math.pi:
                    relative_angle = relative_angle - (2 * math.pi)
                if relative_angle < -math.pi:
                    relative_angle = relative_angle + (2 * math.pi)
                    
                if relative_angle > 0:
                    current_angle += (time_delta * self.rotate_speed)
                else:
                    current_angle -= (time_delta * self.rotate_speed)

                self.current_vector[0] = math.cos(current_angle)
                self.current_vector[1] = math.sin(current_angle)

        return relative_angle

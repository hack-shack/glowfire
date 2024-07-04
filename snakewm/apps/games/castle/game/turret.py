import math
import pygame

from .base_monster import BaseMonster

class Turret(pygame.sprite.Sprite):
    def __init__(self, initial_position, build_cost, initial_radius, turret_id, *groups):
        super().__init__(*groups)
        self.original_image = None
        self.image = None
        self.rect = None
        self.placed = False
        self.build_cost = build_cost
        self.level = 1  # turret's current upgrade level
        self.max_level = 3  # the maximum upgrade level
        self.turret_id = turret_id

        self.current_target = None
        self.target_distance = 0.0
        self.target_vector = [0.0, -1.0]
        self.current_vector = [0.0, -1.0]
        self.current_angle = 0.0
        self.position = [float(initial_position[0]), float(initial_position[1])]

        self.radius = initial_radius
        self.projectile_speed = 10000
        self.rotate_speed = 10.0
        self.show_radius = False
        self.can_fire = True

    def set_image_direct(self, image):
        self.original_image = image
        self.image = image
        self.rect = self.image.get_rect()
        self.rect.center = self.position
        
    def update_sprite(self, all_turret_sprites):
        all_turret_sprites.add(self)
        return all_turret_sprites
    
    def get_max_level(self):
        return self.max_level

    def get_level(self):
        return self.level
    
    def get_upgrade_cost(self):
        return (self.level + 1) * self.build_cost

    def get_sell_value(self):
        return int(self.build_cost / 2)
    
    def draw_radius_circle(self, screen):
        if self.show_radius:
            ck = (127, 33, 33)
            int_position = [0, 0]
            int_position[0] = int(self.position[0]-self.radius)
            int_position[1] = int(self.position[1]-self.radius)
            s = pygame.Surface((self.radius*2, self.radius*2))

            # first, "erase" the surface by filling it with a color and
            # setting this color as colorkey, so the surface is empty
            s.fill(ck)
            s.set_colorkey(ck)

            pygame.draw.circle(s, pygame.Color("#B4B4B4"), (self.radius, self.radius), self.radius)

            # after drawing the circle, we can set the 
            # alpha value (transparency) of the surface
            s.set_alpha(75)
            screen.blit(s, int_position)

    def set_position(self, position):
        self.position = position
        self.rect.center = self.position

    def update_shooting(self, time_delta, monsters, projectiles):
        pass

    def update_movement_and_collision(self, time_delta, monsters, bullets, mouse_position):
        if self.placed:
            if self.rect.collidepoint(mouse_position):
                self.show_radius = True
            else:
                self.show_radius = False
                
            self.update_shooting(time_delta, monsters, bullets)

            direction_magnitude = math.sqrt(self.current_vector[0] ** 2 + self.current_vector[1] ** 2)
            unit_dir_vector = [0, 0]
            if direction_magnitude > 0.0:
                unit_dir_vector = [self.current_vector[0] / direction_magnitude,
                                   self.current_vector[1] / direction_magnitude]
            facing_angle = math.atan2(-unit_dir_vector[0], -unit_dir_vector[1])*180/math.pi
            if facing_angle != self.current_angle:
                self.current_angle = facing_angle
                turret_centre_position = self.rect.center
                self.image = pygame.transform.rotate(self.original_image, facing_angle)
                self.rect = self.image.get_rect()
                self.rect.center = turret_centre_position

    def rotate_current_angle_to_target(self, time_delta):
        current_angle = math.atan2(self.current_vector[1], self.current_vector[0])
        target_angle = math.atan2(self.target_vector[1], self.target_vector[0])
        relative_angle = target_angle - current_angle

        if abs(relative_angle) < 0.05:
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

    def calc_distance_to_target(self, target: BaseMonster):
        x_dist = self.position[0] - target.position[0]
        y_dist = self.position[1] - target.position[1]
        current_dist = math.sqrt((x_dist * x_dist) + (y_dist * y_dist))
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
            if guess_dist < self.radius:
                if guess_dist < closest_monster_distance:
                    closest_monster_distance = guess_dist
                    closest_monster_in_radius = monster
        return closest_monster_in_radius, closest_monster_distance

    # leads the target by trying to aim where the target *will* be
    # rather than where it is now
    def calculate_aiming_vector(self, target, distance):
        time_to_reach_target = distance/self.projectile_speed
        guess_position = target.guess_position_at_time(time_to_reach_target)
        x_direction = guess_position[0] - self.position[0]
        y_direction = guess_position[1] - self.position[1]
        dist = math.sqrt((x_direction ** 2) + (y_direction ** 2))
        return [[x_direction/dist, y_direction/dist], guess_position]

    # doesn't lead the target
    def calculate_rough_aiming_vector(self, target):
        x_direction = target.position[0] - self.position[0]
        y_direction = target.position[1] - self.position[1]
        dist = math.sqrt((x_direction ** 2) + (y_direction ** 2))
        return [x_direction/dist, y_direction/dist]

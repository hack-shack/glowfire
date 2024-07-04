import math
import pygame
from .projectile import Projectile
from .damage import Damage, DamageType


class Laser(Projectile):
    def __init__(self, start_position, initial_heading_vector, target, damage_per_tick, beam_colour, *groups):
        super().__init__(*groups)
        self.time_to_tick = 0.1
        self.damage_acc = 0.0
        self.damage_per_tick = damage_per_tick
        self.current_target = target
        self.beam_colour = beam_colour
        self.target = target

        self.heading_vector = initial_heading_vector
        
        self.current_angle = math.atan2(self.heading_vector[0], self.heading_vector[1]) * 180 / math.pi
        self.position = [start_position[0], start_position[1]]
 
        self.should_die = False

        x_length_squared = (self.position[0] - self.target.position[0]) ** 2
        y_length_squared = (self.position[1] - self.target.position[1]) ** 2
        self.laser_length = math.sqrt(x_length_squared + y_length_squared)

        self.image = pygame.Surface([2, int(self.laser_length)])
        self.image.fill(self.beam_colour, None, pygame.BLEND_RGBA_ADD)
        self.image.set_colorkey(pygame.Color("#00000000"))
        self.image = pygame.transform.rotate(self.image, self.current_angle)
        self.image.set_alpha(150)
        self.rect = self.image.get_rect()

        self.rect.center = [int(self.position[0] + (self.heading_vector[0] * self.laser_length / 2)),
                            int(self.position[1] + (self.heading_vector[1] * self.laser_length / 2))]

    def update_sprite(self, all_sprites):
        all_sprites.add(self)
        return all_sprites
    
    def update_movement_and_collision(self, monsters, time_delta, new_explosions, explosions):
        if self.target is not None and not self.target.should_die:
            self.damage_acc += time_delta
            if self.damage_acc > self.time_to_tick:
                self.damage_acc = 0.0
                self.target.take_damage(Damage(self.damage_per_tick, DamageType.LASER))

    def set_beam_data(self, turret_position, aiming_vector, beam_colour):
        self.heading_vector = aiming_vector
        self.position = turret_position
        self.beam_colour = beam_colour

        self.current_angle = math.atan2(self.heading_vector[0], self.heading_vector[1]) * 180 / math.pi

        x_length_squared = (self.position[0] - self.target.position[0]) ** 2
        y_length_squared = (self.position[1] - self.target.position[1]) ** 2
        self.laser_length = math.sqrt(x_length_squared + y_length_squared)

        self.image = pygame.Surface([3, int(self.laser_length)])
        self.image.fill(self.beam_colour, None, pygame.BLEND_RGBA_ADD)
        self.image.set_colorkey(pygame.Color("#00000000"))
        self.image = pygame.transform.rotate(self.image, self.current_angle)
        self.image.set_alpha(150)
        self.rect = self.image.get_rect()
        self.rect.center = [int(self.position[0] + (self.heading_vector[0] * self.laser_length / 2)),
                            int(self.position[1] + (self.heading_vector[1] * self.laser_length / 2))]

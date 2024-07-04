import pygame
from .projectile import Projectile
from .explosion import Explosion
from .damage import DamageType


class FlameCone(Projectile):
    def __init__(self, start_pos, target_position, initial_heading_vector, damage, speed, shot_range,
                 explosions_sprite_sheet, collision_grid, *groups):
        super().__init__(*groups)
        self.explosions_sprite_sheet = explosions_sprite_sheet

        self.collision_grid = collision_grid

        self.rect = pygame.Rect(0, 0, 4, 4)
        self.rect.center = start_pos
        self.current_vector = [initial_heading_vector[0], initial_heading_vector[1]]
        self.position = [float(self.rect.center[0]), float(self.rect.center[1])]

        self.should_die = False

        self.bullet_speed = speed
        self.damage = damage

        self.target_position = target_position
        self.shot_range = shot_range

        self.shot_distance_acc = 0.0
        self.current_puff_radius = 4
        self.current_puff_gap = 4

    def update_sprite(self, all_bullet_sprites):
        return all_bullet_sprites

    def update_movement_and_collision(self, monsters, time_delta, new_explosions, explosions):
        self.shot_range -= time_delta * self.bullet_speed
        self.shot_distance_acc += time_delta * self.bullet_speed
        self.position[0] += (self.current_vector[0] * time_delta * self.bullet_speed)
        self.position[1] += (self.current_vector[1] * time_delta * self.bullet_speed)
        self.rect.center = (int(self.position[0]), int(self.position[1]))

        if self.shot_range <= 0.0:
            self.should_die = True

        if self.shot_distance_acc >= self.current_puff_gap:
            new_explosion = Explosion(self.position, self.explosions_sprite_sheet,
                                      self.current_puff_radius, self.damage,
                                      DamageType.FIRE, self.collision_grid)
            new_explosions.append(new_explosion)
            explosions.append(new_explosion)
            self.current_puff_radius += 3
            self.current_puff_gap += self.current_puff_radius - 2

    def draw_collision_rect(self, screen):
        pass

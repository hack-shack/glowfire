import math
import pygame
from .projectile import Projectile
from .explosion import Explosion
from .damage import DamageType

from ..collision.collision_shapes import CollisionRect
from ..collision.drawable_collision_shapes import DrawableCollisionRect
from .game_collision_types import GameCollisionType


class Bullet(Projectile):
    def __init__(self, start_pos, initial_heading_vector, target_position, damage, bullet_speed,
                 explosions_sprite_sheet, image_atlas, collision_grid, *groups):

        super().__init__(*groups)
        self.explosions_sprite_sheet = explosions_sprite_sheet
        self.image_atlas = image_atlas
        self.original_image = image_atlas.subsurface((6, 256, 4, 8))

        self.current_vector = [initial_heading_vector[0], initial_heading_vector[1]]
        self.position = [float(start_pos[0]), float(start_pos[1])]
        
        facing_angle = math.atan2(-self.current_vector[0], -self.current_vector[1]) * 180 / math.pi
        self.image = pygame.transform.rotate(self.original_image, facing_angle)

        self.rect = self.image.get_rect()
        self.rect.center = start_pos

        self.collision_grid = collision_grid
        handlers_by_type = {GameCollisionType.MONSTER: self.collision_grid.no_handler}
        self.collision_shape = CollisionRect(self.original_image.get_rect(),
                                             math.atan2(-self.current_vector[0],
                                                        -self.current_vector[1]),
                                             handlers_by_type,
                                             GameCollisionType.TURRET_PROJECTILE,
                                             [GameCollisionType.MONSTER])
        self.collision_shape.set_owner(self)
        self.collision_grid.add_new_shape_to_grid(self.collision_shape)

        self.drawable_collision_rect = DrawableCollisionRect(self.collision_shape)
        
        self.should_die = False

        self.bullet_speed = bullet_speed
        self.damage = damage

        self.target_position = target_position
        x_diff = self.target_position[0] - self.position[0]
        y_diff = self.target_position[1] - self.position[1]
        total_target_dist = math.sqrt(x_diff * x_diff + y_diff * y_diff)
        self.shot_range = total_target_dist + 16.0

    def draw_collision_rect(self, screen):
        self.drawable_collision_rect.update_collided_colours()
        self.drawable_collision_rect.draw(screen)

    def update_sprite(self, all_bullet_sprites):
        all_bullet_sprites.add(self)
        return all_bullet_sprites

    def react_to_collision(self):
        for shape in self.collision_shape.collided_shapes_this_frame:
            if shape.game_type == GameCollisionType.MONSTER:
                self.should_die = True
            
    def update_movement_and_collision(self, monsters, time_delta, new_explosions, explosions):
        self.shot_range -= time_delta * self.bullet_speed
        self.position[0] += (self.current_vector[0] * time_delta * self.bullet_speed)
        self.position[1] += (self.current_vector[1] * time_delta * self.bullet_speed)
        self.rect.center = (int(self.position[0]), int(self.position[1]))

        self.collision_shape.set_position(self.position)
        
        if self.shot_range <= 0.0:
            self.should_die = True

        if self.should_die:
            self.collision_grid.remove_shape_from_grid(self.collision_shape)
            explosion_pos = [0.0, 0.0]
            explosion_pos[0] = self.position[0] + (self.current_vector[0] * 5.0)
            explosion_pos[1] = self.position[1] + (self.current_vector[1] * 5.0)
            new_explosion = Explosion(explosion_pos, self.explosions_sprite_sheet, 6,
                                      self.damage, DamageType.BULLET, self.collision_grid)
            new_explosions.append(new_explosion)
            explosions.append(new_explosion)

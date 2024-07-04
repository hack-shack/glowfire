import random
import pygame
from .damage import Damage
from ..collision.collision_shapes import CollisionCircle
from .game_collision_types import GameCollisionType


class Explosion(pygame.sprite.DirtySprite):
    def __init__(self, start_pos, explosion_sheet, size, damage_amount, damage_type, collision_grid, *groups):

        super().__init__(*groups)
        self.collision_grid = collision_grid
        self.radius = size
        self.collide_radius = self.radius
        self.explosion_sheet = explosion_sheet
        self.explosion_frames = 16
        self.explosion_images = []
        random_explosion_int = random.randrange(0, 512, 64)
        for i in range(0, self.explosion_frames):
            x_start_index = (i * 64)
            explosion_frame = self.explosion_sheet.subsurface(pygame.Rect(x_start_index + 1,
                                                                          random_explosion_int + 1, 62, 62))
            explosion_frame = pygame.transform.scale(explosion_frame, (self.radius*2, self.radius*2))
            self.explosion_images.append(explosion_frame)

        self.image = self.explosion_images[0]
                
        self.rect = self.explosion_images[0].get_rect()
        self.rect.center = start_pos

        self.position = [float(self.rect.center[0]), float(self.rect.center[1])]

        # handle collision shape setup
        self.collision_grid = collision_grid
        handlers_by_type = {GameCollisionType.MONSTER: self.collision_grid.no_handler}
        self.collision_shape = CollisionCircle(self.position[0], self.position[1], self.collide_radius,
                                               handlers_by_type,
                                               GameCollisionType.EXPLOSION,
                                               [GameCollisionType.MONSTER])
        self.collision_shape.set_owner(self)
        self.collision_grid.add_new_shape_to_grid(self.collision_shape)
        
        self.should_die = False
        self.life_time = 0.45
        self.time = self.life_time
        self.frame_time = self.life_time / self.explosion_frames
        self.frame = 1

        self.damage = Damage(damage_amount, damage_type)

        self.should_kill_explosion_collision = False
        self.has_collision = True
        
    def update_sprite(self, all_explosion_sprites, time_delta):
        self.time -= time_delta
        if self.time < 0.0:
            self.should_die = True
            if self.has_collision:  # destroy collision shape if it's not gone already
                self.collision_grid.remove_shape_from_grid(self.collision_shape)
                self.has_collision = False

        if self.frame < self.explosion_frames and (self.life_time - self.time) > (self.frame_time * self.frame):
            self.image = self.explosion_images[self.frame]
            self.frame += 1

        all_explosion_sprites.add(self)

        # for now we only one one frame's worth of collision tests from an explosion
        if self.should_kill_explosion_collision and self.has_collision:
            self.collision_grid.remove_shape_from_grid(self.collision_shape)
            self.has_collision = False
        else:
            self.should_kill_explosion_collision = True
            
        return all_explosion_sprites

    def update_movement_and_collision(self):
        pass

    def react_to_collision(self):
        pass

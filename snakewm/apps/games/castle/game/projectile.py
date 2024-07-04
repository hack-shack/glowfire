import pygame


class Projectile(pygame.sprite.Sprite):
    def __init__(self, *groups):
        super().__init__(*groups)

        self.image = None
        self.rect = None

    def update_sprite(self, all_bullet_sprites):
        return all_bullet_sprites

    def update_movement_and_collision(self, monsters, time_delta, new_explosions, explosions):
        pass

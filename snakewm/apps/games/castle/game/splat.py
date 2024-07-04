"""
A class representing a splat displayed when and where a monster is killed. the splat sticks around for 10 seconds then
fades away.
"""
import pygame
import random


class SplatLoader:
    def __init__(self):
        self.splat_map = pygame.image.load("images/splat.png").convert_alpha()
        self.splats = [self.splat_map.subsurface(pygame.Rect((0, 0), (32, 32))),
                       self.splat_map.subsurface(pygame.Rect((0, 32), (32, 32))),
                       self.splat_map.subsurface(pygame.Rect((0, 64), (32, 32))),
                       self.splat_map.subsurface(pygame.Rect((0, 96), (32, 32))),
                       self.splat_map.subsurface(pygame.Rect((32, 0), (32, 32))),
                       self.splat_map.subsurface(pygame.Rect((32, 32), (32, 32))),
                       self.splat_map.subsurface(pygame.Rect((32, 64), (32, 32))),
                       self.splat_map.subsurface(pygame.Rect((32, 96), (32, 32)))]

    def create_random_coloured_splat(self, colour):
        splat = random.choice(self.splats).copy()
        splat.fill(colour, None, pygame.BLEND_RGBA_MULT)
        return splat


class Splat(pygame.sprite.Sprite):
    def __init__(self, position, splat_image, *groups):
        super().__init__(*groups)
        self.original_image = splat_image
        self.image = self.original_image.copy()
        self.rect = self.image.get_rect(centerx=position[0], centery=position[1])

        self.life_timer = 30.0
        self.fade_duration = 10.0
        self.fade_timer = self.fade_duration
        self.fade_step = 10

    def update(self, time_delta):
        if self.life_timer > 0.0:
            self.life_timer -= time_delta
        else:
            if self.fade_timer > 0.0:
                self.fade_timer -= time_delta
                if int(self.fade_timer) < self.fade_step:
                    self.fade_step = int(self.fade_timer)
                    lerp_value = self.fade_timer / self.fade_duration
                    alpha = max(0, self.lerp(0, 255, lerp_value))
                    self.image = self.original_image.copy()
                    self.image.fill((255, 255, 255, alpha), None, pygame.BLEND_RGBA_MULT)
            else:
                self.kill()

    @staticmethod
    def lerp(a, b, c):
        return (c * b) + ((1.0 - c) * a)


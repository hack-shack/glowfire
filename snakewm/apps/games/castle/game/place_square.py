import pygame


class PlaceSquare(pygame.sprite.Sprite):
    def __init__(self, start_pos, square_sprites, image_atlas, *groups):
        super().__init__(*groups)
        rect = (0, 288, 32, 32)
        self.image = image_atlas.subsurface(rect)

        self.rect = self.image.get_rect()
        self.rect.centerx = start_pos[0]
        self.rect.centery = start_pos[1]

        self.world_position = [start_pos[0], start_pos[1]]
        self.position = [start_pos[0], start_pos[1]]
        
        self.occupied = False
        square_sprites.add(self)

    def update_offset_position(self, offset):
        self.position[0] = self.world_position[0] - offset[0]
        self.position[1] = self.world_position[1] - offset[1]
        self.rect.centerx = self.position[0]
        self.rect.centery = self.position[1]

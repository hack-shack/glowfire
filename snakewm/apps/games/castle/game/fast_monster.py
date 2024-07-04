import pygame
from .base_monster import BaseMonster


class FastMonster(BaseMonster):
    monster_id = "fast"

    def __init__(self, monster_path, image_dictionary, monster_type_dict,
                 all_monster_sprites, screen_offset, collision_grid, splat_loader, ui_manager, *groups):
        image = image_dictionary[FastMonster.monster_id]
        monster_type = monster_type_dict[FastMonster.monster_id]
        super().__init__(monster_path, FastMonster.monster_id, image, monster_type.points,
                         all_monster_sprites, screen_offset, collision_grid, splat_loader, ui_manager, *groups)
        self.setup_splat(pygame.Color("#79b176FF"))
        self.cash_value = 50
        self.move_speed = self.set_average_speed(130)
        self.set_starting_health(65)

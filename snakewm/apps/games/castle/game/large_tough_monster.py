import pygame
from .base_monster import BaseMonster


class LargeToughMonster(BaseMonster):
    monster_id = "large_tough"

    def __init__(self, monster_path, image_dictionary, monster_type_dict,
                 all_monster_sprites, screen_offset, collision_grid, splat_loader, ui_manager, *groups):
        image = image_dictionary[LargeToughMonster.monster_id]
        monster_type = monster_type_dict[LargeToughMonster.monster_id]
        super().__init__(monster_path, LargeToughMonster.monster_id, image, monster_type.points,
                         all_monster_sprites, screen_offset,
                         collision_grid, splat_loader, ui_manager, *groups)
        self.setup_splat(pygame.Color("#20afc9FF"))
        self.cash_value = 200
        self.move_speed = self.set_average_speed(40)
        self.set_starting_health(1500)

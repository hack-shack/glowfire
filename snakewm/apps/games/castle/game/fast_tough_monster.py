import pygame
from .base_monster import BaseMonster


# ---------------------------------------------------------------
# Challenge 2
# 
# For this monster we want to combine the attributes of the fast
# monster and the tough monster. Check out the existing code for
# these monsters in the 'game' sub-folder
#
# You will need to change:
# - the health
# - the average speed
# - and increase the cash value (how much you get for killing this guy).
# ---------------------------------------------------------------
class FastToughMonster(BaseMonster):
    monster_id = "fast_tough"

    def __init__(self, monster_path, image_dictionary, monster_type_dict, all_monster_sprites, screen_offset,
                 collision_grid, splat_loader, ui_manager, *groups):
        image = image_dictionary[FastToughMonster.monster_id]
        monster_type = monster_type_dict[FastToughMonster.monster_id]
        super().__init__(monster_path, FastToughMonster.monster_id, image,
                         monster_type.points, all_monster_sprites, screen_offset,
                         collision_grid, splat_loader, ui_manager, *groups)
        self.setup_splat(pygame.Color("#20afc9FF"))
        self.cash_value = 60
        self.move_speed = self.set_average_speed(120)
        self.set_starting_health(150)

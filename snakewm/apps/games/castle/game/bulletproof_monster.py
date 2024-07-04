import pygame
from .base_monster import BaseMonster
from .damage import DamageType


class BulletproofMonster(BaseMonster):
    monster_id = "bulletproof"

    def __init__(self, monster_path, image_dictionary, monster_type_dict, all_monster_sprites, screen_offset,
                 collision_grid, splat_loader, ui_manager, *groups):

        image = image_dictionary[BulletproofMonster.monster_id]
        monster_type = monster_type_dict[BulletproofMonster.monster_id]
        super().__init__(monster_path, BulletproofMonster.monster_id, image, monster_type.points,
                         all_monster_sprites, screen_offset, collision_grid, splat_loader, ui_manager, *groups)
        self.setup_splat(pygame.Color("#79b176FF"))
        self.cash_value = 40
        self.move_speed = self.set_average_speed(60)
        self.set_starting_health(225)

    def take_damage(self, damage):
        # we are bullet proof so only take 10% damage from bullets!
        if damage.type == DamageType.BULLET:
            self.current_health -= int(damage.amount * 0.10)
        if damage.type == DamageType.MISSILE:
            self.current_health -= int(damage.amount * 0.50)
        else:
            self.current_health -= damage.amount

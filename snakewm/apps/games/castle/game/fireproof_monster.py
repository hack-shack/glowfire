import pygame
from .base_monster import BaseMonster
from .damage import DamageType


# --------------------------------------------------------------
# Challenge 3
#
# To make the fireproof monster you need to:
# - change the image
# - import the game.damage file as DamageCode
# - add a take_damage function that reduces the damage the monster
#   takes when the damage is fire by 90%
#
# For help in adding the take_damage function open up the bulletproof_monster
# file and examine the take_damage function in there.
# --------------------------------------------------------------
class FireproofMonster(BaseMonster):
    monster_id = "fireproof"

    def __init__(self, monster_path, image_dictionary, monster_type_dict,
                 all_monster_sprites, screen_offset, collision_grid, splat_loader, ui_manager, *groups):

        image = image_dictionary[FireproofMonster.monster_id]
        monster_type = monster_type_dict[FireproofMonster.monster_id]
        super().__init__(monster_path, FireproofMonster.monster_id, image, monster_type.points,
                         all_monster_sprites, screen_offset, collision_grid, splat_loader, ui_manager, *groups)
        self.setup_splat(pygame.Color("#c86464FF"))
        self.cash_value = 40
        self.move_speed = self.set_average_speed(60)
        self.set_starting_health(225)

    def take_damage(self, damage):
        # we are fire proof so only take 10% damage from fire!
        if damage.type == DamageType.FIRE:
            self.current_health -= int(damage.amount * 0.10)
        if damage.type == DamageType.MISSILE:
            self.current_health -= int(damage.amount * 0.50)
        else:
            self.current_health -= damage.amount

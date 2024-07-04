import random
from .standard_monster import StandardMonster
from .tough_monster import ToughMonster
from .fast_monster import FastMonster
from .bulletproof_monster import BulletproofMonster
from .fireproof_monster import FireproofMonster
from .large_monster import LargeMonster
from .fast_tough_monster import FastToughMonster
from .large_tough_monster import LargeToughMonster


class MonsterType:
    def __init__(self, monster_id, monster_points):
        self.points = monster_points
        self.id = monster_id


class MonsterWaveSpawner:

    def __init__(self, monsters, monster_walk_path, initial_wave_points,
                 all_monster_sprites, image_atlas, collision_grid, splat_loader, ui_manager):
        self.monsters = monsters
        self.monster_walk_path = monster_walk_path
        self.current_wave_number = 0
        self.maximum_wave_number = 20
        self.wave_base_difficulty = 0
        self.initial_wave_points = initial_wave_points
        self.point_increase_per_wave = 0
        self.wave_points = initial_wave_points
        self.splat_loader = splat_loader
        self.ui_manager = ui_manager
        self.image_atlas = image_atlas
        self.screen_offset = [0, 0]

        self.collision_grid = collision_grid

        self.time_to_display_countdown = 5.0
        self.time_between_waves = 30.0
        self.sub_wave_time = 4.0
        self.sub_wave_acc = 2.0
        self.wave_time_accumulator = self.time_between_waves

        self.should_show_wave_countdown = False
        self.count_down_message = ""

        self.available_monsters_for_wave = []

        self.all_monster_point_list = {StandardMonster.monster_id: MonsterType(StandardMonster.monster_id, 1),
                                       ToughMonster.monster_id: MonsterType(ToughMonster.monster_id, 2),
                                       FastMonster.monster_id: MonsterType(FastMonster.monster_id, 3),
                                       BulletproofMonster.monster_id: MonsterType(BulletproofMonster.monster_id, 4),
                                       FireproofMonster.monster_id: MonsterType(FireproofMonster.monster_id, 5),
                                       LargeMonster.monster_id: MonsterType(LargeMonster.monster_id, 6),
                                       FastToughMonster.monster_id: MonsterType(FastToughMonster.monster_id, 7),
                                       LargeToughMonster.monster_id: MonsterType(LargeToughMonster.monster_id, 8)}

        self.monster_image_dict = {StandardMonster.monster_id: self.image_atlas.subsurface((0, 160, 16, 16)),
                                   ToughMonster.monster_id: self.image_atlas.subsurface((16, 160, 16, 16)),
                                   BulletproofMonster.monster_id: self.image_atlas.subsurface((32, 160, 16, 16)),
                                   FireproofMonster.monster_id: self.image_atlas.subsurface((48, 160, 16, 16)),
                                   FastMonster.monster_id: self.image_atlas.subsurface((0, 192, 16, 24)),
                                   FastToughMonster.monster_id: self.image_atlas.subsurface((16, 192, 16, 24)),
                                   LargeMonster.monster_id: self.image_atlas.subsurface((0, 224, 32, 32)),
                                   LargeToughMonster.monster_id: self.image_atlas.subsurface((32, 224, 32, 32))}

        self.all_monster_sprites = all_monster_sprites

        self.spawning_sub_waves = False
        self.number_of_sub_waves = 1
        self.current_sub_wave = 1

        self.cheapest_point_monster = 1000000000

        self.changed_wave = False
        
    def update(self, time_delta, offset):
        self.screen_offset = offset
        # if all monsters dead, speed up next wave arrival
        if not self.spawning_sub_waves and len(self.monsters) == 0 and self.wave_time_accumulator < 25.0:
            self.wave_time_accumulator = self.time_between_waves - self.time_to_display_countdown

        new_wave_time = self.time_between_waves - self.time_to_display_countdown
        new_wave_countdown = str(int(self.time_between_waves - self.wave_time_accumulator))
        if self.wave_time_accumulator >= self.time_between_waves and\
                self.current_wave_number < self.maximum_wave_number:
            self.should_show_wave_countdown = False
            self.spawn_new_wave()
            self.wave_time_accumulator = 0.0
        elif self.wave_time_accumulator >= new_wave_time and self.current_wave_number < self.maximum_wave_number:
            self.count_down_message = "New wave in " + new_wave_countdown + " seconds"
            self.should_show_wave_countdown = True
            self.wave_time_accumulator += time_delta
        elif self.current_wave_number < self.maximum_wave_number:
            self.wave_time_accumulator += time_delta
        else:
            pass

        if self.spawning_sub_waves:
            if self.sub_wave_acc > self.sub_wave_time:
                self.sub_wave_acc = 0.0
                self.spawn_new_sub_wave(int(self.wave_points / self.number_of_sub_waves), self.cheapest_point_monster)
            else:
                self.sub_wave_acc += time_delta

            if self.current_sub_wave > self.number_of_sub_waves:
                self.spawning_sub_waves = False
                self.current_sub_wave = 1
                self.point_increase_per_wave = self.point_increase_per_wave + ((self.current_wave_number + 1) * 12)
                self.wave_points = self.initial_wave_points + self.point_increase_per_wave

    def spawn_new_wave(self):
        self.changed_wave = True
        self.current_wave_number += 1
        self.available_monsters_for_wave[:] = []
        point_cost_of_cheapest_available_monster = 1000000000
        for monsterID in self.all_monster_point_list:
            if self.all_monster_point_list[monsterID].points <= (self.current_wave_number + self.wave_base_difficulty):
                self.available_monsters_for_wave.append(self.all_monster_point_list[monsterID])
                if point_cost_of_cheapest_available_monster > self.all_monster_point_list[monsterID].points:
                    point_cost_of_cheapest_available_monster = self.all_monster_point_list[monsterID].points

        self.number_of_sub_waves = 1 + self.current_wave_number
        self.spawning_sub_waves = True

        self.cheapest_point_monster = point_cost_of_cheapest_available_monster

    def spawn_new_sub_wave(self, points, point_cost_of_cheapest_available_monster):
        sub_wave_points = points
        self.current_sub_wave += 1
        while sub_wave_points >= point_cost_of_cheapest_available_monster:
            new_monster = self.pick_new_monster()
            self.monsters.append(new_monster)
            self.wave_points -= new_monster.point_cost
            sub_wave_points -= new_monster.point_cost

    def pick_new_monster(self):
        monster_type = random.choice(self.available_monsters_for_wave)
        new_monster = None
        if monster_type.id == StandardMonster.monster_id:
            new_monster = StandardMonster(self.monster_walk_path, self.monster_image_dict,
                                          self.all_monster_point_list, self.all_monster_sprites,
                                          self.screen_offset, self.collision_grid, self.splat_loader, self.ui_manager)
        if monster_type.id == ToughMonster.monster_id:
            new_monster = ToughMonster(self.monster_walk_path, self.monster_image_dict,
                                       self.all_monster_point_list, self.all_monster_sprites,
                                       self.screen_offset, self.collision_grid, self.splat_loader, self.ui_manager)
        if monster_type.id == FastMonster.monster_id:
            new_monster = FastMonster(self.monster_walk_path, self.monster_image_dict,
                                      self.all_monster_point_list, self.all_monster_sprites,
                                      self.screen_offset, self.collision_grid, self.splat_loader, self.ui_manager)
        if monster_type.id == BulletproofMonster.monster_id:
            new_monster = BulletproofMonster(self.monster_walk_path, self.monster_image_dict,
                                             self.all_monster_point_list,
                                             self.all_monster_sprites,
                                             self.screen_offset, self.collision_grid,
                                             self.splat_loader, self.ui_manager)
        if monster_type.id == LargeMonster.monster_id:
            new_monster = LargeMonster(self.monster_walk_path, self.monster_image_dict,
                                       self.all_monster_point_list, self.all_monster_sprites,
                                       self.screen_offset, self.collision_grid, self.splat_loader, self.ui_manager)
        if monster_type.id == FireproofMonster.monster_id:
            new_monster = FireproofMonster(self.monster_walk_path, self.monster_image_dict,
                                           self.all_monster_point_list, self.all_monster_sprites,
                                           self.screen_offset, self.collision_grid, self.splat_loader, self.ui_manager)
        if monster_type.id == FastToughMonster.monster_id:
            new_monster = FastToughMonster(self.monster_walk_path, self.monster_image_dict,
                                           self.all_monster_point_list, self.all_monster_sprites,
                                           self.screen_offset, self.collision_grid, self.splat_loader, self.ui_manager)
        if monster_type.id == LargeToughMonster.monster_id:
            new_monster = LargeToughMonster(self.monster_walk_path, self.monster_image_dict,
                                            self.all_monster_point_list, self.all_monster_sprites,
                                            self.screen_offset, self.collision_grid, self.splat_loader, self.ui_manager)
        
        return new_monster

    def has_changed_wave(self) -> bool:
        if self.changed_wave:
            self.changed_wave = False
            return True

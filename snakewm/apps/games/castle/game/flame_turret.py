import math
from .turret import Turret
from .flame_cone import FlameCone


class FlameTurret(Turret):
    def __init__(self, initial_position, build_cost, explosions_sprite_sheet, image_atlas, collision_grid, *groups):
        initial_radius = 80
        super().__init__(initial_position, build_cost, initial_radius, "flame_turret.png", *groups)

        self.collision_grid = collision_grid
        self.image_atlas = image_atlas
        self.set_image_direct(self.image_atlas.subsurface((0, 32, 32, 32)))
        self.fire_rate = 0.2
        self.fire_rate_acc = 0.0
        self.per_flame_damage = 1
        self.projectile_speed = 50.0
        self.rotate_speed = 10.0
        self.explosions_sprite_sheet = explosions_sprite_sheet

    def update_shooting(self, time_delta, monsters, projectiles):
        # calculate when it is time to fire
        if self.fire_rate_acc < self.fire_rate:
            self.fire_rate_acc += time_delta
        else:
            self.can_fire = True

        if self.current_target is None or self.current_target.should_die or self.target_distance > self.radius:
            self.current_target, self.target_distance = self.get_closest_monster_in_radius(monsters)

        if self.current_target is not None:
            # aim at the monster
            self.target_distance = self.calc_distance_to_target(self.current_target)
            
            results = self.calculate_aiming_vector(self.current_target, self.target_distance)
            self.target_vector = results[0]
            target_pos = results[1]
            relative_angle_to_target = self.rotate_current_angle_to_target(time_delta)
            
            # fire a flame cone
            # don't shoot unless we are pointing within at least 45 degrees of target
            if self.can_fire and abs(relative_angle_to_target) < math.pi/8:
                self.fire_rate_acc = 0.0
                self.can_fire = False
                gun_pos = [self.position[0] + (self.current_vector[0] * 12.0),
                           self.position[1] + (self.current_vector[1] * 12.0)]
                projectiles.append(FlameCone(gun_pos, target_pos, self.current_vector, self.per_flame_damage,
                                             self.projectile_speed, self.radius, self.explosions_sprite_sheet,
                                             self.collision_grid))
    
    def upgrade(self):
        self.level += 1
        self.fire_rate -= 0.05
        self.radius += 24
        if self.level == 2:
            self.set_image_direct(self.image_atlas.subsurface((32, 32, 32, 32)))
        if self.level == 3:
            self.set_image_direct(self.image_atlas.subsurface((64, 32, 32, 32)))

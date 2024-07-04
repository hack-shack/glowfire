import math
from .turret import Turret
from .missile import Missile


class MissileTurret(Turret):
    def __init__(self, initial_position, build_cost, explosions_sprite_sheet, image_atlas, collision_grid, *groups):
        initial_radius = 160
        # this calls the __init__ function of our base turret class
        super().__init__(initial_position, build_cost, initial_radius, "missile_turret.png", *groups)

        self.image_atlas = image_atlas
        self.set_image_direct(self.image_atlas.subsurface((0, 64, 32, 32)))
        self.rotate_speed = 10.0

        self.collision_grid = collision_grid

        self.fire_rate = 2.0  # fire rate, this is the time between shots, so smaller is faster
        self.fire_rate_acc = 0.0

        self.per_missile_damage = 55  # damage per missile
        self.explosions_sprite_sheet = explosions_sprite_sheet
        self.projectile_speed = 225.0

    # ------------------------------------------------------------------
    # function that determines when to shoot, what to shoot at and what to
    # shoot at it
    # --------------------------------------------------------------------
    def update_shooting(self, time_delta, monsters, projectiles):
        # time gap between shots
        if self.fire_rate_acc < self.fire_rate:
            self.fire_rate_acc += time_delta
        else:
            self.can_fire = True

        if self.current_target is None or self.current_target.should_die or self.target_distance > self.radius:
            # get new target
            self.current_target, self.target_distance = self.get_closest_monster_in_radius(monsters)

        if self.current_target is not None:
            # aim at the monster
            self.target_distance = self.calc_distance_to_target(self.current_target)
            
            results = self.calculate_aiming_vector(self.current_target, self.target_distance)
            self.target_vector = results[0]
            relative_angle_to_target = self.rotate_current_angle_to_target(time_delta)

            # fire some missiles
            if self.can_fire and abs(relative_angle_to_target) < math.pi/8:
                self.fire_rate_acc = 0.0
                self.can_fire = False
                gun_pos = [self.position[0], self.position[1]]
                
                projectiles.append(Missile(gun_pos, self.current_vector, self.current_target,
                                           self.current_target.position, self.per_missile_damage, self.projectile_speed,
                                           self.explosions_sprite_sheet, self.image_atlas,
                                           self.radius, self.collision_grid))

    def upgrade(self):
        self.level += 1
        self.fire_rate -= 0.25
        self.radius += (32 * self.level)
        self.per_missile_damage += (15 * self.level - 1)
        if self.level == 2:
            self.set_image_direct(self.image_atlas.subsurface((32, 64, 32, 32)))
        if self.level == 3:
            self.set_image_direct(self.image_atlas.subsurface((64, 64, 32, 32)))

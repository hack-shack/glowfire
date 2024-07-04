import math
from .turret import Turret
from .bullet import Bullet


class GunTurret(Turret):
    def __init__(self, initial_position, build_cost, explosions_sprite_sheet, image_atlas, collision_grid, *groups):
        initial_radius = 128
        # this calls the __init__ function of our base turret class
        super().__init__(initial_position, build_cost, initial_radius, "gun_turret.png", *groups)
        self.image_atlas = image_atlas
        self.collision_grid = collision_grid
        self.set_image_direct(self.image_atlas.subsurface((0, 0, 32, 32)))

        self.fire_rate = 0.5  # fire rate, this is the time between shots, so smaller is faster
        self.fire_rate_acc = 0.0
        self.per_bullet_damage = 5  # damage per bullet
        self.projectile_speed = 300
        self.explosions_sprite_sheet = explosions_sprite_sheet

        self.rotate_speed = 10.0

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
            self.current_target, self.target_distance = self.get_closest_monster_in_radius(monsters)

        if self.current_target is not None:
            # aim at the monster
            self.target_distance = self.calc_distance_to_target(self.current_target)
            
            results = self.calculate_aiming_vector(self.current_target, self.target_distance)
            self.target_vector = results[0]
            target_pos = results[1]

            relative_angle_to_target = self.rotate_current_angle_to_target(time_delta)
            # fire some bullets
            if self.can_fire and abs(relative_angle_to_target) < math.pi/8:
                self.fire_rate_acc = 0.0
                self.can_fire = False
                
                gun_pos1 = [self.position[0] + (self.current_vector[1] * 6),
                            self.position[1] - (self.current_vector[0] * 6)]
                bullet_vec1_x = target_pos[0] - gun_pos1[0]
                bullet_vec1_y = target_pos[1] - gun_pos1[1]
                bullet1_dist = math.sqrt((bullet_vec1_x ** 2) + (bullet_vec1_y ** 2))
                bullet_vec1 = [bullet_vec1_x/bullet1_dist, bullet_vec1_y/bullet1_dist]
                
                gun_pos2 = [self.position[0] - (self.current_vector[1] * 6),
                            self.position[1] + (self.current_vector[0] * 6)]
                bullet_vec2_x = target_pos[0] - gun_pos2[0]
                bullet_vec2_y = target_pos[1] - gun_pos2[1]
                bullet2_dist = math.sqrt((bullet_vec2_x ** 2) + (bullet_vec2_y ** 2))
                bullet_vec2 = [bullet_vec2_x/bullet2_dist, bullet_vec2_y/bullet2_dist]
                
                projectiles.append(Bullet(gun_pos1, bullet_vec1, target_pos, self.per_bullet_damage,
                                          self.projectile_speed, self.explosions_sprite_sheet,
                                          self.image_atlas, self.collision_grid))
                projectiles.append(Bullet(gun_pos2, bullet_vec2, target_pos, self.per_bullet_damage,
                                          self.projectile_speed, self.explosions_sprite_sheet,
                                          self.image_atlas, self.collision_grid))

    def upgrade(self):
        self.level += 1
        self.fire_rate -= 0.075
        self.radius += (12 * self.level)
        self.per_bullet_damage += 2
        if self.level == 2:
            self.set_image_direct(self.image_atlas.subsurface((32, 0, 32, 32)))
        if self.level == 3:
            self.set_image_direct(self.image_atlas.subsurface((64, 0, 32, 32)))

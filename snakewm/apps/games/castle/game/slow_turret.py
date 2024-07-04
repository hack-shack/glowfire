import math
from .turret import Turret


class SlowTurret(Turret):
    def __init__(self, initial_position, build_cost, image_atlas, *groups):
        initial_radius = 80
        self.slow_down_percentage = 0.85
        # this calls the __init__ function of our base turret class
        super().__init__(initial_position, build_cost, initial_radius, "slow_turret", *groups)

        self.image_atlas = image_atlas
        self.set_image_direct(self.image_atlas.subsurface((0, 96, 32, 32)))

    # ------------------------------------------------------------------
    # function that determines when to shoot, what to shoot at and what to
    # shoot at it
    # --------------------------------------------------------------------
    def update_shooting(self, time_delta, monsters, projectiles):
        for monster in monsters:
            x_dist = self.position[0] - monster.position[0]
            y_dist = self.position[1] - monster.position[1]
            total_dist = math.sqrt((x_dist ** 2) + (y_dist ** 2))
            if total_dist < self.radius:
                monster.set_slowdown(self.slow_down_percentage)

    def upgrade(self):
        self.level += 1
        self.slow_down_percentage -= 0.075
        self.radius += 24
        if self.level == 2:
            self.set_image_direct(self.image_atlas.subsurface((32, 96, 32, 32)))
        if self.level == 3:
            self.set_image_direct(self.image_atlas.subsurface((64, 96, 32, 32)))

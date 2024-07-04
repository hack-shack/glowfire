
def enum(*sequential, **named):
    enums = dict(zip(sequential, range(len(sequential))), **named)
    return type('Enum', (), enums)


DamageType = enum('BULLET', 'FIRE', 'MISSILE', 'LASER')


class Damage:
    def __init__(self, amount, damage_type):
        self.amount = amount
        self.type = damage_type

import random

from game.enemy import Enemy
from game.utils import Utils
from mgl2d.math.rect import Rect


class Boss(Enemy):
    SURROUND_DISTANCE = 90

    def __init__(
            self,
            world,
            frames_store,
            x,
            y,
            footprint_dim=Rect(0, 0, 60, 14),
            attack_reach=100,
    ):
        super().__init__(world, frames_store, x, y, footprint_dim, attack_reach)

        self.ENERGY_MAX_ENERGY = 250
        self.energy = self.ENERGY_MAX_ENERGY
        self.attack_force = 4
        self.clear_targeting()
        self.move_speed_modifier = 3

        if Utils.probability_check(30):
            self.say(
                random.choice([
                    "I CLAIM THIS STATION!",
                    "YOU SHOULD TAKE THE U-BAHN!",
                ]),
                time=2500,
            )

    def blocked_response(self):
        self.punch()
        self.mark_successful_action()
        if Utils.probability_check(Enemy.SAY_SOMETHING_PROBABILITY):
            self.say_something_when_blocked()

    def say_something_when_blocked(self):
        self.say(random.choice([
            "OUT OF MY WAY!",
        ]))

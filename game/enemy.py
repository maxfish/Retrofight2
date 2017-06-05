import random

from game.character import Character
from lib.frames_store import FramesStore
from lib.utils import Utils
from lib.vector2d import Vector2d

DEBUG = 0


class Enemy(Character):
    DEFAULT_DIRECTION = Character.DIR_LEFT  # enemies default to looking left
    SAY_SOMETHING_PROBABILITY = 10
    SURROUND_DISTANCE = 170

    def __init__(self, world, frames_store, x, y, footprint_dim=Character.DEFAULT_FOOTPRINT_DIM, attack_reach=70):
        super().__init__(world, frames_store, x, y, footprint_dim, attack_reach)
        self.ENERGY_MAX_ENERGY = 50
        self.energy = self.ENERGY_MAX_ENERGY
        self.attack_force = 1
        self.clear_targeting()
        self.move_speed_modifier = 1.2

    def begin(self):
        self.stop()
        if random.randint(0, 10) >= 8:
            self.say('TICKETS, PLEASE', time=4000)

    def set_action(self, action):
        super().set_action(action)

        if self.action == self.ACTION_DIE:
            self._sprite.play_animation("fall", (FramesStore.FLAG_FLIP_X if self.direction == self.DIR_LEFT else 0))
        elif self.action == self.ACTION_HURT:
            self._sprite.play_animation("hurt", (FramesStore.FLAG_FLIP_X if self.direction == self.DIR_LEFT else 0))
            self.move_v.x = 0
            self.move_v.y = 0
        elif self.action == self.ACTION_STAND:
            self._sprite.play_animation("stand", (FramesStore.FLAG_FLIP_X if self.direction == self.DIR_LEFT else 0))
        elif self.action == self.ACTION_WALK:
            self._sprite.play_animation("walk", (
                FramesStore.FLAG_FLIP_X if self.direction == self.DIR_LEFT else 0) | FramesStore.FLAG_LOOP_ANIMATION)
        elif self.action == self.ACTION_PUNCH_1:
            self._sprite.play_animation("punch", (FramesStore.FLAG_FLIP_X if self.direction == self.DIR_LEFT else 0))

    def update(self, game_speed):
        if self.action == self.ACTION_DIE:
            if not self._sprite.animating:
                self._world.remove_character(self)

        elif self.action in (self.ACTION_STAND, self.ACTION_WALK):
            players_in_attack_range = self._world.players_in_attack_range(self)
            if players_in_attack_range and not self.is_surround_targeting:
                # may attack a player, unless surrounding
                if (random.randint(0, 100) < 10):
                    player = players_in_attack_range[0]
                    self.direction = self.direction_towards(player)
                    self.punch()
            elif self.targeted_player:
                if self.is_surround_targeting:
                    target_surround_x = self.targeted_player.position.x + self.surround_side * self.SURROUND_DISTANCE * 0.9
                    if (
                                        self.surround_side < 0 and self._position.x <= target_surround_x or
                                        self.surround_side > 0 and self._position.x >= target_surround_x
                    ):
                        # surrounding run finished - begin targeting approach
                        self.is_surround_targeting = False
                        self.surround_side = None
                        self.walk_towards(self.targeted_player)
                    else:
                        # run to surround targeted player
                        self.surround(self.targeted_player)
                        if DEBUG:
                            print(id(self), 'surround', self.targeted_player.id)
                else:
                    # chase targeted player
                    self.walk_towards(self.targeted_player)
                    if DEBUG:
                        print(id(self), 'chase', self.targeted_player.id)

            elif not self.targeted_player:
                # target a new player
                players_worth_attacking = self._world.players_worth_attacking(self)
                if players_worth_attacking:
                    player = players_worth_attacking[0]
                    if DEBUG:
                        print(id(self), 'TARGET', player.id)
                    self.target(player)

        elif self.action == self.ACTION_HURT:
            if not self._sprite.animating:
                self.stop()

        elif self.action == self.ACTION_PUNCH_1:
            if not self._sprite.animating:
                self.stop()

        if not self.has_recent_successful_action() and not self._world.is_game_over():
            self.blocked_response()

        super().update(game_speed)

    def blocked_response(self):
        self.stop()
        self.mark_successful_action()
        if Utils.probability_check(Enemy.SAY_SOMETHING_PROBABILITY):
            self.say_something_when_blocked()

    def say_something_when_blocked(self):
        self.say(random.choice([
            "WHAT AM I DOING HERE?!",
            "THIS PLACE HAS GOOD REVIEWS!",
            "I'LL GIVE IT A 1 STAR!",
            "I SHOULD CHECK IN",
        ]))

    def handle_bound_overflow(self, left=0, right=0, top=0, bottom=0):
        new_move_v = self.move_v

        if top or bottom:
            return top or bottom
        else:
            # they're allowed to be off-screen
            return 0

    def _update_sprite(self, game_speed):
        self._sprite.x = self._position.x
        self._sprite.y = self._position.y
        self._sprite.update(game_speed)

    def hit(self, offender, force):
        # when enemy gets hit his anger grows and he reconsiders his target
        super().hit(offender, force)
        self.anger[offender] += 1
        self.clear_targeting()
        self.mark_successful_action()

        if offender.__class__ != self.__class__:
            self._world.increment_score(1)

    def die(self):
        super().die()
        self._world.increment_score(100)

    def walk_towards(self, player):
        side_of_player = (player.position.x - self._position.x) / (abs(player.position.x - self._position.x) +0.01)
        position_next_to_player = Vector2d(
            player._position.x - (side_of_player * self.attack_reach * 0.8),
            player._position.y,
        )
        rel_player_pos = (position_next_to_player - self._position)
        # TODO: !!!!
        player_dir_v = rel_player_pos.direction()
        move_speed = (random.randint(20, 20 + 4 * self.anger_towards(player)) / 20) * self.move_speed_modifier
        self.move(player_dir_v * move_speed)

    def surround(self, player):
        before_run = self.direction_towards(player) == self.surround_side
        if before_run:
            target_y = player.position.y + self.run_around_vertical_side * (
                player.footprint_dim.h * 0.7 + self.footprint_dim.h * 0.7)
            if target_y >= self._world.bounds.bottom or target_y <= self._world.bounds.top:
                # try again via the other side
                self.run_around_vertical_side *= -1
                self.surround(player)
                return

            target_surround_pos = Vector2d(
                player.position.x + self.surround_side * (self.SURROUND_DISTANCE * 0.2),
                target_y,
            )
        else:
            target_surround_pos = Vector2d(
                player.position.x + self.surround_side * self.SURROUND_DISTANCE,
                (self._position.y + player.position.y) / 2,
            )

        rel_target_pos = (target_surround_pos - self._position)
        target_dir_v = rel_target_pos.direction()
        move_speed = 2.2 * self.move_speed_modifier  # RUN!
        self.move(target_dir_v * move_speed)

    def clear_targeting(self):
        self.targeted_player = None
        self.is_surround_targeting = False
        self.surround_side = None
        self.run_around_vertical_side = None

    def target(self, player):
        self.targeted_player = player

        targeting_enemies = player.targeting_enemies()
        non_surround_targeting_enemies = [
            enemy for enemy in targeting_enemies
            if not enemy.is_surround_targeting
            ]
        surround_targeting_enemies = [
            enemy for enemy in targeting_enemies
            if enemy.is_surround_targeting
            ]

        if len(non_surround_targeting_enemies) >= 2 and not surround_targeting_enemies:
            # consider surround targeting
            my_attack_direction = self.direction_towards(player)
            attack_directions = [
                enemy.direction_towards(player)
                for enemy in non_surround_targeting_enemies
                ]
            same_attack_directions = len([
                                             at_dir for at_dir in attack_directions
                                             if at_dir == my_attack_direction
                                             ]) - 1  # exclude myself
            other_attack_directions = len(non_surround_targeting_enemies) - same_attack_directions - 1  # exlude myself

            diff = same_attack_directions - other_attack_directions
            if diff > 0 and random.randint(0, diff) >= 0:  # randomness of surrounding
                # surround targeting!!!
                self.is_surround_targeting = True
                self.surround_side = my_attack_direction
                if self._position.y != player.position.y:
                    self.run_around_vertical_side = (self._position.y - player.position.y) / abs(
                        self._position.y - player.position.y)
                else:
                    self.run_around_vertical_side = 1

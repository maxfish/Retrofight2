from collections import defaultdict

from game.entity import Entity
from lib.pyglet.gfx import Gfx
from lib.rect import Rect
from lib.utils import Utils
from lib.vector2d import Vector2d

INTRO_DEBUG = 0
HIT_DEBUG = 0


class Character(Entity):
    ACTION_DEBUG = False
    FOOTPRINT_DEBUG = False

    ACTION_DIE = 0
    ACTION_STAND = 1
    ACTION_FALL = 2
    ACTION_ON_THE_GROUND = 3
    ACTION_WALK = 4
    ACTION_JUMP = 5
    ACTION_LAND = 6
    ACTION_BLOCK = 7
    ACTION_HURT = 8
    ACTION_PUNCH_1 = 9
    ACTION_PUNCH_2 = 10
    ACTION_SPECIAL = 11

    ACTION_TO_STRING = ['DIE', 'STAND', 'FALL', 'ON_THE_GROUND', 'WALK', 'JUMP', 'LAND', 'BLOCK', 'HURT',
                        'PUNCH_1', 'PUNCH_2', 'SPECIAL']

    WALKING_SPEED_X = 1.0
    WALKING_SPEED_Y = 0.5

    MAX_ANGER = 3

    DEFAULT_FOOTPRINT_DIM = Rect(0, 0, 40, 15)
    WATCHDOG_THRESHOLD = 1000

    # Direction
    DIR_LEFT = -1  # left
    DIR_RIGHT = 1  # right

    DEFAULT_DIRECTION = DIR_RIGHT  # default looking direction is right

    def __init__(self, world, frames_store, x, y, footprint_dim=DEFAULT_FOOTPRINT_DIM, attack_reach=70):
        """
        footprint_dim_rect - Rect of (0, 0 - w, h) of char's ground footprint
        """
        super().__init__(world, frames_store, x, y)
        self.id = id(self)

        self.mark_successful_action()

        self.footprint_dim = footprint_dim
        self.footprint = self._get_footprint_by_position(self._position.x, self._position.y)
        self.attack_reach = attack_reach

        self.move_v = Vector2d(0, 0)

        self.action = self.ACTION_STAND

        self.old_action = self.action
        self.direction = self.DIR_RIGHT

        self.ENERGY_MAX_ENERGY = 1
        self.energy = self.ENERGY_MAX_ENERGY
        self.attack_force = 0

        self.set_action(self.ACTION_STAND)

        # self.punch_1_sound = pygame.mixer.Sound('resources/sounds/punch_1.wav')
        # self.punch_2_sound = pygame.mixer.Sound('resources/sounds/punch_2.wav')
        # self.punch_hit_sound = pygame.mixer.Sound('resources/sounds/player_hit.wav')
        # self.game_over_sound = pygame.mixer.Sound('resources/sounds/die.wav')

        self.anger = defaultdict(int)

        self.shut_up()  # to initialize `say`

    def begin(self):
        pass

    def set_action(self, action):
        self.old_action = self.action
        self.action = action

    def draw(self, surface):
        super().draw(surface)

        if Character.ACTION_DEBUG:
            if self.action != self.ACTION_DIE:
                Gfx.render_centered_text(
                    surface,
                    self.ACTION_TO_STRING[self.action],
                    center_x=self._position.x - self._world.window_x,
                    center_y=self._position.y - self._sprite.frame.rect.height - 10 - self._world.window_y - self._z,
                )
        elif self.text_to_say:
            Gfx.render_centered_text(
                surface,
                self.text_to_say,
                center_x=self._position.x - self._world.window_x,
                center_y=self._position.y - 100 - self._world.window_y,
            )

            # if Character.FOOTPRINT_DEBUG and self.action != self.ACTION_DIE:
            #     draw.rect(
            #         surface,
            #         (255, 0, 0),
            #         self.footprint.move(
            #             -self._world.window_x,
            #             -self._world.window_y,
            #         ),
            #     )

    def _get_footprint_by_position(self, fx, fy):
        return Rect(
            fx - self.footprint_dim.w / 2,
            fy - self.footprint_dim.h / 2,
            self.footprint_dim.w,
            self.footprint_dim.h,
        )

    def direction_towards(self, character):
        return (character.position.x - self._position.x) / abs(character.position.x - self._position.x)

    def anger_towards(self, character):
        return min(self.anger.get(character.id, 0), self.MAX_ANGER)

    def update(self, game_speed):

        # Say update.
        ticks = Utils.time_in_ms()
        interval = ticks - self.text_started
        if INTRO_DEBUG:
            if self == self._world.intro_player:
                print()
                print(':: text ::', self.text_to_say)
                print('ticks', ticks)
                print('- text_started', self.text_started)
                print('= interval', interval)
                print('time', self.text_time)
                print()

        if self.text_to_say and interval >= self.text_time:
            self.shut_up()

        # Calculate Char's new position by its movement vector.
        new_fx = self._position.x + self.move_v.x * game_speed
        new_fy = self._position.y + self.move_v.y * game_speed
        new_pos = Vector2d(new_fx, new_fy)

        # Calculate Char's new footprint on the ground.
        new_pos = self.check_bumping(new_pos)

        # Update Char's position and footprint
        self._position.x = new_pos.x
        self._position.y = new_pos.y
        self.footprint = self._get_footprint_by_position(self._position.x, self._position.y)

        self.check_attack(self.attack_force)

        self._update_sprite(game_speed)

    def check_bumping(self, new_pos_v, collisions=0, exclude_chars=None):
        new_pos_v = self.check_map_bounds(new_pos_v)
        new_footprint = self._get_footprint_by_position(new_pos_v.x, new_pos_v.y)

        exclude_chars = exclude_chars or []

        if collisions == 3:
            # Too many collisions, stop where you are.
            return Vector2d(self._position.x, self._position.y)

        for ch in self._world.other_characters(self):
            if ch in exclude_chars:
                continue

            if new_footprint.collide_with_rect(ch.footprint):
                ch_rel_pos = Vector2d(ch.position.x, ch.position.y) - new_pos_v

                # Check if we should go around clockwise or counter-clockwise.
                if self.move_v.x >= 0 and ch_rel_pos.x >= 0:
                    is_circling_clockwise = self.move_v.y < ch_rel_pos.y
                elif self.move_v.x < 0 and ch_rel_pos.x < 0:
                    is_circling_clockwise = self.move_v.y > ch_rel_pos.y
                elif self.move_v.y >= 0 and ch_rel_pos.y >= 0:
                    is_circling_clockwise = self.move_v.x > ch_rel_pos.x
                elif self.move_v.y < 0 and ch_rel_pos.y < 0:
                    is_circling_clockwise = self.move_v.x < ch_rel_pos.x
                else:
                    is_circling_clockwise = True

                # Check if you can go around the character on your way.
                new_move_v = self.move_v
                # TODO: !!!!!
                # self.move_v.rotate(
                # -90 if is_circling_clockwise else 90
                # )

                # Angle between vector pointing from you towards the other char
                # and the direction in which you want to move. 0 - 180 deg.
                # If it's small, means you're pushing directly in his direction.
                # If it's around 90, you're circling around him.
                # 180 means you're going in the opposite direction.
                angle = self.angle_between_vectors_to_180(ch_rel_pos, self.move_v)
                if angle < 45:
                    magnitude = 0.4 + (angle / 90)
                else:
                    magnitude = 1.0
                new_move_v = new_move_v * magnitude

                new_pos_v = self._position + new_move_v

                # Recursively check the new position
                return self.check_bumping(
                    new_pos_v,
                    collisions=collisions + 1,
                    exclude_chars=exclude_chars + [ch]
                )
        else:
            # no character colisions found for new position, still check map bounds
            # and return new pos
            return new_pos_v

    def check_map_bounds(self, pos):
        footprint = self._get_footprint_by_position(pos.x, pos.y)

        # Check top-bottom map bounds
        top_overflow = self._world.bounds.y - footprint.y
        bottom_overflow = footprint.bottom - self._world.bounds.bottom
        if top_overflow > 0:
            y_correction = self.handle_bound_overflow(top=top_overflow)
        elif bottom_overflow > 0:
            y_correction = -self.handle_bound_overflow(bottom=bottom_overflow)
        else:
            y_correction = 0
        new_fy = pos.y + y_correction

        # Check left-right map bounds
        left_overflow = self._world.bounds.x + self._world.window_x - footprint.x
        right_overflow = footprint.right - self._world.bounds.right - self._world.window_x
        if left_overflow > 0:
            x_correction = self.handle_bound_overflow(left=left_overflow)
        elif right_overflow > 0:
            x_correction = -self.handle_bound_overflow(right=right_overflow)
        else:
            x_correction = 0
        new_fx = pos.x + x_correction

        return Vector2d(new_fx, new_fy)

    def angle_between_vectors_to_180(self, v1, v2):
        angle = abs(v1.angle_to(v2))
        return min(angle, 360 - angle)

    def handle_bound_overflow(self, left=0, right=0, top=0, bottom=0):
        return left or right or top or bottom

    def _update_sprite(self, game_speed):
        self._sprite.x = self._position.x
        self._sprite.y = self._position.y
        self._sprite.update(game_speed)

    default_direction = object()

    def move_direction(self, move_v, default=default_direction):
        if move_v.x < 0:
            return self.DIR_LEFT  # left
        elif move_v.x > 0:
            return self.DIR_RIGHT  # right
        elif default is self.default_direction:
            return self.DEFAULT_DIRECTION
        else:
            return default

    def hit(self, offender, force):
        # TODO: Here we need a way to know the position of the hit (high|low)
        if self.__class__ == offender.__class__:
            force /= 3

        self.energy -= force

        if self.energy > 0:
            self.feel_the_pain()
        else:
            self.energy = 0
            self.die()

    def feel_the_pain(self):
        self.set_action(self.ACTION_HURT)
        # self.punch_hit_sound.play()

    def die(self):
        self.set_action(self.ACTION_DIE)
        # if Utils.probability_check(30):
        #     self.game_over_sound.play()
        self.shut_up()

    def check_attack(self, force):
        if not self._sprite.attack_box:
            return

        hit_count = 0
        for c in self._world.other_characters(self):
            if c.sprite.hit_box and self._sprite.attack_box.collide_with_rect(c.sprite.hit_box):
                if abs(self._position.y - c.position.y) < self.footprint.h:
                    # This prevents multiple damages from a single hit over several frames (I think?)
                    if c.action != self.ACTION_HURT:
                        hit_count += 1
                        c.hit(self, force)
                        if hit_count == 3:
                            if HIT_DEBUG:
                                print('*** SKIP HIT!!!')
                            break
                            # if hit_count:
                            #     self.punch_hit_sound.play()

    def move(self, move_v):
        if move_v.length() > 0.3:
            self.mark_successful_action()

        if abs(move_v.x) < 0.5:  # walking near vertical, he might start changing direction like crazy
            move_v.x = 0
        self.direction = self.move_direction(move_v, default=self.direction)
        self.move_v = move_v
        self.set_action(self.ACTION_WALK)

    def stop(self):
        self.clear_targeting()
        self.move_v = Vector2d(0, 0)
        self.set_action(self.ACTION_STAND)

    def punch(self):
        self.mark_successful_action()
        self.stop()
        # if Utils.probability_check(50):
        #     self.punch_1_sound.play()
        # else:
        #     self.punch_2_sound.play()
        self.set_action(self.ACTION_PUNCH_1)

    def say(self, text, time=1000, color=(255, 255, 255), bgcolor=(20, 20, 20)):
        self.text_to_say = text
        self.text_time = time
        self.text_started = Utils.time_in_ms()

    def shut_up(self):
        self.text_to_say = None
        self.text_time = 0
        self.text_started = 0

    def mark_successful_action(self):
        self.last_successful_action_time = Utils.time_in_ms()

    def has_recent_successful_action(self):
        ticks = Utils.time_in_ms()
        return (ticks - self.last_successful_action_time) <= self.WATCHDOG_THRESHOLD

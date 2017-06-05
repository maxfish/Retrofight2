import math

from game.character import Character
from game.entity import Entity
from lib.controller import Controller
from lib.frames_store import FramesStore
from lib.pyglet.gfx import Gfx
from lib.sprite import Sprite
from lib.utils import Utils
from lib.vector2d import Vector2d


class Player(Character):
    WALK_H_SPEED = 3 * 2  # pixels/frame
    WALK_V_SPEED = 1.5 * 2  # pixels/frame

    JUMP_HEIGHT = 100  # pixels
    JUMP_SPEED = 0.06
    JUMP_SPEED_H = WALK_H_SPEED * 2  # pixels/frame

    ATTACK_FORCE_PUNCH_1 = 10
    ATTACK_FORCE_PUNCH_2 = 14
    ATTACK_FORCE_SPECIAL = 10

    MAX_DISTANCE_TO_PICKUP = 20

    def __init__(self, id, world, gamepad, player_name, footprint_dim=Character.DEFAULT_FOOTPRINT_DIM):
        self.frames_store = FramesStore()
        self.frames_store.load('resources/sprites/' + player_name, 'sprites.json')
        self._sprite = Sprite(self.frames_store)
        # TODO: The face should be a frame within the sprite definition
        self.face = Gfx.load_image('resources/sprites/' + player_name + '/face.png')

        super().__init__(world, self.frames_store, 0, 0, footprint_dim)

        self.id = id
        self.gamepad = gamepad if gamepad else GamePad(None)

        self.STATE_DEAD = PlayerStateDead(self)
        self.STATE_GROUND = PlayerStateGround(self)
        self.STATE_RAISE = PlayerStateRaise(self)
        self.STATE_STAND = PlayerStateStand(self)
        self.STATE_WALK = PlayerStateWalk(self)
        self.STATE_PUNCH = PlayerStatePunch(self)
        self.STATE_HURT = PlayerStateHurt(self)
        self.STATE_JUMP = PlayerStateJump(self)
        self.STATE_FALL = PlayerStateFall(self)
        self.STATE_PICKUP = PlayerStatePickUp(self)

        self.current_state = None
        self.change_state_to(self.STATE_STAND)

        self.energy = self.ENERGY_MAX_ENERGY = 120
        self.attack_force = 0

    def change_state_to(self, new_state):
        old_state = self.current_state
        if new_state != old_state:
            if old_state is not None:
                old_state.leave(new_state)
            new_state.enter(old_state)
            self.current_state = new_state

    def set_action(self, action):
        super().set_action(action)

    def handle_input(self):
        self.change_state_to(self.current_state.handle_input())

    def update(self, game_speed):
        self.change_state_to(self.current_state.update(game_speed))
        super().update(game_speed)
        print(self.position)

    def draw(self, surface):
        super().draw(surface)

        Y_DEFAULT_OFFSET = 2
        ENERGY_BAR_X_DEFAULT_OFFSET = 10
        ENERGY_BAR_MARGIN_BETWEEN_BARS = 10
        ENERGY_BAR_WIDTH = 80

        x = ENERGY_BAR_X_DEFAULT_OFFSET + self.id * (
            ENERGY_BAR_WIDTH + ENERGY_BAR_MARGIN_BETWEEN_BARS + self.face.width)
        Gfx.draw_image_at(surface, self.face, x, Y_DEFAULT_OFFSET)

        bar_x = x + self.face.width
        bar_y = Y_DEFAULT_OFFSET

        energy_amount = (self.energy / self.ENERGY_MAX_ENERGY) * ENERGY_BAR_WIDTH
        # draw.rect(surface, (40, 40, 40), pygame.Rect(bar_x, bar_y, ENERGY_BAR_WIDTH, 10))
        # if energy_amount > 0:
        #     draw.rect(surface, (0, 240, 0), pygame.Rect(bar_x, bar_y, energy_amount, 10))

    def targeting_enemies(self):
        return [
            enemy for enemy in self._world.enemies
            if enemy.targeted_player is self
            ]

    def hit(self, offender, force):
        self.change_state_to(self.current_state.hit(offender, force))


class PlayerState(Entity.State):
    def __init__(self, player):
        super().__init__()
        self.p = player

    def handle_input(self):
        self.p.gamepad.update()
        return self

    def update(self, game_speed):
        super().update(game_speed)
        return self

    def stop(self):
        self.p.move_v = Vector2d(0, 0)

    def hit(self, offender, force):
        # Friendly fire
        if self.__class__ == offender.__class__:
            force /= 3

        self.p.energy -= force

        if self.p.energy > 0:
            if self.p._z > 0:
                return self.p.STATE_FALL
            else:
                return self.p.STATE_HURT
        else:
            self.p.energy = 0
            return self.p.STATE_FALL

    def play_anim(self, anim_name, loop=False, speed=1):
        self.p.sprite.play_animation(anim_name, (
            FramesStore.FLAG_FLIP_X if self.p.direction == Character.DIR_LEFT else 0) |
                                     (FramesStore.FLAG_LOOP_ANIMATION if loop else 0), speed=speed)


class PlayerStateDead(PlayerState):
    def enter(self, old_state):
        super().enter(old_state)
        self.stop()
        # self.p.game_over_sound.play()
        self.p.shut_up()
        # self.play_anim("fall")

    def update(self, game_speed):
        super().update(game_speed)
        self.p.should_be_removed = True
        return self


class PlayerStateGround(PlayerState):
    def enter(self, old_state):
        super().enter(old_state)
        self.stop()
        self.p._z = 0
        self.play_anim("ground")

    def update(self, game_speed):
        super().update(game_speed)

        if not self.p.sprite.animating:
            if self.p.energy > 0:
                return self.p.STATE_RAISE
            else:
                return self.p.STATE_DEAD
        return self


class PlayerStateRaise(PlayerState):
    def enter(self, old_state):
        super().enter(old_state)
        self.stop()
        self.play_anim("raise")

    def update(self, game_speed):
        super().update(game_speed)

        if not self.p.sprite.animating:
            return self.p.STATE_STAND

        return self


class PlayerStateStand(PlayerState):
    def enter(self, old_state):
        super().enter(old_state)
        self.stop()
        self.p.z = 0
        self.play_anim("stand", loop=True)

    def handle_input(self):
        super().handle_input()

        # GAME OVER
        if self.p._world.scene == self.p._world.SCENE_GAME_OVER:
            if self.p._world.game_over_state >= 10:
                if self.p.gamepad.is_button_pressed('A') or self.p.gamepad.is_button_pressed('B'):
                    self.p._world.restart_game()
                    return self

        if self.p.gamepad.is_button_pressed('A') \
                or self.p.gamepad.is_button_pressed('B'):
            match = self.p._world.nearby_item(self.p.position, max_distance=self.p.MAX_DISTANCE_TO_PICKUP)
            if match:
                return self.p.STATE_PICKUP
            else:
                return self.p.STATE_PUNCH

        if self.p.gamepad.is_button_pressed('Y'):
            return self.p.STATE_JUMP

        if self.p.gamepad.is_button_down(Controller.K_RIGHT) or \
                self.p.gamepad.is_button_down('LEFT') or \
                self.p.gamepad.is_button_down('DOWN') or \
                self.p.gamepad.is_button_down('UP'):
            return self.p.STATE_WALK

        return self


class PlayerStateWalk(PlayerState):
    def enter(self, old_state):
        super().enter(old_state)

    def handle_input(self):
        super().handle_input()

        if self.p.gamepad.is_button_pressed('A') \
                or self.p.gamepad.is_button_pressed('B'):
            return self.p.STATE_PUNCH

        if self.p.gamepad.is_button_pressed('Y'):
            return self.p.STATE_JUMP

        if not self.p.gamepad.is_button_down('LEFT') and not self.p.gamepad.is_button_down('RIGHT') \
                and not self.p.gamepad.is_button_down('UP') and not self.p.gamepad.is_button_down('DOWN'):
            return self.p.STATE_STAND

        anim_speed = 1

        if self.p.gamepad.is_button_down('RIGHT'):
            self.p.direction = self.p.DIR_RIGHT
            self.p.move_v.x = self.p.WALK_H_SPEED
        elif self.p.gamepad.is_button_down('LEFT'):
            self.p.direction = self.p.DIR_LEFT
            self.p.move_v.x = -self.p.WALK_H_SPEED
        elif self.p.gamepad.is_button_down('DOWN'):
            self.p.move_v.y = self.p.WALK_V_SPEED
            anim_speed = 0.4
        elif self.p.gamepad.is_button_down('UP'):
            self.p.move_v.y = -self.p.WALK_V_SPEED
            anim_speed = 0.4

        self.play_anim("walk", loop=True, speed=anim_speed)
        return self


class PlayerStatePunch(PlayerState):
    def enter(self, old_state):
        super().enter(old_state)
        self.stop()

        if self.p.gamepad.is_button_down('A') and self.p.gamepad.is_button_down('B'):
            self.p.attack_force = self.p.ATTACK_FORCE_SPECIAL
            self.play_anim("special")
        elif self.p.gamepad.is_button_down('A'):
            self.p.attack_force = self.p.ATTACK_FORCE_PUNCH_1
            # self.p.punch_1_sound.play()
            self.play_anim("punch")
        elif self.p.gamepad.is_button_down('B'):
            self.p.attack_force = self.p.ATTACK_FORCE_PUNCH_2
            # self.p.punch_2_sound.play()
            self.play_anim("punch_low")

    def update(self, game_speed):
        super().update(game_speed)
        return self if self.p.sprite.animating else self.p.STATE_STAND


class PlayerStateHurt(PlayerState):
    def enter(self, old_state):
        super().enter(old_state)
        self.stop()
        # self.p.punch_hit_sound.play()
        self.play_anim("hurt")

    def update(self, game_speed):
        super().update(game_speed)
        return self if self.p.sprite.animating else self.p.STATE_STAND


class PlayerStatePickUp(PlayerState):
    def enter(self, old_state):
        super().enter(old_state)
        self.stop()
        self.play_anim("pickup")
        item = self.p._world.nearby_item(self.p.position, max_distance=self.p.MAX_DISTANCE_TO_PICKUP)
        if item:
            value = item.picked_up_by(self.p)
            if value.get('energy'):
                self.p.energy += value['energy']
                self.p.energy = Utils.clamp(self.p.energy, 0, self.p.ENERGY_MAX_ENERGY)
            if value.get('points'):
                # TODO: Points should be added to the player not to the world
                self.p._world.increment_score(value['points'])

    def update(self, game_speed):
        super().update(game_speed)
        return self if self.p.sprite.animating else self.p.STATE_STAND


class PlayerStateJump(PlayerState):
    ACTION_PREPARE_TO_JUMP = 0
    ACTION_JUMP = 1
    ACTION_PREPARE_TO_STAND = 2

    TERRAIN_TRESHOLD = 6

    def __init__(self, player):
        super().__init__(player)
        self.action = 0
        self.jump_offset = 0
        self.long_jump = False

    def enter(self, old_state):
        super().enter(old_state)
        self.jump_offset = 0
        self.action = self.ACTION_PREPARE_TO_JUMP

        self.long_jump = (
            old_state == self.p.STATE_WALK or self.p.gamepad.is_button_down('RIGHT') or self.p.gamepad.is_button_down(
                'LEFT'))

        if self.long_jump:
            self.p.move_v.x = self.p.JUMP_SPEED_H * self.p.direction
        else:
            self.stop()

        self.play_anim("jump_in_out")

    def handle_input(self):
        super().handle_input()
        if self.p.gamepad.is_button_pressed('A') and self.p.gamepad.is_button_down('DOWN'):
            self.p.attack_force = self.p.ATTACK_FORCE_PUNCH_1
            self.play_anim("dive_attack")
        elif self.p.gamepad.is_button_pressed('A'):
            if self.long_jump:
                self.p.attack_force = self.p.ATTACK_FORCE_PUNCH_1
                self.play_anim("leap_attack")
            else:
                self.p.attack_force = self.p.ATTACK_FORCE_PUNCH_1
                self.play_anim("jump_attack")

        return self

    def update(self, game_speed):
        super().update(game_speed)
        self.jump_offset += self.p.JUMP_SPEED * game_speed
        new_z = math.sin(math.pi * self.jump_offset) * self.p.JUMP_HEIGHT

        if self.action == self.ACTION_PREPARE_TO_JUMP:
            if new_z > self.TERRAIN_TRESHOLD:
                self.action = self.ACTION_JUMP
                if self.long_jump:
                    self.play_anim("leap")
                else:
                    self.play_anim("jump")
        elif self.action == self.ACTION_JUMP:
            self.p._z = new_z
            if new_z < self.TERRAIN_TRESHOLD:
                self.p._z = 0
                self.action = self.ACTION_PREPARE_TO_STAND
                self.play_anim("jump_in_out")
        elif self.action == self.ACTION_PREPARE_TO_STAND:
            if new_z <= 0:
                return self.p.STATE_STAND
            pass

        return self


class PlayerStateFall(PlayerState):
    TERRAIN_TRESHOLD = 6

    def __init__(self, player):
        super().__init__(player)
        self.fall_offset = 0
        self.initial_z = 0

    def enter(self, old_state):
        super().enter(old_state)

        self.initial_z = self.p._z
        self.fall_offset = 0

        # TODO: if Z is 0 then it should be set to a higher value. Otherwise falling from Stand doesn't look good
        # TODO: fall direction should be defined by the direction of the hit
        self.fall_direction = -self.p.direction
        self.p.move_v.x = self.p.JUMP_SPEED_H * self.fall_direction
        self.play_anim("fall")

    def handle_input(self):
        return self

    def update(self, game_speed):
        super().update(game_speed)

        self.fall_offset += self.p.JUMP_SPEED * game_speed
        new_z = math.cos(math.pi * self.fall_offset) * self.initial_z

        if new_z <= self.TERRAIN_TRESHOLD:
            return self.p.STATE_GROUND

        self.p._z = new_z

        return self

import pygame
from lib.frames_store import FramesStore


class Sprite:
    DEBUG = False

    def __init__(self, sprite_bank):
        self.sprite_bank = sprite_bank
        self.x = self.y = 0
        self.flags = 0
        self.frame = None

        self.attack_box = None
        self.hit_box = None

        self.animation = None
        self.animation_name = None
        self.animation_frame_index = None
        self.animation_frame_delay = 0
        self.animating = False

    def draw(self, surface, window_x=0, window_y=0):
        if self.frame is None:
            return

        flags = self.flags
        animation_frame = self.animation.frames[self.animation_frame_index]

        # Override animation flip if the frame is also flipped
        if animation_frame.flip_x:
            flags |= FramesStore.FLAG_FLIP_X
        if animation_frame.flip_y:
            flags |= FramesStore.FLAG_FLIP_Y

        dest_x = self.x - window_x
        dest_y = self.y - window_y
        # # Add animation frame offset
        # if animation_frame.offset.x != 0:
        #     dest_x += animation_frame.offset.x
        # if animation_frame.offset.y != 0:
        #     dest_x += animation_frame.offset.y

        self.sprite_bank.draw_frame(surface, self.frame, dest_x, dest_y, flags)

        # DEBUG boxes
        if Sprite.DEBUG:
            # anchor_x = self.frame.rect['x'] + self.frame.anchor['x'] - window_x
            # anchor_y = self.frame.rect['y'] + self.frame.anchor['y'] - window_y
            # pygame.draw.rect(surface, (255, 255, 255), pygame.Rect(anchor_x, anchor_y, 1, 1), 1)

            if self.hit_box and self.hit_box.w > 0 and self.hit_box.h > 0:
                pygame.draw.rect(surface, (0, 200, 0), self.hit_box.move(-window_x, -window_y), 1)
            if self.attack_box and self.attack_box.w > 0 and self.attack_box.h > 0:
                pygame.draw.rect(surface, (200, 0, 0), self.attack_box.move(-window_x, -window_y), 1)

    def set_frame(self, frame_name):
        self.stop_animation()
        self.animation = None
        self.frame = self.sprite_bank.get_frame(frame_name)

    def stop_animation(self):
        self.animation_frame_delay = 0
        self.animation_frame_index = 0
        self.animating = False

    def play_animation(self, animation_name, flags=0):
        if (self.flags & FramesStore.FLAG_LOOP_ANIMATION) > 0 and \
                        self.flags == flags and animation_name == self.animation_name:
            return

        self.animating = True
        self.animation_name = animation_name
        self.flags = flags
        self._set_animation_frame(0)

    def skip_to_last_animation_frame(self):
        if not self.animating:
            return

        self.animating = False
        self._set_animation_frame(len(self.animation.frames) - 1)

    def update(self, game_speed):
        self._update_collision_boxes()
        if not self.animating:
            return

        if self.animation_frame_delay <= 0:
            self.next_animation_frame()
            return
        else:
            self.animation_frame_delay -= game_speed
            return

    def next_animation_frame(self):
        new_animation_frame_index = self.animation_frame_index + 1
        if new_animation_frame_index > len(self.animation.frames) - 1:
            if not (self.flags & FramesStore.FLAG_LOOP_ANIMATION) > 0:
                self.animating = False
                # TODO Notify animation ended
                return
            else:
                new_animation_frame_index = 0

        # TODO: notify frame changed
        self._set_animation_frame(new_animation_frame_index)

    def previous_animation_frame(self):
        new_animation_frame_index = self.animation_frame_index - 1
        if new_animation_frame_index < 0:
            new_animation_frame_index = len(self.animation.frames) - 1

        self._set_animation_frame(new_animation_frame_index)

    def _set_animation_frame(self, frame_index):
        self.animation = self.sprite_bank.get_animation(self.animation_name)
        self.animation_frame_index = frame_index
        new_frame = self.animation.frames[frame_index]
        self.animation_frame_delay = new_frame.delay
        self.frame = self.sprite_bank.get_frame(new_frame.frame_name)

    def _update_collision_boxes(self):
        # NOTE: this crashes when there is no animation running
        # TODO: flip_y should be handled as well
        animation_frame = self.animation.frames[self.animation_frame_index]
        flip_x = ((self.flags & FramesStore.FLAG_FLIP_X) > 0) ^ animation_frame.flip_x

        if self.frame.hit_box:
            self.hit_box = self.frame.hit_box.copy()
            if flip_x:
                self.hit_box.left = - self.hit_box.left - self.hit_box.width
            self.hit_box.move_ip(self.x, self.y)
        else:
            self.hit_box = None

        if self.frame.attack_box:
            self.attack_box = self.frame.attack_box.copy()
            if flip_x:
                self.attack_box.left = - self.attack_box.left - self.attack_box.width
            self.attack_box.move_ip(self.x, self.y)
        else:
            self.attack_box = None

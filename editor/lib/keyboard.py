from lib.controller import Controller
import pygame


class Keyboard(Controller):
    RS_UP = 'RS_UP'
    RS_DOWN = 'RS_DOWN'
    RS_LEFT = 'RS_LEFT'
    RS_RIGHT = 'RS_RIGHT'

    def __init__(self):
        self._button_down = {}
        self._button_pressed = {}
        self._keys = list(KEYS_MAPPING.keys())
        for btn_name in self._keys:
            self._button_down[btn_name] = False
            self._button_pressed[btn_name] = False

    def update(self):
        for btn_name in self._keys:
            self._button_pressed[btn_name] = False

        pressed = pygame.key.get_pressed()
        for btn_name in self._keys:
            is_down = pressed[KEYS_MAPPING[btn_name]]
            if is_down and not self._button_down[btn_name]:
                self._button_pressed[btn_name] = True

            self._button_down[btn_name] = is_down

        return

    def is_button_down(self, button_name):
        if button_name in self._keys:
            return self._button_down[button_name]
        return False

    def is_button_pressed(self, button_name):
        if button_name in self._keys:
            return self._button_pressed[button_name]
        return False

    def get_axis(self, axis_name):
        if axis_name == Controller.RS_H:
            # Horizontal
            if self.is_button_down(Keyboard.RS_LEFT):
                return -1
            elif self.is_button_down(Keyboard.RS_RIGHT):
                return 1
        elif axis_name == Controller.RS_V:
            # Vertical
            if self.is_button_down(Keyboard.RS_UP):
                return -1
            elif self.is_button_down(Keyboard.RS_DOWN):
                return 1
        elif axis_name == Controller.LS_H:
            # Horizontal
            if self.is_button_down(Controller.K_LEFT):
                return -1
            elif self.is_button_down(Controller.K_RIGHT):
                return 1
        elif axis_name == Controller.LS_V:
            # Vertical
            if self.is_button_down(Controller.K_UP):
                return -1
            elif self.is_button_down(Controller.K_DOWN):
                return 1
        return 0

    def get_axis_digital_value(self, axis_name):
        return self.get_axis(axis_name)


KEYS_MAPPING = {
    Controller.K_UP: pygame.K_w,
    Controller.K_DOWN: pygame.K_s,
    Controller.K_LEFT: pygame.K_a,
    Controller.K_RIGHT: pygame.K_d,
    Controller.K_A: pygame.K_DOWN,
    Controller.K_B: pygame.K_RIGHT,
    Controller.K_X: pygame.K_LEFT,
    Controller.K_Y: pygame.K_UP,
    Controller.K_START: pygame.K_RETURN,
    Controller.K_BACK: pygame.K_BACKSPACE,
    Controller.K_GUIDE: pygame.K_SPACE,
    Keyboard.RS_UP: pygame.K_i,
    Keyboard.RS_DOWN: pygame.K_k,
    Keyboard.RS_LEFT: pygame.K_j,
    Keyboard.RS_RIGHT: pygame.K_l
}

import abc


class Controller:
    __metaclass__ = abc.ABCMeta
    K_UP = 'UP'
    K_DOWN = 'DOWN'
    K_LEFT = 'LEFT'
    K_RIGHT = 'RIGHT'
    K_A = 'A'
    K_B = 'B'
    K_X = 'X'
    K_Y = 'Y'
    K_START = 'START'
    K_BACK = 'BACK'
    K_GUIDE = 'GUIDE'
    RS_H = 'RS_H'
    RS_V = 'RS_V'
    LS_H = 'LS_H'
    LS_V = 'LS_V'

    @abc.abstractmethod
    def update(self):
        return

    @abc.abstractmethod
    def is_button_down(self, button_name):
        return

    @abc.abstractmethod
    def is_button_pressed(self, button_name):
        return

    @abc.abstractmethod
    def get_axis(self, axis_name):
        return

    @abc.abstractmethod
    def get_axis_digital_value(self, axis_name):
        return

import re
from lib.controller import Controller


class GamePad(Controller):
    _DEBUG_CONTROLLER = False

    def __init__(self, joystick):
        self._mapping = None
        self._enabled = False
        self.joystick = joystick
        self._button_down = {}
        self._button_pressed = {}
        if joystick:
            self._init_device()

    def _init_device(self):
        self.joystick.init()
        joystick_name = self.joystick.get_name()

        for device in DEVICE_MAPPINGS:
            if re.match(device['name_regex'], joystick_name, re.IGNORECASE):
                self._mapping = device
                # print('Joystick \'%s\' found.' % device['name'])
                break

        if not self._mapping:
            print('Joystick \'%s\' not recognized!' % joystick_name)
            return

        for (btn_name, btn_id) in self._mapping['buttons'].items():
            self._button_down[btn_name] = False
            self._button_pressed[btn_name] = False

        self._enabled = True

    def update(self):
        if not self._enabled:
            return

        if self._DEBUG_CONTROLLER:
            for i in range(0, self.joystick.get_numbuttons()):
                if self.joystick.get_button(i):
                    print("Joystick %i => button: %i" % (self.joystick.get_id(), i))

                    # axes = {}
                    # for i in range(0, self.joystick.get_numaxes()):
                    #     axes[i] = self.joystick.get_axis(i)
                    # print("Joystick %i => axes: ")
                    # print(axes)

        for (btn_name, btn_id) in self._mapping['buttons'].items():
            self._button_pressed[btn_name] = False

        for (btn_name, btn_id) in self._mapping['buttons'].items():
            is_down = self.joystick.get_button(btn_id)
            if is_down and not self._button_down[btn_name]:
                self._button_pressed[btn_name] = True

            self._button_down[btn_name] = is_down

    def is_button_down(self, button_name):
        if not self._enabled:
            return False
        return self._button_down[button_name]

    def is_button_pressed(self, button_name):
        if not self._enabled:
            return False
        return self._button_pressed[button_name]

    def get_axis(self, axis_name):
        if not self._enabled:
            return 0
        return self.joystick.get_axis(self._mapping['axis'][axis_name])

    def get_axis_digital_value(self, axis_name):
        if not self._enabled:
            return 0
        value = self.joystick.get_axis(self._mapping['axis'][axis_name])
        if value > self._mapping['axis_threshold']:
            return 1
        elif value < -self._mapping['axis_threshold']:
            return -1
        return 0


DEVICE_MAPPINGS = [
    {
        'name': 'XBox 360',
        'name_regex': '[ ]*xbox[ ]*360.*',
        'buttons': {
            Controller.K_UP: 0,
            Controller.K_DOWN: 1,
            Controller.K_LEFT: 2,
            Controller.K_RIGHT: 3,
            Controller.K_START: 4,
            Controller.K_BACK: 5,
            'LS': 6,  # Left stick pressed
            'RS': 7,  # Right stick pressed
            'LB': 8,
            'RB': 9,
            Controller.K_GUIDE: 10,
            Controller.K_A: 11,
            Controller.K_B: 12,
            Controller.K_X: 13,
            Controller.K_Y: 14,
        },
        'axis': {
            Controller.LS_H: 0,  # Left stick H axis
            Controller.LS_V: 1,  # Left stick V axis
            Controller.RS_H: 2,  # Right stick H axis
            Controller.RS_V: 3,  # Right stick V axis
            'LT': 4,  # Left trigger
            'RT': 5,  # Right trigger
        },
        'axis_threshold': 0.8,
    }
]

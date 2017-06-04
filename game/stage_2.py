from game.stage import Stage
from lib.tmx_map import TMXMap
from lib.utils import Utils


class Stage2(Stage):
    def __init__(self):
        super().__init__()
        self.map = TMXMap('resources/stages/stage_2/stage_2.tmx')
        tonno = 0
        # self.train_w = 2544
        # self.train_x = -self.train_w - 10000
        # self.train_y = 0
        # self.train_accumulator = 0

    def get_width(self):
        return self.map.tmx_data.width

    def update(self, game_speed):
        # self.train_accumulator += game_speed
        # self.train_x += 40 * game_speed
        # if self.train_x > self.get_width():
        #     self.train_x = - self.train_w - 8000
        #
        # if self.train_accumulator > 1:
        #     self.train_y = Utils.random.randint(-1, 1)
        #     self.train_accumulator = 0
        pass

    def draw_background(self, surface, window_x, window_y):
        self.map.draw()
        # self.map.layer_offsets[0].x = window_x/3
        # self.map.layer_offsets[1].x = -self.train_x
        # self.map.layer_offsets[1].y = self.train_y
        # self.map.layer_offsets[2].x = window_x/2
        # self.map.layer_offsets[3].x = window_x
        # self.map.layer_offsets[4].x = window_x
        # self.map.draw_layers_range(0, 4)
        pass

    def draw_foreground(self, surface, window_x, window_y):
        # self.map.draw_layers_range(4, 1)
        pass

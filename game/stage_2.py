from game.stage import Stage
from lib.pyglet.gfx import Gfx


class Stage2(Stage):
    def __init__(self):
        super().__init__()

        self.img_bg = Gfx.load_image('resources/images/stage_2/bg.jpg')

    def get_width(self):
        return self.img_bg.width * 3

    def update(self, game_speed):
        pass
        # self.train_accumulator += game_speed
        # self.train_x += 40 * game_speed
        # if self.train_x > self.get_width():
        #     self.train_x = - self.img_train.get_width() - 8000
        #
        # if self.train_accumulator > 1:
        #     self.train_y = Utils.random.randint(-1, 1)
        #     self.train_accumulator = 0

    def draw_background(self, surface, window_x, window_y):
        Gfx.draw_image_at(surface, self.img_bg, -window_x / 3, 14)

        # for i in range(0, 14):
        #     x = -window_x / 2 + i * 220
        #     Gfx.draw_image_at(surface, self.img_pillar, x, 14)
        #
        # Gfx.draw_image_at(surface, self.img_train, self.train_x - window_x, 48 + self.train_y)
        #
        # for i in range(0, 5):
        #     x = -window_x - self.img_fg_bottom.get_width()
        #     x = divmod(x, self.img_fg_bottom.get_width())[1]
        #     Gfx.draw_image_at(surface, self.img_fg_bottom, x + (i - 1) * self.img_fg_bottom.get_width(), 195)
        #
        # if window_x < self.img_fg_left.get_width():
        #     Gfx.draw_image_at(surface, self.img_fg_left, -window_x, 14)

    def draw_foreground(self, surface, window_x, window_y):
        return
        # super().draw_foreground(surface, window_x, window_y)
        # Gfx.draw_image_at(surface, self.img_grid, 450-window_x * 1.2, 270-self.img_grid.get_height())

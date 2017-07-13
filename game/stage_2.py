from mgl2d.graphics.tmx_map import TMXMap
from mgl2d.math.rect import Rect
from mgl2d.math.vector2 import Vector2
from game.stage import Stage


class Vector2d(object):
    pass


class Stage2(Stage):
    def __init__(self):
        super().__init__()
        self.map = TMXMap('resources/stages/stage_2/stage_2.tmx')
        self.entities = self.map.all_objects_as_dict('entities')
        self._load_floor_data()

    def _load_floor_data(self):
        floor = self.map.all_objects_as_list('floor')
        for f in floor:
            rect = Rect(f.x, f.y, f.width, f.height)
            self.floor_rects.append(rect)

    def entity_pos(self, entity_name):
        e = self.entities[entity_name]
        return Vector2(e.x, e.y)

    def get_width(self):
        return self.map._tmx_data.width

    def update(self, game_speed):
        pass

    def draw_background(self, screen, window_x, window_y):
        self.map.draw(screen)

    def draw_foreground(self, screen, window_x, window_y):
        pass

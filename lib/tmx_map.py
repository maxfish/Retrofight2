import pytmx
import pytmx.util_pyglet

from lib.pyglet.gfx import Gfx
from lib.vector2d import Vector2d


class TMXMap(object):
    def __init__(self, filename):
        tm = pytmx.util_pyglet.load_pyglet(filename)
        self.size = tm.width * tm.tilewidth, tm.height * tm.tileheight
        self.tmx_data = tm
        self.layer_offsets = [Vector2d(0, 0) for _ in range(0, len(self.tmx_data.layers))]

    @property
    def width_in_pixels(self):
        return self.size[0]

    @property
    def height_in_pixels(self):
        return self.size[0]

    def draw(self):
        self.draw_layers_range(0, len(self.tmx_data.layers))

    def draw_layers_range(self, start, how_many):
        for index in range(start, start + how_many):
            layer = self.tmx_data.layers[index]
            offset_x = layer.offsetx + self.layer_offsets[index].x
            offset_y = layer.offsety + self.layer_offsets[index].y

            if isinstance(layer, pytmx.TiledTileLayer):
                # for x, y, image in layer.tiles():
                pass
            elif isinstance(layer, pytmx.TiledObjectGroup):
                for obj in layer:
                    if hasattr(obj, 'points'):
                        # draw_lines(poly_color, obj.closed, obj.points, 3)
                        pass
                    elif obj.image:
                        obj.image.blit(obj.x - offset_x, Gfx.screen_height - obj.y - obj.height - offset_y)
                    else:
                        # draw_rect(rect_color, (obj.x, obj.y, obj.width, obj.height), 3)
                        pass
            elif isinstance(layer, pytmx.TiledImageLayer):
                if layer.image:
                    pass

    def set_layer_offset(self, layer_index, x, y):
        self.layer_offsets[layer_index].x = x
        self.layer_offsets[layer_index].y = y

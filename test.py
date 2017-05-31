import logging

logger = logging.getLogger(__name__)
ch = logging.StreamHandler()
ch.setLevel(logging.INFO)
logger.addHandler(ch)
logger.setLevel(logging.INFO)

from pytmx import *
from pytmx.util_pyglet import load_pyglet
import pyglet
from pyglet import gl


class TiledRenderer(object):
    """
    Super simple way to render a tiled map with pyglet

    no shape drawing yet
    """

    def __init__(self, filename):
        tm = load_pyglet(filename)
        self.size = tm.width * tm.tilewidth, tm.height * tm.tileheight
        self.tmx_data = tm
        self.batches = []  # list of batches, e.g. layers
        self.sprites = []  # container for tiles
        self.generate_sprites()
        self.clock_display = pyglet.clock.ClockDisplay()

    def draw_rect(self, color, rect, width):
        pass

    def draw_lines(self, color, closed, points, width):
        pass

    def generate_sprites(self):
        tw = self.tmx_data.tilewidth
        th = self.tmx_data.tileheight
        mw = self.tmx_data.width
        mh = self.tmx_data.height - 1
        pixel_height = (mh + 1) * th
        draw_rect = self.draw_rect
        draw_lines = self.draw_lines

        rect_color = (255, 0, 0)
        poly_color = (0, 255, 0)

        for layer in self.tmx_data.visible_layers:
            # batch = pyglet.graphics.Batch()  # create a new batch
            # self.batches.append(batch)  # add the batch to the list
            # draw map tile layers
            if isinstance(layer, TiledTileLayer):

                # iterate over the tiles in the layer
                for x, y, image in layer.tiles():
                    y = mh - y
                    x = x * tw
                    y = y * th
                    # TODO

            # draw object layers
            elif isinstance(layer, TiledObjectGroup):

                # iterate over all the objects in the layer
                for obj in layer:
                    logger.info(obj)

                    # objects with points are polygons or lines
                    if hasattr(obj, 'points'):
                        draw_lines(poly_color, obj.closed, obj.points, 3)

                    # some object have an image
                    elif obj.image:
                        # obj.image.blit(0,0)
                        if obj.x >= 0 and obj.x < 600 and obj.y >=-0 and obj.y< 600:
                            obj.image.blit(obj.x, 600 - obj.y - obj.height)

                    # draw a rect for everything else
                    else:
                        draw_rect(rect_color,
                                  (obj.x, obj.y, obj.width, obj.height), 3)

            # draw image layers
            elif isinstance(layer, TiledImageLayer):
                if layer.image:
                    x = mw // 2  # centers image
                    y = mh // 2
                    # TODO

    def draw(self):
        self.generate_sprites()
        self.clock_display.draw()


class SimpleTest(object):
    def __init__(self, filename):
        self.renderer = None
        self.running = False
        self.dirty = False
        self.exit_status = 0
        self.load_map(filename)

    def load_map(self, filename):
        self.renderer = TiledRenderer(filename)

        logger.info("Objects in map:")
        for obj in self.renderer.tmx_data.objects:
            logger.info(obj)
            for k, v in obj.properties.items():
                logger.info("%s\t%s", k, v)

        logger.info("GID (tile) properties:")
        for k, v in self.renderer.tmx_data.tile_properties.items():
            logger.info("%s\t%s", k, v)

    def draw(self):
        self.renderer.draw()


class TestWindow(pyglet.window.Window):
    contents = None

    def on_draw(self):
        self.clear()
        if self.contents:
            self.contents.draw()

    def on_key_press(self, symbol, mod):
        if symbol == pyglet.window.key.ESCAPE:
            pyglet.app.exit()


if __name__ == '__main__':
    contents = SimpleTest('resources/stages/stage_1/stage_1.tmx')

    window = TestWindow(600, 600, vsync=False)
    window.contents = contents
    gl.glEnable(gl.GL_BLEND)
    gl.glBlendFunc(gl.GL_SRC_ALPHA, gl.GL_ONE_MINUS_SRC_ALPHA)

    # Add schedule_interval with a dummy callable to force speeding up fps
    pyglet.clock.schedule_interval(int, 1. / 240)
    pyglet.app.run()

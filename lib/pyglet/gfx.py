import pyglet
from pyglet.gl import *

from lib.pyglet.image import Image
from pyglet.image.codecs.png import PNGImageDecoder


class Gfx:
    _fonts = {}
    screen_width = 0
    screen_height = 0

    @staticmethod
    def initialize():
        # set orthographic projection (2D only)
        # glMatrixMode(gl.GL_PROJECTION)
        # glLoadIdentity()
        # glOrtho(0, Gfx.screen_width, 0, Gfx.screen_height, -1, 1)
        # glMatrixMode(GL_MODELVIEW)

        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        glEnable(GL_TEXTURE_2D)
        glShadeModel(GL_SMOOTH)
        glClearColor(0, 0, 0, 0)
        glClearDepth(1.0)
        glEnable(GL_DEPTH_TEST)
        glDepthFunc(GL_LEQUAL)
        glHint(GL_PERSPECTIVE_CORRECTION_HINT, GL_NICEST)

    @staticmethod
    def load_image(file_name):
        # print("[Gfx] Loading image '%s'" % file_name)
        new_image = Image()
        new_image.pyglet_image = pyglet.image.load(file_name)
        # new_image.pyglet_image = pyglet.image.load(file_name, decoder=PNGImageDecoder())
        new_image.texture = new_image.pyglet_image.get_texture()
        return new_image

    @staticmethod
    def text_rect(text, size):
        return 0
        # if size not in Gfx._fonts:
        #     Gfx._fonts[size] = pygame.font.Font(None, size)
        # font = Gfx._fonts[size]
        # text_ = font.render(text, 0, (255, 255, 255), (0, 0, 0))
        # return text_.get_rect(x=0, y=0)

    @staticmethod
    def render_text(surface, text, x, y, size=18, color=(255, 255, 255), bg_color=(20, 20, 20), antialias=1):
        pass
        # if size not in Gfx._fonts:
        #     Gfx._fonts[size] = pyglet.font.load('Arial', size, bold=False, italic=False)
        #
        # font = Gfx._fonts[size]
        # text = 'Hello, world!'
        # glyphs = font.get_glyphs(text)
        # glyph_string = pyglet.font.GlyphString(text, glyphs)
        # glyph_string.draw()

        # text = Text(font, text)
        # text.draw()
        return
        # if size not in Gfx._fonts:
        #     Gfx._fonts[size] = pygame.font.Font(None, size)
        # font = Gfx._fonts[size]
        # text_ = font.render(text, antialias, color, bg_color)
        # surface.blit(text_, (x, y))

    @staticmethod
    def render_centered_text(surface, text, center_x, center_y, size=18, color=(255, 255, 255), bg_color=(20, 20, 20)):
        pass
        # if size not in Gfx._fonts:
        #     Gfx._fonts[size] = pyglet.font.load('Arial', size, bold=False, italic=False)
        #
        # font = Gfx._fonts[size]
        # text = 'Hello, world!'
        # glyphs = font.get_glyphs(text)
        # glyph_string = pyglet.font.GlyphString(text, glyphs)
        # glyph_string.draw()

        # if size not in Gfx._fonts:
        #     Gfx._fonts[size] = pygame.font.Font(None, size)
        # font = Gfx._fonts[size]
        # text_ = font.render(text, 1, color, bg_color)
        # text_position = text_.get_rect(centerx=center_x, centery=center_y)
        # surface.blit(text_, text_position)

    @staticmethod
    def draw_image_at(surface, image, x, y):
        image.pyglet_image.blit(x, Gfx.screen_height - y - image.height, 0,
                                image.width,
                                image.height)

    @staticmethod
    def draw_anchored_image_at(source_image, source_rect, dest_x, dest_y, anchor_x, anchor_y, flip_x=False,
                               flip_y=False, scale=1, angle=0):
        texture = source_image.texture
        source_image = source_image.pyglet_image
        # picW = texture.tex_coords
        # picH = texture.owner.height

        t_x1 = 0  # source_rect.x / picW
        t_y1 = 0  # source_rect.y / picH
        t_x2 = texture.tex_coords[3]  # t_x1 + (source_rect.width) / picW
        t_y2 = texture.tex_coords[7]  # t_y1 + (source_rect.height) / picH
        # < class 'tuple'>: (0.0, 0.0, 0.0, 0.9375, 0.0, 0.0, 0.9375, 0.875, 0.0, 0.0, 0.875, 0.0)
        s_w = source_rect.width * scale
        s_h = source_rect.height * scale

        hotx = anchor_x * scale
        hoty = anchor_y * scale

        if flip_x:
            # tmp = t_x1
            # t_x1 = t_x2
            # t_x2 = tmp
            hotx = s_w - hotx
            # s_w = -s_w

        if flip_y:
            tmp = t_y1
            t_y1 = t_y2
            t_y2 = tmp
            hoty = s_h - hoty

        z = 0
        colorR = 1
        colorG = 1
        colorB = 1
        alphaValue = 1

        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
        glTranslatef(dest_x, Gfx.screen_height - dest_y - s_h, 0)
        glRotatef(angle, 0, 0, 1)
        glScalef(-1 if flip_x else 1, -1 if flip_y else 1, 1)
        glTranslatef(-hotx, hoty, 0)
        glScalef(s_w, s_h, 1)

        glColor4f(colorR, colorG, colorB, alphaValue)
        glBindTexture(texture.target, texture.id)
        glBegin(GL_QUADS)
        glTexCoord2f(t_x1, t_y1)
        glVertex3f(0, 0, z)
        glTexCoord2f(t_x2, t_y1)
        glVertex3f(1, 0, z)
        glTexCoord2f(t_x2, t_y2)
        glVertex3f(1, 1, z)
        glTexCoord2f(t_x1, t_y2)
        glVertex3f(0, 1, z)
        glEnd()

        glColor4f(1, 1, 1, 1)
        glLoadIdentity()

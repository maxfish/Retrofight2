import pygame


class Gfx:
    _fonts = {}

    @staticmethod
    def load_image(file_name, alpha=1):
        if alpha == 1:
            return pygame.image.load(file_name).convert_alpha()
        else:
            return pygame.image.load(file_name).convert()

    @staticmethod
    def text_rect(text, size):
        if size not in Gfx._fonts:
            Gfx._fonts[size] = pygame.font.Font(None, size)
        font = Gfx._fonts[size]
        text_ = font.render(text, 0, (255, 255, 255), (0, 0, 0))
        return text_.get_rect(x=0, y=0)

    @staticmethod
    def render_text(surface, text, x, y, size=18, color=(255, 255, 255), bg_color=(20, 20, 20), antialias=1):
        if size not in Gfx._fonts:
            Gfx._fonts[size] = pygame.font.Font(None, size)
        font = Gfx._fonts[size]
        text_ = font.render(text, antialias, color, bg_color)
        surface.blit(text_, (x, y))

    @staticmethod
    def render_centered_text(surface, text, center_x, center_y, size=18, color=(255, 255, 255), bg_color=(20, 20, 20)):
        if size not in Gfx._fonts:
            Gfx._fonts[size] = pygame.font.Font(None, size)
        font = Gfx._fonts[size]
        text_ = font.render(text, 1, color, bg_color)
        text_position = text_.get_rect(centerx=center_x, centery=center_y)
        surface.blit(text_, text_position)

    @staticmethod
    def draw_image_at(surface, image, x, y):
        surface.blit(
            image,
            (x, y, image.get_width(), image.get_height()),
            (0, 0, image.get_width(), image.get_height()),
        )

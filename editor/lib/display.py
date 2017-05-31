import pygame


class Display:
    def __init__(self, surface_width, surface_height, screen_scale=1, full_screen=False, scan_lines_color=None):
        super().__init__()
        self._surface_width = surface_width
        self._surface_height = surface_height
        self._screen_scale = screen_scale
        self._full_screen = full_screen
        self._scan_lines_color = scan_lines_color

        self._screen_args = 0
        self._screen_width = self._surface_width * self._screen_scale
        self._screen_height = self._surface_height * self._screen_scale

        self._screen = None
        self._back_buffer = None
        self._scan_line = None

    def setup(self):
        if self._full_screen:
            self._screen_args = pygame.FULLSCREEN | pygame.HWACCEL

        self._screen = pygame.display.set_mode((self._screen_width, self._screen_height), self._screen_args)
        self._back_buffer = pygame.Surface((self._surface_width, self._surface_height)).convert(self._screen)

        if self._scan_lines_color:
            self._scan_line = pygame.Surface((self._screen_width, 1), pygame.SRCALPHA)
            self._scan_line.fill(self._scan_lines_color)

    def flip(self):
        # TODO: if scale == 1 then remove the transform
        if self._screen_scale > 1:
            pygame.transform.scale(self._back_buffer, (self._screen_width, self._screen_height), self._screen)
        else:
            self._screen.blit(self._back_buffer, (0,0))

        # if self._scan_line:
            # NOTE: without hardware acceleration there are no better ways
            # for y in range(0, self._surface_height):
            #     self._screen.blit(self._scan_line, (0, y * self._screen_scale))

        pygame.display.flip()

    @property
    def back_buffer(self):
        return self._back_buffer

    @property
    def full_screen(self):
        return self._full_screen

    @property
    def surface_width(self):
        return self._surface_width

    @property
    def surface_height(self):
        return self._surface_height

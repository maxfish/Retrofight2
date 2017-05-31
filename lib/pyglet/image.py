class Image:
    __slots__ = ('pyglet_image', 'texture')

    def __init__(self):
        self.pyglet_image = None
        self.texture = None

    @property
    def width(self):
        return self.pyglet_image.width

    @property
    def height(self):
        return self.pyglet_image.height

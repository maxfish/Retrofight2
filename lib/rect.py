class Rect(object):
    __slots__ = ('x', 'y', 'w', 'h')

    def __init__(self, x=0.0, y=0.0, w=0.0, h=0.0):
        self.x = x
        self.y = y
        self.w = w
        self.h = h

    def move_ip(self, amount_x, amount_y):
        self.x += amount_x
        self.y += amount_y

    def move(self, amount_x, amount_y):
        return Rect(self.x + amount_x, self.y + amount_y, self.w, self.h)

    def collide_with_rect(self, rect):
        return not (self.left > rect.right
                    or self.right < rect.left
                    or self.top > rect.bottom
                    or self.bottom < rect.top)

    def to_dictionary(self):
        return {
            'x': self.x,
            'y': self.y,
            'width': self.w,
            'height': self.h
        }

    def copy(self):
        return Rect(self.x, self.y, self.w, self.h)

    @property
    def top(self): return self.y

    @property
    def bottom(self): return self.y + self.h

    @property
    def left(self): return self.x

    @property
    def right(self): return self.x + self.w

    @property
    def width(self): return self.w

    @property
    def height(self): return self.h

    @property
    def center_x(self): return self.x + self.w / 2

    @property
    def center_y(self): return self.y + self.h / 2

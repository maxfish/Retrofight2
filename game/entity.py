from lib.sprite import Sprite
from lib.vector2d import Vector2d


class Entity:
    def __init__(self, world, frames_store, x, y, z=0):
        self._world = world
        self._sprite = Sprite(frames_store)
        self._position = Vector2d(x, y)
        self._z = z
        self.should_be_removed = False

    @property
    def position(self):
        return self._position

    @property
    def sprite(self):
        return self._sprite

    def draw(self, surface):
        self._sprite.draw(surface, self._world.window_x, self._z + self._world.window_y)

    def handle_input(self):
        pass

    def update(self, game_speed):
        self._sprite.x = self._position.x
        self._sprite.y = self._position.y
        self._sprite.update(game_speed)

    class State:
        def __init__(self):
            pass

        def enter(self, old_state):
            return

        def leave(self, new_state):
            return

        def update(self, game_speed):
            return

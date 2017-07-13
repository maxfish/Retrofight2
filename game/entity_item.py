from game.entity import Entity


class EntityItem(Entity):
    def __init__(self, world, frames_store, animation, x, y):
        super().__init__(world, frames_store, x, y)
        self._sprite.play_animation(animation)

    def picked_up_by(self, character):
        self.should_be_removed = True
        type = self._sprite.animation.name
        if type == 'pizza':
            return {
                'energy': 20,
                'points': 100,
            }

        return None

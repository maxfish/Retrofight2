import pyglet


class ImageLoader:
    _images = {}
    _textures = {}

    def load_image(self, key, file_name):
        if key in self._images:
            return

        image = pyglet.resource.image(file_name)
        self._images[key] = image
        self._textures[key] = image.get_texture()

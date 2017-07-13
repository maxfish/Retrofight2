#!/usr/bin/env python
import pyglet
from pyglet.gl import *

from game.player import Player
from game.stage_1 import Stage1
from game.world import World
from mgl2d.pyglet.gamepad import GamePad
from mgl2d.pyglet.gfx import Gfx
from mgl2d.pyglet.shaders_manager import ShadersManager
from mgl2d.rect import Rect

pyglet.options['shadow_window'] = False

config = pyglet.gl.Config(double_buffer=True,
                          depth_size=24,
                          major_version=2,
                          minor_version=1,
                          forward_compatible=True
                          )
window = pyglet.window.Window(width=1920, height=1080, config=config)
# window.set_fullscreen(True)

# Print the version of the context created.
print('OpenGL version:', window.context.get_info().get_version())
print('OpenGL 2.1 support:', window.context.get_info().have_version(2, 1))

Gfx.screen_width = window.width
Gfx.screen_height = window.height
Gfx.initialize()
pyglet.gl.glClearColor(0, 0, 0, 0)
window.clear()

# shader = ShadersManager()
# shader.test()


# =================================

joysticks = GamePad.available_joysticks()
print("Joysticks available: %d" % len(joysticks))
gamepads = [GamePad(j) for j in joysticks]

# ================================

world = World(
    bounds=Rect(0, 200, 600, 400),
    stage=Stage1(),
)


def add_players(
        world,
        gamepads,
        sprites=(
                # sprite,  footprint, posx, posy
                ('max', Player.DEFAULT_FOOTPRINT_DIM, 130, 245),
                ('haggar', Rect(0, 0, 50, 12), 160, 230),
                ('guy', Player.DEFAULT_FOOTPRINT_DIM, 200, 260),
        ),
):
    for num, gamepad in enumerate(gamepads):
        sprite, footprint, posx, posy = sprites[num]
        world.add_player(
            Player(num, world, gamepad, sprite, posx, posy, footprint_dim=footprint),
        )


add_players(world, gamepads)


def update_frames(dt):
    for p in world.players:
        p.handle_input()
    world.update(1)


fps_display = pyglet.clock.ClockDisplay()


@window.event
def on_draw():
    pyglet.gl.glClearColor(0, 0, 0, 0)
    window.clear()
    world.draw(None)
    fps_display.draw()


pyglet.clock.set_fps_limit(60)
pyglet.clock.schedule(update_frames)
pyglet.app.run()
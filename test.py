#!/usr/bin/env python
import pyglet
from pyglet.gl import *
from pyglet.font import load as load_font
import pyglet.font

from game.player import Player
from game.stage_1 import Stage1
from game.stage_2 import Stage2
from game.world import World
from lib.pyglet.gamepad import GamePad
from lib.pyglet.gfx import Gfx
from lib.rect import Rect

pyglet.options['shadow_window'] = False

config = pyglet.gl.Config(double_buffer=True,
                          depth_size=24,
                          major_version=2,
                          minor_version=1,
                          forward_compatible=True
                          )
window = pyglet.window.Window(width=1280, height=720, config=config)
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

world = World(bounds=Rect(0, 200, 600, 400))
world.set_stage(Stage2())

def add_players(
        world,
        gamepads,
        sprites=(
                # sprite,  footprint, posx, posy
                ('max', Player.DEFAULT_FOOTPRINT_DIM),
                ('haggar', Rect(0, 0, 50, 12)),
                ('guy', Player.DEFAULT_FOOTPRINT_DIM),
        ),
):
    for num, gamepad in enumerate(gamepads):
        sprite, footprint = sprites[num]
        world.add_player(
            Player(num, world, gamepad, sprite, footprint_dim=footprint),
        )


add_players(world, gamepads)


def update_frames(dt):
    for p in world.players:
        p.handle_input()
    world.update(1)


fps_display = pyglet.clock.ClockDisplay()


# font = load_font('', 36, bold=True)
# label = pyglet.font.Text(font, '', color=(1,1,1,1), x=10, y=600)

@window.event
def on_draw():
    global label
    pyglet.gl.glClearColor(0, 0, 0, 0)
    window.clear()
    world.draw(None)
    fps_display.draw()
    # label.text = "TONNO"
    # label.draw()


pyglet.clock.set_fps_limit(60)
pyglet.clock.schedule(update_frames)
pyglet.app.run()

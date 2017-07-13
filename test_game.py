#!/usr/bin/env python
import logging

from mgl2d.app import App
from mgl2d.graphics.postprocessing_step import PostprocessingStep
from mgl2d.graphics.screen import Screen
from mgl2d.graphics.shader import Shader
from mgl2d.input.game_controller import GameController
from mgl2d.input.joystick import Joystick
from mgl2d.math.rect import Rect

from game.player import Player
from game.stage_2 import Stage2
from game.world import World

logging.basicConfig(level=logging.INFO)

app = App()
screen = Screen(1280, 720, 'Test')
screen.print_info()

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


GameController.load_database('resources/gamecontrollerdb.txt')
j = Joystick()
j.open(0)
add_players(world, [j])

ppe = PostprocessingStep(screen.width, screen.height)
ppe.drawable.shader = Shader.from_files('resources/shaders/base.vert', 'resources/shaders/postprocessing_retro.frag')
screen.add_postprocessing_step(ppe)


def draw_frame(screen):
    world.draw(screen)


def update_frame(millis):
    world.update(1)
    for p in world.players:
        p.handle_input()


app.run(screen, draw_frame, update_frame)

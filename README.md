INSTALL
=======

python3 -m venv <name-of-venv>

source <name-of-venv>/bin/activate

pip install -r requirements.txt

RUN
===

python test_game.py

XBOX 360 ON MAC
===============

https://github.com/360Controller/360Controller/releases

ANIMATION EDITOR
================

cd anim_editor

python3 -m venv <name-of-venv>

source <name-of-venv>/bin/activate

pip install -r requirements.txt

# Connect a Joystick (only XBOX360 for now!)

python anim_editor.py

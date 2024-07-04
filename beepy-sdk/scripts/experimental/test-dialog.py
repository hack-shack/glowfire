#!/usr/bin/python

# A fancy installer.
# (c) 2023 Asa Durkee. MIT License.

# Requires:
# sudo apt install -y tmux
# sudo pip install pythondialog libtmux
import os
import sys
import locale
import time


# tmux
# ------------------------------------------
import libtmux
server = libtmux.Server()
server
server.new_session(session_name='console',attach=True,window_name='console')
server.new_window(attach=True,window_name='console')
window = server.attached_window
pane = window.split_window()


# dialog
# ------------------------------------------
from dialog import Dialog

locale.setlocale(locale.LC_ALL, '')

d = Dialog(dialog="dialog")

button_names = {d.OK:     "OK",
                d.CANCEL: "Cancel",
                d.HELP:   "Help"}

code, tag = d.checklist("""\
The default settings below will build the full beepy SDK.\n\
Use UP/DOWN ARROWS to move to an option.\n\
Press SPACE to toggle an option on/off.\n\
Which packages should be built?""",
    choices=[("rp2040", "Build RP2040 firmware", False),
             ("directfb", "Build DirectFB", True),
             ("sdl2", "Build SDL2", True),
             ("pygame", "Build pygame", True),
             ("bluealsa", "Audio to Bluetooth headphones", True)],
    help_button=True)

if code == d.ESC:
    d.msgbox("You got out of the menu by pressing the Escape key.")
if code == d.HELP:
    d.msgbox("You clicked the HELP button.")
else:
    text = "You got out of the menu by choosing the {} button".format(
        button_names[code])

    if code != d.CANCEL:
        text += ", and the highlighted entry at that time had tag {!r}".format(
        tag)

    d.msgbox(text + ".", width=40, height=10)


os.system('clear')
sys.exit(0)
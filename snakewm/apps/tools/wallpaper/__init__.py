""" Sets wallpaper. """
import os
from pathlib import Path
import pygame
import pygame_gui
from pygame_gui.core import ObjectID
import i18n


def load(manager, params):
    """
    Launch a file dialog to change the desktop background.
    """

    # default position
    position = (0, 0)

    if params is not None and len(params) > 0:
        position = params[0]

    wm_dir = Path(os.path.dirname(os.path.abspath(__file__))).parents[2] # hopefully, snakewm folder
    wallpaper_dir = os.path.join(wm_dir,"data/wallpaper")

    i18n.load_path.append(os.path.join(os.path.dirname(__file__),"data/translations"))

    pygame_gui.windows.UIFileDialog(
        rect=pygame.Rect(position, (300, 180)),
        manager=manager,
        window_title=i18n.t("select_wallpaper_image"),
        allowed_suffixes=["gif","jpg","png"],
        initial_file_path=wallpaper_dir,
        allow_picking_directories=False,
        object_id=ObjectID(class_id="@wallpaper_filedialog",
                               object_id="#wallpaper_picker"
        )
    )
from .maze3dwindow import Maze3DWindow


def load(manager, params):
    pos = (0, 0)

    if params is not None and len(params) > 0:
        pos = params[0]

    Maze3DWindow(pos, manager)

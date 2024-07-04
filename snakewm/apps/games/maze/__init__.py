from .mazewindow import MazeWindow


def load(manager, params):
    position = (0, 0)

    if params is not None and len(params) > 0:
        position = params[0]

    MazeWindow(position, manager)

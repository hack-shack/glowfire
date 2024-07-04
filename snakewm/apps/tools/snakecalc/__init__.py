from .calc import SnakeCalc


def load(manager, params):
    """
    Create and launch a new instance of SnakeCalc.
    """
    # default position
    position = (0, 0)

    if params is not None and len(params) > 0:
        position = params[0]

    SnakeCalc(position, manager)

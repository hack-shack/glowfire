from .fps import SnakeFPS


def load(manager, params):
    """
    Create and launch a new instance of SnakeFPS.
    """
    # default position
    pos = (280,108)

    if params is not None and len(params) > 0:
        pos = params[0]

    SnakeFPS(pos, manager)

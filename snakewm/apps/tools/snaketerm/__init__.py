from .term import SnakeTerm


def load(manager, params):
    """
    Create and launch a new instance of snaketerm.
    """
    # default position
    pos = (0, 0)

    if params is not None and len(params) > 0:
        pos = params[0]

    SnakeTerm(pos, manager)
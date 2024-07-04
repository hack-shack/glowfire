from .dance import Dance


def load(manager, params):
    """
    Create and launch a new instance of Dance.
    """
    # default position
    pos = (0, 0)

    if params is not None and len(params) > 0:
        pos = params[0]

    Dance(pos, manager)

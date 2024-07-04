from .ditherbox import DitherBox


def load(manager, params):
    """
    Create and launch a new instance of DitherBox.
    """
    # default position
    position = (0, 0)

    if params is not None and len(params) > 0:
        position = params[0]

    DitherBox(position, manager)

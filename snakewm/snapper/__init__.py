from .snapper import Snapper


def load(manager, params):
    """
    Create and launch a new instance of snapper.
    """
    # default position
    pos = (200, 0)

    if params is not None and len(params) > 0:
        pos = params[0]

    Snapper(pos, manager)

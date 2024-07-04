from .minitime import MiniTime

def load(manager, params):
    """
    Create and launch a new instance of MiniTime.
    """
    # default position
    position = (261, 0)

    if params is not None and len(params) > 0:
        position = params[0]

    MiniTime(position, manager)

from .wildbeast import WildBeast

def load(manager, params):
    """
    Create and launch a new instance of WildBeast.
    """
    # default position
    position = (0, 0)

    if params is not None and len(params) > 0:
        position = params[0]

    WildBeast(position, manager)

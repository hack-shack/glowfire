from .castle import Castle

def load(manager, params):
    """
    Create Tower Defence game and add it to the UI manager.
    params[0] should be the desired position. A default
    position will be used if a position is not provided.
    """
    # default position
    position = (0, 0)

    if params is not None and len(params) > 0:
        position = params[0]

    Castle(position=position, manager=manager)
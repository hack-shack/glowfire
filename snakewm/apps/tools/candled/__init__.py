from .candled import CandLED


def load(manager, params):
    """
    Create and launch a new instance of CandLED.
    """
    # default position
    position = (0, 0)

    if params is not None and len(params) > 0:
        position = params[0]

    CandLED(position, manager)

from .voicebox import VoiceBox


def load(manager, params):
    """
    Create and launch a new instance of VoiceBox.
    """
    # default position
    pos = (0, 0)

    if params is not None and len(params) > 0:
        pos = params[0]

    VoiceBox(pos, manager)

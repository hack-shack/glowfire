from .base_app_state import BaseAppState


class QuitState(BaseAppState):
    def __init__(self, state_manager):
        super().__init__('quit', '', state_manager)

        self.time_to_quit_app = True

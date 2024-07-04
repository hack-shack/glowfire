import pygame
import pygame_gui

import datetime


class MiniTime(pygame_gui.elements.UIWindow):
    def __init__(self, position, manager):
        super().__init__(
            rect=pygame.Rect(position, (133, 80)),
            manager=manager,
            window_display_title="minitime",
            object_id="#minitime",
            resizable=False,
        )

        self.textbox = pygame_gui.elements.UITextBox(
            html_text="",
            relative_rect=pygame.Rect(0, 0, 107, 49),
            manager=manager,
            container=self,
            anchors={
                "left": "left",
                "right": "right",
                "top": "top",
                "bottom": "bottom",
            },
        )

    def process_event(self, event):
        super().process_event(event)

    def update(self, time_delta):
        super().update(time_delta)

        dt = datetime.datetime.now()
        current_time = dt.strftime("%H:%M:%S")
        current_date = dt.strftime("%Y-%m-%d")

        self.set_text("<font face='ProFont'><font pixel-size=20>" + current_time + "<p>" + current_date + "</font>")

    def set_text(self, text):
        self.textbox.html_text = text
        self.textbox.rebuild()

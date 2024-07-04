""" chrono: stopwatch with lap tracker """
import i18n
import os
import pygame
import pygame_gui
from pygame_gui.core import ObjectID

class Chrono(pygame_gui.elements.UIWindow):
    btn_height = 25  # button height
    def __init__(self, pos, manager):
        super().__init__(
            pygame.Rect(pos, (175, 226)),
            manager=manager,
            window_display_title="chrono",
            object_id="#chrono",
            resizable=False,
        )

        i18n.load_path.append(os.path.join(os.path.dirname(__file__),"data/translations"))

        self.currtime = pygame_gui.elements.UITextBox(
            "<font face='ProFont'><font pixel-size=14>0 : 0 : 0 : 0</font>",
            relative_rect=pygame.Rect(0, 0, 143, 30),
            container=self,
            manager=manager,
            object_id=ObjectID(class_id="@chrono_textbox",
                               object_id="#chrono_currtime"
            )
        )

        btn_startpause = pygame.Rect(0, 28, 143, self.btn_height)
        self.start_button = pygame_gui.elements.UIButton(
            relative_rect=btn_startpause,
            text=i18n.t("start_pause"),
            container=self,
            manager=manager,
            object_id=ObjectID(class_id="@chrono_button",
                               object_id="#chrono_startbtn"
            )
        )

        btn_savelap = pygame.Rect(0, 51, 143, self.btn_height)
        self.save_time = pygame_gui.elements.UIButton(
            relative_rect=btn_savelap,
            text=i18n.t("save_lap"),
            container=self,
            manager=manager,
            object_id=ObjectID(class_id="@chrono_button",
                               object_id="#chrono_flagbtn"
            )
        )

        btn_reset = pygame.Rect(0, 74, 143, self.btn_height)
        self.reset_button = pygame_gui.elements.UIButton(
            relative_rect=btn_reset,
            text=i18n.t("reset_all"),
            container=self,
            manager=manager,
            object_id=ObjectID(class_id="@chrono_button",
                               object_id="#chrono_resetbtn"
            )
        )

        self.laps_box = pygame_gui.elements.UITextBox(
            "",
            relative_rect=pygame.Rect(0, 97, 143, 78),
            container=self,
            manager=manager,
            object_id=ObjectID(class_id="@chrono_textbox",
                               object_id="#chrono_lapsbox"
            )
        )

        self.arr = []
        self.saver = False
        self.time_counter = 0
        self.currently_counting = False

    def process_event(self, event):
        super().process_event(event)
        if event.type == pygame.USEREVENT:
            if event.user_type == pygame_gui.UI_BUTTON_PRESSED:
                if event.ui_element == self.start_button:
                    self.currently_counting = not self.currently_counting
                elif event.ui_element == self.reset_button:
                    self.reset_time()
                elif event.ui_element == self.save_time:
                    self.saver = True

    def update(self, time_delta):
        super().update(time_delta)
        if self.currently_counting:
            self.time_counter += time_delta
        mili = int(self.time_counter * 100 % 100)
        secs = int(self.time_counter % 60)
        mins = int((self.time_counter % (60 ** 2)) // 60)
        hours = int(self.time_counter // (60 ** 2))

        counter_str = f"{str(hours)}:{str(mins)}:{str(secs)}:{str(mili)}"
        self.set_text(counter_str)

    def set_text(self, text):
        self.currtime.html_text = text
        self.currtime.rebuild()
        if self.saver:
            self.arr.append(text.replace("     ", "  "))
            self.laps_box.html_text = "<br>".join(self.arr)
            self.laps_box.rebuild()
            self.saver = False

    def reset_time(self):
        self.time_counter = 0
        self.currently_counting = False
        self.update(0)
        self.laps_box.html_text = ""
        self.laps_box.rebuild()
        self.arr.clear()

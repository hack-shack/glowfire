# wildbeast.py
# Makes a wild beast using the Teranoptia creature font.
# Tip: Open Teranoptia with FontForge to see all the glyphs.
# (c) 2024 Asa Durkee. MIT License.

import datetime
import pygame
import pygame_gui
from pygame_gui.elements import UIPanel
from pygame_gui.elements import UILabel
import random


class WildBeast(UIPanel):
    """ Draws a wild beast in a frame. """
    manager = None
    RESOLUTION = (400,240)
    def __init__(self,
                position,
                starting_height=0,
                manager=manager,
                size=RESOLUTION,
                element_id="#wildbeast"
                ):
        super().__init__(
            pygame.Rect(0, 0, self.RESOLUTION[0], self.RESOLUTION[1])
        )

        self.beast_box = UILabel(
            text="",
            relative_rect=pygame.Rect(0,69,400,110),
            manager=manager,
            container=self,
            anchors={
                "left": "left",
                "right": "right",
                "top": "top",
                "bottom": "bottom",
            },
            object_id="#beast_box"
        )

        self.beast_frame_top    = UILabel(text="{XYẊbc}",  # ouroboros
                                          relative_rect=pygame.Rect(0,0,400,60),
                                          manager=manager,
                                          container=self,
                                          object_id="#beast_frame_top")
        self.beast_frame_bottom = UILabel(text="[YXḅcb]",  # ouroboros
                                          relative_rect=pygame.Rect(0,187,400,62),
                                          manager=manager,
                                          container=self,
                                          object_id="#beast_frame_bottom")

        self.set_beast_box_text(self.make_a_beast())
        self.timer_start_time = pygame.time.get_ticks()
        self.timer_alert_time = self.timer_start_time + 5000  # display beast for this time


    def process_event(self, event):
        super().process_event(event)

    def update(self, time_delta):
        super().update(time_delta)

        self.current_time = pygame.time.get_ticks()
        if self.current_time > self.timer_alert_time:
            self.kill()

    def set_beast_box_text(self, text):
        self.beast_box.text = text
        self.beast_box.rebuild()

    def set_beast_frame_top_text(self,text):
        self.beast_frame_top.text = text
        self.beast_frame_top.rebuild()

    def set_beast_frame_bottom_text(self,text):
        self.beast_frame_bottom.text = text
        self.beast_frame_bottom.rebuild()



    def make_a_beast(self, less_creepy=True):
        heads_left  = ['a','e','i','m','p','s','y','ź']
        bodies_left = ['b','c','f','g','j','k','n','q','t','D','P','ž']
        tails_left  = ['d','h','l','o','r','u','x','z','E','ż']

        heads_right = ['B','H','K','N','R','V','Z','Ż']
        bodies_right= ['w','G','M','Q','T','U','X','Y','Ž']
        tails_right = ['v','A','C','F','I','J','L','O','S','W','Ź']

        if less_creepy is True:
            if 'e' in heads_left:
                heads_left.remove('e')  # human head
            if 'V' in heads_right:
                heads_right.remove('V')  # human head

        beast_direction = random.choice(['left','right'])

        if beast_direction == 'left':
            head       = random.choice(heads_left)
            body_fore  = random.choice(bodies_left)
            body_aft   = random.choice(bodies_left)
            tail       = random.choice(tails_left)
            longbeast  = head + body_fore + body_aft + tail
            shortbeast = head + body_fore + tail

        if beast_direction == 'right':
            head       = random.choice(heads_right)
            body_fore  = random.choice(bodies_right)
            body_aft   = random.choice(bodies_right)
            tail       = random.choice(tails_right)
            longbeast  = tail + body_aft + body_fore + head
            shortbeast = tail + body_fore + head

        if less_creepy is True:
            return shortbeast
        return longbeast



# ouroboros
    head_eating_tail_left = 'ḅ'
    head_eating_tail_right = 'Ẋ'

# frames
    line_horizontal    = '$'  # also the octothorpe character #
    line_vertical      = '€'
    elbow_left_bottom  = '}'
    elbow_left_top     = ']'
    elbow_right_bottom = '{'
    elbow_right_top    = '['
    tee_horizontal_bottom = '«'
    tee_horizontal_top = '»'
    tee_vertical_left  = '‹'
    tee_vertical_right = '›'
    end_vertical_bottom = '‘'
    end_vertical_top   = '’'
    hyphen_vertical    = '“'
    hypen_horizontal   = '”'
    plug_horizontal_left  = '('
    plug_horizontal_right = ')'

# dingbats
    bone_hypen = '-'
    moon_left  = ','
    star       = '*'

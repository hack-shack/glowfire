"""
cyber animation

(c) 2020 Joshua Moore
(c) 2024 Asa Durkee

MIT License
"""

import math
import random
import pygame
from pygame import Rect
import pygame_gui
from pygame_gui.core import ObjectID
from pygame_gui.elements.ui_button import UIButton
from pygame_gui.elements.ui_image import UIImage
from pygame_gui.elements.ui_panel import UIPanel

BLACK = (0,)*3
WHITE = (255,)*3
DIMS = 400, 240  # game area size; it is independent from cyber's UIPanel size

# horizontal line offsets for "scrolling effect"
CYBER_OFFS = 0

# list of tuples containing star information
# (x, y, radius)
CYBER_STARS = None

# horizontal position of the ship
CYBER_SHIP_X = 100



class Cyber(UIPanel):
    """ cyberspace wallpaper """
    def __init__(self, position, manager):
        super().__init__(
            Rect(position, (400,240)),
            manager = manager,
            object_id = ObjectID(class_id="@cyber_panel",object_id="#cyber")
        )

        """ The destination surface; the rectangular contents of the cyber window. """
        self.dsurf = UIImage(
            Rect((0, 0),DIMS),
            pygame.Surface(DIMS).convert(),
            manager = manager,
            container = self,
            parent_element = self,
        )

        self.ui_manager.get_theme().load_theme('data/theme.json')

        self.button_quit = UIButton(
            relative_rect = Rect(380,0,20,20),
            text="",
            manager=manager,
            container=self,
            tool_tip_text="Quit cyber app.",
            parent_element=self,
            object_id=ObjectID(class_id="@cyber_button",
                               object_id="#cyber_button_quit"
            )
        )

    def update(self, time_delta):
        super().update(time_delta)
        self.drawbg(self.dsurf.image)

    def drawbg(self, surface):
        """ Draw background image. """
        global CYBER_OFFS
        global CYBER_STARS
        global CYBER_SHIP_X

        SURF_WIDTH = surface.get_width()
        SURF_HEIGHT = surface.get_height()

        # generate stars if needed
        if CYBER_STARS is None:
            CYBER_STARS = []
            for x in range(50, 100):
                CYBER_STARS.append(
                    (
                        random.randint(0, SURF_WIDTH),
                        random.randint(0, math.ceil(SURF_HEIGHT / 2 - 5)),
                        random.randint(1, 2),
                    )
                )

        # black background
        surface.fill(BLACK)

        # draw horizon line
        pygame.draw.line(surface = surface,
                         color = WHITE,
                         start_pos = (0, SURF_HEIGHT / 2),
                         end_pos   = (SURF_WIDTH, SURF_HEIGHT / 2))

        # draw single point perspective lines, radiating from horizon
        for theta in range(0, 180, 10):
            tdeg = math.radians(theta)
            pygame.draw.line(surface = surface,
                             color = WHITE,
                             start_pos = (SURF_WIDTH / 2, SURF_HEIGHT / 2),
                             end_pos = (SURF_WIDTH / 2 + math.cos(tdeg) * 2000,
                                        SURF_HEIGHT / 2 + math.sin(tdeg) * 2000,),)

        # draw horizontal lines, moving towards the viewer
        y = (SURF_HEIGHT / 2) - 20
        dy = 1
        while y <= SURF_HEIGHT:
            ty = y + CYBER_OFFS * (dy / 10)
            if ty > SURF_HEIGHT / 2:
                pygame.draw.line(surface = surface,
                                 color = WHITE,
                                 start_pos = (0, ty),
                                 end_pos = (SURF_WIDTH, ty))
            y = y + dy
            dy = dy + 5

        CYBER_OFFS = CYBER_OFFS + 0.1
        if CYBER_OFFS > 10:
            CYBER_OFFS = 0

        CYBER_SHIP_X = CYBER_SHIP_X - int((CYBER_SHIP_X - pygame.mouse.get_pos()[0]) / 50)
        #CYBER_SHIP_X = 50

        # draw stars
        for star in CYBER_STARS:
            pygame.draw.circle(surface, (WHITE), (star[0], star[1]), star[2])

        # draw sun
        sun_diam = 95  # pixels
        pygame.draw.arc(surface = surface,
                        color = WHITE,
                        rect = pygame.Rect(
                            SURF_WIDTH / 2 - (sun_diam / 2),
                            SURF_HEIGHT / 2 - (sun_diam / 2),
                            sun_diam, sun_diam),
                        start_angle = 0.0,
                        stop_angle = math.radians(180),
                        width = 2)

        self.draw_ship(surface, (int(SURF_WIDTH / 2), int(SURF_HEIGHT / 2)), CYBER_SHIP_X / SURF_WIDTH)

    def draw_ship(self, surface, origin, dx):
        """
        Draw the "space ship"
        origin - tuple representing center of the screen
        dx - (shipX / screen_width)
        """
        fx = (
            #origin[0] - int(math.cos(math.radians(dx * 180)) * 700),
            #origin[1] + int(math.sin(math.radians(dx * 180)) * 300),
            origin[0] - int(math.cos(math.radians(dx * 180)) * 100),
            origin[1] + int(math.sin(math.radians(dx * 180)) * 50),
        )

        fl = (
            #origin[0] - int(math.cos(math.radians((dx - 0.05) * 180)) * 700),
            #origin[1] + int(math.sin(math.radians((dx - 0.1) * 180)) * 500),
            origin[0] - int(math.cos(math.radians((dx - 0.05) * 180)) * 100),
            origin[1] + int(math.sin(math.radians((dx - 0.1) * 180)) * 50),
        )

        fr = (
            #origin[0] - int(math.cos(math.radians((dx + 0.05) * 180)) * 700),
            #origin[1] + int(math.sin(math.radians((dx + 0.1) * 180)) * 500),
            origin[0] - int(math.cos(math.radians((dx + 0.05) * 180)) * 100),
            origin[1] + int(math.sin(math.radians((dx + 0.1) * 180)) * 50),
        )
        pygame.draw.polygon(surface=surface, color=WHITE, points=(fx, fl, fr), width=4)

    def process_event(self, event):
        super().process_event(event)

        if event.type == pygame.USEREVENT:
            if event.user_type == pygame_gui.UI_BUTTON_PRESSED:
                if event.ui_object_id == "#cyber.#cyber_button_quit":
                    self.kill()

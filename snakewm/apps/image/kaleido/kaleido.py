import pygame
import pygame_gui
from pygame_gui.core import ObjectID
from pygame_gui.elements.ui_image import UIImage

from math import sin, cos, pi
import random, time

RES = 64
RES2 = RES / 2
SRES = 230
FPS = 15


class Kaleido(pygame_gui.elements.UIWindow):
    DIMS = SRES, int(0.75 * SRES)

    def __init__(self, pos, manager):
        super().__init__(
            pygame.Rect(pos, (self.DIMS[0] + 32, self.DIMS[1] + 60)),
            manager=manager,
            window_display_title="kaleido",
            object_id=ObjectID(class_id="@kaleido_window",object_id="#kaleido"),
            resizable=True,
        )

        self.dsurf = UIImage(
            pygame.Rect((0, 0), self.DIMS),
            pygame.Surface(self.DIMS).convert(),
            manager=manager,
            container=self,
            parent_element=self,
        )
        self.kaleido = pygame.Surface((RES, RES))
        self.pow = 1
        self.lastpow = 0
        self.lastframe = 0
        self.paused = False
        self.step = False
        self.manager = manager

    def process_event(self, event):
        super().process_event(event)
        r = super().get_abs_rect()
        if event.type == pygame.MOUSEBUTTONUP and (
            r.w != self.DIMS[0] + 32 or r.h != self.DIMS[1] + 60
        ):
            self.DIMS = r.w - 32, r.h - 60
            super().kill()
            self.__init__((r.left, r.top), self.manager)
        if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
            self.paused = not self.paused
        if event.type == pygame.KEYDOWN and event.key == pygame.K_PERIOD:
            self.step = True

    def draw(self, x, y, c):
        pygame.draw.line(self.kaleido, c, (RES2 + x, RES2 + y), (RES2 + x, RES2 + y))
        pygame.draw.line(self.kaleido, c, (RES2 - x, RES2 + y), (RES2 - x, RES2 + y))
        pygame.draw.line(self.kaleido, c, (RES2 + x, RES2 - y), (RES2 + x, RES2 - y))
        pygame.draw.line(self.kaleido, c, (RES2 - x, RES2 - y), (RES2 - x, RES2 - y))

    def update(self, delta):
        super().update(delta)
        if (self.paused and not self.step) or (time.time() - self.lastframe < 1 / FPS):
            return
        self.step = False
        self.lastframe = time.time()
        c = (
            85 * random.randint(0, 3),
            85 * random.randint(0, 3),
            85 * random.randint(0, 3),
        )
        if random.random() < random.uniform(0.2, 1):
            c = 0, 0, 0
        if random.random() < random.uniform(0.01, 0.03):
            c = 255, 255, 255
        amp = random.gauss(0, 0.1) + time.time() % 29
        phi = random.gauss(0, 0.1) + time.time() % 11
        off = random.gauss(0, 0.3) * sin(time.time() / 23)
        if time.time() - self.lastpow > 19:
            self.pow = random.randint(1, 3)
            self.lastpow = time.time()
        for t in range(0, 360, random.randint(1, 3)):
            x = amp * (sin(phi * t * pi / 180) + off) ** self.pow
            y = amp * (cos(phi * t * pi / 180) + off) ** self.pow
            self.draw(x, y, c)
            x = 2 * x
            y = 2 * y
            self.draw(x, y, c)
            x = 1.5 * x
            y = 1.5 * y
            self.draw(x, y, c)

        out = pygame.transform.scale(self.kaleido, (self.DIMS))
        self.dsurf.image.blit(out, (0, 0))

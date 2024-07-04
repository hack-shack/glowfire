"""
graphs for pygame
(c) 2022 Jason Zhang and CaseyHackerMan. MIT License.
(c) 2024 Asa Durkee. Snakeware port.
"""
import pygame
#from guipy.components._component import Component
#from guipy.utils import *
from math import *

BLACK = ((0,)*3)
WHITE = ((255,)*3)

def line(surf, points):
    """
    Example/default plot style

    :param surf: Surface to draw to
    :param points: List of pixel coordinates to draw. ex: [(1,1),(2,3),...]
    """
    last = None
    for p in points:
        if last:
            pygame.draw.line(surf, BLACK, last, p, 2)
        last = p


class Plot(pygame.Surface):
    """
    Plot component. Simple and fast way to display data.
    """

    def __init__(
        self, width, height, xlabel=None, ylabel=None, xaxis_height=100, yaxis_width=100
    ):
        """
        Plot init

        :param width: Plot width in pixels
        :param height: Plot height in pixels
        :param xlabel: X-axis label
        :param ylabel: Y-axis label
        :param xaxis_height: X-axis height in pixels
        :param yaxis_width: Y-axis width in pixels
        """

        self.long_tick = 30
        self.short_tick = 10

        self.width = width
        self.height = height

        self.xlabel = xlabel
        self.ylabel = ylabel

        self.range_set = False
        self.points = []
        self.styles = []

        self.set_range((0, 0), (0, 0))

        self.font = get_default_font()
        self.root = pygame.Surface((self.width, self.height)).convert_alpha()
        self.window = pygame.Surface((width - yaxis_width, height - xaxis_height))
        self.windrect = self.window.get_rect().inflate(-5, -5)

    def _x(self, x):  # coordinate to pixel
        return translate(
            x, self.xmin, self.xmax, self.windrect.left, self.windrect.right
        )

    def _y(self, y):  # coordinate to pixel
        return translate(
            y, self.ymax, self.ymin, self.windrect.top, self.windrect.bottom
        )

    def _draw(self):
        w = self.window.get_width()
        h = self.window.get_height()

        self.root.fill(WHITE)
        if self.range_set:

            # draw x-axis
            scale = floor(log10(self.xmax - self.xmin))
            res = 10 ** (scale - 1)

            i = ceil(self.xmin / res)

            while i * res <= self.xmax:
                x = self._x(i * res)

                if i % 10 == 0:
                    p2 = (x, h + self.long_tick)
                    n = float_format(i * res, scale)
                    num = self.font.render(n, True, BLACK)
                    self.root.blit(num, p2)
                else:
                    p2 = (x, h + self.short_tick)
                pygame.draw.line(self.root, BLACK, (x, h), p2, 1)
                i += 1

            # draw y-axis
            scale = floor(log10(self.ymax - self.ymin))
            res = 10 ** (scale - 1)

            i = ceil(self.ymin / res)

            while i * res <= self.ymax:
                y = self._y(i * res)

                if i % 10 == 0:
                    p2 = (w + self.long_tick, y)
                    n = float_format(i * res, scale)
                    self.root.blit(self.font.render(n, True, BLACK), p2)
                else:
                    p2 = (w + self.short_tick, y)
                pygame.draw.line(self.root, BLACK, (w, y), p2, 1)
                i += 1

        if not self.xlabel == None:
            label = self.font.render(self.xlabel, True, BLACK)
            p = ((w - label.get_width()) / 2, self.height - label.get_height())
            self.root.blit(label, p)

        if not self.ylabel == None:
            label = self.font.render(self.ylabel, True, BLACK)
            label = pygame.transform.rotate(label, 90)
            p = (self.width - label.get_width(), (h - label.get_height()) / 2)
            self.root.blit(label, p)

        for i in range(len(self.points)):
            self.styles[i](self.window, self.points[i])

        self.root.blit(self.window, (0, 0))
        pygame.draw.rect(self.root, BLACK, self.window.get_rect(), 1)

    def set_range(self, xrange, yrange):
        """
        Sets the plot X and Y range

        :param xrange: Tuple of minimum and maximum X values. ex: (0,100)
        :param yrange: Tuple of minimum and maximum Y values. ex: (0,100)

        :return: self
        """

        self.xmin = xrange[0]
        self.xmax = xrange[1]

        self.ymin = yrange[0]
        self.ymax = yrange[1]

        self.range_set = not (self.xmin == self.xmax or self.ymin == self.ymax)
        return self

    def plot(self, data, style=line):
        """
        Plots a list of points. Will not plot is the range is not valid.

        :param data: List of points to be plotted. ex: [(1.0,1.0),(1.2,1.3),...]
        :param style: Style function to be used. Should have the signature (surf:Surface, points:List[Tuple])

        :return: True is the range is valid
        """
        if self.range_set:
            self.points.append(list((self._x(d[0]), self._y(d[1])) for d in data))
            self.styles.append(style)
        return self.range_set

    def update(self, rel_mouse, events):
        """
        Update the plot

        :param rel_mouse: Relative mouse position
        :param events: Pygame Event list
        """
        self._draw()
        self.window.fill(WHITE)
        self.points = []
        self.styles = []


class LivePlot(Plot):
    """
    Live plot component. Unlike Plot, this will receive data continouously and add it to a buffer. Data is deleted from the buffer when it falls outside of a specified time range (time_range). \
    The Y-axis will adjust automatically.
    """

    def __init__(
        self,
        width,
        height,
        style=line,
        glide=10,
        xlabel="Time",
        ylabel="Data",
        time_range=5,
    ):
        """
        LivePlot init

        :param width: Plot width in pixels
        :param height: Plot height in pixels
        :param style: Style function to be used. Should have the signature (surf:Surface, points:List[Tuple])
        :param glide: y-axis glide value. A glide value above 1 will adjust the range gradually. 1 will make the range snap to the new value. 0 will only increase the range. -1 will not change the y range.
        :param xlabel: x-axis label
        :param ylabel: y-axis label
        :param time_range: x-axis range width
        """

        super().__init__(width, height, xlabel=xlabel, ylabel=ylabel)

        self.glide = glide
        # self.auto_range = True
        self.style = style
        self.time_range = time_range

        self.buffer = []
        self.min_window = 10**-12

    def add(self, data):
        """
        Add a single data point to the plot. Removes data that is outside of the time range

        :param data: data to add. ex: (time:float,data:float)

        :return: Number of points removed
        """

        self.buffer.append(data)
        i = 0
        if self.time_range >= 0 and len(self.buffer) > 1:

            while (self.buffer[-1][0] - self.buffer[i + 1][0]) > self.time_range:
                i += 1
            self.buffer = self.buffer[i:]
        return i

    def reset(self):
        """
        Clears the buffer and resets the range
        """
        self.buffer = []
        self.range_set = False

    def update(self, rel_mouse, events):
        """
        Updates the plot

        :param rel_mouse: relative mouse position
        :param events: Pygame event list
        """
        if len(self.buffer) > 1:
            if self.glide < 0:
                ymin = self.ymin
                ymax = self.ymax
            else:
                data = list(i[1] for i in self.buffer)
                low = min(data)
                high = max(data)

                if low == high:
                    ymin = low - self.min_window
                    ymax = high + self.min_window
                elif self.range_set:
                    xmin = self.xmin
                    xmax = self.xmax
                    ymin = self.ymin
                    ymax = self.ymax

                    if self.glide >= 1:
                        ymin += (low - ymin) / self.glide
                        ymax += (high - ymax) / self.glide
                    else:
                        if high > ymax:
                            ymax = high
                        if low < ymin:
                            ymin = low
                else:
                    ymax = high
                    ymin = low

            t = self.buffer[-1][0]
            xmax = t
            xmin = t - self.time_range

            self.set_range((xmin, xmax), (ymin, ymax))

        self.plot(self.buffer, self.style)
        super().update(rel_mouse, events)


def float_format(n, exponent):
    return str(n) if exponent < 0 else str(int(n))

def get_default_font():
    font_name = pygame.font.get_fonts()[0]
    return pygame.font.SysFont(font_name, 20)

def translate(value, min1, max1, min2, max2):
    """
    Maps one value from one range to another range

    :param value: Value to be mapped
    :param min1: Min of range 1
    :param max1: Max of range 1
    :param min2: Min of range 2
    :param max2: Max of range 2
    """
    span1 = max1 - min1
    span2 = max2 - min2
    if span1 == 0:
        return 0
    if value == None:
        return None
    valueScaled = float(value - min1) / float(span1)
    return min2 + (valueScaled * span2)

""" maze: 2D randomly generated maze """

import locale
import os
from pathlib import Path
from random import randrange, shuffle, random
import i18n
import pygame

class Maze:
    """ A 2D randomly generated maze. """
    dirToDelta = {
        0: (0, -1),
        1: (1, 0),
        2: (0, 1),
        3: (-1, 0),
    }

    def __init__(self, size):

        app_path = os.path.dirname(os.path.abspath(__file__))
        assets_path = app_path + "/assets"

        p = Path(app_path)
        wm_dir = p.parents[2]  # hopefully, snakewm folder
        font_dir = os.path.join(wm_dir,"data/fonts")
        i18n.load_path.append(os.path.join(os.path.dirname(__file__),"data/translations"))

        self.size = size
        self.sprite_size = (32, 32)
        self.width = int(self.size[0] / self.sprite_size[0]) - 8
        self.height = int(self.size[1] / self.sprite_size[1]) - 2
        self.font_color = (0, 0, 0)
        self.font_bgcolor = (255,255,255)
        self.background = pygame.Surface(size)  # make a background surface
        self.background = self.background.convert()
        self.background.fill((255,255,255))

        self.player = []
        self.player.append(pygame.image.load(assets_path + "/player_up.png").convert())
        self.player.append(pygame.image.load(assets_path + "/player_right.png").convert())
        self.player.append(pygame.image.load(assets_path + "/player_down.png").convert())
        self.player.append(pygame.image.load(assets_path + "/player_left.png").convert())
        self.floor = []
        self.floor.append(pygame.image.load(assets_path + "/floor0.png").convert())
        self.floor.append(pygame.image.load(assets_path + "/floor1.png").convert())
        self.floor.append(pygame.image.load(assets_path + "/floor2.png").convert())
        self.wall = pygame.image.load(assets_path + "/wall.png").convert()

        # TODO: if Japanese language code, use "KH-Dot-Dougenzaka-16.ttf
        self.font = pygame.font.Font(os.path.join(font_dir,"ProFontIIx/ProFontIIx.ttf"), 14)
        self.font_height = self.font.size("")[1]
        self.font_xpos = (self.width + 3) * self.sprite_size[1]
        self.font_width = self.size[0] - self.font_xpos

        self.maze = [[-1 for x in range(self.height)] for x in range(self.width)]

        self.walls = self.height * self.width - 1
        self.moves = 0
        self.direction = 0
        self.x, self.y = randrange(self.width), randrange(self.height)

        self.maze[self.x][self.y] = 1
        self.visited = 1
        self.visited2 = 0
        self.unvisited = 0
        self.bumps = 0

        self.generate()

    def process_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LEFT:
                self.turn(-1)
            elif event.key == pygame.K_RIGHT:
                self.turn()
            elif event.key == pygame.K_UP:
                self.move()
            else:
                return False
            return True
        return False

    def draw(self, surface):
        surface.blit(self.background, (0, 0))
        for y in range(-1, self.height + 1):
            self.draw_wall(surface, -1, y)
            self.draw_wall(surface, self.width, y)
        for x in range(-1, self.width + 1):
            self.draw_wall(surface, x, -1)
            self.draw_wall(surface, x, self.height)
        self.draw_stats_table(surface)
        for y in range(self.height):
            for x in range(self.width):
                if self.block_free((x, y)):
                    self.draw_empty(surface, x, y)
                else:
                    self.draw_wall(surface, x, y)
        self.draw_player(surface)

    def draw_wall(self, surface, x, y):
        rect = (
            ((x + 1) * self.sprite_size[0], (y + 1) * self.sprite_size[1]),
            (self.sprite_size),
        )
        surface.blit(self.wall, rect)

    def draw_empty(self, surface, x, y):
        rect = (
            ((x + 1) * self.sprite_size[0], (y + 1) * self.sprite_size[1]),
            (self.sprite_size),
        )
        surface.blit(self.floor[self.maze[x][y]], rect)

    def render_stats_text(self, surface, text, y):
        text = self.font.render(text=text, antialias=False, color=self.font_color)
        textpos = text.get_rect()
        textpos.move_ip(self.font_xpos, y * self.font_height)
        textpos.width = self.font_width
        surface.fill(self.font_bgcolor, textpos)
        surface.blit(text, textpos)

    def draw_player(self, surface):
        rect = (
            ((self.x + 1) * self.sprite_size[0], (self.y + 1) * self.sprite_size[1]),
            (self.sprite_size),
        )
        surface.blit(self.player[self.direction], rect)

    def draw_stats_table(self, surface):
        self.render_stats_text(surface, i18n.t("size")+"{}x{}".format(self.width, self.height), 1)
        self.render_stats_text(surface, i18n.t("walls")+"{}".format(self.walls), 2)
        self.render_stats_text(surface, i18n.t("unvisited")+"{}".format(self.unvisited), 3)
        self.render_stats_text(surface, i18n.t("visited")+"{}".format(self.visited), 4)
        self.render_stats_text(surface, i18n.t("visited2")+"{}".format(self.visited2), 5)
        self.render_stats_text(surface, i18n.t("impacts")+"{}".format(self.bumps), 6)

    def generate(self, deep=True, loop_prob=0.05):
        x, y = self.x, self.y
        self.loop_prob = loop_prob
        ends = self.walled_neigbour_blocks((x, y))
        while ends:
            if deep:
                x, y = ends.pop()
            else:
                x, y = ends.pop(randrange(len(ends)))
            if self.block_removeable((x, y)):
                self.maze[x][y] = 0
                self.walls -= 1
                self.unvisited += 1
                ends += self.walled_neigbour_blocks((x, y))

    def block_free(self, coord):
        x, y = coord[0], coord[1]
        return self.maze[x][y] != -1

    def in_bounds(self, coord):
        x, y = coord[0], coord[1]
        return x >= 0 and x < self.width and y >= 0 and y < self.height

    def block_removeable(self, coord):
        if self.block_free(coord):
            return False

        x, y = coord[0], coord[1]
        bl = [(x - 1, y), (x + 1, y), (x, y - 1), (x, y + 1)]
        n = 0
        for i in bl:
            if self.in_bounds(i) and self.block_free(i):
                n += 1
        return n <= 1 or random() < self.loop_prob

    def walled_neigbour_blocks(self, coord):
        x, y = coord[0], coord[1]
        bl = [(x - 1, y), (x + 1, y), (x, y - 1), (x, y + 1)]
        shuffle(bl)
        rbl = []
        for i in bl:
            if self.in_bounds(i) and not self.block_free(i):
                rbl.append(i)
        return rbl

    def turn(self, n=1):
        self.direction += n
        self.direction %= 4

    def move(self):
        x, y = self.x, self.y
        nx = x + self.dirToDelta[self.direction][0]
        ny = y + self.dirToDelta[self.direction][1]

        if self.in_bounds((nx, ny)) and self.block_free((nx, ny)):
            if self.maze[nx][ny] == 0:
                self.maze[nx][ny] = 1
                self.visited += 1
                self.unvisited -= 1
            elif self.maze[nx][ny] == 1:
                self.maze[nx][ny] = 2
                self.visited2 += 1
            self.x, self.y = nx, ny
            self.moves += 1
        else:
            self.bumps += 1

import pygame as pg

from .. import tools, prepare
from ..components.labels import Label
from ..components.animation import Animation


class Fish(pg.sprite.Sprite):
    def __init__(self, midleft):
        self.image = prepare.GFX["pixel-fish"]
        self.rect = self.image.get_rect(midleft=midleft)
        self.last_pos = self.rect.right

    def update(self, grid):
        self.rect.left -= 16
        try:
            x = (self.rect.right // 16) + 1
            y = self.rect.centery // 16
            cell = grid[(x, y)]
            if "title" in cell.value:
                cell.value = "title-fish"
            else:
                cell.value = "fish"
        except KeyError:
            pass

    def draw(self, surface):
        surface.blit(self.image, self.rect)


class Shark(pg.sprite.Sprite):
    def __init__(self, midleft):
        self.image = prepare.GFX["pixel-shark"]
        self.rect = self.image.get_rect(midleft=midleft)

    def update(self, grid):
        self.rect.left -= 16
        for cell in grid:
            if grid[cell].value in ("title-water", "title-fish"):
                if grid[cell].rect.right > self.rect.right - 48:
                    grid[cell].value = "title"

    def draw(self, surface):
        surface.blit(self.image, self.rect)


class Cell(object):
    colors = {
            "water": (18, 38, 53),
            "fish": (58, 170, 150),
            "title-water": (18, 38, 53),
            "title-fish": (58, 170, 150),
            "title": (211, 103, 103)} #(255, 255, 255)}
    def __init__(self, index, topleft, cell_size, value):
        self.index = index
        self.rect = pg.Rect(topleft, (cell_size, cell_size))
        self.value = value

    def draw(self, surface):
        pg.draw.rect(surface, self.colors[self.value], self.rect)


class Grid(object):
    def __init__(self, topleft, size, cell_size):
        self.rect = pg.Rect(topleft, size)
        self.cell_size = cell_size
        self.make_cells()

    def make_cells(self):
        self.cells = {}
        for x in range(self.rect.width//self.cell_size):
            for y in range(self.rect.height//self.cell_size):
                cell = Cell((x, y), (x * self.cell_size, y * self.cell_size),
                                self.cell_size, "water")
                self.cells[(x, y)] = cell

    def update(self):
        new_fish = []
        for c in self.cells:
            if self.cells[c].value in ("fish", "title-fish"):
                offsets = [(0, -1), (0, 1), (1, 0), (-1, 0)]
                for off in offsets:
                    new_fish.append((c[0] + off[0], c[1] + off[1]))
        for n in new_fish:
            try:
                current = self.cells[n].value
                if current in ("water", "fish"):
                    new_val = "fish"
                elif current in ("title-water", "title-fish"):
                    new_val = "title-fish"
                elif current == "title":
                    new_val = "title"
                self.cells[n].value = new_val
            except KeyError:
                pass

    def draw(self, surface):
        for c in self.cells.values():
            c.draw(surface)


class TitleScreen(tools._State):
    def __init__(self):
        super(TitleScreen, self).__init__()
        r = prepare.SCREEN_RECT
        self.grid = Grid((0, 0), (1152, 656), 16)
        self.fish = Fish((r.w + 240, r.centery))
        self.shark = Shark((r.w + 2160, r.centery))
        self.animations = pg.sprite.Group()
        self.make_title()
        self.tick_length = 30
        self.timer = 0

    def startup(self, persistent):
        self.persist = persistent

    def make_title(self):
        lines = [
            "XOOOXOOOXOOOOOOXXXXXOOXXXOOXXXXO",
            "XOOOXOOXOXOOOOOOOXOOOXOOOXOXOOOX",
            "XOOOXOOXXXOOXXOOOXOOOXOOOXOXXXXO",
            "XOXOXOXOOOXOOOOOOXOOOXOOOXOXOXOO",
            "OXOXOOXOOOXOOOOOOXOOOOXXXOOXOOXO"]
        left = 20
        top = 19
        for y, line in enumerate(lines):
            for x, char in enumerate(line):
                if char == "X":
                    self.grid.cells[(left + x, top + y)].value = "title-water"

    def get_event(self,event):
        if event.type == pg.QUIT:
            self.quit = True
        elif event.type == pg.KEYUP:
            if event.key == pg.K_ESCAPE:
                self.quit = True
        elif event.type == pg.MOUSEBUTTONUP:
            self.done = True
            self.next = "SIM_SETUP"
            self.grid = None

    def update(self, dt):
        self.timer += dt
        if self.timer >= self.tick_length:
            self.timer -= self.tick_length

            self.fish.update(self.grid.cells)
            self.shark.update(self.grid.cells)
            self.grid.update()

    def draw(self, surface):
        self.grid.draw(surface)
        self.fish.draw(surface)
        self.shark.draw(surface)


from random import sample, choice

import pygame as pg

from .. import prepare

class WatorWorld(object):
    shark_color = prepare.SHARK_COLOR
    fish_color = prepare.FISH_COLOR
    water_color = prepare.WATER_COLOR
    offsets = [(-1, 0), (0, -1), (1, 0), (0, 1)]
    def __init__(self, setup_dict):
        d = setup_dict
        self.left, self.top = d["topleft"]
        size = d["size"]
        self.cell_size = d["cell size"]
        self.num_rows = size[1] // self.cell_size
        self.num_columns = size[0] // self.cell_size
        self.width = self.num_columns * self.cell_size
        self.height = self.num_rows * self.cell_size
        self.world_rect = pg.Rect((self.left, self.top),
                                              (self.width, self.height))
        self.fish_reproduce_age = d["fish reproduce age"]
        self.shark_reproduce_age = d["shark reproduce age"]
        self.shark_starve_time = d["shark starve time"]
        self.fish_img = prepare.GFX["fish1"]
        self.shark_img = prepare.GFX["shark1"]
        self.generate_world(setup_dict)
        self.ticks = 0

    def get_neighbors(self, index):
        vacant = []
        fishes = []
        neighbors = ((offset[0] + index[0], offset[1] + index[1])
                            for offset in self.offsets)
        for dx, dy in neighbors:
            try:
                occupant = self.grid[(dx, dy)]
            except KeyError:
                if dx > self.num_columns - 1:
                    dx = 0
                elif dx < 0:
                    dx = self.num_columns - 1
                if dy > self.num_rows - 1:
                    dy = 0
                elif dy < 0:
                    dy = self.num_rows - 1
                occupant = self.grid[(dx, dy)]
            if occupant is None:
                vacant.append((dx, dy))
            elif occupant[0] == "fish":
                fishes.append((dx, dy))
        return vacant, fishes

    def generate_world(self, setup_dict):
        indexes = [(x, y) for x in range(self.num_columns)
                        for y in range(self.num_rows)]
        self.grid = {indx_: None for indx_ in indexes}
        self.lefttops = {indx: (self.left + (indx[0] * self.cell_size),
                               self.top + (indx[1] * self.cell_size))
                               for indx in self.grid}
        fish_spots = sample(indexes, setup_dict["num fish"])
        open = [x for x in indexes if x not in fish_spots]
        shark_spots = sample(open, setup_dict["num sharks"])
        self.fishes = pg.sprite.Group()
        for f in fish_spots:
            self.grid[f] = ["fish", 0]
        for s in shark_spots:
            self.grid[s] = ["shark", 0, self.shark_starve_time]

    def update(self):
        self.ticks += 1
        for cell in self.grid:
            occupant = self.grid[cell]
            if occupant is None:
                continue
            vacant, fishes = self.get_neighbors(cell)
            if occupant[0] == "fish":
                occupant[1] += 1
                if vacant:
                    new_spot = choice(vacant)
                    self.grid[new_spot] = self.grid[cell]
                    if occupant[1] >= self.fish_reproduce_age:
                        self.grid[new_spot][1] = 0
                        self.grid[cell] = ["fish", 0]
                    else:
                        self.grid[cell] = None

            elif occupant[0] == "shark":
                occupant[1] += 1
                occupant[2] -= 1
                if occupant[2] <= 0:
                    self.grid[cell] = None
                else:
                    if fishes:
                        dest = choice(fishes)
                        self.grid[cell][2] = self.shark_starve_time
                        self.move_shark(cell, dest)
                    elif vacant:
                        dest = choice(vacant)
                        self.move_shark(cell, dest)
        
    def add_fish(self):
        for indx in self.grid:
            if self.grid[indx] is None:
                self.grid[indx] = ["fish", 0]
                break

    def add_shark(self):
        for indx in self.grid:
            if self.grid[indx] is None:
                self.grid[indx] = ["shark", 0, self.shark_starve_time]
                break
                
    def move_shark(self, cell, dest):
        self.grid[dest] = self.grid[cell]
        if self.grid[dest][1] >= self.shark_reproduce_age:
            self.grid[cell] = ["shark", 0, self.shark_starve_time]
            self.grid[dest][1] = 0
        else:
            self.grid[cell] = None

    def draw(self, surface):
        surface.fill(self.water_color, self.world_rect)
        for indx, val in self.grid.items():
            if val is None:
                continue
            if val[0] == "fish":
                surface.blit(self.fish_img, self.lefttops[indx])
            else:
                surface.blit(self.shark_img, self.lefttops[indx])


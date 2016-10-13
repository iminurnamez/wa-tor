import pygame as pg

from ..components.labels import Label


class Graph(object):
    def __init__(self, topleft, size):
        self.left, self.top = topleft
        self.width, self.height = size
        self.bottom = self.top + self.height
        self.high_label = Label("0", {"topright": (self.left - 8, self.top)})
        self.low_label = Label("0", {"bottomright": (self.left - 8, self.bottom)})
        self.bg_color = (18, 38, 53) #(106, 121, 132)
        self.rect = pg.Rect(topleft, size)

    def make_lines(self, data_lines):
        points = []
        low = 0
        high = 0
        x_scale = self.width / float(len(data_lines[0][1]))
        for d in data_lines:
            color = d[0]
            vals = d[1]
            for v in vals:
                if v > high:
                    high = v
        y_scale = float(self.height) / (high - low)   
        for color, vals_ in data_lines:
            scaled = [(self.left + (int(i * x_scale)), self.bottom - int(v * y_scale))
                          for i, v in enumerate(vals_)]
            if len(scaled) < 2:
                scaled.append(scaled[0])
            points.append([color, scaled])
        self.points = points
        self.high_label.set_text("{}".format(high))
        self.low_label.set_text("{}".format(low))
        

    def draw(self, surface):
        pg.draw.rect(surface, self.bg_color, self.rect)
        for color, pts in self.points:
            pg.draw.lines(surface, pg.Color(*color), False, pts, 1)
        self.low_label.draw(surface)
        self.high_label.draw(surface)
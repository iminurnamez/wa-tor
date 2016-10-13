import pygame as pg

from .. import tools, prepare
from ..components.labels import Label, Button


class Incrementer(object):
    def __init__(self, midtop, default_val, minimum, maximum):
        self.value = default_val
        self.minimum = minimum
        self.maximum = maximum
        self.value_label = Label("{}".format(self.value), {"midtop": midtop})
        self.down_img = prepare.GFX["arrow-left"]
        self.up_img = prepare.GFX["arrow-right"]
        self.down_rect = self.down_img.get_rect(midtop=(midtop[0] - 50, midtop[1] + 5))
        self.up_rect = self.up_img.get_rect(midtop=(midtop[0] + 50, midtop[1] + 5))
        self.increasing = False
        self.decreasing = False
        self.hold_time = 0
        self.changes = 0
        self.effect_time = 250
        self.effect_min = 10
        
    def get_event(self, event):
        if event.type == pg.MOUSEBUTTONDOWN:
            self.hold_time = 0
            if self.down_rect.collidepoint(event.pos):
                self.decreasing = True
                self.increasing = False
            elif self.up_rect.collidepoint(event.pos):
                self.increasing = True
                self.decreasing = False
        elif event.type == pg.MOUSEBUTTONUP:
            if self.down_rect.collidepoint(event.pos):
                self.decrement()
                self.idle()
            elif self.up_rect.collidepoint(event.pos):
                self.increment()
                self.idle()
                
    def update(self, dt, mouse_pos):
        if self.changes and not self.changes % 5:
            if self.effect_time >= 100:
                self.effect_time -= 50
            elif self.effect_time > self.effect_min:
                self.effect_time -= 10            
        if self.decreasing:
            if not self.down_rect.collidepoint(mouse_pos):
                self.idle()
            else:
                self.hold_time += dt
                while self.hold_time >= self.effect_time:
                    self.hold_time -= self.effect_time
                    self.decrement()                
        elif self.increasing:
            if not self.up_rect.collidepoint(mouse_pos):
                self.idle()
            else:
                self.hold_time += dt
                while self.hold_time >= self.effect_time:
                    self.hold_time -= self.effect_time
                    self.increment()
                    
    def idle(self):
        self.decreasing = False
        self.increasing = False
        self.hold_time = 0
        self.changes = 0
        self.effect_time = 250

    def decrement(self):
        if self.value > self.minimum:
            self.value -= 1
            self.value_label.set_text("{}".format(self.value))
            self.changes += 1
            
    def increment(self):
        if self.value < self.maximum:
            self.value += 1        
            self.value_label.set_text("{}".format(self.value))
            self.changes += 1
            
    def draw(self, surface):
        self.value_label.draw(surface)
        surface.blit(self.down_img, self.down_rect)
        surface.blit(self.up_img, self.up_rect)        
            
            
class SimSetup(tools._State):
    def __init__(self):
        super(SimSetup, self).__init__()
        self.statics = pg.sprite.Group()
        cx = prepare.SCREEN_RECT.centerx
        Label("Wa-Tor Setup", {"midtop": prepare.SCREEN_RECT.midtop},
                 self.statics, font_size=48, text_color=(211, 103, 103))
        Label("Starting Fish", {"midtop": (cx, 80)}, self.statics,
                 font_size=24, text_color=(58, 170, 150))
        Label("Starting Sharks", {"midtop": (cx, 160)}, self.statics,
                 font_size=24, text_color=(58, 170, 150))
        Label("Fish Reproduction", {"midtop": (cx, 240)}, self.statics,
                 font_size=24, text_color=(58, 170, 150))
        Label("Shark Reproduction", {"midtop": (cx, 320)}, self.statics,
                 font_size=24, text_color=(58, 170, 150))
        Label("Shark Starvation", {"midtop": (cx, 400)}, self.statics,
                 font_size=24, text_color=(58, 170, 150))
        self.bg = (18, 38, 53)
        self.make_incrementers()
        b_img = prepare.GFX["start_button"]
        b_size= b_img.get_size()
        self.start_button = Button((cx-(b_size[0]//2), 500), button_size=b_size,
                                               idle_image=b_img, call=self.start)
        
    def make_incrementers(self):
        self.PARAMS = {
                "topleft": (176, 16),
                "size": (960, 512),
                "cell size": 8,
                "num fish": 7000,
                "num sharks": 1,
                "fish reproduce age": 2,
                "shark reproduce age": 3,
                "shark starve time": 2
                }
        settings = [("num fish", 0, 7680),
                         ("num sharks", 0, 7680),
                         ("fish reproduce age", 1, 2000),
                         ("shark reproduce age", 1, 2000),
                         ("shark starve time", 1, 2000)]
        self.incrementers = {}
        cx = prepare.SCREEN_RECT.centerx
        top = 120
        for name, mini, maxi in settings:
           inc = Incrementer((cx, top), self.PARAMS[name], mini, maxi)
           self.incrementers[name] = inc
           top += 80
           
    def start(self, *args):
        self.set_params()
        self.persist["PARAMS"] = self.PARAMS
        self.done = True
        self.next = "GAMEPLAY"
        
    def set_params(self):
        settings = ["num fish", "num sharks", "fish reproduce age",
                         "shark reproduce age", "shark starve time"]
        for s in settings:
            self.PARAMS[s] = self.incrementers[s].value
        
    def startup(self, persistent):
        self.persist = persistent
        
    def get_event(self, event):
        if event.type == pg.QUIT:
            self.quit = True
        elif event.type == pg.KEYUP:
            if event.key == pg.K_ESCAPE:
                self.quit = True
        for inc in self.incrementers.values():
            inc.get_event(event)
        self.start_button.get_event(event)
        
    def update(self, dt):
        mouse_pos = pg.mouse.get_pos()
        for inc in self.incrementers.values():
            inc.update(dt, mouse_pos)
        self.start_button.update(mouse_pos)
        
    def draw(self, surface):
        surface.fill(self.bg)
        self.statics.draw(surface)
        for inc in self.incrementers.values():
            inc.draw(surface)
        self.start_button.draw(surface)
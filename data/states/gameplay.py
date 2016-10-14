import pygame as pg

from .. import tools, prepare
from ..components.labels import Label, Button, ButtonGroup
from ..components.world import WatorWorld
from ..components.graph import Graph


class Slider(object):
    def __init__(self, midtop, size, values):
        self.rect = pg.Rect((0, 0), size)
        self.rect.midtop = midtop
        self.values = values
        self.slider_tab_img = prepare.GFX["slider_tab"]
        self.slider_tab = self.slider_tab_img.get_rect(center=(self.rect.centerx, self.rect.centery + 5))
        self.val_width = (self.rect.width - self.slider_tab.width) // float(len(self.values) - 1)
        self.grabbed = False
        self.left_edge = self.rect.left + self.slider_tab.width // 2

    def get_event(self, event):
        if event.type == pg.MOUSEBUTTONDOWN:
            if self.slider_tab.collidepoint(event.pos):
                x, y = event.pos
                self.grabbed = True
                self.grab_offset = x - self.slider_tab.centerx

        elif event.type == pg.MOUSEBUTTONUP:
            self.grabbed = False
            self.grab_offset = 0

    def update(self, mouse_pos, sim_state):
        mx, my = mouse_pos
        if self.grabbed:
            self.slider_tab.centerx = mx - self.grab_offset
            self.slider_tab.clamp_ip(self.rect)
            val = self.slider_tab.centerx - self.left_edge
            indx = int(val // self.val_width)
            self.current_val = self.values[indx]
            sim_state.tick_length = self.current_val

    def draw(self, surface):
        pg.draw.rect(surface, (18, 38, 53), self.rect)
        pg.draw.line(surface, pg.Color("gray60"),
                           (self.rect.left, self.rect.centery + 5), (self.rect.right, self.rect.centery + 5), 2)
        surface.blit(self.slider_tab_img, self.slider_tab)


class FrameRect(object):
    def __init__(self, rect):
        self.rect = rect.inflate(16, 16)
        left = prepare.GFX["frame_left"]
        top = pg.transform.rotate(left, 270)
        tiles_high = self.rect.height // 8
        tiles_wide = self.rect.width // 8
        self.left_img = pg.Surface((8, self.rect.height))
        for y in range(0, self.rect.height, 8):
            self.left_img.blit(left, (0, y))
        self.top_img = pg.Surface((self.rect.width - 14, 8))
        for x in range(0, self.rect.width, 8):
            self.top_img.blit(top, (x, 0))
        self.right_img = pg.transform.flip(self.left_img, True, False)
        self.bottom_img = pg.transform.flip(self.top_img, False, True)
        self.corner_imgs = [
                pg.transform.rotate(prepare.GFX["frame_topleft"], x * 90)
                for x in range(4)]
        self.corners = [self.rect.topleft, (self.rect.left, self.rect.bottom - 16),
                              (self.rect.right - 16, self.rect.bottom - 16),
                              (self.rect.right - 16, self.rect.top)]

    def draw(self, surface):
        surface.blit(self.left_img, self.rect.topleft)
        surface.blit(self.right_img, (self.rect.right - 8, self.rect.top))
        surface.blit(self.top_img, (self.rect.left + 7, self.rect.top))
        surface.blit(self.bottom_img,
                         (self.rect.left + 7, self.rect.bottom - 8))
        for img, corner in zip(self.corner_imgs, self.corners):
            surface.blit(img, corner)


class Gameplay(tools._State):
    def __init__(self):
        super(Gameplay, self).__init__()
        self.tick_length = 200
        self.timer = 0
        self.bg_color = prepare.LIGHT_WATER
        self.frame_color = 167, 190, 206
        self.paused = False
        self.tick_lengths = [60, 70, 80, 90, 100, 120, 200, 300,
                                     400, 500, 1000, 2000, 5000]
        self.tick_index = 5
        self.dark_bg = (18, 38, 53)

    def startup(self, persistent):
        self.persist = persistent
        PARAMS = self.persist["PARAMS"]
        self.world_rect = pg.Rect(PARAMS["topleft"], PARAMS["size"])
        self.frame_rect = FrameRect(self.world_rect)
        self.world = WatorWorld(PARAMS)
        self.graph_frame = FrameRect(pg.Rect((176, 548), (960, 96)))
        self.graph = Graph((176, 548), (960, 96))
        self.icon_rect = pg.Rect(16, 16, 136, 100)
        self.icon_frame = FrameRect(self.icon_rect)
        self.reports = {"fish": [PARAMS["num fish"]],
                              "shark": [PARAMS["num sharks"]]}
        self.labels = pg.sprite.Group()

        self.make_icon_buttons()
        self.make_slider()
        b_size = 64, 16
        Button((self.speed_slider.rect.centerx - (b_size[0]//2),
                   self.speed_slider.rect.bottom + 16),
                   self.icons, idle_image=prepare.GFX["pause_button"],
                   call=self.pause_sim, bindings=[pg.K_SPACE])
        self.make_add_buttons()
        self.make_adjusters()

    def make_add_buttons(self):
        num_fish = self.persist["PARAMS"]["num fish"]
        num_sharks = self.persist["PARAMS"]["num sharks"]
        f_img = prepare.GFX["fish_button"]
        s_img = prepare.GFX["shark_button"]
        w, h = f_img.get_size()
        cx = self.icon_rect.centerx
        offset = 10
        top = 500
        self.fish_label = Label("{} Fish".format(num_fish),
                                        {"topright": (cx - offset, top)},
                                        self.labels, text_color=prepare.FISH_COLOR)
        self.shark_label = Label("{} Shark".format(num_sharks),
                                           {"topleft": (cx + offset, top)},
                                           self.labels, text_color=prepare.SHARK_COLOR)
        Button((cx - (offset + w), top + 20), self.icons, button_size=(w, h),
                   idle_image=f_img, call=self.add_fish)
        Button((cx + offset, top + 20), self.icons, button_size=(w, h),
                   idle_image=s_img, call=self.add_shark)

    def make_adjusters(self):
        self.adjusters = ButtonGroup()
        cx = self.icon_rect.centerx
        offset = 50
        style = {"button_size": prepare.GFX["arrow-left"].get_size()}
        Label("Fish Reproduce Age", {"midtop": (cx, 280)}, self.labels)
        self.fish_repro_label = Label("{}".format(self.world.fish_reproduce_age),
                                                  {"midtop": (cx, 300)}, self.labels)
        Button((cx-offset, 300), self.adjusters, idle_image=prepare.GFX["arrow-left"],
                   call=self.adjust_fish_reproduce_age, args=-1, **style)
        Button((cx+offset, 300), self.adjusters, idle_image=prepare.GFX["arrow-right"],
                   call=self.adjust_fish_reproduce_age, args=1, **style)
        Label("Shark Reproduce Age", {"midtop": (cx, 360)}, self.labels)
        self.shark_repro_label = Label("{}".format(self.world.shark_reproduce_age),
                                                    {"midtop": (cx, 380)}, self.labels)
        Button((cx-offset, 380), self.adjusters, idle_image=prepare.GFX["arrow-left"],
                   call=self.adjust_shark_reproduce_age, args=-1, **style)
        Button((cx+offset, 380), self.adjusters, idle_image=prepare.GFX["arrow-right"],
                   call=self.adjust_shark_reproduce_age, args=1, **style)
        Label("Shark Starvation Ticks", {"midtop": (cx, 440)}, self.labels)
        self.shark_starve_label = Label("{}".format(self.world.shark_starve_time),
                                                      {"midtop": (cx, 460)}, self.labels)
        Button((cx-offset, 460), self.adjusters, idle_image=prepare.GFX["arrow-left"],
                   call=self.adjust_shark_starve_time, args=-1, **style)
        Button((cx+offset, 460), self.adjusters, idle_image=prepare.GFX["arrow-right"],
                   call=self.adjust_shark_starve_time, args=1, **style)

    def add_fish(self, *args):
        self.world.add_fish()

    def add_shark(self, *args):
        self.world.add_shark()

    def adjust_fish_reproduce_age(self, amount):
        self.world.fish_reproduce_age += amount
        if self.world.fish_reproduce_age < 0:
            self.world.fish_reproduce_age = 0
        text = "{}".format(self.world.fish_reproduce_age)
        self.fish_repro_label.set_text(text)

    def adjust_shark_reproduce_age(self, amount):
        self.world.shark_reproduce_age += amount
        if self.world.shark_reproduce_age < 0:
            self.world.shark_reproduce_age = 0
        text = "{}".format(self.world.shark_reproduce_age)
        self.shark_repro_label.set_text(text)

    def adjust_shark_starve_time(self, amount):
        self.world.shark_starve_time += amount
        if self.world.shark_starve_time < 0:
            self.world.shark_starve_time = 0
        text = "{}".format(self.world.shark_starve_time)
        self.shark_starve_label.set_text(text)

    def pause_sim(self, *args):
        self.paused = not self.paused

    def make_slider(self):
        self.speed_slider = Slider((self.icon_rect.centerx, 150),
                                              (self.icon_rect.width, 40),
                                              self.tick_lengths[::-1])
        self.slider_frame = FrameRect(self.speed_slider.rect)
        Label("Simulation Speed",
                {"midtop": (self.speed_slider.rect.centerx,
                self.speed_slider.rect.top)}, self.labels)

    def make_icon_buttons(self):
        self.icons = ButtonGroup()
        shark_imgs = [prepare.GFX["shark{}".format(x)] for x in range(1, 16)]
        fish_imgs = [prepare.GFX["fish{}".format(x)] for x in range(1, 16)]
        Label("Shark Image",
                {"midtop": (self.icon_rect.centerx, self.icon_rect.top)},
                self.labels)
        top = 40
        left = 20
        for i, s in enumerate(shark_imgs):
            Button((left, top), self.icons, idle_image=s,
                       call=self.set_shark_img, args=s, button_size=(8, 8))
            left += 16
            if i == 7:
                left = 20
                top += 16
        Label("Fish Image", {"midtop": (self.icon_rect.centerx, 68)},
                self.labels)
        left = 20
        top = 90
        for i, f in enumerate(fish_imgs):
            Button((left, top), self.icons, idle_image=f,
                       call=self.set_fish_img, args=f, button_size=(8, 8))
            left += 16
            if i == 7:
                left = 20
                top += 16

    def change_tick_length(self, direction):
        indx = self.tick_index + direction
        if indx < 0:
            indx = 0
        elif indx > len(self.tick_lengths) - 1:
            indx = len(self.tick_lengths) - 1
        self.tick_index = indx
        self.tick_length = self.tick_lengths[self.tick_index]

    def set_shark_img(self, img):
        self.world.shark_img = img

    def set_fish_img(self, img):
        self.world.fish_img = img

    def get_event(self,event):
        if event.type == pg.QUIT:
            self.quit = True
        elif event.type == pg.KEYUP:
            if event.key == pg.K_ESCAPE:
                self.quit = True
        self.icons.get_event(event)
        self.adjusters.get_event(event)
        self.speed_slider.get_event(event)

    def report(self):
        num_sharks = len([x for x in self.world.grid.values()
                                    if x is not None and x[0] == "shark"])
        num_fish = len([x for x in self.world.grid.values()
                                if x is not None and x[0] == "fish"])
        self.reports["fish"].append(num_fish)
        self.reports["shark"].append(num_sharks)
        num = len(self.reports["fish"])
        if num > 2000:
            self.reports["fish"] = self.reports["fish"][num-2000:]
            self.reports["shark"] = self.reports["shark"][num-2000:]
        return num_fish, num_sharks

    def update(self, dt):
        mouse_pos = pg.mouse.get_pos()
        self.icons.update(mouse_pos)
        self.adjusters.update(mouse_pos)
        self.speed_slider.update(mouse_pos, self)
        if not self.paused:
            self.timer += dt
            while self.timer >= self.tick_length:
                self.timer -= self.tick_length
                self.world.update()
                num_fish, num_sharks = self.report()
                self.fish_label.set_text("{} Fish".format(num_fish))
                self.shark_label.set_text("{} Sharks".format(num_sharks))
        data_lines = [
                [self.world.fish_color, self.reports["fish"]],
                [self.world.shark_color, self.reports["shark"]]]
        self.graph.make_lines(data_lines)

    def draw(self, surface):
        surface.fill(self.bg_color)
        pg.draw.rect(surface, self.dark_bg, self.icon_rect)
        self.icons.draw(surface)
        self.speed_slider.draw(surface)
        self.labels.draw(surface)
        self.adjusters.draw(surface)
        self.slider_frame.draw(surface)
        self.icon_frame.draw(surface)
        self.world.draw(surface)
        self.graph.draw(surface)
        self.frame_rect.draw(surface)
        self.graph_frame.draw(surface)

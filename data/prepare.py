import os
import pygame as pg
from . import tools


SCREEN_SIZE = (1152, 656)
ORIGINAL_CAPTION = "Wa-Tor"

pg.mixer.pre_init(44100, -16, 1, 512)

pg.init()
os.environ['SDL_VIDEO_CENTERED'] = "TRUE"
pg.display.set_caption(ORIGINAL_CAPTION)
SCREEN = pg.display.set_mode(SCREEN_SIZE)
SCREEN_RECT = SCREEN.get_rect()

FISH_COLOR = 58, 170, 150
SHARK_COLOR = 211, 103, 103
WATER_COLOR = 18, 38, 53
LIGHT_WATER = 32, 70, 96

FONTS = tools.load_all_fonts(os.path.join("resources", "fonts"))
MUSIC = tools.load_all_music(os.path.join("resources", "music"))
SFX   = tools.load_all_sfx(os.path.join("resources", "sound"))
GFX   = tools.load_all_gfx(os.path.join("resources", "graphics"))
GFX["arrow-right"] = pg.transform.flip(GFX["arrow-left"], True, False)
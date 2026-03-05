#Game-wideconstantsanddefaultsettings(sharedacrossfiles)
import pygame

WIDTH, HEIGHT = 800, 600

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY  = (180, 180, 180)
BLUE  = (100, 150, 255)
GREEN = (0, 150, 0)
MAGENTA = (255, 0, 255)
GREY = (40, 40, 40)


#JSONfilesusedtopersistplayerprogress/settingsbetweenruns
SAVE_FILE = "data/save.json"
SETTINGS_FILE = "data/settings.json"
HIGH_SCORE_FILE = "data/highscore.json"

#Defaultkeybindsusedwhensettingsfiledoesntexist
DEFAULT_CONTROLS = {
    "up": pygame.K_UP,
    "down": pygame.K_DOWN,
    "left": pygame.K_LEFT,
    "right": pygame.K_RIGHT,
}


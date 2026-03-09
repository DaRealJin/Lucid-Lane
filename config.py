import pygame

# Screen resolution used throughout the game.
WIDTH, HEIGHT = 800, 600

# Reusable colour constants.
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY  = (180, 180, 180)
BLUE  = (100, 150, 255)
GREEN = (0, 150, 0)
MAGENTA = (255, 0, 255)
GREY = (40, 40, 40) # I made this by accident when I forgot I added GRAY in as well.

# File paths used for save data and settings.
SAVE_FILE = "data/save.json"
SETTINGS_FILE = "data/settings.json"
HIGH_SCORE_FILE = "data/highscore.json"

# Default movement controls used when no settings file exists.
DEFAULT_CONTROLS = {
    "up": pygame.K_UP,
    "down": pygame.K_DOWN,
    "left": pygame.K_LEFT,
    "right": pygame.K_RIGHT,
}

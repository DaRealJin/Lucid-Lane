import pygame
from config import WIDTH, HEIGHT, WHITE
from storage import load_controls
from ui_components import make_draw_bg
import menus

# Initialises pygame before any display or font code is used.
pygame.init()

# Creates the game window.
screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()
font = pygame.font.SysFont(None, 40)
pygame.display.set_caption("Lucid Lane")

# Loads and scales the menu background image.
background = pygame.image.load("Assets/NEA background image.png").convert()
background = pygame.transform.scale(background, (WIDTH, HEIGHT))

# Creates a dark transparent overlay so menu text is easier to read.
overlay = pygame.Surface((WIDTH, HEIGHT))
overlay.set_alpha(120)
overlay.fill((0, 0, 0))

# Creates a helper function that draws the background each frame.
draw_bg = make_draw_bg(background, overlay)

# Loads the saved controls.
controls = load_controls()

# Starts the main menu loop.
menus.menu(screen, clock, font, draw_bg, controls)


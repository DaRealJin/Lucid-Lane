import pygame
from config import WIDTH, HEIGHT, WHITE
from storage import load_controls
from ui_components import make_draw_bg
import menus  # your screens.py

pygame.init()
#Initialises pygame once; menus and game reuse the same window and clock
screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()
font = pygame.font.SysFont(None, 40)
pygame.display.set_caption("Lucid Lane")

#load background
background = pygame.image.load("Assets/NEA background image.png").convert()
background = pygame.transform.scale(background, (WIDTH, HEIGHT))

overlay = pygame.Surface((WIDTH, HEIGHT))
overlay.set_alpha(120)
overlay.fill((0, 0, 0))

draw_bg = make_draw_bg(background, overlay)
#Creates a reusable background draw function for all menu screens

controls = load_controls()
#Loads user-selected keybinds so the menu and game share the same control scheme

menus.menu(screen, clock, font, draw_bg, controls)

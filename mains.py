#Programentrypoint:initialisespygame,loadsassets,thenhandscontroltomenus
import pygame
from config import WIDTH, HEIGHT, WHITE
from storage import load_controls
from ui_components import make_draw_bg
import menus  # your screens.py

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()
font = pygame.font.SysFont(None, 40)
pygame.display.set_caption("Lucid Lane")

#load background
background = pygame.image.load("Assets/NEA background image.png").convert()
#convert()matchesdisplayformat(fasterblits)sincebackgroundhasnoalpha
background = pygame.transform.scale(background, (WIDTH, HEIGHT))

overlay = pygame.Surface((WIDTH, HEIGHT))
overlay.set_alpha(120)
#Darkoverlayimprovestextreadabilityoverbrightbackground
overlay.fill((0, 0, 0))

draw_bg = make_draw_bg(background, overlay)

controls = load_controls()
#Loadcustomkeybindssoallmenus/gameusesamecontrols

menus.menu(screen, clock, font, draw_bg, controls)
#Menuloopreturnsonlywhenuserquits

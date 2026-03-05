import pygame
import sys
from config import GRAY, BLUE, BLACK

class Button:
    #Simple clickable UI button used across menus
    def __init__(self, text, x, y, width, height):
        self.text = text
        self.rect = pygame.Rect(x, y, width, height)

    def draw(self, surface, font):
        #Highlights the button when the mouse is hovering over it
        colour = BLUE if self.rect.collidepoint(pygame.mouse.get_pos()) else GRAY
        pygame.draw.rect(surface, colour, self.rect)
        pygame.draw.rect(surface, BLACK, self.rect, 2)

        text_surface = font.render(self.text, True, BLACK)
        text_rect = text_surface.get_rect(center=self.rect.center)
        surface.blit(text_surface, text_rect)

    def clicked(self, event):
        #Returns True only on a left-mouse click inside the button rectangle
        return event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and self.rect.collidepoint(event.pos)

def make_draw_bg(background, overlay):
    #Returns a closure so menus can reuse the same background draw logic without duplicating code
    #returns a function you can call each frame
    def draw_bg(screen):
        screen.blit(background, (0, 0))
        screen.blit(overlay, (0, 0))
    return draw_bg

def simple_screen(screen, clock, font, draw_bg, text, text_colour):
    #Reusable screen loop for showing a single message and waiting for ESC(screen, clock, font, draw_bg, text, text_colour):
    while True:
        draw_bg(screen)

        title = font.render(text, True, text_colour)
        screen.blit(title, title.get_rect(center=(screen.get_width()//2, screen.get_height()//2)))

        hint = font.render("Press ESC to return", True, text_colour)
        screen.blit(hint, (20, 20))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                return

        pygame.display.update()
        clock.tick(60)
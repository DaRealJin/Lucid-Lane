#BaseSpriteclasswithimagecaching(avoidsre-loadingthesamePNGformanyentities)
import pygame
from camera import Camera

sprites = []
loaded = {}

class Sprite:
    def __init__(self, image_path, x, y):
        if image_path in loaded:
            #Reusethealready-loadedSurfaceforperformance
            self.image = loaded[image_path]
        else:
            img = pygame.image.load(image_path)
            if pygame.display.get_init() and pygame.display.get_surface() is not None:
                img = img.convert_alpha()
            loaded[image_path] = img
            self.image = img

        self.rect = self.image.get_rect(topleft=(x, y))
        sprites.append(self)
        #Globalregistry(usefulfordebug/optionalbatchupdates)

    def draw(self, screen):
        screen.blit(self.image, self.rect)

    def delete(self):
        if self in sprites:
            sprites.remove(self)

    def update(self):
        pass

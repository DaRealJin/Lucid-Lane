import pygame
from camera import Camera

# Global sprite registry.
sprites = []

# Cache for already-loaded images so the same file is not loaded repeatedly.
loaded = {}

class Sprite:
    def __init__(self, image_path, x, y):
        # Reuses a cached image when possible.
        if image_path in loaded:
            self.image = loaded[image_path]
        else:
            img = pygame.image.load(image_path)
            if pygame.display.get_init() and pygame.display.get_surface() is not None:
                img = img.convert_alpha()
            loaded[image_path] = img
            self.image = img

        # Creates the position rectangle for the sprite.
        self.rect = self.image.get_rect(topleft=(x, y))
        sprites.append(self)

    def draw(self, screen):
        # Draws the sprite at its current rectangle position.
        screen.blit(self.image, self.rect)

    def delete(self):
        # Removes the sprite from the global registry.
        if self in sprites:
            sprites.remove(self)

    def update(self):
        # Placeholder method for subclasses.
        pass

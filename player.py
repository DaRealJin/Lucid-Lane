import pygame
from sprite import Sprite
from storage import load_controls

class Player(Sprite):
    #Player sprite with movement controlled by configurable keybinds
    def __init__(self, image, x, y):
        super().__init__(image, x, y)

        self.movement_speed = 10
        self.controls = load_controls()
        #Uses saved settings so the player can choose WASD or arrow keys

    def update(self, tilemap=None):
        keys = pygame.key.get_pressed()

        dx = 0
        dy = 0

        #Movement
        if keys[self.controls["left"]]:
            dx -= self.movement_speed
        if keys[self.controls["right"]]:
            dx += self.movement_speed
        if keys[self.controls["up"]]:
            dy -= self.movement_speed
        if keys[self.controls["down"]]:
            dy += self.movement_speed

        #Move
        if tilemap:
            self.move_with_collision(dx, dy, tilemap)
        else:
            self.rect.x += dx
            self.rect.y += dy

    #Moves on each axis separately so collision resolution is simpler and more stable
    def move_with_collision(self, dx, dy, tilemap):
        self.rect.x += dx
        self.handle_collision(tilemap)

        self.rect.y += dy
        self.handle_collision(tilemap)

    #Stops the player entering solid tiles by snapping their rect away from walls
    def handle_collision(self, tilemap):
        corners = [
            (self.rect.left, self.rect.top),
            (self.rect.right - 1, self.rect.top),
            (self.rect.left, self.rect.bottom - 1),
            (self.rect.right - 1, self.rect.bottom - 1),
        ]

        for px, py in corners:
            tx = px // tilemap.TILE
            ty = py // tilemap.TILE

            if not (0 <= tx < tilemap.COLS and 0 <= ty < tilemap.ROWS):
                continue

            tile_type = tilemap.grid[ty][tx]

            if tilemap.is_solid_tile(tile_type):
                tile_rect = pygame.Rect(
                    tx * tilemap.TILE,
                    ty * tilemap.TILE,
                    tilemap.TILE,
                    tilemap.TILE
                )

                if self.rect.colliderect(tile_rect):
                    dx_left = tile_rect.right - self.rect.left
                    dx_right = self.rect.right - tile_rect.left
                    dy_top = tile_rect.bottom - self.rect.top
                    dy_bottom = self.rect.bottom - tile_rect.top

                    min_push = min(dx_left, dx_right, dy_top, dy_bottom)

                    if min_push == dx_left:
                        self.rect.left = tile_rect.right
                    elif min_push == dx_right:
                        self.rect.right = tile_rect.left
                    elif min_push == dy_top:
                        self.rect.top = tile_rect.bottom
                    else:
                        self.rect.bottom = tile_rect.top
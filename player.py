import pygame
from sprite import Sprite
from storage import load_controls

class Player(Sprite):
    def __init__(self, image, x, y):
        # Calls the shared Sprite constructor.
        super().__init__(image, x, y)

        # Character's movement speed per frame.
        self.movement_speed = 2

        # Loads the current saved movement controls.
        self.controls = load_controls()

    def update(self, tilemap=None):
        # Reads the keyboard state every frame.
        keys = pygame.key.get_pressed()

        dx = 0
        dy = 0

        # Converts key input into x and y movement values.
        if keys[self.controls["left"]]:
            dx -= self.movement_speed
        if keys[self.controls["right"]]:
            dx += self.movement_speed
        if keys[self.controls["up"]]:
            dy -= self.movement_speed
        if keys[self.controls["down"]]:
            dy += self.movement_speed

        # Uses collision-based movement when a collision map is provided.
        if tilemap:
            self.move_with_collision(dx, dy, tilemap)
        else:
            self.rect.x += dx
            self.rect.y += dy

    def move_with_collision(self, dx, dy, tilemap):
        # Handles horizontal and vertical movement separately for cleaner collision resolution.
        self.rect.x += dx
        self.handle_collision(tilemap)

        self.rect.y += dy
        self.handle_collision(tilemap)

    def handle_collision(self, tilemap):
        # Checks the four corners of the player rectangle against the tilemap.
        corners = [
            (self.rect.left, self.rect.top),
            (self.rect.right - 1, self.rect.top),
            (self.rect.left, self.rect.bottom - 1),
            (self.rect.right - 1, self.rect.bottom - 1),
        ]

        for px, py in corners:
            tx = px // tilemap.TILE
            ty = py // tilemap.TILE

            # Ignores coordinates outside the map bounds.
            if not (0 <= tx < tilemap.COLS and 0 <= ty < tilemap.ROWS):
                continue

            tile_type = tilemap.grid[ty][tx]

            # Only solid tiles block movement.
            if tilemap.is_solid_tile(tile_type):
                tile_rect = pygame.Rect(
                    tx * tilemap.TILE,
                    ty * tilemap.TILE,
                    tilemap.TILE,
                    tilemap.TILE
                )

                if self.rect.colliderect(tile_rect):
                    # Measures overlap from all four sides.
                    dx_left = tile_rect.right - self.rect.left
                    dx_right = self.rect.right - tile_rect.left
                    dy_top = tile_rect.bottom - self.rect.top
                    dy_bottom = self.rect.bottom - tile_rect.top

                    # Smallest overlap shows the easiest direction to push the player out.
                    min_push = min(dx_left, dx_right, dy_top, dy_bottom)

                    if min_push == dx_left:
                        self.rect.left = tile_rect.right
                    elif min_push == dx_right:
                        self.rect.right = tile_rect.left
                    elif min_push == dy_top:
                        self.rect.top = tile_rect.bottom
                    else:
                        self.rect.bottom = tile_rect.top

import pygame
from sprite import Sprite

class Zombie(Sprite):
    def __init__(self, x, y):

        # Calls the parent Sprite constructor and starts with the front-facing image of the zombie.
        super().__init__("Assets/Zombie_front.png", x, y)

        # Loads a different sprite for each movement direction.
        self.images = {
            "down": pygame.image.load("Assets/Zombie_front.png").convert_alpha(),
            "up": pygame.image.load("Assets/Zombie_behind.png").convert_alpha(),
            "left": pygame.image.load("Assets/Zombie_left.png").convert_alpha(),
            "right": pygame.image.load("Assets/Zombie_right.png").convert_alpha(),
        }

        # Stores the current facing direction.
        self.direction = "down"

        # Movement speed in pixels per frame.
        self.speed = 2

        # Target pixel position used for step-by-step movement.
        self.target_px = self.rect.x
        self.target_py = self.rect.y

        # Timer that delays how often the AI makes a new movement choice.
        self.think_timer = 0

        # Number of frames between AI decisions.
        self.think_every = 20

        # Original spawn position so the zombie can return after losing the player.
        self.spawn_px = x
        self.spawn_py = y

        # Distance in tiles before the zombie starts chasing.
        self.aggro_radius = 8

        # Current AI state.
        # idle = waiting
        # chase = following the player
        # return = moving back to spawn
        self.state = "idle"


    def set_dir_image(self, d):
        # Updates the image only when the direction changes.
        if d != self.direction:
            self.direction = d
            self.image = self.images[d]


    def is_moving(self):
        # Returns True while the zombie has not yet reached its target tile.
        return self.rect.x != self.target_px or self.rect.y != self.target_py


    def update(self, grid, tilemap, player):

        # Continues moving toward the current target before choosing a new action.
        if self.is_moving():
            self._move_to_target()
            return

        # Runs the AI only every few frames instead of every single frame.
        self.think_timer += 1
        if self.think_timer < self.think_every:
            return
        self.think_timer = 0

        # Zombie tile position.
        zx = self.rect.centerx // tilemap.TILE
        zy = self.rect.centery // tilemap.TILE

        # Player tile position.
        px = player.rect.centerx // tilemap.TILE
        py = player.rect.centery // tilemap.TILE

        # Distance is used to measure how close the player is.
        distance = abs(px - zx) + abs(py - zy)

        # State transitions for the AI.
        if self.state == "idle":
            if distance <= self.aggro_radius:
                self.state = "chase"

        elif self.state == "chase":
            if distance > self.aggro_radius:
                self.state = "return"

        elif self.state == "return":
            spawn_tx = self.spawn_px // tilemap.TILE
            spawn_ty = self.spawn_py // tilemap.TILE
            if zx == spawn_tx and zy == spawn_ty:
                self.state = "idle"

        # Chooses the target tile based on the current state.
        if self.state == "chase":
            target_tx, target_ty = px, py

        elif self.state == "return":
            target_tx = self.spawn_px // tilemap.TILE
            target_ty = self.spawn_py // tilemap.TILE

        else:
            return

        # Attempts to move one tile toward the selected target.
        self._step_toward(grid, tilemap, target_tx, target_ty)


    def _step_toward(self, grid, tilemap, target_tx, target_ty):

        # Current zombie tile position.
        zx = self.rect.centerx // tilemap.TILE
        zy = self.rect.centery // tilemap.TILE

        dx = target_tx - zx
        dy = target_ty - zy

        options = []

        # Adds preferred movement directions first so the zombie heads toward the target.
        if abs(dx) > abs(dy):
            if dx > 0: options.append(("right", zx + 1, zy))
            if dx < 0: options.append(("left",  zx - 1, zy))
            if dy > 0: options.append(("down",  zx, zy + 1))
            if dy < 0: options.append(("up",    zx, zy - 1))
        else:
            if dy > 0: options.append(("down",  zx, zy + 1))
            if dy < 0: options.append(("up",    zx, zy - 1))
            if dx > 0: options.append(("right", zx + 1, zy))
            if dx < 0: options.append(("left",  zx - 1, zy))

        # Backup directions are added afterward in case the preferred path is blocked.
        options += [("right", zx + 1, zy), ("left", zx - 1, zy), ("down", zx, zy + 1), ("up", zx, zy - 1)]

        # Chooses the first valid walkable direction.
        for d, nx, ny in options:
            if self._walkable(grid, tilemap, nx, ny):
                self.set_dir_image(d)
                self.target_px = nx * tilemap.TILE
                self.target_py = ny * tilemap.TILE
                break

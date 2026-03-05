#EnemyAI(Zombie):simplechase/returnstate-machine(noA*pathfinding)
import pygame
from sprite import Sprite

class Zombie(Sprite):
    def __init__(self, x, y):
        #Start facing down
        super().__init__("Assets/Zombie_front.png", x, y)

        #Direction sprites
        self.images = {
            "down": pygame.image.load("Assets/Zombie_front.png").convert_alpha(),
            "up": pygame.image.load("Assets/Zombie_behind.png").convert_alpha(),
            "left": pygame.image.load("Assets/Zombie_left.png").convert_alpha(),
            "right": pygame.image.load("Assets/Zombie_right.png").convert_alpha(),
        }
        self.direction = "down"
        self.speed = 2
        self.target_px = self.rect.x
        self.target_py = self.rect.y
        self.think_timer = 0
        #Thinktimerreduceshowoftenwepickanewtargetdirection(preventsjitter)
        self.think_every = 20
        self.spawn_px = x
        #Usedtoreturntospawnwhentheplayerescapes
        self.spawn_py = y
        self.aggro_radius = 8
        self.state = "idle"

    def set_dir_image(self, d):
        if d != self.direction:
            self.direction = d
            self.image = self.images[d]

    def is_moving(self):
        return self.rect.x != self.target_px or self.rect.y != self.target_py

    def update(self, grid, tilemap, player):
        #State-drivenbehaviour:idle->chase->return
        #If currently moving toward a tile, keep moving
        if self.is_moving():
            self._move_to_target()
            return

        #Only decide a new move every N frames
        self.think_timer += 1
        if self.think_timer < self.think_every:
            return
        self.think_timer = 0
        #Thinktimerreduceshowoftenwepickanewtargetdirection(preventsjitter)

        #Tile positions
        zx = self.rect.centerx // tilemap.TILE
        zy = self.rect.centery // tilemap.TILE
        px = player.rect.centerx // tilemap.TILE
        py = player.rect.centery // tilemap.TILE

        distance = abs(px - zx) + abs(py - zy)

        #State changes
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

        #Behaviour target
        if self.state == "chase":
            target_tx, target_ty = px, py
        elif self.state == "return":
            target_tx = self.spawn_px // tilemap.TILE
            target_ty = self.spawn_py // tilemap.TILE
        else:
            return

        #One step at a time
        self._step_toward(grid, tilemap, target_tx, target_ty)

    def _step_toward(self, grid, tilemap, target_tx, target_ty):
        zx = self.rect.centerx // tilemap.TILE
        zy = self.rect.centery // tilemap.TILE

        dx = target_tx - zx
        dy = target_ty - zy

        options = []
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
        options += [("right", zx + 1, zy), ("left", zx - 1, zy), ("down", zx, zy + 1), ("up", zx, zy - 1)]

        for d, nx, ny in options:
            if self._walkable(grid, tilemap, nx, ny):
                self.set_dir_image(d)
                self.target_px = nx * tilemap.TILE
                self.target_py = ny * tilemap.TILE
                break

    def _walkable(self, grid, tilemap, tx, ty):
        if ty < 0 or ty >= len(grid) or tx < 0 or tx >= len(grid[0]):
            return False
        ch = grid[ty][tx]

        if hasattr(tilemap, "is_solid_tile"):
            return not tilemap.is_solid_tile(ch)
        return ch not in ("#", "T")

    def _move_to_target(self):
        dx = self.target_px - self.rect.x
        dy = self.target_py - self.rect.y

        if dx != 0:
            self.rect.x += self.speed if dx > 0 else -self.speed
            if (dx > 0 and self.rect.x > self.target_px) or (dx < 0 and self.rect.x < self.target_px):
                self.rect.x = self.target_px

        if dy != 0:
            self.rect.y += self.speed if dy > 0 else -self.speed
            if (dy > 0 and self.rect.y > self.target_py) or (dy < 0 and self.rect.y < self.target_py):
                self.rect.y = self.target_py
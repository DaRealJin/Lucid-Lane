#Tilemaploader/drawer:mapsaretxtgridswhereeachcharrepresentsatile
import os
import pygame
from config import GREEN, MAGENTA

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TILE = 32
#EachmapcharacterisdrawnasoneTILExTILEimage

def load_tile_images():
    def load(rel_path):
        full = os.path.join(BASE_DIR, rel_path)
        img = pygame.image.load(full).convert_alpha()
        return pygame.transform.scale(img, (TILE, TILE))

    return {
        ".": load("Assets/grass.png"),
        "m": load("Assets/Mud.png"),
        "D": load("Assets/Door.png"),
        "#": load("Assets/grass_wall.png"),
        "P": load("Assets/grass.png"),
        "l": load("Assets/grass_path_left.png"),
        "r": load("Assets/grass_path_right.png"),
        "c": load("Assets/Checkpoint.png"),
        "M": load("Assets/grass_path_middle.png"),
        "T": load("Assets/grass_wall_top.png"),
        "B": load("Assets/Zombie_Boss.png")

    }

def load_map(area_name):
    #Loadsadata/areas/<area>.txtfileandreturnslistofstrings(rows)
    path = os.path.join(BASE_DIR, "data", "areas", f"{area_name}.txt")
    with open(path, "r", encoding="utf-8") as f:
        lines = [line.rstrip("\n") for line in f]
    while lines and lines[-1] == "":
        lines.pop()

    return lines

def find_spawn(grid):
    for y, row in enumerate(grid):
        for x, ch in enumerate(row):
            if ch == "P":
                return x * TILE, y * TILE
    return 0, 0

def draw_map(screen, grid, tiles, cam):
    scaled_tile_size = int(TILE * cam.zoom)

    for y, row in enumerate(grid):
        for x, ch in enumerate(row):

            world_x = x * TILE
            world_y = y * TILE

            sx, sy = cam.apply_pos(world_x, world_y)

            if sx < -scaled_tile_size or sy < -scaled_tile_size:
                continue
            if sx > screen.get_width() or sy > screen.get_height():
                continue

            base_tile = tiles["."]
            base_scaled = pygame.transform.scale(
                base_tile,
                (scaled_tile_size, scaled_tile_size)
            )
            screen.blit(base_scaled, (sx, sy))

            if ch in tiles and ch != ".":
                overlay_scaled = pygame.transform.scale(
                    tiles[ch],
                    (scaled_tile_size, scaled_tile_size)
                )
                screen.blit(overlay_scaled, (sx, sy))
DOOR_LINKS = {
#Doorlinksuse(world,tx,ty)->(next_world,spawn_tx,spawn_ty)
    #Entrance <> Path
    ("l1_plains_entrance", 23, 16): ("l1_plains_path", 2, 2),
    ("l1_plains_path", 2, 2): ("l1_plains_entrance", 23, 16),

    #Path <> Boss
    ("l1_plains_path", 23, 16): ("l1_plains_boss", 3, 2),
    ("l1_plains_boss", 3, 2): ("l1_plains_path", 23, 16),

    #Boss > Path
    ("l1_plains_boss", 23, 3): ("l1_plains_path", 2, 2),
}



def tile_under_player(player, grid):
    tx = player.rect.centerx // TILE
    ty = player.rect.centery // TILE
    if 0 <= ty < len(grid) and 0 <= tx < len(grid[0]):
        return grid[ty][tx]
    return "#"

def world_size(grid):
    rows = len(grid)
    cols = len(grid[0]) if rows else 0
    return cols * TILE, rows * TILE

SOLID_TILES = {"#", "T"}
#Characterslistedhereblockmovement

def is_solid_tile(ch: str) -> bool:
    return ch in SOLID_TILES

class CollisionMap:
    #Collisionchecksusegridcharacters(betterthansamplingpixels)
    def __init__(self, grid):
        self.grid = grid
        self.TILE = TILE
        self.ROWS = len(grid)
        self.COLS = len(grid[0]) if self.ROWS else 0

    def is_solid_tile(self, ch: str) -> bool:
        return is_solid_tile(ch)
    
    
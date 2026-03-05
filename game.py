import pygame
from player import Player
from config import WIDTH, HEIGHT, BLACK, WHITE, GREY
import tilemap
from camera import Camera
from storage import save_checkpoint, load_checkpoint
from enemy import Zombie
from battle import Battle

def find_zombies(grid, TILE):
    spawns = []
    new_grid = []
    for y, row in enumerate(grid):
        row_list = list(row)
        for x, ch in enumerate(row_list):
            if ch == "Z":
                spawns.append((x * TILE, y * TILE))
                row_list[x] = "."  
        new_grid.append("".join(row_list))
    return spawns, new_grid

checkpoint_prompt = False
checkpoint_choice = 0  #Where 0 = Yes, 1 = No

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()

#Load tiles
tiles = tilemap.load_tile_images()

#Load first area
current_area = "l1_plains_entrance"
grid = tilemap.load_map(current_area)
collision_map = tilemap.CollisionMap(grid)
z_spawns, grid = find_zombies(grid, tilemap.TILE)
zombies = [Zombie(x, y) for x, y in z_spawns]

collision_map = tilemap.CollisionMap(grid)
world_w, world_h = tilemap.world_size(grid)

print("GRID ROWS:", len(grid))
print("FIRST ROW:", grid[0] if grid else "EMPTY GRID")

#Create camera
zoom = 1
cam = Camera(WIDTH, HEIGHT, zoom=zoom)

#World size
world_w, world_h = tilemap.world_size(grid)

#Spawns da player
spawn_x, spawn_y = tilemap.find_spawn(grid)
player = Player("Assets/Character.png", spawn_x, spawn_y)
in_battle = False
battle = None
collided_zombie = None
running = True
while running:
    interacted = False
    load_pressed = False

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if in_battle:
                battle.handle_event(event)
                continue

        if event.type == pygame.KEYDOWN:
            if checkpoint_prompt:
                if event.key == player.controls["left"]:
                    checkpoint_choice = 0
                elif event.key == player.controls["right"]:
                    checkpoint_choice = 1
                elif event.key == pygame.K_e:
                    #Confirm choices
                    if checkpoint_choice == 0:
                        tx = player.rect.centerx // tilemap.TILE
                        ty = player.rect.centery // tilemap.TILE
                        save_checkpoint(current_area, tx, ty)
                    checkpoint_prompt = False

            else:
                #Normal gameplay input
                if event.key == pygame.K_e:
                    interacted = True
                elif event.key == pygame.K_l:
                    load_pressed = True

    if in_battle:
        battle.update()
        battle.draw(screen)

        #Exit battle results
        if battle.is_over():
            result = battle.end_result

            if result == "run":
    #Push player away so you don't instantly re-collide
                player.rect.x -= 40
                collided_zombie = None
                in_battle = False
                battle = None

            elif result == "win":
                if collided_zombie in zombies:
                    zombies.remove(collided_zombie)
                collided_zombie = None
                in_battle = False
                battle = None

            elif result == "lose":
                #GAME OVER SCREEN - MUST ADD LATER
                in_battle = False
                battle = None

            pygame.display.flip()
            clock.tick(60)
            continue



    #Load checkpoint (L)
    if load_pressed:
        cp = load_checkpoint()
        if cp:
            current_area = cp["area"]
            grid = tilemap.load_map(current_area)
            collision_map = tilemap.CollisionMap(grid)
            world_w, world_h = tilemap.world_size(grid)
            player.rect.topleft = (cp["tx"] * tilemap.TILE, cp["ty"] * tilemap.TILE)

    #Update player only if popup not open
    if not checkpoint_prompt:
        player.update(collision_map)

    #Interactions (E)
    if interacted:
        tx = player.rect.centerx // tilemap.TILE
        ty = player.rect.centery // tilemap.TILE

        if 0 <= ty < len(grid) and 0 <= tx < len(grid[0]):
            standing_tile = grid[ty][tx]

            #Checkpoint tile (c)
            if standing_tile == "c":
                checkpoint_prompt = True
                checkpoint_choice = 0

            #Door tile (D)
            if standing_tile == "D":
                key = (current_area, tx, ty)
                if key in tilemap.DOOR_LINKS:
                    next_area, spawn_tx, spawn_ty = tilemap.DOOR_LINKS[key]

                    current_area = next_area
                    grid = tilemap.load_map(current_area)
                    collision_map = tilemap.CollisionMap(grid)
                    world_w, world_h = tilemap.world_size(grid)

                    player.rect.topleft = (spawn_tx * tilemap.TILE, spawn_ty * tilemap.TILE)

    #Camera follows after movement/teleport
    cam.follow(player.rect, world_w, world_h)

    screen.fill(BLACK)
    tilemap.draw_map(screen, grid, tiles, cam)

        #Update zombies
    for z in zombies:
        z.update(grid, tilemap, player)

     #START BATTLE ON COLLISION
    if not in_battle:
        for z in zombies:
            if player.rect.colliderect(z.rect):
                collided_zombie = z

                player_stats = {"hp": 100, "max_hp": 100, "energy": 50, "max_energy": 50}
                enemy_list = [
                    {"name": "Enemy 1", "hp": 30, "max_hp": 30},
                    {"name": "Enemy 2", "hp": 30, "max_hp": 30},
                    {"name": "Enemy 3", "hp": 30, "max_hp": 30},
            ]

                battle = Battle(player_stats, enemy_list)
                in_battle = True
                break

    
    
    
    
    
    #Draw zombies
    for z in zombies:
        z_screen_rect = cam.apply_rect(z.rect)
        z_scaled = pygame.transform.scale(
            z.image,
            (int(z_screen_rect.width), int(z_screen_rect.height))
        )
        screen.blit(z_scaled, z_screen_rect.topleft)

    player_screen_rect = cam.apply_rect(player.rect)
    player_scaled = pygame.transform.scale(
        player.image,
        (int(player_screen_rect.width), int(player_screen_rect.height))
    )
    screen.blit(player_scaled, player_screen_rect.topleft)
     
    #Checkpoint popup UI
    if checkpoint_prompt:
        panel = pygame.Rect(200, 450, 400, 120)
        pygame.draw.rect(screen, (GREY), panel)
        pygame.draw.rect(screen, (WHITE), panel, 2)

        font = pygame.font.SysFont(None, 36)
        text = font.render("Save checkpoint?", True, (WHITE))
        screen.blit(text, (panel.x + 40, panel.y + 15))

        yes_rect = pygame.Rect(panel.x + 70, panel.y + 60, 110, 40)
        no_rect  = pygame.Rect(panel.x + 220, panel.y + 60, 110, 40)

        #Highlight box
        if checkpoint_choice == 0:
            pygame.draw.rect(screen, (WHITE), yes_rect, 2)
        else:
            pygame.draw.rect(screen, (WHITE), no_rect, 2)

        screen.blit(font.render("Yes", True, (WHITE)), (yes_rect.x + 25, yes_rect.y + 5))
        screen.blit(font.render("No",  True, (WHITE)), (no_rect.x + 35,  no_rect.y + 5))

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
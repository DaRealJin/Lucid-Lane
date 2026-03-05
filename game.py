#Overworldloopwrappedasrun_game()whenlaunchedfrommenus
import pygame
from player import Player
from config import WIDTH, HEIGHT, BLACK, WHITE, GREY
import tilemap
from camera import Camera
from storage import save_checkpoint, load_checkpoint
from enemy import Zombie
from battle import Battle
from boss import make_boss, make_minion

dead_zombies = {}
respawn_queue = []
#Entriesare(spawn_time_ms,area,tx,ty)soenemiescanrespawnafterdelay

def enter_area(area_name, spawn_tx=None, spawn_ty=None):
    global current_area, grid, collision_map, world_w, world_h, zombies

    current_area = area_name

    #Load map
    grid_raw = tilemap.load_map(current_area)

    #Find Z spawns and remove Z tiles
    z_spawns, grid_clean = find_zombies(grid_raw, tilemap.TILE)

    #Update global grid + collision + world size
    grid = grid_clean
    collision_map = tilemap.CollisionMap(grid)
    world_w, world_h = tilemap.world_size(grid)

    #Spawn zombies for this area (skip dead ones)
    zombies = []
    if current_area not in dead_zombies:
        dead_zombies[current_area] = []

    for px, py, tx, ty in z_spawns:
        if (tx, ty) not in dead_zombies[current_area]:
            z = Zombie(px, py)
            z.spawn_tx = tx
            z.spawn_ty = ty
            zombies.append(z)

    #Move player if needed
    if spawn_tx is not None and spawn_ty is not None:
        player.rect.topleft = (spawn_tx * tilemap.TILE, spawn_ty * tilemap.TILE)

    print("Entered:", current_area, "Zombies:", len(zombies))

def find_zombies(grid, TILE):
    spawns = []
    new_grid = []
    for y, row in enumerate(grid):
        row_list = list(row)
        for x, ch in enumerate(row_list):
            if ch == "Z":
                spawns.append((x * TILE, y * TILE, x, y))
                row_list[x] = "."  
        new_grid.append("".join(row_list))
    return spawns, new_grid

checkpoint_prompt = False
checkpoint_choice = 0  #Where 0 = Yes, 1 = No

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()

def show_ending_screen(screen, clock):
#Calledafterbossdefeat;blocksuntilplayerexits
    font=pygame.font.SysFont(None,72)
    small=pygame.font.SysFont(None,32)

    def draw_bg(scr):
        scr.fill((WHITE))

    while True:
        draw_bg(screen)

        title=font.render("YOU ESCAPED!",True,(BLACK))
        screen.blit(title,title.get_rect(center=(WIDTH//2,HEIGHT//2-40)))

        hint=small.render("Press ESC to quit",True,(BLACK))
        screen.blit(hint,hint.get_rect(center=(WIDTH//2,HEIGHT//2+40)))

        for event in pygame.event.get():
            if event.type==pygame.QUIT:
                pygame.quit()
                raise SystemExit
            if event.type==pygame.KEYDOWN and event.key==pygame.K_ESCAPE:
                pygame.quit()
                raise SystemExit

        pygame.display.flip()
        clock.tick(60)

#Load tiles
tiles = tilemap.load_tile_images()

#Load first area
current_area = "l1_plains_entrance"
grid = tilemap.load_map(current_area)
collision_map = tilemap.CollisionMap(grid)
enter_area("l1_plains_entrance")

#Spawns da player
spawn_x, spawn_y = tilemap.find_spawn(grid)
player = Player("Assets/Character.png", spawn_x, spawn_y)

collision_map = tilemap.CollisionMap(grid)
world_w, world_h = tilemap.world_size(grid)

print("GRID ROWS:", len(grid))
print("FIRST ROW:", grid[0] if grid else "EMPTY GRID")

#Create camera
zoom = 1
cam = Camera(WIDTH, HEIGHT, zoom=zoom)

#World size
world_w, world_h = tilemap.world_size(grid)

in_battle = False
battle = None
boss_battle=False
collided_zombie = None
running = True
while running:
    interacted = False
    load_pressed = False

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if in_battle and battle is not None:
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
    #Safety: battle must exist
        if battle is None:
            in_battle = False
        else:
            battle.update()
            battle.draw(screen)

        #Only handle results when the battle is actually over
            if battle.is_over():
                result = battle.end_result

                if result == "run":
                #Push player away so you don't instantly re-collide
                    player.rect.x -= 40

                elif result == "win":
                    if boss_battle:
                        show_ending_screen(screen,clock)
                    if collided_zombie in zombies:
                        tx = collided_zombie.spawn_tx
                        ty = collided_zombie.spawn_ty

                        if current_area not in dead_zombies:
                            dead_zombies[current_area] = []

                        respawn_queue.append((pygame.time.get_ticks(), current_area, tx, ty))
                        zombies.remove(collided_zombie)

                #clear battle state for ALL results
                collided_zombie = None
                in_battle = False
                battle = None

            pygame.display.flip()
            clock.tick(60)
            continue


    #Load checkpoint (L)
    if load_pressed:
        cp = load_checkpoint()
        if cp:
            enter_area(cp["area"], cp["tx"], cp["ty"])

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

            #Boss tile (B)
            if standing_tile == "B":
                player_stats = {
                    "hp": 100,
                    "max_hp": 100,
                    "energy": 50,
                    "max_energy": 50
                }

                enemy_list = [make_boss()]

                battle = Battle(player_stats, enemy_list)
                in_battle = True
                boss_battle=True

            #Door tile (D)
            if standing_tile == "D":
                key = (current_area, tx, ty)
                if key in tilemap.DOOR_LINKS:
                    next_area, spawn_tx, spawn_ty = tilemap.DOOR_LINKS[key]
                    enter_area(next_area, spawn_tx, spawn_ty)

    #Camera follows after movement/teleport
    cam.follow(player.rect, world_w, world_h)

    screen.fill(BLACK)
    tilemap.draw_map(screen, grid, tiles, cam)

    #Respawn zombies after 20 seconds
    current_time = pygame.time.get_ticks()

    for item in respawn_queue[:]:
        spawn_time, area, tx, ty = item

        if current_time - spawn_time >= 20000:  #20 seconds
            if area == current_area:
                px = tx * tilemap.TILE
                py = ty * tilemap.TILE

                z = Zombie(px, py)
                z.spawn_tx = tx
                z.spawn_ty = ty

                zombies.append(z)
    
            respawn_queue.remove(item)

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
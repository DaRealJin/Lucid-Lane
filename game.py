import pygame
from player import Player
from config import WIDTH, HEIGHT, BLACK, WHITE
import tilemap
from camera import Camera
from storage import save_checkpoint, load_checkpoint, save_high_score, load_high_score
from enemy import Zombie
from battle import Battle
from boss import make_boss

# Global world state used by the area-loading system.
current_area = None
grid = None
collision_map = None
world_w = 0
world_h = 0
zombies = []

# Stores zombies that should respawn later.
# Format: (spawn_time_ms, area, tx, ty)
respawn_queue = []


def find_zombies(grid_lines, TILE):
    # Scans the map text for Z markers and converts them into zombie spawn positions.
    spawns = []
    new_grid = []
    for y, row in enumerate(grid_lines):
        row_list = list(row)
        for x, ch in enumerate(row_list):
            if ch == "Z":
                spawns.append((x * TILE, y * TILE, x, y))
                row_list[x] = "."
        new_grid.append("".join(row_list))
    return spawns, new_grid


def enter_area(area_name, player, spawn_tx=None, spawn_ty=None):
    global current_area, grid, collision_map, world_w, world_h, zombies

    # Updates the current area name.
    current_area = area_name

    # Loads the raw text map for the selected area.
    grid_raw = tilemap.load_map(current_area)

    # Finds zombie spawns and removes the Z markers from the drawn map.
    z_spawns, grid_clean = find_zombies(grid_raw, tilemap.TILE)

    # Rebuilds map-related global state.
    grid = grid_clean
    collision_map = tilemap.CollisionMap(grid)
    world_w, world_h = tilemap.world_size(grid)

    # Creates a fresh zombie list for the new area.
    zombies = []
    for px, py, tx, ty in z_spawns:
        z = Zombie(px, py)
        z.spawn_tx = tx
        z.spawn_ty = ty
        zombies.append(z)

    # Teleports the player if a specific spawn tile was supplied.
    if spawn_tx is not None and spawn_ty is not None:
        player.rect.topleft = (spawn_tx * tilemap.TILE, spawn_ty * tilemap.TILE)

    print("Entered:", current_area, "Zombies:", len(zombies))


def show_ending_screen(screen, clock):
    # Displays the ending screen until quit or Escape is pressed.
    font = pygame.font.SysFont(None, 72)
    small = pygame.font.SysFont(None, 32)

    while True:
        screen.fill(WHITE)

        title = font.render("YOU ESCAPED!", True, BLACK)
        screen.blit(title, title.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 40)))

        hint = small.render("Press ESC to quit", True, BLACK)
        screen.blit(hint, hint.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 40)))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                raise SystemExit
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                pygame.quit()
                raise SystemExit

        pygame.display.flip()
        clock.tick(60)


def run_game(screen, clock, difficulty):
    global respawn_queue

    # Clears run-specific state when a new game starts.
    respawn_queue = []

    # Difficulty changes player health, enemy damage, and score multiplier.
    if difficulty == "Easy":
        player_hp = 140
        enemy_dmg = 3
        score_mult = 1
    elif difficulty == "Hard":
        player_hp = 90
        enemy_dmg = 6
        score_mult = 3
    else:
        player_hp = 110
        enemy_dmg = 4
        score_mult = 2

    # Score starts at zero each run.
    score = 0

    # Loads all tile graphics.
    tiles = tilemap.load_tile_images()

    # Creates the player at the map spawn point.
    first_area_raw = tilemap.load_map("l1_plains_entrance")
    spawn_x, spawn_y = tilemap.find_spawn(first_area_raw)
    player = Player("Assets/Character.png", spawn_x, spawn_y)

    # Loads the first playable area.
    enter_area("l1_plains_entrance", player)

    # Camera starts zoomed in.
    cam = Camera(WIDTH, HEIGHT, zoom=2)

    # Battle-related state flags.
    in_battle = False
    battle = None
    boss_battle = False
    collided_zombie = None

    running = True
    while running:
        interacted = False
        load_pressed = False

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "quit"

            # During battle, all events are sent to the battle system instead.
            if in_battle and battle is not None:
                battle.handle_event(event)
                continue

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_e:
                    interacted = True
                elif event.key == pygame.K_l:
                    load_pressed = True

        # Battle loop replaces the normal overworld loop while active.
        if in_battle and battle is not None:
            battle.update()
            battle.draw(screen)

            if battle.is_over():
                result = battle.end_result

                if result == "win":
                    # Winning the boss battle ends the game and updates high score.
                    if boss_battle:
                        score += 500 * score_mult
                        hs = load_high_score()
                        if score > hs:
                            save_high_score(score)
                        show_ending_screen(screen, clock)

                    # Normal enemies give score and are queued for later respawn.
                    if collided_zombie in zombies:
                        score += 100 * score_mult
                        tx = collided_zombie.spawn_tx
                        ty = collided_zombie.spawn_ty
                        respawn_queue.append((pygame.time.get_ticks(), current_area, tx, ty))
                        zombies.remove(collided_zombie)

                elif result == "lose":
                    hs = load_high_score()
                    if score > hs:
                        save_high_score(score)
                    return "lose"

                elif result == "run":
                    # Pushes the player away slightly after escaping battle.
                    player.rect.x -= 40

                # Resets battle state after any battle result.
                collided_zombie = None
                in_battle = False
                boss_battle = False
                battle = None

            pygame.display.flip()
            clock.tick(60)
            continue

        # Loads the saved checkpoint when L is pressed.
        if load_pressed:
            cp = load_checkpoint()
            if cp:
                enter_area(cp["area"], player, cp["tx"], cp["ty"])

        # Updates player movement and collisions.
        player.update(collision_map)

        # E key interactions depend on the tile the player is standing on.
        if interacted:
            standing_tile = tilemap.tile_under_player(player, grid)

            # Boss tile starts the boss battle.
            if standing_tile == "B":
                player_stats = {"hp": player_hp, "max_hp": player_hp, "energy": 50, "max_energy": 50}
                battle = Battle(player_stats, [make_boss()])
                battle.enemy_damage = enemy_dmg
                in_battle = True
                boss_battle = True

            # Door tile changes the current area.
            if standing_tile == "D":
                tx = player.rect.centerx // tilemap.TILE
                ty = player.rect.centery // tilemap.TILE
                key = (current_area, tx, ty)
                if key in tilemap.DOOR_LINKS:
                    next_area, spawn_tx, spawn_ty = tilemap.DOOR_LINKS[key]
                    enter_area(next_area, player, spawn_tx, spawn_ty)

            # Checkpoint tile saves the current location.
            if standing_tile == "c":
                tx = player.rect.centerx // tilemap.TILE
                ty = player.rect.centery // tilemap.TILE
                save_checkpoint(current_area, tx, ty)

        # Camera follows the player in the overworld.
        cam.follow(player.rect, world_w, world_h)

        # Draws the map.
        screen.fill(BLACK)
        tilemap.draw_map(screen, grid, tiles, cam)

        # Respawns defeated zombies after 20 seconds.
        current_time = pygame.time.get_ticks()
        for item in respawn_queue[:]:
            spawn_time, area, tx, ty = item
            if current_time - spawn_time >= 20000:
                if area == current_area:
                    z = Zombie(tx * tilemap.TILE, ty * tilemap.TILE)
                    z.spawn_tx = tx
                    z.spawn_ty = ty
                    zombies.append(z)
                respawn_queue.remove(item)

        # Updates all zombies in the current area.
        for z in zombies:
            z.update(grid, tilemap, player)

        # Collision with a zombie starts a standard battle.
        if not in_battle:
            for z in zombies:
                if player.rect.colliderect(z.rect):
                    collided_zombie = z
                    player_stats = {"hp": player_hp, "max_hp": player_hp, "energy": 50, "max_energy": 50}
                    enemy_list = [
                        {"name": "Enemy 1", "hp": 30, "max_hp": 30, "energy": 20, "max_energy": 20},
                        {"name": "Enemy 2", "hp": 30, "max_hp": 30, "energy": 20, "max_energy": 20},
                        {"name": "Enemy 3", "hp": 30, "max_hp": 30, "energy": 20, "max_energy": 20},
                    ]
                    battle = Battle(player_stats, enemy_list)
                    battle.enemy_damage = enemy_dmg
                    in_battle = True
                    boss_battle = False
                    break

        # Draws zombies using the camera transform.
        for z in zombies:
            z_screen_rect = cam.apply_rect(z.rect)
            z_scaled = pygame.transform.scale(z.image, (int(z_screen_rect.width), int(z_screen_rect.height)))
            screen.blit(z_scaled, z_screen_rect.topleft)

        # Draws the player using the camera transform.
        p_rect = cam.apply_rect(player.rect)
        p_scaled = pygame.transform.scale(player.image, (int(p_rect.width), int(p_rect.height)))
        screen.blit(p_scaled, p_rect.topleft)

        # Draws the score HUD in the top-left corner.
        font = pygame.font.SysFont(None, 28)
        screen.blit(font.render(f"Score:{score}", True, WHITE), (10, 10))

        pygame.display.flip()
        clock.tick(60)

import pygame
from config import WIDTH, HEIGHT, WHITE, BLACK, GRAY, BLUE
from storage import load_controls
from boss import make_minion

class Battle:
    """
    Main class for the turn-based battle system.

    This class controls:
    - battle state
    - menu navigation
    - player and enemy turns
    - victory / defeat checking
    - battle UI drawing
    """

    def __init__(self, player_stats: dict, enemies: list[dict]):
        # Example structure for the player and enemy dictionaries.
        # player_stats = {"hp": 100, "max_hp": 100, "energy": 50, "max_energy": 50}
        # enemies = [{"name":"Enemy 1","hp":30,"max_hp":30}, ...

        # Stores the player stats used during battle.
        self.player = player_stats

        # Stores all enemies currently active in the fight.
        self.enemies = enemies

        # Loads the player sprite shown in the battle UI.
        self.player_img = pygame.image.load("Assets/Character.png").convert_alpha()

        # Loads the standard enemy sprite.
        self.enemy_img = pygame.image.load("Assets/Zombie_front.png").convert_alpha()

        # Loads the boss sprite used when an enemy has type "boss".
        self.boss_image = pygame.image.load("Assets/Zombie_Boss.png").convert_alpha()

        # Font used for normal interface text.
        self.font = pygame.font.SysFont(None, 28)

        # Slightly larger font used for headings and labels.
        self.big_font = pygame.font.SysFont(None, 34)

        # Possible states:
        # "menu" = selecting an action
        # "message" = showing battle text
        # "end" = battle finished
        self.state = "menu"

        # Stores the final battle result once the fight ends.
        # Possible values: None / "run" / "win" / "lose"
        self.end_result = None

        # Four menu options displayed in a 2x2 grid.
        self.options = ["Attack", "Skill", "Back", "Items"]

        # Tracks which menu option is currently highlighted.
        self.menu_index = 0

        # Text currently shown in the message box.
        self.message = ""

        # Frame timer controlling how long the message is visible.
        self.message_timer = 0

        # Tracks whose turn it is. This makes the system easier to extend later.
        self.turn = "player"

        # Loads saved movement controls.
        self.controls = load_controls()

        # These sets allow both the custom saved key and the arrow key equivalent.
        self.key_left  = {self.controls["left"], pygame.K_LEFT}
        self.key_right = {self.controls["right"], pygame.K_RIGHT}
        self.key_up    = {self.controls["up"], pygame.K_UP}
        self.key_down  = {self.controls["down"], pygame.K_DOWN}

        # Confirmation keys used to choose an option.
        self.key_confirm = {pygame.K_RETURN, pygame.K_e, pygame.K_SPACE}

        # Counts completed rounds so boss summon logic can trigger.
        self.round_count = 0

    def is_over(self) -> bool:
        # Returns True once the battle has a final result.
        return self.end_result is not None

    def handle_event(self, event):
        # No input should be processed after the battle ends.
        if self.is_over():
            return

        # Only keyboard presses matter here.
        if event.type != pygame.KEYDOWN:
            return

        # While a message is displayed, confirmation closes the message box.
        if self.state == "message":
            if event.key in (pygame.K_RETURN, pygame.K_e, pygame.K_SPACE):
                self.state = "menu"
            return

        # Menu navigation and option selection.
        if self.state == "menu":
            if event.key in self.key_left:
                # Move left only when currently in the right column.
                if self.menu_index % 2 == 1:
                    self.menu_index -= 1

            elif event.key in self.key_right:
                # Move right only when currently in the left column.
                if self.menu_index % 2 == 0:
                    self.menu_index += 1

            elif event.key in self.key_up:
                # Move up one row inside the 2x2 menu grid.
                if self.menu_index >= 2:
                    self.menu_index -= 2

            elif event.key in self.key_down:
                # Move down one row inside the 2x2 menu grid.
                if self.menu_index <= 1:
                    self.menu_index += 2

            elif event.key in self.key_confirm:
                # Runs the selected action.
                self._choose_option()

            # Escape is currently treated as an attempt to run from battle.
            elif event.key == pygame.K_ESCAPE:
                self._try_run()

    def update(self):
        # No further updating is needed after the battle ends.
        if self.is_over():
            return

        # Defeat condition.
        if self.player["hp"] <= 0:
            self.player["hp"] = 0
            self.end_result = "lose"
            return

        # Victory condition.
        if len(self.enemies) == 0:
            self.end_result = "win"
            return

        # Counts down the message timer and returns to the menu when it ends.
        if self.message_timer > 0:
            self.message_timer -= 1
            if self.message_timer == 0 and self.state == "message":
                self.state = "menu"

    def _choose_option(self):
        # Reads the currently highlighted menu choice.
        choice = self.options[self.menu_index]

        if choice == "Attack":
            self._player_attack()

        elif choice == "Skill":
            # Placeholder until a real skill system is added.
            self._set_message("Skills not added yet.", 45)

        elif choice == "Items":
            # Placeholder until an inventory or item system is added.
            self._set_message("Items not added yet.", 45)

        elif choice == "Back":
            # Placeholder because there is not currently a previous submenu.
            self._set_message("No previous menu yet.", 45)

    def _player_attack(self):
        # If no enemies remain, the fight immediately ends as a win.
        if not self.enemies:
            self.end_result = "win"
            return

        # Targets the first enemy in the list.
        # Target selection can be expanded later.
        target = self.enemies[0]

        # Fixed damage value for the current basic attack.
        dmg = 10
        target["hp"] -= dmg

        # Removes the enemy if its health reaches zero.
        if target["hp"] <= 0:
            target["hp"] = 0
            self.enemies.pop(0)
            self._set_message(f"You defeated {target['name']}!", 60)
        else:
            self._set_message(f"You hit {target['name']} for {dmg}!", 60)

        # Enemy turn always follows the player's attack.
        self._enemy_turn()

    def _enemy_turn(self):
        # Stops the turn if the battle has already ended.
        if self.is_over():
            return
        if len(self.enemies) == 0:
            self.end_result = "win"
            return

        # The first active enemy attacks the player.
        attacker = self.enemies[0]

        # Uses difficulty-adjusted damage if provided, otherwise defaults to 5.
        dmg = getattr(self, "enemy_damage", 5)
        self.player["hp"] -= dmg
        if self.player["hp"] < 0:
            self.player["hp"] = 0

        # Shows a short message to make the turn structure feel clearer.
        self._set_message(f"{attacker['name']} hits you for {dmg}!", 60)

        # Checks defeat after taking damage.
        if self.player["hp"] <= 0:
            self.end_result = "lose"

        # Increases the round count after both sides have acted.
        self.round_count += 1

        # Allows the boss to summon extra enemies on specific rounds.
        self._spawn_minions_if_needed()

    def _try_run(self):
        # Running always succeeds in the current version.
        self.end_result = "run"

    def _set_message(self, msg: str, frames: int):
        # Stores the message, sets its duration, and switches to message state.
        self.message = msg
        self.message_timer = frames
        self.state = "message"

    # ----------------- Drawing UI -----------------

    def draw(self, screen):
        # Fills the background for the battle scene.
        screen.fill((240, 240, 240))

        # Draws all battle interface sections.
        self._draw_enemies(screen)
        self._draw_player_panel(screen)
        self._draw_menu(screen)

        # The message box is only drawn while the state is "message".
        if self.state == "message":
            self._draw_message(screen)

    def _draw_enemies(self, screen):
        # Creates three enemy slots across the top-right section.
        box_w, box_h = 140, 140
        start_x = WIDTH - (box_w * 3) - 40
        y = 40

        for i in range(3):
            x = start_x + i * (box_w + 10)

            pygame.draw.rect(screen, (220, 220, 220), (x, y, box_w, box_h))
            pygame.draw.rect(screen, (GRAY), (x, y, box_w, box_h), 2)

            if i < len(self.enemies):
                e = self.enemies[i]
                name = self.big_font.render(e["name"], True, BLACK)
                screen.blit(name, (x + 10, y + 10))

                # Health and energy bars are drawn underneath the enemy name.
                self._draw_bar(screen, x + 10, y + 95, 120, 14, e["hp"], e["max_hp"], label="Health")
                self._draw_bar(screen, x + 10, y + 115, 120, 14, 0, 1, label="Energy")

                # Bosses use a different image so they are visually distinct.
                if e.get("type") == "boss":
                    img = pygame.transform.scale(self.boss_image, (72, 72))
                else:
                    img = pygame.transform.scale(self.enemy_img, (48, 48))

                screen.blit(img, (x + 10, y + 40))
            else:
                # Empty enemy slots show a dash.
                empty = self.font.render("—", True, (80, 80, 80))
                screen.blit(empty, (x + 10, y + 10))

    def _draw_player_panel(self, screen):
        # Player box shown in the lower-left area.
        x, y, w, h = 40, HEIGHT - 220, 160, 160
        pygame.draw.rect(screen, (220, 220, 220), (x, y, w, h))
        pygame.draw.rect(screen, (GRAY), (x, y, w, h), 2)

        title = self.big_font.render("Player", True, BLACK)
        screen.blit(title, (x + 10, y + 10))
        img = pygame.transform.scale(self.player_img, (64, 64))
        screen.blit(img, (x + 10, y + 40))

        # Player health and energy values are taken from the player dictionary.
        self._draw_bar(screen, x + 10, y + 110, 140, 16, self.player["hp"], self.player["max_hp"], label="Health")
        self._draw_bar(screen, x + 10, y + 135, 140, 16, self.player["energy"], self.player["max_energy"], label="Energy")

    def _draw_menu(self, screen):
        # Main action menu shown at the bottom-middle of the screen.
        box_x, box_y = 240, HEIGHT - 200
        box_w, box_h = 320, 150

        pygame.draw.rect(screen, (220, 220, 220), (box_x, box_y, box_w, box_h))
        pygame.draw.rect(screen, (GRAY), (box_x, box_y, box_w, box_h), 2)

        btn_w, btn_h = 140, 45
        pad_x, pad_y = 20, 20

        for i, text in enumerate(self.options):
            col = i % 2
            row = i // 2
            x = box_x + pad_x + col * (btn_w + 20)
            y = box_y + pad_y + row * (btn_h + 15)

            # The currently selected option uses a darker border.
            selected = (i == self.menu_index and self.state == "menu")
            outline = (0, 0, 0) if selected else (GRAY)

            pygame.draw.rect(screen, (235, 235, 235), (x, y, btn_w, btn_h))
            pygame.draw.rect(screen, outline, (x, y, btn_w, btn_h), 2)

            label = self.big_font.render(text, True, BLACK)
            screen.blit(label, label.get_rect(center=(x + btn_w // 2, y + btn_h // 2)))

        # This hint displays the current control bindings.
        l = pygame.key.name(self.controls["left"]).upper()
        r = pygame.key.name(self.controls["right"]).upper()
        u = pygame.key.name(self.controls["up"]).upper()
        d = pygame.key.name(self.controls["down"]).upper()
        hint = self.font.render(f"{u}{l}{d}{r} + Enter/E", True, (80, 80, 80))
        screen.blit(hint, (box_x + 10, box_y - 25))

    def _draw_message(self, screen):
        # Message box positioned above the menu.
        x, y, w, h = 240, HEIGHT - 260, 320, 50
        pygame.draw.rect(screen, (WHITE), (x, y, w, h))
        pygame.draw.rect(screen, (GRAY), (x, y, w, h), 2)

        msg = self.font.render(self.message, True, BLACK)
        screen.blit(msg, (x + 10, y + 15))

    def _draw_bar(self, screen, x, y, w, h, value, max_value, label=""):
        # Chooses a colour depending on bar type.
        if label == "Health":
            colour = (220, 60, 60)
        elif label == "Energy":
            colour = (BLUE)
        else:
            colour = (GRAY)

        # Draws the bar background and border.
        pygame.draw.rect(screen, (WHITE), (x, y, w, h))
        pygame.draw.rect(screen, (GRAY), (x, y, w, h), 4)

        # Calculates the filled width based on the current ratio.
        fill_w = 0
        if max_value > 0:
            ratio = max(0.0, min(1.0, value / max_value))
            fill_w = int((w - 4) * ratio)
        pygame.draw.rect(screen, colour, (x + 2, y + 2, fill_w, h - 4))

        # Draws the label in the centre of the bar.
        if label:
           txt = self.font.render(label, True, BLACK)
           txt_rect = txt.get_rect(center=(x + w // 2, y + h // 2))
           screen.blit(txt, txt_rect)

    def _spawn_minions_if_needed(self):
        # Searches the enemy list for a boss entry.
        boss = None

        for e in self.enemies:
            if e.get("type") == "boss":
                boss = e
                break

        # No summon logic should run if there is no boss.
        if boss is None:
            return

        every = boss.get("summon_every", 0)

        # summon_every of 0 or less disables summoning.
        if every <= 0:
            return

        # Summons only on the correct round interval.
        if self.round_count % every != 0:
            return

        # Maximum of three enemies can be shown at once.
        slots = 3 - len(self.enemies)

        if slots <= 0:
            return

        # Spawns at most two minions in one summon action.
        spawn_count = min(2, slots)

        for i in range(spawn_count):
           self.enemies.append(make_minion(i+1))

        # Shows a message after summoning.
        self._set_message("Zombie Boss summons zombies", 60)

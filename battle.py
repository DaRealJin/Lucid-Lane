import pygame
from config import WIDTH, HEIGHT, WHITE, BLACK, GRAY

class Battle:
    #Turn-based battle controller with a small state machine ("menu","message","end")
    """
    Simple turn-based battle:
    - Player chooses: Attack / Skill / Items / Run
    - Enemy turn happens after Attack (and can be extended later)
    - Ends on: win / lose / run
    """

    def __init__(self, player_stats: dict, enemies: list[dict]):
        #Example:
        #player_stats = {"hp": 100, "max_hp": 100, "energy": 50, "max_energy": 50}
        #enemies = [{"name":"Enemy 1","hp":30,"max_hp":30}, ...]
        self.player = player_stats
        self.enemies = enemies

        self.font = pygame.font.SysFont(None, 28)
        self.big_font = pygame.font.SysFont(None, 34)

        #states: "menu", "message", "end"
        self.state = "menu"

        #end_result: None / "run" / "win" / "lose"
        self.end_result = None

        #Menu like your mockup (2x2)
        self.options = ["Attack", "Skill", "Back", "Items"]
        #Menu layout matches a 2x2 grid like classic JRPGs
        self.menu_index = 0

        #Message box (so it feels more like Pokémon/Omori)
        self.message = ""
        self.message_timer = 0

        #Turn ownership (easy to extend later into speed/party)
        self.turn = "player"

    def is_over(self) -> bool:
        return self.end_result is not None

    def handle_event(self, event):
        #Handles player input differently depending on current battle state(self, event):
        if self.is_over():
            return

        if event.type != pygame.KEYDOWN:
            return

        #If you're in a "message" pause, allow confirm to continue
        if self.state == "message":
            if event.key in (pygame.K_RETURN, pygame.K_e, pygame.K_SPACE):
                self.state = "menu"
            return

        #MENU input
        if self.state == "menu":
            if event.key == pygame.K_LEFT:
                #move within the 2 columns
                if self.menu_index % 2 == 1:
                    self.menu_index -= 1

            elif event.key == pygame.K_RIGHT:
                if self.menu_index % 2 == 0:
                    self.menu_index += 1

            elif event.key == pygame.K_UP:
                if self.menu_index >= 2:
                    self.menu_index -= 2

            elif event.key == pygame.K_DOWN:
                if self.menu_index <= 1:
                    self.menu_index += 2

            elif event.key in (pygame.K_RETURN, pygame.K_e, pygame.K_SPACE):
                self._choose_option()

            #Optional: allow ESC to attempt run
            elif event.key == pygame.K_ESCAPE:
                self._try_run()

    def update(self):
        #You can extend this for animations later
        if self.is_over():
            return

        #Auto-check win/lose conditions
        if self.player["hp"] <= 0:
            self.player["hp"] = 0
            self.end_result = "lose"
            return

        if len(self.enemies) == 0:
            self.end_result = "win"
            return

        if self.message_timer > 0:
            self.message_timer -= 1
            if self.message_timer == 0 and self.state == "message":
                self.state = "menu"

    def _choose_option(self):
        choice = self.options[self.menu_index]

        if choice == "Attack":
            self._player_attack()

        elif choice == "Skill":
            self._set_message("Skills not added yet.", 45)

        elif choice == "Items":
            self._set_message("Items not added yet.", 45)

        elif choice == "Back":
            #In your mockup, Back would return to a previous menu.
            #For now, we just show a message.
            self._set_message("No previous menu yet.", 45)

    def _player_attack(self):
        if not self.enemies:
            self.end_result = "win"
            return

        #Attack first enemy (you can add target selection later)
        target = self.enemies[0]
        dmg = 10
        target["hp"] -= dmg
        if target["hp"] <= 0:
            target["hp"] = 0
            self.enemies.pop(0)
            self._set_message(f"You defeated {target['name']}!", 60)
        else:
            self._set_message(f"You hit {target['name']} for {dmg}!", 60)

        #After player action, enemy turn happens
        self._enemy_turn()

    def _enemy_turn(self):
        if self.is_over():
            return
        if len(self.enemies) == 0:
            self.end_result = "win"
            return

        #Simple enemy action: first enemy attacks
        attacker = self.enemies[0]
        dmg = 5
        self.player["hp"] -= dmg
        if self.player["hp"] < 0:
            self.player["hp"] = 0

        #Add a message pause (feels turn-based)
        self._set_message(f"{attacker['name']} hits you for {dmg}!", 60)

        if self.player["hp"] <= 0:
            self.end_result = "lose"

    def _try_run(self):
        #Simple: always run successfully for now
        self.end_result = "run"

    def _set_message(self, text, frames=60):
        #Shows a message for a fixed number of frames to pace the battle like Pokémon/Omori(self, msg: str, frames: int):
        self.message = msg
        self.message_timer = frames
        self.state = "message"

    #----------------- Drawing UI (your mockup layout) -----------------

    def draw(self, screen):
        screen.fill((240, 240, 240))

        #Enemy panels (top right)
        self._draw_enemies(screen)

        #Player panel (bottom left)
        self._draw_player_panel(screen)

        #Menu (bottom middle)
        self._draw_menu(screen)

        #Message box (optional, over menu)
        if self.state == "message":
            self._draw_message(screen)

    def _draw_enemies(self, screen):
        #3 boxes across the top-right area like your image
        box_w, box_h = 140, 140
        start_x = WIDTH - (box_w * 3) - 40
        y = 40

        for i in range(3):
            x = start_x + i * (box_w + 10)

            pygame.draw.rect(screen, (220, 220, 220), (x, y, box_w, box_h))
            pygame.draw.rect(screen, (120, 120, 120), (x, y, box_w, box_h), 2)

            if i < len(self.enemies):
                e = self.enemies[i]
                name = self.big_font.render(e["name"], True, BLACK)
                screen.blit(name, (x + 10, y + 10))

                self._draw_bar(screen, x + 10, y + 95, 120, 14, e["hp"], e["max_hp"], label="Health")
                self._draw_bar(screen, x + 10, y + 115, 120, 14, 0, 1, label="Energy")  # placeholder
            else:
                empty = self.font.render("—", True, (80, 80, 80))
                screen.blit(empty, (x + 10, y + 10))

    def _draw_player_panel(self, screen):
        x, y, w, h = 40, HEIGHT - 220, 160, 160
        pygame.draw.rect(screen, (220, 220, 220), (x, y, w, h))
        pygame.draw.rect(screen, (120, 120, 120), (x, y, w, h), 2)

        title = self.big_font.render("Player", True, BLACK)
        screen.blit(title, (x + 10, y + 10))

        self._draw_bar(screen, x + 10, y + 110, 140, 16, self.player["hp"], self.player["max_hp"], label="Health")
        self._draw_bar(screen, x + 10, y + 135, 140, 16, self.player["energy"], self.player["max_energy"], label="Energy")

    def _draw_menu(self, screen):
        #Big menu bar like your mockup (2x2 buttons)
        box_x, box_y = 240, HEIGHT - 200
        box_w, box_h = 320, 150

        pygame.draw.rect(screen, (220, 220, 220), (box_x, box_y, box_w, box_h))
        pygame.draw.rect(screen, (120, 120, 120), (box_x, box_y, box_w, box_h), 2)

        btn_w, btn_h = 140, 45
        pad_x, pad_y = 20, 20

        for i, text in enumerate(self.options):
            col = i % 2
            row = i // 2
            x = box_x + pad_x + col * (btn_w + 20)
            y = box_y + pad_y + row * (btn_h + 15)

            selected = (i == self.menu_index and self.state == "menu")
            outline = (0, 0, 0) if selected else (120, 120, 120)

            pygame.draw.rect(screen, (235, 235, 235), (x, y, btn_w, btn_h))
            pygame.draw.rect(screen, outline, (x, y, btn_w, btn_h), 2)

            label = self.big_font.render(text, True, BLACK)
            screen.blit(label, label.get_rect(center=(x + btn_w // 2, y + btn_h // 2)))

        hint = self.font.render("Arrows + Enter/E", True, (80, 80, 80))
        screen.blit(hint, (box_x + 10, box_y - 25))

    def _draw_message(self, screen):
        #Message box above the menu
        x, y, w, h = 240, HEIGHT - 260, 320, 50
        pygame.draw.rect(screen, (255, 255, 255), (x, y, w, h))
        pygame.draw.rect(screen, (120, 120, 120), (x, y, w, h), 2)

        msg = self.font.render(self.message, True, BLACK)
        screen.blit(msg, (x + 10, y + 15))

    def _draw_bar(self, screen, x, y, w, h, value, max_value, label=""):
        #Outline
        pygame.draw.rect(screen, (255, 255, 255), (x, y, w, h))
        pygame.draw.rect(screen, (120, 120, 120), (x, y, w, h), 2)

        #Fill
        if max_value <= 0:
            fill_w = 0
        else:
            ratio = max(0.0, min(1.0, value / max_value))
            fill_w = int((w - 4) * ratio)

        pygame.draw.rect(screen, (180, 180, 180), (x + 2, y + 2, fill_w, h - 4))

        #Label text
        if label:
            t = self.font.render(label, True, BLACK)
            screen.blit(t, (x + 2, y - 18))
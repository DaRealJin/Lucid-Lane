#Turn-basedbattleUIandlogic(state-machine:menu->message->end)
import pygame
from config import WIDTH, HEIGHT, WHITE, BLACK, GRAY, BLUE
from storage import load_controls
from boss import make_minion

class Battle:
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
        self.player_img = pygame.image.load("Assets/Character.png").convert_alpha()
        self.enemy_img = pygame.image.load("Assets/Zombie_front.png").convert_alpha()
        self.boss_image = pygame.image.load("Assets/Zombie_Boss.png").convert_alpha()
        self.font = pygame.font.SysFont(None, 28)
        self.big_font = pygame.font.SysFont(None, 34)

        #states: "menu", "message", "end"
        self.state = "menu"
        #statecontrolswhichinputsareacceptedandwhatgetsdrawn

        #end_result: None / "run" / "win" / "lose"
        self.end_result = None

        #Menu like your mockup (2x2)
        self.options = ["Attack", "Skill", "Back", "Items"]
        self.menu_index = 0

        #Message box (so it feels more like Pokémon/Omori)
        self.message = ""
        self.message_timer = 0

        #Turn ownership (easy to extend later into speed/party)
        self.turn = "player"

        self.controls = load_controls()
        #Battlemenususeplayerskeybinds(sameasoverworldmovement)
        self.key_left  = {self.controls["left"], pygame.K_LEFT}
        self.key_right = {self.controls["right"], pygame.K_RIGHT}
        self.key_up    = {self.controls["up"], pygame.K_UP}
        self.key_down  = {self.controls["down"], pygame.K_DOWN}

        #confirm keys
        self.key_confirm = {pygame.K_RETURN, pygame.K_e, pygame.K_SPACE}

        #Track battle rounds
        self.round_count = 0
        #Usedforbosssummontiming(every5fullrounds)

    def is_over(self) -> bool:
        return self.end_result is not None

    def handle_event(self, event):
        if self.is_over():
            return

        if event.type != pygame.KEYDOWN:
            return

        #If you're in a "message" pause, allow confirm to continue
        if self.state == "message":
            if event.key in (pygame.K_RETURN, pygame.K_e, pygame.K_SPACE):
                self.state = "menu"
        #statecontrolswhichinputsareacceptedandwhatgetsdrawn
            return

        #MENU input
        if self.state == "menu":
            if event.key in self.key_left:
                #move within the 2 columns
                if self.menu_index % 2 == 1:
                    self.menu_index -= 1

            elif event.key in self.key_right:
                if self.menu_index % 2 == 0:
                    self.menu_index += 1

            elif event.key in self.key_up:
                if self.menu_index >= 2:
                    self.menu_index -= 2

            elif event.key in self.key_down:
                if self.menu_index <= 1:
                    self.menu_index += 2

            elif event.key in self.key_confirm:
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
        #statecontrolswhichinputsareacceptedandwhatgetsdrawn

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
        #Enemyturnappliesdamageandadvancesroundcounter
        if self.is_over():
            return
        if len(self.enemies) == 0:
            self.end_result = "win"
            return

        #Simple enemy action: first enemy attacks
        attacker = self.enemies[0]
        dmg = 4
        self.player["hp"] -= dmg
        if self.player["hp"] < 0:
            self.player["hp"] = 0

        #Add a message pause (feels turn-based)
        self._set_message(f"{attacker['name']} hits you for {dmg}!", 60)

        if self.player["hp"] <= 0:
            self.end_result = "lose"

        #End of round
        self.round_count += 1

        #Boss summon check
        self._spawn_minions_if_needed()

    def _try_run(self):
        #Simple: always run successfully for now
        self.end_result = "run"

    def _set_message(self, msg: str, frames: int):
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
            pygame.draw.rect(screen, (GRAY), (x, y, box_w, box_h), 2)

            if i < len(self.enemies):
                e = self.enemies[i]
                name = self.big_font.render(e["name"], True, BLACK)
                screen.blit(name, (x + 10, y + 10))

                self._draw_bar(screen, x + 10, y + 95, 120, 14, e["hp"], e["max_hp"], label="Health")
                self._draw_bar(screen, x + 10, y + 115, 120, 14, 0, 1, label="Energy")  # placeholder
                if e.get("type") == "boss":
                    img = pygame.transform.scale(self.boss_image, (72, 72))
                else:
                    img = pygame.transform.scale(self.enemy_img, (48, 48))

                screen.blit(img, (x + 10, y + 40))
            else:
                empty = self.font.render("—", True, (80, 80, 80))
                screen.blit(empty, (x + 10, y + 10))

    def _draw_player_panel(self, screen):
        x, y, w, h = 40, HEIGHT - 220, 160, 160
        pygame.draw.rect(screen, (220, 220, 220), (x, y, w, h))
        pygame.draw.rect(screen, (GRAY), (x, y, w, h), 2)

        title = self.big_font.render("Player", True, BLACK)
        screen.blit(title, (x + 10, y + 10))
        img = pygame.transform.scale(self.player_img, (64, 64))
        screen.blit(img, (x + 10, y + 40))

        self._draw_bar(screen, x + 10, y + 110, 140, 16, self.player["hp"], self.player["max_hp"], label="Health")
        self._draw_bar(screen, x + 10, y + 135, 140, 16, self.player["energy"], self.player["max_energy"], label="Energy")

    def _draw_menu(self, screen):
        #Big menu bar like your mockup (2x2 buttons)
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

            selected = (i == self.menu_index and self.state == "menu")
            outline = (0, 0, 0) if selected else (GRAY)

            pygame.draw.rect(screen, (235, 235, 235), (x, y, btn_w, btn_h))
            pygame.draw.rect(screen, outline, (x, y, btn_w, btn_h), 2)

            label = self.big_font.render(text, True, BLACK)
            screen.blit(label, label.get_rect(center=(x + btn_w // 2, y + btn_h // 2)))

        l = pygame.key.name(self.controls["left"]).upper()
        r = pygame.key.name(self.controls["right"]).upper()
        u = pygame.key.name(self.controls["up"]).upper()
        d = pygame.key.name(self.controls["down"]).upper()
        hint = self.font.render(f"{u}{l}{d}{r} + Enter/E", True, (80, 80, 80))
        screen.blit(hint, (box_x + 10, box_y - 25))

    def _draw_message(self, screen):


        #Message box above the menu
        x, y, w, h = 240, HEIGHT - 260, 320, 50
        pygame.draw.rect(screen, (WHITE), (x, y, w, h))
        pygame.draw.rect(screen, (GRAY), (x, y, w, h), 2)

        msg = self.font.render(self.message, True, BLACK)
        screen.blit(msg, (x + 10, y + 15))

    def _draw_bar(self, screen, x, y, w, h, value, max_value, label=""):
        
        if label == "Health":
            colour = (220, 60, 60)
        elif label == "Energy":
            colour = (BLUE) 
        else:
            colour = (GRAY)
    
    
    #Outline
        pygame.draw.rect(screen, (WHITE), (x, y, w, h))
        pygame.draw.rect(screen, (GRAY), (x, y, w, h), 4)

    #Fill
        fill_w = 0
        if max_value > 0:
            ratio = max(0.0, min(1.0, value / max_value))
            fill_w = int((w - 4) * ratio)
        pygame.draw.rect(screen, colour, (x + 2, y + 2, fill_w, h - 4))

    #Label
        if label:
           txt = self.font.render(label, True, BLACK)
           txt_rect = txt.get_rect(center=(x + w // 2, y + h // 2))
           screen.blit(txt, txt_rect)
    
    def _spawn_minions_if_needed(self):
        #Boss-onlymechanic:spawnminionswithoutbreaking3-enemyUIlimit

        boss = None

    #Find boss
        for e in self.enemies:
            if e.get("type") == "boss":
                boss = e
                break

        if boss is None:
            return

        every = boss.get("summon_every", 0)

        if every <= 0:
            return

        #Only summon every 5 rounds
        if self.round_count % every != 0:
            return

        #Max enemies allowed on screen
        slots = 3 - len(self.enemies)

        if slots <= 0:
            return

        #Spawn up to 2 minions
        spawn_count = min(2, slots)

        for i in range(spawn_count):
           self.enemies.append(make_minion(i+1))

        self._set_message("Zombie Boss summons zombies", 60)
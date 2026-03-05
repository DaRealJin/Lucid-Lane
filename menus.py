import pygame
import sys
from config import WIDTH, HEIGHT, WHITE, BLACK
from ui_components import Button, simple_screen
from storage import (
    has_save,
    save_game,
    load_game_data,
    save_controls,
    load_high_score,
)


def lore_screen(screen, clock, font, draw_bg):
    #Lore
    simple_screen(screen, clock, font, draw_bg,
                  "Lore: You wake up in Lucid Lane with no memory... \n" \
    "                              Escape the world.",
                  WHITE)


def mech_instructions(screen, clock, font, draw_bg):
    simple_screen(screen, clock, font, draw_bg,
                  "Happy beats angry, Angry beats Sad, Sad beats angry",
                  WHITE)


def score_screen(screen, clock, font, draw_bg):
    high_score = load_high_score()
    simple_screen(screen, clock, font, draw_bg,
                  f"Highest Score: {high_score}",
                  WHITE)


def information_menu(screen, clock, font, draw_bg, controls):
    buttons = [
        Button("Game Lore", 300, 260, 200, 50),
        Button("Mechanics", 300, 330, 200, 50),
        Button("Score", 300, 400, 200, 50),
        Button("Back", 300, 470, 200, 50),
    ]

    while True:
        draw_bg(screen)

        title = font.render("Information", True, WHITE)
        screen.blit(title, title.get_rect(center=(WIDTH // 2, 150)))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                return controls

            for btn in buttons:
                if btn.clicked(event):
                    if btn.text == "Game Lore":
                        lore_screen(screen, clock, font, draw_bg)
                    elif btn.text == "Mechanics":
                        mech_instructions(screen, clock, font, draw_bg)
                    elif btn.text == "Score":
                        score_screen(screen, clock, font, draw_bg)
                    elif btn.text == "Back":
                        return controls

        for btn in buttons:
            btn.draw(screen, font)

        pygame.display.update()
        clock.tick(60)


def controls_menu(screen, clock, font, draw_bg, controls):
    def make_buttons():
        return [
            Button(f"Up: {pygame.key.name(controls['up']).upper()}", 260, 200, 280, 50),
            Button(f"Down: {pygame.key.name(controls['down']).upper()}", 260, 270, 280, 50),
            Button(f"Left: {pygame.key.name(controls['left']).upper()}", 260, 340, 280, 50),
            Button(f"Right: {pygame.key.name(controls['right']).upper()}", 260, 410, 280, 50),
            Button("Back", 260, 480, 280, 50),
        ]

    buttons = make_buttons()
    waiting_for = None

    while True:
        draw_bg(screen)

        title = font.render("Controls", True, WHITE)
        screen.blit(title, title.get_rect(center=(WIDTH // 2, 120)))

        info = font.render("Click a control, then press a key", True, WHITE)
        screen.blit(info, info.get_rect(center=(WIDTH // 2, 160)))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                if waiting_for:
                    waiting_for = None
                else:
                    return controls

            if waiting_for is None:
                for btn in buttons:
                    if btn.clicked(event):
                        if btn.text.startswith("Up:"):
                            waiting_for = "up"
                        elif btn.text.startswith("Down:"):
                            waiting_for = "down"
                        elif btn.text.startswith("Left:"):
                            waiting_for = "left"
                        elif btn.text.startswith("Right:"):
                            waiting_for = "right"
                        elif btn.text == "Back":
                            return controls

            if waiting_for and event.type == pygame.KEYDOWN:
                controls[waiting_for] = event.key
                save_controls(controls)
                buttons = make_buttons()
                waiting_for = None

        for btn in buttons:
            btn.draw(screen, font)

        pygame.display.update()
        clock.tick(60)


def reset_controls_to_defaults(controls):
    #Reset the keys
    controls["up"] = pygame.K_UP
    controls["down"] = pygame.K_DOWN
    controls["left"] = pygame.K_LEFT
    controls["right"] = pygame.K_RIGHT
    save_controls(controls)


def settings_menu(screen, clock, font, draw_bg, controls):
    buttons = [
        Button("Controls", 300, 260, 200, 50),
        Button("Reset Controls", 300, 330, 200, 50),
        Button("Back", 300, 400, 200, 50),
    ]

    while True:
        draw_bg(screen)

        title = font.render("Settings", True, WHITE)
        screen.blit(title, title.get_rect(center=(WIDTH // 2, 150)))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                return controls

            for btn in buttons:
                if btn.clicked(event):
                    if btn.text == "Controls":
                        controls = controls_menu(screen, clock, font, draw_bg, controls)
                    elif btn.text == "Reset Controls":
                        reset_controls_to_defaults(controls)
                    elif btn.text == "Back":
                        return controls

        for btn in buttons:
            btn.draw(screen, font)

        pygame.display.update()
        clock.tick(60)


def start_game_menu(screen, clock, font, draw_bg, controls):
#Difficulty selection screen; returns the chosen difficulty string or None(screen, clock, font, draw_bg, controls):
    buttons = [
        Button("Easy", 300, 220, 200, 50),
        Button("Normal", 300, 300, 200, 50),
        Button("Hard", 300, 380, 200, 50),
    ]

    if has_save():
        buttons.append(Button("Load Game", 300, 460, 200, 50))
        buttons.append(Button("Back", 300, 540, 200, 50))
    else:
        buttons.append(Button("Back", 300, 460, 200, 50))

    while True:
        draw_bg(screen)

        title = font.render("Choose Difficulty", True, WHITE)
        screen.blit(title, title.get_rect(center=(WIDTH // 2, 120)))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                return controls

            for btn in buttons:
                if btn.clicked(event):
                    if btn.text in ("Easy", "Normal", "Hard"):
                        save_game(btn.text)
                        simple_screen(screen, clock, font, draw_bg, f"Game Running: {btn.text}", WHITE)
                    elif btn.text == "Load Game":
                        data = load_game_data()
                        if data:
                            diff = data.get("difficulty", "Normal")
                            simple_screen(screen, clock, font, draw_bg, f"Loaded Game: {diff}", WHITE)
                        else:
                            simple_screen(screen, clock, font, draw_bg, "No save found!", WHITE)
                    elif btn.text == "Back":
                        return controls

        for btn in buttons:
            btn.draw(screen, font)

        pygame.display.update()
        clock.tick(60)


def menu(screen, clock, font, draw_bg, controls):
#Main menu loop; returns only when the program quitsscreen, clock, font, draw_bg, controls):
    buttons = [
        Button("Start Game", 300, 160, 200, 50),
        Button("Information", 300, 260, 200, 50),
        Button("Settings", 300, 360, 200, 50),
        Button("QUIT", 300, 460, 200, 50)
    ]

    while True:
        draw_bg(screen)

        title = font.render("Lucid Lane", True, WHITE)
        screen.blit(title, title.get_rect(center=(WIDTH // 2, 80)))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            for btn in buttons:
                if btn.clicked(event):
                    if btn.text == "Start Game":
                        controls = start_game_menu(screen, clock, font, draw_bg, controls)
                    elif btn.text == "Information":
                        controls = information_menu(screen, clock, font, draw_bg, controls)
                    elif btn.text == "Settings":
                        controls = settings_menu(screen, clock, font, draw_bg, controls)
                    elif btn.text == "QUIT":
                        pygame.quit()
                        sys.exit()

        for btn in buttons:
            btn.draw(screen, font)

        pygame.display.update()
        clock.tick(60)


import os
import json
from config import SAVE_FILE, SETTINGS_FILE, HIGH_SCORE_FILE, DEFAULT_CONTROLS

def has_save():
    return os.path.exists(SAVE_FILE)

def save_game(difficulty):
    with open(SAVE_FILE, "w") as f:
        json.dump({"difficulty": difficulty}, f)

def load_game_data():
    if not has_save():
        return None
    with open(SAVE_FILE, "r") as f:
        return json.load(f)

def save_controls(controls):
#Stores keybinds as integers in JSON so custom controls persist between sessions(controls):
    data = {k: int(v) for k, v in controls.items()}
    with open(SETTINGS_FILE, "w") as f:
        json.dump({"controls": data}, f)

def load_controls():
#Loads saved keybinds or falls back to defaults if settings file is missing/corrupt():
    controls = DEFAULT_CONTROLS.copy()
    if not os.path.exists(SETTINGS_FILE):
        return controls
    with open(SETTINGS_FILE, "r") as f:
        data = json.load(f)
    saved = data.get("controls", {})
    for k in controls:
        if k in saved:
            controls[k] = saved[k]
    return controls

def load_high_score():
#Loads the highest score achieved so far (used for the score menu)():
    if not os.path.exists(HIGH_SCORE_FILE):
        return 0
    with open(HIGH_SCORE_FILE, "r") as f:
        data = json.load(f)
    return data.get("high_score", 0)

def save_high_score(score):
#Updates the stored high score when a run ends with a higher value(score):
    with open(HIGH_SCORE_FILE, "w") as f:
        json.dump({"high_score": score}, f)

def load_save():
#Loads the main save JSON file containing checkpoint, difficulty, and other progress
    if not os.path.exists(SAVE_FILE):
        return {}
    with open(SAVE_FILE, "r") as f:
        return json.load(f) or {}

def write_save(data: dict):
    os.makedirs(os.path.dirname(SAVE_FILE), exist_ok=True)
    with open(SAVE_FILE, "w") as f:
        json.dump(data, f)

def save_checkpoint(area, tx, ty):
#Saves the player's current area and tile position so they can reload later(area: str, tx: int, ty: int):
    data = load_save()
    data["checkpoint"] = {"area": area, "tx": tx, "ty": ty}
    write_save(data)

def load_checkpoint():
#Returns the saved checkpoint data if it exists, otherwise None():
    data = load_save()
    return data.get("checkpoint")

def save_game(difficulty):
    data = load_save()
    data["difficulty"] = difficulty
    write_save(data)
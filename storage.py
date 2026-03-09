import os
import json
from config import SAVE_FILE, SETTINGS_FILE, HIGH_SCORE_FILE, DEFAULT_CONTROLS

# Returns True when a save file already exists.
def has_save():
    return os.path.exists(SAVE_FILE)

# Saves only the selected difficulty.
def save_game(difficulty):
    with open(SAVE_FILE, "w") as f:
        json.dump({"difficulty": difficulty}, f)

# Loads the main save file as a dictionary.
def load_game_data():
    if not has_save():
        return None
    with open(SAVE_FILE, "r") as f:
        return json.load(f)

# Stores the control bindings in JSON format.
def save_controls(controls):
    data = {k: int(v) for k, v in controls.items()}
    with open(SETTINGS_FILE, "w") as f:
        json.dump({"controls": data}, f)

# Loads controls and falls back to defaults if no settings file exists.
def load_controls():
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

# Returns the saved high score or zero if the file does not exist.
def load_high_score():
    if not os.path.exists(HIGH_SCORE_FILE):
        return 0
    with open(HIGH_SCORE_FILE, "r") as f:
        data = json.load(f)
    return data.get("high_score", 0)

# Writes a new high score file.
def save_high_score(score):
    with open(HIGH_SCORE_FILE, "w") as f:
        json.dump({"high_score": score}, f)

# Loads the entire save structure.
def load_save():
    if not os.path.exists(SAVE_FILE):
        return {}
    with open(SAVE_FILE, "r") as f:
        return json.load(f) or {}

# Writes the full save dictionary and creates folders if needed.
def write_save(data: dict):
    os.makedirs(os.path.dirname(SAVE_FILE), exist_ok=True)
    with open(SAVE_FILE, "w") as f:
        json.dump(data, f)

# Saves the current checkpoint location.
def save_checkpoint(area: str, tx: int, ty: int):
    data = load_save()
    data["checkpoint"] = {"area": area, "tx": tx, "ty": ty}
    write_save(data)

# Loads the checkpoint entry if present.
def load_checkpoint():
    data = load_save()
    return data.get("checkpoint")

# Updated version of save_game that keeps existing save data and only changes difficulty.
def save_game(difficulty):
    data = load_save()
    data["difficulty"] = difficulty
    write_save(data)

# frontend/save_system.py

import json
import os

SAVE_PATH = "save.json"

DEFAULT_SAVE = {
    "game_time": {
        "year": 1,
        "month": 1,
        "day": 1,
        "hour": 12,
        "minute": 0,
        "am": True
    },
    "food": {
        "pellets": 0,
        "water": 0
    }
}


def load_save():
    """Load the JSON save file or create defaults if missing/corrupt."""
    if not os.path.exists(SAVE_PATH):
        save(DEFAULT_SAVE)
        return DEFAULT_SAVE.copy()

    try:
        with open(SAVE_PATH, "r") as f:
            data = json.load(f)

        # make sure all expected keys exist
        for k, v in DEFAULT_SAVE.items():
            if k not in data:
                data[k] = v

        return data
    except Exception:
        # if anything goes wrong, start fresh
        save(DEFAULT_SAVE)
        return DEFAULT_SAVE.copy()


def save(data):
    """Write save data to disk."""
    with open(SAVE_PATH, "w") as f:
        json.dump(data, f, indent=4)


def save_game_time(save_data, game_time_dict):
    save_data["game_time"] = dict(game_time_dict)


def save_food(save_data, pellets, water):
    save_data["food"]["pellets"] = pellets
    save_data["food"]["water"] = water

import json
import os

COINS_FILE = "data/coins.json"
ROLES_FILE = "data/roles.json"
ROOMS_FILE = "data/rooms.json"


def load_coins():
    if not os.path.exists(COINS_FILE):
        return {}

    with open(COINS_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def save_coins(data):
    with open(COINS_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)


def load_roles():
    if not os.path.exists(ROLES_FILE):
        return {}

    with open(ROLES_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def save_roles(data):
    with open(ROLES_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)


# ============================================================
# ROOMS
# ============================================================

def load_rooms():
    if not os.path.exists(ROOMS_FILE):
        return {}

    with open(ROOMS_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def save_rooms(data):
    with open(ROOMS_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

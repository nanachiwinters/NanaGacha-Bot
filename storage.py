import json
import os

COINS_FILE = "data/coins.json"


def load_coins():
    if not os.path.exists(COINS_FILE):
        return {}

    with open(COINS_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def save_coins(data):
    with open(COINS_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

def load_roles():
    try:
        with open("data/roles.json", "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print("Couldn't load roles.json:", e)
        return {}


def save_roles(data):
    with open("data/roles.json", "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

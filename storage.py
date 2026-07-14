import json
import os

COINS_FILE = "coins.json"


def load_coins():
    if not os.path.exists(COINS_FILE):
        return {}

    with open(COINS_FILE, "r") as f:
        return json.load(f)


def save_coins(data):
    with open(COINS_FILE, "w") as f:
        json.dump(data, f, indent=4)

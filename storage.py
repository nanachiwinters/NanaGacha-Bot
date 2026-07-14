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


def load_roles():
    try:
        with open("roles.json", "r") as f:
            return json.load(f)
    except:
        return {}


def save_roles(data):
    with open("roles.json", "w") as f:
        json.dump(data, f, indent=4)

import json
import os

DB_FILE = "waifus.json"

# Agar file exist nahi karti, toh basic structure create karo
if not os.path.exists(DB_FILE):
    with open(DB_FILE, "w") as f:
        json.dump({"waifus": [], "users": {}, "current_drop": None}, f)

def load_data():
    with open(DB_FILE, "r") as f:
        return json.load(f)

def save_data(data):
    with open(DB_FILE, "w") as f:
        json.dump(data, f, indent=2)
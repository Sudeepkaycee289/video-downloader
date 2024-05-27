import json
import os

HISTORY_FILE = "download_history.json"

def load_history():
    # Load the history from the JSON file if it exists
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, "r") as f:
            return json.load(f)
    return []

def save_history(history):
    # Save the history to a JSON file
    with open(HISTORY_FILE, "w") as f:
        json.dump(history, f)

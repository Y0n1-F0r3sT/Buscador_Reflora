import os
import json

CONFIG_FILE = "config.json"

def get_config():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, 'r') as f:
            return json.load(f)
    else:
        default_config = {"first_run": True}
        with open(CONFIG_FILE, 'w') as f:
            json.dump(default_config, f)
        return default_config

def update_config(key, value):
    config = get_config()
    config[key] = value
    with open(CONFIG_FILE, 'w') as f:
        json.dump(config, f)
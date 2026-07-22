import json
import requests
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

config_file = BASE_DIR / 'config.json'

def send_discord_notification(message):

    with open(config_file, "r") as file:
        config = json.load(file)

    webhook = config["webhook"]
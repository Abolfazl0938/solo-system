from core.models import Player
import os
import json


class StorageService:
    def __init__(self, filepath: str = "data/player_save.json"):
        self.filepath = filepath

    def save_player(self, player: Player) -> None:
        os.makedirs("data", exist_ok=True)
        dictform_of_player = player.to_dict()
        with open(self.filepath, "w", encoding="utf-8") as f:
            json.dump(dictform_of_player, f, indent=4)

    def load_player_data(self):
        try:
            with open(self.filepath, "r", encoding="utf-8") as f:
                return json.load(f)
        except FileNotFoundError:
            return None

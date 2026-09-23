"""Storage Service: Multi-profile persistence using pathlib and JSON."""

import json
from pathlib import Path
from typing import List, Optional
from core.models import Player


class StorageService:

    def __init__(self, data_dir: str = "data"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.meta_file = self.data_dir / "profiles.json"
        self._ensure_meta_file()

    def _ensure_meta_file(self) -> None:
        if not self.meta_file.exists():
            with open(self.meta_file, "w", encoding="utf-8") as f:
                json.dump(
                    {"profiles": [], "active_profile": None},
                    f,
                    indent=4,
                    ensure_ascii=False,
                )

    def list_profiles(self) -> List[str]:
        with open(self.meta_file, "r", encoding="utf-8") as f:
            data = json.load(f)
        return data.get("profiles", [])

    def get_active_profile_name(self) -> Optional[str]:
        with open(self.meta_file, "r", encoding="utf-8") as f:
            data = json.load(f)
        return data.get("active_profile")

    def set_active_profile(self, name: str) -> None:
        with open(self.meta_file, "r", encoding="utf-8") as f:
            data = json.load(f)
        data["active_profile"] = name
        if name not in data["profiles"]:
            data["profiles"].append(name)
        with open(self.meta_file, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)

    def _get_player_file(self, name: str) -> Path:
        safe_name = "".join(
            c for c in name if c.isalnum() or c in (" ", "_", "-")
        ).strip()
        return self.data_dir / f"player_{safe_name}.json"

    def save_player(self, player: Player) -> None:
        file_path = self._get_player_file(player.name)
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(player.to_dict(), f, indent=4, ensure_ascii=False)
        self.set_active_profile(player.name)

    def load_player(self, name: str) -> Optional[Player]:
        file_path = self._get_player_file(name)
        if not file_path.exists():
            return None
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return Player.from_dict(data)

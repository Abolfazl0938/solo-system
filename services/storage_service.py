import json
from pathlib import Path
from typing import Optional
from core.models import Player


class StorageService:
    def __init__(self, file_path: str = "data/player_save.json") -> None:
        self.path = Path(file_path)
        # ایجاد پوشه والد در صورت عدم وجود
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def save_player(self, player: Player) -> bool:
        """ذخیره‌سازی اطلاعات بازیکن به صورت JSON با استاندارد UTF-8"""
        try:
            with open(self.path, "w", encoding="utf-8") as f:
                json.dump(player.to_dict(), f, indent=4, ensure_ascii=False)
            return True
        except (OSError, IOError) as e:
            print(f"[Error] Failed to save player data: {e}")
            return False

    def load_player(self) -> Optional[Player]:
        """بازیابی اطلاعات بازیکن از فایل JSON"""
        if not self.path.exists():
            return None

        try:
            with open(self.path, "r", encoding="utf-8") as f:
                data = json.load(f)
                return Player.from_dict(data)
        except (json.JSONDecodeError, KeyError, OSError) as e:
            print(f"[Warning] Save file corrupted or unreadable: {e}")
            return None

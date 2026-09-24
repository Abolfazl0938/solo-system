import json
from pathlib import Path
from core.models import Player


class StorageService:
    DATA_DIR = Path("data")

    @classmethod
    def list_profiles(cls) -> list[str]:
        cls.DATA_DIR.mkdir(exist_ok=True)
        files = list(cls.DATA_DIR.glob("*.json"))
        # بازگشت نام فایل‌ها بدون پسوند
        return [f.stem for f in files] if files else ["Sung Jin-Woo"]

    @classmethod
    def save_profile(cls, player: Player) -> None:
        cls.DATA_DIR.mkdir(exist_ok=True)
        file_path = cls.DATA_DIR / f"{player.name}.json"
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(player.to_dict(), f, indent=4)

    @classmethod
    def load_profile(cls, name: str) -> Player:
        cls.DATA_DIR.mkdir(exist_ok=True)
        file_path = cls.DATA_DIR / f"{name}.json"

        if file_path.exists():
            with open(file_path, "r", encoding="utf-8") as f:
                try:
                    data = json.load(f)
                    return Player.from_dict(data)
                except Exception:
                    # اگر فایل خراب بود، یه پروفایل جدید بساز
                    return Player(name=name)
        return Player(name=name)

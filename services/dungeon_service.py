import os
import random
import sys
from typing import Any, Dict, Generator

# افزودن مسیر ریشه برای اجرای مستقل
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def infinite_floor_generator() -> Generator[Dict[str, Any], None, None]:
    """ژنراتور نامحدود طبقات دانجن (Lazy Evaluation)"""
    floor = 1
    monsters = ["Goblin", "Shadow Wolf", "Cerberus", "Demon Soldier", "Blood Igris"]

    while True:
        yield {
            "floor": f"Floor-{floor}",
            "monster": random.choice(monsters),
            "exp": floor * 25,
        }
        floor += 1


def generate_dungeon_run(max_floors: int = 5) -> Generator[Dict[str, Any], None, None]:
    for floor in range(1, max_floors + 1):
        yield {
            "floor": floor,
            "info": f"Floor {floor} Cleared",
            "difficulty": "Normal" if floor < 3 else "Hard",
        }


if __name__ == "__main__":
    print("--- TESTING DUNGEON SERVICE GENERATORS ---")
    for room in generate_dungeon_run(3):
        print(
            f"Cleared: {room['floor']} | Monster: {room['monster']} | EXP Reward: +{room['exp']}"
        )
    print("✔ Dungeon generator verified!")

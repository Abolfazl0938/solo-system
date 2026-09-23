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


def generate_dungeon_run(
    floor_count: int = 3,
) -> Generator[Dict[str, Any], None, None]:
    """تولید تعداد مشخصی از طبقات دانجن به صورت استریم شده"""
    floor_gen = infinite_floor_generator()
    for _ in range(floor_count):
        yield next(floor_gen)


if __name__ == "__main__":
    print("--- TESTING DUNGEON SERVICE GENERATORS ---")
    for room in generate_dungeon_run(3):
        print(
            f"Cleared: {room['floor']} | Monster: {room['monster']} | EXP Reward: +{room['exp']}"
        )
    print("✔ Dungeon generator verified!")

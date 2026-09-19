import sys
import os

# اضافه کردن مسیر ریشه پروژه به sys.path به صورت داینامیک
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.models import HunterRank, Quest, QuestStatus

import time
from typing import Any, Dict, Iterator


class DungeonFloor:
    """کلاس نمایانگر یک طبقه از دانجن"""

    def __init__(
        self, floor_number: int, monster_name: str, exp_reward: int, rank: str
    ):
        self.floor_number = floor_number
        self.monster_name = monster_name
        self.exp_reward = exp_reward
        self.rank = rank

    def to_quest(self) -> Quest:
        """تبدیل طبقه دانجن به یک ماموریت سیستمی قابل ثبت در کاراکتر"""
        return Quest(
            id=f"dungeon_f{self.floor_number}_{int(time.time())}",
            title=f"Floor {self.floor_number}: Defeat {self.monster_name}",
            description=f"Clear floor {self.floor_number} guarded by {self.monster_name} (Rank {self.rank}).",
            exp_reward=self.exp_reward,
            status=QuestStatus.PENDING,
        )

    def __repr__(self) -> str:
        return f"DungeonFloor(F{self.floor_number} | {self.monster_name} | Rank {self.rank} | +{self.exp_reward} EXP)"


class DungeonService:
    """سرویس مدیریت سیاهچال با استفاده از ژنراتورهای نامحدود و تنبل"""

    MONSTERS = {
        "E": ["Goblin Scout", "Giant Ant", "Shadow Wolf"],
        "D": ["Hobgoblin", "Lesser Demon", "Stone Golem"],
        "C": ["Blood Ifrit", "Undead Knight", "Frost Troll"],
        "B": ["Shadow Assassin", "Wyvern", "Abyssal Behemoth"],
        "A": ["High Orc Chieftain", "Ancient Drake", "Iron Sovereign"],
        "S": ["Dragon Monarch", "Arch-Lich", "Ant King"],
    }

    @staticmethod
    def _calculate_floor_rank(floor_number: int) -> str:
        if floor_number <= 5:
            return "E"
        elif floor_number <= 15:
            return "D"
        elif floor_number <= 30:
            return "C"
        elif floor_number <= 50:
            return "B"
        elif floor_number <= 75:
            return "A"
        return "S"

    def infinite_floor_generator(self, start_floor: int = 1) -> Iterator[DungeonFloor]:
        """ژنراتور نامحدود: تولید طبقات دانجن به صورت بی‌پایان و در زمان واقعی (On-the-fly)"""
        current_floor = start_floor
        while True:
            rank = self._calculate_floor_rank(current_floor)
            # انتخاب نام هیولا بر اساس شماره طبقه
            monster_list = self.MONSTERS[rank]
            monster_name = monster_list[(current_floor - 1) % len(monster_list)]

            # پاداش EXP تصاعدی
            exp_reward = current_floor * 50

            floor = DungeonFloor(
                floor_number=current_floor,
                monster_name=monster_name,
                exp_reward=exp_reward,
                rank=rank,
            )

            # توقف اجرای تابع و تحویل شیء طبقه به فراخواننده
            yield floor

            # افزایش شماره طبقه برای فراخوانی بعدی next()
            current_floor += 1

    def generate_dungeon_run(
        self, total_floors: int, start_floor: int = 1
    ) -> Iterator[DungeonFloor]:
        """تولید تعداد مشخصی از طبقات با استفاده از ژنراتور نامحدود"""
        dungeon_stream = self.infinite_floor_generator(start_floor)
        for _ in range(total_floors):
            yield next(dungeon_stream)


# ==========================================
# --- تست‌های اعتبارسنجی (Automated Tests) ---
# ==========================================
if __name__ == "__main__":
    print("--- 1. TESTING INFINITE GENERATOR ---")
    service = DungeonService()
    infinite_stream = service.infinite_floor_generator(start_floor=1)

    # دریافت ۳ طبقه اول به صورت دستی با next()
    f1 = next(infinite_stream)
    f2 = next(infinite_stream)
    f3 = next(infinite_stream)

    print(f"Generated Floor: {f1}")
    print(f"Generated Floor: {f2}")
    print(f"Generated Floor: {f3}")
    assert f1.floor_number == 1 and f1.rank == "E"
    assert f3.floor_number == 3

    print("\n--- 2. TESTING LIMITED RUN GENERATOR (YIELD PIPELINE) ---")
    # شبیه‌سازی یک ران ۵ طبقه‌ای از طبقه ۱۸ (باید رنک C باشد)
    run = service.generate_dungeon_run(total_floors=5, start_floor=18)
    for floor in run:
        print(f"Cleared -> {floor}")

    print("\n--- 3. TESTING CONVERSION TO SYSTEM QUEST ---")
    boss_floor = DungeonFloor(
        floor_number=100, monster_name="Ant King", exp_reward=10000, rank="S"
    )
    system_quest = boss_floor.to_quest()
    assert system_quest.title == "Floor 100: Defeat Ant King"
    assert system_quest.exp_reward == 10000
    print(f"✔ Converted to Quest: {system_quest}")

    print("\n[SUCCESS] Dungeon Generators fully verified!")

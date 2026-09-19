from contextlib import contextmanager
import copy
import os
import sys
import time
from typing import Iterator

# ایمپورت مسیر برای اجرای مستقیم
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.models import Player, Quest, QuestStatus


class DungeonRaidSession:
    """کانتکست منیجر برای مدیریت چرخه حیات ورود و پاک‌سازی دانجن"""

    def __init__(self, player: Player, dungeon_name: str):
        self.player = player
        self.dungeon_name = dungeon_name
        self.start_time: float = 0.0
        self.is_success: bool = False

    def mark_cleared(self) -> None:
        """علامت‌گذاری سشن به عنوان پیروزی"""
        self.is_success = True

    def __enter__(self) -> "DungeonRaidSession":
        self.start_time = time.perf_counter()
        print(
            f"\n[SYSTEM] Hunter {self.player.name} entered dungeon: {self.dungeon_name}"
        )
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> bool:
        elapsed = time.perf_counter() - self.start_time

        if exc_type:
            # اگر خطایی رخ داده باشد
            print(f"[SYSTEM] RAID FAILED! Reason: {exc_val}")
            print(f"[SYSTEM] Time spent before collapse: {elapsed:.2f}s")
            return False  # اجازه بده خطا به لایه‌های بالاتر بره

        if self.is_success:
            print(f"[SYSTEM] RAID CLEARED! Dungeon: {self.dungeon_name}")
            print(f"[SYSTEM] Total clearing time: {elapsed:.4f}s")
        else:
            print(f"[SYSTEM] RAID ENDED: Dungeon was not cleared (Exited safely).")

        return True


@contextmanager
def quest_transaction(player: Player) -> Iterator[None]:
    """کانتکست منیجر تراکنش امن کوئست‌ها با قابلیت Rollback خودکار در صورت خطا"""
    # تهیه نسخه پشتیبان از لیست کوئست‌ها (Deep Copy برای امنیت کامل)
    quest_snapshot = copy.deepcopy(player.quests)

    try:
        print("[DATABASE] Starting quest transaction...")
        yield  # اینجا کنترل به بدنه دستور with داده می‌شود
        print("[DATABASE] Transaction committed successfully.")

    except Exception as e:
        # در صورت بروز هرگونه خطا، لیست را به حالت قبل برمی‌گردانیم
        print(f"[TRANSACTION ROLLBACK] Reverting quests state due to: {e}")
        player.quests = quest_snapshot
        raise  # خطا را مجددا پرتاب کن تا برنامه مطلع شود

    finally:
        print("[DATABASE] Closing transaction session.")


# ==========================================
# --- تست‌های اعتبارسنجی (Automated Tests) ---
# ==========================================
if __name__ == "__main__":
    player = Player(name="Sung Jin-Woo", level=1)

    print("--- 1. TESTING DUNGEON RAID SUCCESS ---")
    with DungeonRaidSession(player, "Double Dungeon") as session:
        time.sleep(0.1)
        session.mark_cleared()

    print("\n--- 2. TESTING QUEST TRANSACTION (ROLLBACK TEST) ---")
    q1 = Quest(
        id="q1",
        title="Training",
        description="Run 10km",
        exp_reward=100,
        status=QuestStatus.PENDING,
    )
    player.add_quest(q1)

    print(f"Initial quest count: {len(player)}")

    try:
        with quest_transaction(player):
            q2 = Quest(
                id="q2",
                title="Fatal Quest",
                description="Impossible Task",
                exp_reward=500,
                status=QuestStatus.PENDING,
            )
            player.add_quest(q2)
            print(f"Quest count inside transaction: {len(player)}")

            # شبیه‌سازی خطای دیتابیس یا منطق برنامه
            raise RuntimeError("Database connection lost while saving q2!")

    except RuntimeError as e:
        print(f"Caught expected error: {e}")

    # بررسی صحت Rollback (تعداد کوئست‌ها باید به ۱ برگرده)
    print(f"Final quest count after rollback: {len(player)}")
    assert len(player) == 1, f"Rollback failed! Expected 1 quest, got {len(player)}"
    print("✔ Transaction Rollback successfully verified!")

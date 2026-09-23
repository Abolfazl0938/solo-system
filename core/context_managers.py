import time
from copy import deepcopy
from contextlib import contextmanager
from typing import Generator
from core.models import Player, Quest, QuestStatus


class DungeonRaidSession:
    """Class-based context manager for tracking raid execution and duration."""

    def __init__(self, dungeon_name: str) -> None:
        self.dungeon_name = dungeon_name
        self.start_time: float = 0.0
        self.monsters_defeated: int = 0

    def record_defeat(self) -> None:
        self.monsters_defeated += 1

    def __enter__(self) -> "DungeonRaidSession":
        self.start_time = time.time()
        print(f"\n[System Log] === Raid Started: {self.dungeon_name} ===")
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> bool:
        elapsed = time.time() - self.start_time
        if exc_type is not None:
            print(f"[System Alert] Raid Failed! Reason: {exc_val}")
            print(f"[System Log] Raid Duration before failure: {elapsed:.2f}s")
            return False  # Propagate exception
        print(f"[System Log] === Raid Completed Successfully: {self.dungeon_name} ===")
        print(
            f"[System Log] Defeated: {self.monsters_defeated} | Duration: {elapsed:.2f}s\n"
        )
        return True


@contextmanager
def quest_transaction(player: Player) -> Generator[Player, None, None]:
    """Atomic transaction context manager for modifying quests with rollback on failure."""
    snapshot = deepcopy(player.quests)
    try:
        yield player
    except Exception as e:
        player.quests = snapshot
        print(f"[Transaction Alert] Error detected: {e}. Changes rolled back!")
        raise

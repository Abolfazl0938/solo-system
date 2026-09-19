from enum import Enum
from typing import Any, Dict, Iterator, List, Optional, Union


class HunterRank(str, Enum):
    E = "E"
    D = "D"
    C = "C"
    B = "B"
    A = "A"
    S = "S"


class QuestStatus(str, Enum):
    PENDING = "PENDING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


class Quest:

    def __init__(
        self,
        id: str,
        title: str,
        description: str = "",
        exp_reward: int = 100,
        status: QuestStatus = QuestStatus.PENDING,
    ):
        self.id = id
        self.title = title
        self.description = description
        self.exp_reward = exp_reward
        self.status = status if isinstance(status, QuestStatus) else QuestStatus(status)

    def complete(self) -> None:
        self.status = QuestStatus.COMPLETED

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "exp_reward": self.exp_reward,
            "status": self.status.value,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Quest":
        return cls(
            id=data["id"],
            title=data["title"],
            description=data.get("description", ""),
            exp_reward=data.get("exp_reward", 100),
            status=QuestStatus(data.get("status", "PENDING")),
        )

    def __repr__(self) -> str:
        return (
            f"Quest(id={self.id!r}, title={self.title!r}, status={self.status.value!r})"
        )

    def __str__(self) -> str:
        return f"[{self.status.value}] {self.title} (+{self.exp_reward} EXP)"


class Player:

    def __init__(
        self,
        name: str,
        level: int = 1,
        exp: int = 0,
        quests: Optional[List[Quest]] = None,
    ):
        self.name = name
        self.level = level
        self.exp = exp
        self.quests: List[Quest] = quests if quests is not None else []

    # --- محاسبات داینامیک رنک ---
    @property
    def completed_quest_count(self) -> int:
        return sum(1 for q in self.quests if q.status == QuestStatus.COMPLETED)

    @property
    def rank(self) -> HunterRank:
        completed = self.completed_quest_count
        if completed >= 15:
            return HunterRank.S
        elif completed >= 10:
            return HunterRank.A
        elif completed >= 6:
            return HunterRank.B
        elif completed >= 3:
            return HunterRank.C
        elif completed >= 1:
            return HunterRank.D
        return HunterRank.E

    # --- متدهای مدیریتی کوئست ---
    def add_quest(self, quest: Quest) -> None:
        self.quests.append(quest)

    def complete_quest(self, quest_id: str) -> bool:
        for quest in self.quests:
            if quest.id == quest_id and quest.status != QuestStatus.COMPLETED:
                quest.complete()
                self.exp += quest.exp_reward
                self._check_level_up()
                return True
        return False

    def _check_level_up(self) -> None:
        while self.exp >= self.level * 100:
            self.exp -= self.level * 100
            self.level += 1

    # ==========================================
    # --- پیاده‌سازی Dunder Methods (Container & Iterator) ---
    # ==========================================

    def __len__(self) -> int:
        """برگرداندن تعداد کل کوئست‌ها هنگام صدا زدن len(player)"""
        return len(self.quests)

    def __getitem__(self, item: Union[int, str, slice]) -> Union[Quest, List[Quest]]:
        """دسترسی با کروشه:

        player[0] -> اولین کوئست
        player["q1"] -> کوئست با آیدی یا تایتل q1
        """
        if isinstance(item, (int, slice)):
            return self.quests[item]

        if isinstance(item, str):
            for quest in self.quests:
                if quest.id == item or quest.title == item:
                    return quest
            raise KeyError(
                f"Quest with ID or Title '{item}' not found in player quests."
            )

        raise TypeError(
            f"Player indices must be integers, slices, or strings, not {type(item).__name__}"
        )

    def __contains__(self, item: Union[Quest, str]) -> bool:
        """پشتیبانی از عملگر in:

        'q1' in player
        quest_obj in player
        """
        if isinstance(item, Quest):
            return item in self.quests

        if isinstance(item, str):
            return any(q.id == item or q.title == item for q in self.quests)

        return False

    def __iter__(self) -> Iterator[Quest]:
        """پشتیبانی مستقیم از حلقه for:

        for quest in player:
        """
        return iter(self.quests)

    def __repr__(self) -> str:
        """نمایش فنی و دولوپر-فرندلی"""
        return (
            f"Player(name={self.name!r}, level={self.level}, "
            f"rank={self.rank.value!r}, quests_count={len(self)})"
        )

    def __str__(self) -> str:
        """نمایش متنی تمیز برای لاگ یا چاپ"""
        return f"Hunter {self.name} | Level {self.level} | Rank {self.rank.value} | Total Quests: {len(self)}"

    # --- سریالایزیشن به دیکشنری ---
    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "level": self.level,
            "exp": self.exp,
            "quests": [q.to_dict() for q in self.quests],
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Player":
        quests = [Quest.from_dict(q) for q in data.get("quests", [])]
        return cls(
            name=data["name"],
            level=data.get("level", 1),
            exp=data.get("exp", 0),
            quests=quests,
        )


# ==========================================
# --- تست‌های اعتبارسنجی (Automated Verification) ---
# ==========================================
if __name__ == "__main__":
    print("--- TESTING DUNDER METHODS ON PLAYER ---")

    player = Player(name="Sung Jinwoo")
    q1 = Quest(id="q1", title="Pushups 100x", exp_reward=100)
    q2 = Quest(id="q2", title="Running 10km", exp_reward=200)

    player.add_quest(q1)
    player.add_quest(q2)

    # 1. تست __len__
    assert len(player) == 2, "Test len(player) failed!"
    print(f"✔ len(player): {len(player)}")

    # 2. تست __getitem__ (عددی و رشته‌ای)
    assert player[0] == q1, "Test player[0] failed!"
    assert player["q2"] == q2, "Test player['q2'] failed!"  # سرچ با ID
    assert (
        player["Pushups 100x"] == q1
    ), "Test player['Pushups 100x'] failed!"  # سرچ با Title
    print("✔ player[0] and player['key'] indexing passed!")

    # 3. تست __contains__ (عملگر in)
    assert q1 in player, "Test quest in player failed!"
    assert "q2" in player, "Test 'q2' in player failed!"
    assert "InvalidQuest" not in player, "Test 'InvalidQuest' in player failed!"
    print("✔ 'in' operator (__contains__) passed!")

    # 4. تست __iter__ (حلقه زدن مستقیم روی پلیر)
    collected_titles = [quest.title for quest in player]
    assert collected_titles == ["Pushups 100x", "Running 10km"]
    print(f"✔ Iteration passed: {collected_titles}")

    # 5. تست __repr__ و __str__
    print(f"✔ repr: {repr(player)}")
    print(f"✔ str:  {str(player)}")

    print("\n[SUCCESS] All Dunder Container & Iterator methods fully verified!")

from enum import Enum
from dataclasses import dataclass
from typing import List, Iterator, Any


class QuestStatus(Enum):
    PENDING = "PENDING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


@dataclass
class Quest:
    id: int
    title: str
    description: str
    reward_exp: int
    rank: str = "E"
    status: QuestStatus = QuestStatus.PENDING

    @property
    def is_completed(self) -> bool:
        return self.status == QuestStatus.COMPLETED

    def complete(self) -> None:
        self.status = QuestStatus.COMPLETED

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "reward_exp": self.reward_exp,
            "rank": self.rank,
            "status": self.status.value,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Quest":
        status_val = data.get("status", QuestStatus.PENDING.value)
        return cls(
            id=data["id"],
            title=data["title"],
            description=data["description"],
            reward_exp=data["reward_exp"],
            rank=data.get("rank", "E"),
            status=(
                QuestStatus(status_val) if isinstance(status_val, str) else status_val
            ),
        )


class Player:
    def __init__(
        self, name: str, level: int = 1, exp: int = 0, rank: str = "E"
    ) -> None:
        self.name = name
        self.level = level
        self.exp = exp
        self.rank = rank
        self.quests: List[Quest] = []

    def add_quest(self, quest: Quest) -> None:
        self.quests.append(quest)

    def gain_exp(self, amount: int) -> None:
        self.exp += amount
        while self.exp >= self.level * 100:
            self.exp -= self.level * 100
            self.level += 1

    # --- Container & Magic Methods ---
    def __len__(self) -> int:
        return len(self.quests)

    def __iter__(self) -> Iterator[Quest]:
        return iter(self.quests)

    def __getitem__(self, item: Any) -> Quest:
        if isinstance(item, int):
            return self.quests[item]
        elif isinstance(item, str):
            for quest in self.quests:
                if quest.title == item:
                    return quest
            raise KeyError(f"Quest with title '{item}' not found.")
        raise TypeError("Index must be int or str.")

    def __contains__(self, item: Any) -> bool:
        if isinstance(item, Quest):
            return item in self.quests
        elif isinstance(item, str):
            return any(q.title == item for q in self.quests)
        return False

    # --- Serialization Methods ---
    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "level": self.level,
            "exp": self.exp,
            "rank": self.rank,
            "quests": [q.to_dict() for q in self.quests],
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Player":
        player = cls(
            name=data["name"],
            level=data.get("level", 1),
            exp=data.get("exp", 0),
            rank=data.get("rank", "E"),
        )
        for q_data in data.get("quests", []):
            player.add_quest(Quest.from_dict(q_data))
        return player

    def __repr__(self) -> str:
        return f"<Player {self.name} | Rank: {self.rank} | Level: {self.level}>"

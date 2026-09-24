from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum


class QuestStatus(Enum):
    PENDING = "PENDING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


@dataclass
class Quest:
    title: str
    exp_reward: int = 0
    status: QuestStatus = QuestStatus.PENDING

    def to_dict(self) -> dict:
        return {
            "title": self.title,
            "exp_reward": self.exp_reward,
            "status": self.status.value,
        }

    @classmethod
    def from_dict(cls, data: dict) -> Quest:
        return cls(
            title=data.get("title", "Unknown"),
            exp_reward=data.get("exp_reward", 0),
            status=QuestStatus(data.get("status", "PENDING")),
        )


@dataclass
class Player:
    name: str
    rank: str = "F"
    level: int = 1
    exp: int = 0
    quests: list[Quest] = field(default_factory=list)

    @property
    def exp_to_next_level(self) -> int:
        return self.level * 100

    def add_exp(self, amount: int):
        self.exp += amount
        while self.exp >= self.exp_to_next_level:
            self.exp -= self.exp_to_next_level
            self.level += 1

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "rank": self.rank,
            "level": self.level,
            "exp": self.exp,
            "quests": [q.to_dict() for q in self.quests],
        }

    @classmethod
    def from_dict(cls, data: dict) -> Player:
        quests = [Quest.from_dict(q) for q in data.get("quests", [])]
        return cls(
            name=data.get("name", "Unknown"),
            rank=data.get("rank", "F"),
            level=data.get("level", 1),
            exp=data.get("exp", 0),
            quests=quests,
        )

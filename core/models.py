"""Domain models for Hunter and Quest management."""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional
from services.time_service import TimeService


class QuestStatus(Enum):
    PENDING = "PENDING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


@dataclass
class Quest:
    title: str
    exp_reward: int
    status: QuestStatus = QuestStatus.PENDING
    created_at: dict = field(default_factory=TimeService.get_current_timestamps)
    completed_at: Optional[dict] = None

    def complete(self) -> None:
        self.status = QuestStatus.COMPLETED
        self.completed_at = TimeService.get_current_timestamps()

    def to_dict(self) -> Dict[str, Any]:
        return {
            "title": self.title,
            "exp_reward": self.exp_reward,
            "status": self.status.value,
            "created_at": self.created_at,
            "completed_at": self.completed_at,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Quest":
        quest = cls(
            title=data["title"],
            exp_reward=data["exp_reward"],
            status=QuestStatus(data.get("status", QuestStatus.PENDING.value)),
        )
        quest.created_at = data.get("created_at", TimeService.get_current_timestamps())
        quest.completed_at = data.get("completed_at")
        return quest


@dataclass
class Player:
    name: str
    level: int = 1
    exp: int = 0
    rank: str = "E"
    quests: List[Quest] = field(default_factory=list)

    def __len__(self) -> int:
        return len(self.quests)

    def __getitem__(self, index: int) -> Quest:
        return self.quests[index]

    def __iter__(self):
        return iter(self.quests)

    def __contains__(self, item: Any) -> bool:
        if isinstance(item, Quest):
            return item in self.quests
        if isinstance(item, str):
            return any(q.title == item for q in self.quests)
        return False

    def add_exp(self, amount: int) -> bool:
        self.exp += amount
        leveled_up = False
        while self.exp >= self.exp_to_next_level:
            self.exp -= self.exp_to_next_level
            self.level += 1
            self._update_rank()
            leveled_up = True
        return leveled_up

    @property
    def exp_to_next_level(self) -> int:
        return self.level * 100

    def _update_rank(self) -> None:
        if self.level >= 50:
            self.rank = "S"
        elif self.level >= 40:
            self.rank = "A"
        elif self.level >= 30:
            self.rank = "B"
        elif self.level >= 20:
            self.rank = "C"
        elif self.level >= 10:
            self.rank = "D"
        else:
            self.rank = "E"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "level": self.level,
            "exp": self.exp,
            "rank": self.rank,
            "quests": [q.to_dict() for q in self.quests],
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Player":
        player = cls(
            name=data["name"],
            level=data["level"],
            exp=data["exp"],
            rank=data["rank"],
        )
        player.quests = [Quest.from_dict(q) for q in data.get("quests", [])]
        return player

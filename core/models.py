from enum import Enum
from core.decorators import system_logger


class QuestNotFoundError(Exception):
    pass


class QuestStatus(Enum):
    PENDING = "PENDING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


class HunterRank(Enum):
    E = ("E-Rank", 0)
    D = ("D-Rank", 4)
    C = ("C-Rank", 9)
    B = ("B-Rank", 14)
    A = ("A-Rank", 19)
    S = ("S-Rank", 20)

    def __init__(self, title: str, required_completed: int):
        self.title = title
        self.required_completed = required_completed


class Quest:
    def __init__(
        self,
        id: int,
        title: str,
        reward_exp: int,
        status: QuestStatus = QuestStatus.PENDING,
    ) -> None:
        self.id: int = id
        self.title: str = title
        self.reward_exp: int = reward_exp
        self.status: QuestStatus = status

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "title": self.title,
            "reward_exp": self.reward_exp,
            "status": self.status.value,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Quest":
        return cls(
            id=data["id"],
            title=data["title"],
            reward_exp=data["reward_exp"],
            status=QuestStatus(data["status"]),
        )

    def complete(self) -> None:
        self.status = QuestStatus.COMPLETED

    def __str__(self) -> str:
        return f"Quest(id={self.id}, title='{self.title}', status={self.status.value}, reward={self.reward_exp} EXP)"


class Player:
    def __init__(self, name: str, level: int = 1, hp: int = 100, exp: int = 0) -> None:
        self.name: str = name
        self.quests: list[Quest] = []
        self.level: int = level
        self.hp: int = hp
        self.exp: int = exp

    def gain_exp(self, amount: int) -> None:
        self.exp += amount

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "quests": [q.to_dict() for q in self.quests],
            "level": self.level,
            "hp": self.hp,
            "exp": self.exp,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Player":
        player_instance = cls(
            name=data["name"],
            level=data.get("level", 1),
            hp=data.get("hp", 100),
            exp=data.get("exp", 0),
        )

        if "quests" in data and isinstance(data["quests"], list):
            for quest_data in data["quests"]:
                quest_instance = Quest.from_dict(quest_data)
                player_instance.add_quest(quest_instance)

        return player_instance

    def add_quest(self, quest: Quest) -> None:
        self.quests.append(quest)

    def completed_quest_count(self) -> int:
        """شمارش کوئست‌هایی که وضعیت آن‌ها COMPLETED است."""
        return sum(1 for q in self.quests if q.status == QuestStatus.COMPLETED)

    @property
    def rank(self) -> HunterRank:
        completed = self.completed_quest_count()
        if completed >= 20:
            return HunterRank.S
        elif completed >= 19:
            return HunterRank.A
        elif completed >= 14:
            return HunterRank.B
        elif completed >= 9:
            return HunterRank.C
        elif completed >= 4:
            return HunterRank.D
        else:
            return HunterRank.E

    @system_logger
    def complete_quest(self, quest_id: int) -> None:
        for quest in self.quests:
            if quest.id == quest_id:
                if quest.status == QuestStatus.COMPLETED:
                    return  # جلوگیری از دادن اکسپی تکراری
                quest.complete()
                self.gain_exp(quest.reward_exp)
                return
        raise QuestNotFoundError(f"Quest with ID {quest_id} not found")

    def __str__(self) -> str:
        return f"Player(Name: {self.name}, Rank: {self.rank.title}, Level: {self.level}, HP: {self.hp}, EXP: {self.exp})"

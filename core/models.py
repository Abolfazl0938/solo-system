from enum import Enum


class QuestNotFoundError(Exception):
    pass


class QuestStatus(Enum):
    PENDING = "PENDING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


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
        # 1. ساخت اولیه Player بدون quests
        player_instance = cls(
            name=data["name"],
            level=data.get("level", 1),  # استفاده از .get برای امنیت بیشتر
            hp=data.get("hp", 100),
            exp=data.get("exp", 0),
        )

        # 2. بازسازی و اضافه کردن quests
        # اطمینان از وجود کلید quests و اینکه لیست است
        if "quests" in data and isinstance(data["quests"], list):
            for quest_data in data["quests"]:
                # فراخوانی Quest.from_dict برای هر کوئست
                quest_instance = Quest.from_dict(quest_data)
                player_instance.add_quest(quest_instance)  # اضافه کردن به لیست player

        return player_instance

    def add_quest(self, quest: Quest) -> None:
        self.quests.append(quest)

    def complete_quest(self, quest_id: int) -> None:
        for i in self.quests:
            if i.id == quest_id:
                i.complete()
                self.gain_exp(i.reward_exp)
                return
        raise QuestNotFoundError(f"Quest with ID {quest_id} not found")

    def __str__(self) -> str:
        return f"Player(Name: {self.name}, Level: {self.level}, HP: {self.hp}, EXP: {self.exp})"

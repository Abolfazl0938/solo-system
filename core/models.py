from enum import Enum


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

    def add_quest(self, quest: Quest) -> None:
        self.quests.append(quest)

    def complete_quest(self, quest_id: int) -> bool:
        for i in self.quests:
            if i.id == quest_id:
                i.complete()
                self.gain_exp(i.reward_exp)
                return True
        return False

    def __str__(self) -> str:
        return f"Player(Name: {self.name}, Level: {self.level}, HP: {self.hp}, EXP: {self.exp})"

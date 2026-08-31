class Player:
    def __init__(self, name: str, level: int = 1, hp: int = 100, exp: int = 0) -> None:
        self.name: str = name
        self.level: int = level
        self.hp: int = hp
        self.exp: int = exp

    def gain_exp(self, amount: int) -> None:
        self.exp += amount

    def __str__(self) -> str:
        return f"Player(Name: {self.name}, Level: {self.level}, HP: {self.hp}, EXP: {self.exp})"

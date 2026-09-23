import pytest
from core.models import Player, Quest, QuestStatus


def test_quest_initialization_and_serialization():
    quest = Quest(
        id=1,
        title="Test Push-ups",
        description="Do 50 pushups",
        reward_exp=50,
        rank="E",
    )
    assert quest.id == 1
    assert quest.status == QuestStatus.PENDING
    assert not quest.is_completed

    data = quest.to_dict()
    assert data["title"] == "Test Push-ups"
    assert data["status"] == "PENDING"

    restored = Quest.from_dict(data)
    assert restored.id == quest.id
    assert restored.title == quest.title
    assert restored.status == quest.status


def test_player_exp_and_level_up():
    player = Player(name="Jin-Woo", rank="E")
    assert player.level == 1
    assert player.exp == 0

    # Test EXP gain without level up
    player.gain_exp(50)
    assert player.exp == 50
    assert player.level == 1

    # Test Level Up (Level 1 requires 100 EXP)
    player.gain_exp(60)
    assert player.level == 2
    assert player.exp == 10  # 110 - 100 = 10 EXP remaining


def test_player_container_dunder_methods():
    player = Player(name="Jin-Woo", rank="E")
    q1 = Quest(id=1, title="Q1", description="D1", reward_exp=10, rank="E")
    q2 = Quest(id=2, title="Q2", description="D2", reward_exp=20, rank="E")

    player.add_quest(q1)
    player.add_quest(q2)

    # __len__
    assert len(player) == 2

    # __contains__
    assert q1 in player

    # __getitem__
    assert player[0] == q1
    assert player[1] == q2

    # __iter__
    quests = [q for q in player]
    assert quests == [q1, q2]

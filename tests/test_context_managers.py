import pytest
from core.models import Player, Quest
from core.context_managers import quest_transaction, DungeonRaidSession


def test_quest_transaction_success():
    player = Player(name="Jin-Woo", rank="E")
    q1 = Quest(id=1, title="Q1", description="D1", reward_exp=10, rank="E")

    with quest_transaction(player):
        player.add_quest(q1)

    assert len(player) == 1
    assert q1 in player


def test_quest_transaction_rollback_on_failure():
    player = Player(name="Jin-Woo", rank="E")
    q_initial = Quest(id=1, title="Initial", description="D1", reward_exp=10, rank="E")
    player.add_quest(q_initial)

    q_fail = Quest(id=2, title="Fail", description="D2", reward_exp=20, rank="E")

    with pytest.raises(RuntimeError):
        with quest_transaction(player):
            player.add_quest(q_fail)
            raise RuntimeError("Simulated transaction crash!")

    # Rollback assertion: player state must match initial snapshot
    assert len(player) == 1
    assert q_fail not in player
    assert player.quests[0].id == 1


def test_dungeon_raid_session_success():
    with DungeonRaidSession("Test Raid") as session:
        session.record_defeat()
        session.record_defeat()
    assert session.monsters_defeated == 2

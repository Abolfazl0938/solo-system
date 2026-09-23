from pathlib import Path
from core.models import Player, Quest
from services.storage_service import StorageService


def test_storage_save_and_load(tmp_path: Path):
    # Use temporary file path for safe isolated testing
    test_save_file = tmp_path / "test_save.json"
    storage = StorageService(file_path=str(test_save_file))

    player = Player(name="Shadow Monarch", rank="S")
    quest = Quest(
        id=1,
        title="Shadow Extraction",
        description="Extract 10 shadows",
        reward_exp=500,
        rank="S",
    )
    player.add_quest(quest)

    # Save
    save_result = storage.save_player(player)
    assert save_result is True
    assert test_save_file.exists()

    # Load
    loaded_player = storage.load_player()
    assert loaded_player is not None
    assert loaded_player.name == "Shadow Monarch"
    assert loaded_player.rank == "S"
    assert len(loaded_player) == 1
    assert loaded_player.quests[0].title == "Shadow Extraction"

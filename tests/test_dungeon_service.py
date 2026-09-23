import types
from services.dungeon_service import generate_dungeon_run


def test_generate_dungeon_run_is_generator():
    gen = generate_dungeon_run(max_floors=3)
    assert isinstance(gen, types.GeneratorType)


def test_generate_dungeon_run_output():
    floors = list(generate_dungeon_run(max_floors=3))
    assert len(floors) == 3
    assert floors[0]["floor"] == 1
    assert floors[2]["floor"] == 3

from velvet_rope import __version__
from velvet_rope.characters import MARLOWE
from velvet_rope.state import GameStatus, Mood, new_game_state


def test_package_imports():
    assert __version__ == "0.1.0"


def test_new_game_initializes_marlowe_state():
    state = new_game_state(MARLOWE)

    assert state.character_id == "marlowe"
    assert state.status is GameStatus.ACTIVE
    assert state.mood is Mood.UNIMPRESSED
    assert state.scores.rapport == 20
    assert state.scores.suspicion == 35
    assert state.scores.patience == 70
    assert state.scores.softspot_progress == 0
    assert state.history == []
    assert state.used_tactics == set()

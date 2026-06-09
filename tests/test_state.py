from typing import get_type_hints

from velvet_rope import __version__
from velvet_rope.characters import MARLOWE, VIVIENNE
from velvet_rope.state import GameState, GameStatus, Mood, new_game_state


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


def test_new_game_initializes_vivienne_state():
    state = new_game_state(VIVIENNE)

    assert state.character_id == "vivienne"
    assert state.status is GameStatus.ACTIVE
    assert state.mood is Mood.UNIMPRESSED
    assert state.scores.rapport == 18
    assert state.scores.suspicion == 30
    assert state.scores.patience == 72
    assert state.scores.softspot_progress == 0
    assert state.history == []


def test_new_game_starts_without_used_tactics():
    state = new_game_state(MARLOWE)

    assert state.used_tactics == set()


def test_new_game_state_type_hints_resolve():
    hints = get_type_hints(new_game_state)

    assert hints["character"].__name__ == "CharacterStateConfig"
    assert hints["return"] is GameState

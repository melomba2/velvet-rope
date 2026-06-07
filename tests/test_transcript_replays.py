import json
from pathlib import Path

import pytest

from velvet_rope.game import GameService
from velvet_rope.model_backends import DeterministicMarloweBackend
from velvet_rope.state import GameStatus, Mood


REPLAYS_FIXTURE_PATH = Path(__file__).parent / "fixtures" / "transcript_replays.json"


def load_replays():
    return json.loads(REPLAYS_FIXTURE_PATH.read_text())["replays"]


REPLAYS = load_replays()


def assert_score_bounds(scores, expected_bounds):
    if "rapport_min" in expected_bounds:
        assert scores.rapport >= expected_bounds["rapport_min"]
    if "suspicion_max" in expected_bounds:
        assert scores.suspicion <= expected_bounds["suspicion_max"]
    if "patience_min" in expected_bounds:
        assert scores.patience >= expected_bounds["patience_min"]
    if "softspot_progress" in expected_bounds:
        assert scores.softspot_progress == expected_bounds["softspot_progress"]


@pytest.mark.parametrize("replay", REPLAYS, ids=lambda replay: replay["id"])
def test_deterministic_transcript_replay(replay):
    service = GameService(backend=DeterministicMarloweBackend())
    state = service.new_game()
    mood_path = []

    for line in replay["player_lines"]:
        state = service.play_turn(state, line)
        mood_path.append(state.mood.value)

    assert state.status is GameStatus(replay["expect"]["final_status"])
    assert state.mood is Mood(replay["expect"]["final_mood"])
    assert state.used_tactics == set(replay["expect"]["used_tactics"])
    assert_score_bounds(state.scores, replay["expect"].get("score_bounds", {}))
    if "mood_path" in replay["expect"]:
        assert mood_path == replay["expect"]["mood_path"]
    if "assistant_reply_contains" in replay["expect"]:
        assert replay["expect"]["assistant_reply_contains"].lower() in state.history[-1].content.lower()

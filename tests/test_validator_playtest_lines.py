import json
from pathlib import Path

import pytest

from velvet_rope.characters import MARLOWE
from velvet_rope.parser import ModelTurn
from velvet_rope.state import Mood, ScoreState, new_game_state
from velvet_rope.validator import read_validator_turn


FIXTURE_PATH = Path(__file__).parent / "fixtures" / "validator_playtest_lines.json"
REQUIRED_FOCUSES = {
    "bribery_vs_innocent_money",
    "repeated_soft_spots",
    "overlapping_keywords",
    "entitlement_false_positives",
    "footwear_empathy",
    "line_logistics",
    "crowd_safety",
    "tiny_disasters",
    "win_loss_edge_cases",
}


def load_fixture_cases():
    payload = json.loads(FIXTURE_PATH.read_text())
    return payload["cases"]


PLAYTEST_CASES = load_fixture_cases()


def model_turn_for_case(case):
    delta = case.get("suggested_score_delta") or {}
    return ModelTurn(
        reply="Fixture probe.",
        mood=Mood(case.get("suggested_model_mood", Mood.UNIMPRESSED.value)),
        score_delta=ScoreState(
            rapport=delta.get("rapport", 0),
            suspicion=delta.get("suspicion", 0),
            patience=delta.get("patience", -1),
            softspot_progress=delta.get("softspot_progress", 0),
        ),
        rationale="Fixture probe.",
        tactic=case.get("suggested_model_tactic", "generic"),
    )


def test_validator_playtest_fixture_has_unique_case_ids():
    case_ids = [case["id"] for case in PLAYTEST_CASES]

    assert len(case_ids) == len(set(case_ids))


def test_validator_playtest_fixture_covers_requested_focuses():
    focuses = {case["focus"] for case in PLAYTEST_CASES}

    assert REQUIRED_FOCUSES <= focuses


@pytest.mark.parametrize("case", PLAYTEST_CASES, ids=lambda case: case["id"])
def test_validator_playtest_line_classification_matches_fixture(case):
    state = new_game_state(MARLOWE)

    validator_read = read_validator_turn(
        MARLOWE,
        state,
        case["line"],
        model_turn_for_case(case),
    )

    assert validator_read.tactic == case["expected_tactic"]
    assert validator_read.tactic not in case.get("should_not_classify_as", [])

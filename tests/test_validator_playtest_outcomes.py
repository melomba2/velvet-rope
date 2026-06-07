import json
from dataclasses import replace
from pathlib import Path

import pytest

from velvet_rope.characters import MARLOWE
from velvet_rope.parser import ModelTurn
from velvet_rope.state import GameStatus, Mood, ScoreState, new_game_state
from velvet_rope.validator import validate_turn


LINES_FIXTURE_PATH = Path(__file__).parent / "fixtures" / "validator_playtest_lines.json"
OUTCOMES_FIXTURE_PATH = Path(__file__).parent / "fixtures" / "validator_playtest_outcomes.json"


def load_json(path):
    return json.loads(path.read_text())


LINE_CASES_BY_ID = {case["id"]: case for case in load_json(LINES_FIXTURE_PATH)["cases"]}
OUTCOME_SCENARIOS = load_json(OUTCOMES_FIXTURE_PATH)["scenarios"]


def model_turn_for_turn(turn):
    delta = turn.get("score_delta", {})
    return ModelTurn(
        reply="Fixture probe.",
        mood=Mood(turn.get("model_mood", Mood.UNIMPRESSED.value)),
        score_delta=ScoreState(
            rapport=delta.get("rapport", 0),
            suspicion=delta.get("suspicion", 0),
            patience=delta.get("patience", -1),
            softspot_progress=delta.get("softspot_progress", 0),
        ),
        rationale="Fixture probe.",
        tactic=turn.get("model_tactic", "generic"),
    )


def state_from_config(config):
    state = new_game_state(MARLOWE)
    if not config:
        return state

    scores = config.get("scores")
    if scores:
        state = replace(
            state,
            scores=ScoreState(
                rapport=scores.get("rapport", state.scores.rapport),
                suspicion=scores.get("suspicion", state.scores.suspicion),
                patience=scores.get("patience", state.scores.patience),
                softspot_progress=scores.get("softspot_progress", state.scores.softspot_progress),
            ),
        )
    if "mood" in config:
        state = replace(state, mood=Mood(config["mood"]))
    if "status" in config:
        state = replace(state, status=GameStatus(config["status"]))
    if "used_tactics" in config:
        state = replace(state, used_tactics=set(config["used_tactics"]))
    return state


def assert_scores(state, expected_scores):
    if "rapport" in expected_scores:
        assert state.scores.rapport == expected_scores["rapport"]
    if "suspicion" in expected_scores:
        assert state.scores.suspicion == expected_scores["suspicion"]
    if "patience" in expected_scores:
        assert state.scores.patience == expected_scores["patience"]
    if "softspot_progress" in expected_scores:
        assert state.scores.softspot_progress == expected_scores["softspot_progress"]


def assert_turn_expectations(state, expectation):
    if "status" in expectation:
        assert state.status is GameStatus(expectation["status"])
    if "mood" in expectation:
        assert state.mood is Mood(expectation["mood"])
    if "scores" in expectation:
        assert_scores(state, expectation["scores"])
    for tactic in expectation.get("used_tactics_include", []):
        assert tactic in state.used_tactics
    for tactic in expectation.get("used_tactics_exclude", []):
        assert tactic not in state.used_tactics
    if "hint_contains" in expectation:
        assert expectation["hint_contains"] in state.hint


def test_validator_playtest_outcome_fixture_references_existing_lines():
    referenced_case_ids = {
        turn["case_id"]
        for scenario in OUTCOME_SCENARIOS
        for turn in scenario["turns"]
    }

    assert referenced_case_ids <= set(LINE_CASES_BY_ID)


@pytest.mark.parametrize("scenario", OUTCOME_SCENARIOS, ids=lambda scenario: scenario["id"])
def test_validator_playtest_outcome_scenario(scenario):
    state = state_from_config(scenario.get("initial_state"))

    for turn in scenario["turns"]:
        line_case = LINE_CASES_BY_ID[turn["case_id"]]
        state = validate_turn(
            MARLOWE,
            state,
            line_case["line"],
            model_turn_for_turn(turn),
        )
        assert_turn_expectations(state, turn["expect"])

from velvet_rope.parser import parse_model_turn
from velvet_rope.state import Mood


def test_parse_valid_model_json():
    raw = """
    {
      "reply": "You noticed the line. Alarming competence.",
      "mood": "respected",
      "score_delta": {
        "rapport": 9,
        "suspicion": -4,
        "patience": -2,
        "softspot_progress": 1
      },
      "rationale": "Player noticed line logistics.",
      "tactic": "line_logistics"
    }
    """

    turn = parse_model_turn(raw)

    assert turn.reply == "You noticed the line. Alarming competence."
    assert turn.mood is Mood.RESPECTED
    assert turn.score_delta.rapport == 9
    assert turn.score_delta.suspicion == -4
    assert turn.score_delta.patience == -2
    assert turn.score_delta.softspot_progress == 1
    assert turn.rationale == "Player noticed line logistics."
    assert turn.tactic == "line_logistics"


def test_parse_malformed_json_falls_back_to_reply_text():
    turn = parse_model_turn("Marlowe checks the clipboard and sighs.")

    assert turn.reply == "Marlowe checks the clipboard and sighs."
    assert turn.mood is Mood.UNIMPRESSED
    assert turn.score_delta.rapport == 0
    assert turn.score_delta.suspicion == 0
    assert turn.score_delta.patience == -1
    assert turn.score_delta.softspot_progress == 0
    assert turn.rationale == "Model output was not structured JSON."
    assert turn.tactic == "unstructured"


def test_parse_unknown_mood_falls_back_to_unimpressed():
    raw = '{"reply": "No.", "mood": "sparkly", "score_delta": {}, "rationale": "", "tactic": ""}'

    turn = parse_model_turn(raw)

    assert turn.mood is Mood.UNIMPRESSED

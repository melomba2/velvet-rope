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


def test_parse_truncated_json_does_not_expose_raw_json_to_player():
    raw = """
    {
      "reply": "Aurelia begins to answer...",
      "mood": "respected",
      "score_delta": {
        "rapport": 5,
        "suspicion": -2
    """

    turn = parse_model_turn(raw)

    assert "{" not in turn.reply
    assert '"reply"' not in turn.reply
    assert "Aurelia begins" not in turn.reply
    assert turn.reply == "The reply arrives garbled. Try that read again."
    assert turn.mood is Mood.UNIMPRESSED
    assert turn.rationale == "Model output was malformed JSON."
    assert turn.tactic == "unstructured"


def test_parse_unknown_mood_falls_back_to_unimpressed():
    raw = '{"reply": "No.", "mood": "sparkly", "score_delta": {}, "rationale": "", "tactic": ""}'

    turn = parse_model_turn(raw)

    assert turn.mood is Mood.UNIMPRESSED


def test_parse_json_string_output_falls_back_to_string_reply():
    turn = parse_model_turn('"Marlowe sighs."')

    assert turn.reply == "Marlowe sighs."
    assert turn.mood is Mood.UNIMPRESSED
    assert turn.score_delta.rapport == 0
    assert turn.score_delta.suspicion == 0
    assert turn.score_delta.patience == -1
    assert turn.score_delta.softspot_progress == 0
    assert turn.rationale == "Model output was not a JSON object."
    assert turn.tactic == "unstructured"


def test_parse_json_list_output_falls_back_safely():
    turn = parse_model_turn("[]")

    assert turn.reply == "Marlowe checks the clipboard and says nothing."
    assert turn.mood is Mood.UNIMPRESSED
    assert turn.score_delta.rapport == 0
    assert turn.score_delta.suspicion == 0
    assert turn.score_delta.patience == -1
    assert turn.score_delta.softspot_progress == 0
    assert turn.rationale == "Model output was not a JSON object."
    assert turn.tactic == "unstructured"


def test_parse_non_dict_score_delta_uses_default_score_delta():
    turn = parse_model_turn('{"reply": "No.", "score_delta": "oops"}')

    assert turn.reply == "No."
    assert turn.score_delta.rapport == 0
    assert turn.score_delta.suspicion == 0
    assert turn.score_delta.patience == -1
    assert turn.score_delta.softspot_progress == 0


def test_parse_non_int_score_delta_value_uses_field_default():
    turn = parse_model_turn('{"score_delta": {"rapport": "many", "suspicion": 3}}')

    assert turn.score_delta.rapport == 0
    assert turn.score_delta.suspicion == 3
    assert turn.score_delta.patience == -1
    assert turn.score_delta.softspot_progress == 0

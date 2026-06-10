from __future__ import annotations

from dataclasses import dataclass
import json
from typing import Any

from velvet_rope.state import Mood, ScoreState


@dataclass(frozen=True)
class ModelTurn:
    reply: str
    mood: Mood
    score_delta: ScoreState
    rationale: str
    tactic: str


def parse_model_turn(raw_output: str) -> ModelTurn:
    raw_output = raw_output.strip()
    try:
        payload = json.loads(raw_output)
    except json.JSONDecodeError:
        if _looks_like_malformed_json(raw_output):
            return _fallback_turn(
                reply="The reply arrives garbled. Try that read again.",
                rationale="Model output was malformed JSON.",
            )
        return _fallback_turn(
            reply=raw_output or "Marlowe checks the clipboard and sighs.",
            rationale="Model output was not structured JSON.",
        )

    if not isinstance(payload, dict):
        reply = payload.strip() if isinstance(payload, str) else ""
        return _fallback_turn(
            reply=reply or "Marlowe checks the clipboard and says nothing.",
            rationale="Model output was not a JSON object.",
        )

    score_delta = payload.get("score_delta") or {}
    if not isinstance(score_delta, dict):
        score_delta = {}

    return ModelTurn(
        reply=str(payload.get("reply") or "Marlowe checks the clipboard and says nothing."),
        mood=_parse_mood(payload.get("mood")),
        score_delta=ScoreState(
            rapport=_safe_int(score_delta.get("rapport"), default=0),
            suspicion=_safe_int(score_delta.get("suspicion"), default=0),
            patience=_safe_int(score_delta.get("patience"), default=-1),
            softspot_progress=_safe_int(score_delta.get("softspot_progress"), default=0),
        ),
        rationale=str(payload.get("rationale") or ""),
        tactic=str(payload.get("tactic") or "unspecified"),
    )


def _parse_mood(value: object) -> Mood:
    try:
        return Mood(str(value))
    except ValueError:
        return Mood.UNIMPRESSED


def _looks_like_malformed_json(raw_output: str) -> bool:
    stripped = raw_output.lstrip()
    return stripped.startswith("{") or stripped.startswith("[")


def _fallback_turn(reply: str, rationale: str) -> ModelTurn:
    return ModelTurn(
        reply=reply,
        mood=Mood.UNIMPRESSED,
        score_delta=_default_score_delta(),
        rationale=rationale,
        tactic="unstructured",
    )


def _default_score_delta() -> ScoreState:
    return ScoreState(rapport=0, suspicion=0, patience=-1, softspot_progress=0)


def _safe_int(value: Any, default: int) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return default

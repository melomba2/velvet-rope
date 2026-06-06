from __future__ import annotations

from dataclasses import dataclass
import json

from velvet_rope.state import Mood, ScoreState


@dataclass(frozen=True)
class ModelTurn:
    reply: str
    mood: Mood
    score_delta: ScoreState
    rationale: str
    tactic: str


def parse_model_turn(raw_output: str) -> ModelTurn:
    try:
        payload = json.loads(raw_output.strip())
    except json.JSONDecodeError:
        return ModelTurn(
            reply=raw_output.strip() or "Marlowe checks the clipboard and sighs.",
            mood=Mood.UNIMPRESSED,
            score_delta=ScoreState(rapport=0, suspicion=0, patience=-1, softspot_progress=0),
            rationale="Model output was not structured JSON.",
            tactic="unstructured",
        )

    score_delta = payload.get("score_delta") or {}
    return ModelTurn(
        reply=str(payload.get("reply") or "Marlowe checks the clipboard and says nothing."),
        mood=_parse_mood(payload.get("mood")),
        score_delta=ScoreState(
            rapport=int(score_delta.get("rapport", 0)),
            suspicion=int(score_delta.get("suspicion", 0)),
            patience=int(score_delta.get("patience", -1)),
            softspot_progress=int(score_delta.get("softspot_progress", 0)),
        ),
        rationale=str(payload.get("rationale") or ""),
        tactic=str(payload.get("tactic") or "unspecified"),
    )


def _parse_mood(value: object) -> Mood:
    try:
        return Mood(str(value))
    except ValueError:
        return Mood.UNIMPRESSED

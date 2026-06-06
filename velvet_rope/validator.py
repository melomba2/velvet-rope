from __future__ import annotations

from dataclasses import replace
import re

from velvet_rope.characters import Character
from velvet_rope.parser import ModelTurn
from velvet_rope.state import GameState, GameStatus, Mood, ScoreState

_SOFTSPOT_TACTIC_KEYWORDS = (
    ("comfortable_shoes", ("comfortable shoes", "shoes")),
    ("clipboard_respect", ("clipboard",)),
    ("tiny_disasters", ("tiny disasters", "preventing disasters")),
    ("crowd_safety", ("crowd", "safety", "door work")),
    ("line_logistics", ("line", "queue", "logistics")),
)


def validate_turn(
    character: Character,
    state: GameState,
    player_message: str,
    model_turn: ModelTurn,
) -> GameState:
    if state.status is not GameStatus.ACTIVE:
        return state

    if _contains_any(player_message, character.meta_keywords):
        return _apply_meta_penalty(character, state)

    tactic = _normalized_tactic(player_message, model_turn.tactic)
    repeated_tactic = tactic in state.used_tactics
    touches_softspot = _contains_any(player_message, character.softspot_keywords)
    proposed_winning_mood = model_turn.mood in {Mood.SOFTENED, Mood.LETTING_YOU_IN}
    delta = _clamp_delta(model_turn.score_delta, touches_softspot, repeated_tactic, model_turn.mood)
    delta = _close_endgame_delta(character, state, model_turn.mood, delta)
    next_scores = _apply_delta(state.scores, delta)
    next_mood = _choose_mood(character, next_scores, model_turn.mood)
    if (
        touches_softspot
        and not repeated_tactic
        and next_scores.softspot_progress > state.scores.softspot_progress
        and next_mood is Mood.UNIMPRESSED
    ):
        next_mood = Mood.RESPECTED
    next_status = _choose_status(character, next_scores, proposed_winning_mood)

    if next_status is GameStatus.WON:
        next_mood = Mood.LETTING_YOU_IN
    if next_status is GameStatus.LOST:
        next_mood = Mood.DONE_WITH_YOU

    return replace(
        state,
        scores=next_scores,
        mood=next_mood,
        status=next_status,
        used_tactics=state.used_tactics | {tactic},
        hint=_hint_for(character.display_name, next_mood, touches_softspot, repeated_tactic),
    )


def _clamp_delta(
    delta: ScoreState,
    touches_softspot: bool,
    repeated_tactic: bool,
    proposed_mood: Mood,
) -> ScoreState:
    if repeated_tactic:
        return ScoreState(rapport=1, suspicion=0, patience=-2, softspot_progress=0)

    clamped = ScoreState(
        rapport=_clamp(delta.rapport, -8, 12),
        suspicion=_clamp(delta.suspicion, -10, 15),
        patience=_clamp(delta.patience, -10, 5),
        softspot_progress=_clamp(delta.softspot_progress, 0, 1) if touches_softspot else 0,
    )
    if not touches_softspot or proposed_mood in {Mood.SUSPICIOUS, Mood.DONE_WITH_YOU}:
        return clamped
    return ScoreState(
        rapport=max(clamped.rapport, 6),
        suspicion=min(clamped.suspicion, -2),
        patience=clamped.patience,
        softspot_progress=max(clamped.softspot_progress, 1),
    )


def _close_endgame_delta(
    character: Character,
    state: GameState,
    proposed_mood: Mood,
    delta: ScoreState,
) -> ScoreState:
    missing_rapport = character.win_rapport - state.scores.rapport
    if (
        proposed_mood is Mood.LETTING_YOU_IN
        and state.mood is Mood.SOFTENED
        and 0 < missing_rapport <= 5
        and state.scores.suspicion <= character.max_win_suspicion
        and state.scores.patience > 0
        and state.scores.softspot_progress >= character.min_win_softspot_progress
    ):
        return ScoreState(
            rapport=max(delta.rapport, missing_rapport),
            suspicion=min(delta.suspicion, 0),
            patience=delta.patience,
            softspot_progress=delta.softspot_progress,
        )
    return delta


def _apply_delta(scores: ScoreState, delta: ScoreState) -> ScoreState:
    return ScoreState(
        rapport=_clamp(scores.rapport + delta.rapport, 0, 100),
        suspicion=_clamp(scores.suspicion + delta.suspicion, 0, 100),
        patience=_clamp(scores.patience + delta.patience, 0, 100),
        softspot_progress=_clamp(scores.softspot_progress + delta.softspot_progress, 0, 3),
    )


def _apply_meta_penalty(character: Character, state: GameState) -> GameState:
    scores = ScoreState(
        rapport=state.scores.rapport,
        suspicion=_clamp(state.scores.suspicion + 20, 0, 100),
        patience=_clamp(state.scores.patience - 10, 0, 100),
        softspot_progress=state.scores.softspot_progress,
    )
    status = GameStatus.LOST if scores.patience <= 0 else GameStatus.ACTIVE
    mood = Mood.DONE_WITH_YOU if status is GameStatus.LOST else Mood.SUSPICIOUS
    return replace(
        state,
        scores=scores,
        mood=mood,
        status=status,
        hint=f"{character.display_name} notices you trying to rules-lawyer the door.",
    )


def _choose_mood(character: Character, scores: ScoreState, proposed_mood: Mood) -> Mood:
    if scores.patience <= 0:
        return Mood.DONE_WITH_YOU
    if _meets_win_scores(character, scores) and proposed_mood in {Mood.SOFTENED, Mood.LETTING_YOU_IN}:
        return Mood.LETTING_YOU_IN
    if scores.suspicion >= 60:
        return Mood.SUSPICIOUS
    if scores.softspot_progress >= character.min_win_softspot_progress:
        return Mood.SOFTENED
    if scores.rapport >= 45:
        return Mood.RESPECTED
    if proposed_mood is Mood.AMUSED:
        return Mood.AMUSED
    return proposed_mood


def _choose_status(character: Character, scores: ScoreState, proposed_winning_mood: bool) -> GameStatus:
    if scores.patience <= 0:
        return GameStatus.LOST
    if _meets_win_scores(character, scores) and proposed_winning_mood:
        return GameStatus.WON
    return GameStatus.ACTIVE


def _meets_win_scores(character: Character, scores: ScoreState) -> bool:
    return (
        scores.rapport >= character.win_rapport
        and scores.suspicion <= character.max_win_suspicion
        and scores.patience > 0
        and scores.softspot_progress >= character.min_win_softspot_progress
    )


def _hint_for(display_name: str, mood: Mood, touches_softspot: bool, repeated_tactic: bool) -> str:
    if repeated_tactic:
        return f"{display_name} has heard that angle already."
    if touches_softspot and mood in {Mood.RESPECTED, Mood.SOFTENED, Mood.LETTING_YOU_IN}:
        return f"That landed better than {display_name} expected."
    if mood is Mood.SUSPICIOUS:
        return f"{display_name}'s eyes narrow."
    return ""


def _contains_any(text: str, needles: tuple[str, ...]) -> bool:
    lowered = text.lower()
    return any(_contains_keyword(lowered, needle.lower()) for needle in needles if needle)


def _normalized_tactic(player_message: str, model_tactic: str) -> str:
    for tactic, keywords in _SOFTSPOT_TACTIC_KEYWORDS:
        if _contains_any(player_message, keywords):
            return tactic
    normalized = re.sub(r"\W+", "_", model_tactic.strip().lower()).strip("_")
    return normalized or "unspecified"


def _contains_keyword(lowered_text: str, needle: str) -> bool:
    pattern = r"(?<!\w)" + re.escape(needle) + r"(?!\w)"
    return re.search(pattern, lowered_text) is not None


def _clamp(value: int, minimum: int, maximum: int) -> int:
    return max(minimum, min(maximum, value))

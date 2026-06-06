from __future__ import annotations

from dataclasses import replace

from velvet_rope.characters import Character
from velvet_rope.parser import ModelTurn
from velvet_rope.state import GameState, GameStatus, Mood, ScoreState


def validate_turn(
    character: Character,
    state: GameState,
    player_message: str,
    model_turn: ModelTurn,
) -> GameState:
    if state.status is not GameStatus.ACTIVE:
        return state

    if _contains_any(player_message, character.meta_keywords):
        return _apply_meta_penalty(state)

    tactic = model_turn.tactic or "unspecified"
    repeated_tactic = tactic in state.used_tactics
    touches_softspot = _contains_any(player_message, character.softspot_keywords)
    delta = _clamp_delta(model_turn.score_delta, touches_softspot, repeated_tactic)
    next_scores = _apply_delta(state.scores, delta)
    next_mood = _choose_mood(character, next_scores, model_turn.mood)
    next_status = _choose_status(character, next_scores, next_mood)

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
        hint=_hint_for(next_mood, touches_softspot, repeated_tactic),
    )


def _clamp_delta(delta: ScoreState, touches_softspot: bool, repeated_tactic: bool) -> ScoreState:
    if repeated_tactic:
        return ScoreState(rapport=1, suspicion=0, patience=-2, softspot_progress=0)

    return ScoreState(
        rapport=_clamp(delta.rapport, -8, 12),
        suspicion=_clamp(delta.suspicion, -10, 15),
        patience=_clamp(delta.patience, -10, 5),
        softspot_progress=_clamp(delta.softspot_progress, 0, 1) if touches_softspot else 0,
    )


def _apply_delta(scores: ScoreState, delta: ScoreState) -> ScoreState:
    return ScoreState(
        rapport=_clamp(scores.rapport + delta.rapport, 0, 100),
        suspicion=_clamp(scores.suspicion + delta.suspicion, 0, 100),
        patience=_clamp(scores.patience + delta.patience, 0, 100),
        softspot_progress=_clamp(scores.softspot_progress + delta.softspot_progress, 0, 3),
    )


def _apply_meta_penalty(state: GameState) -> GameState:
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
        hint="Marlowe notices you trying to rules-lawyer the door.",
    )


def _choose_mood(character: Character, scores: ScoreState, proposed_mood: Mood) -> Mood:
    if scores.patience <= 0:
        return Mood.DONE_WITH_YOU
    if _meets_win_scores(character, scores) and proposed_mood in {Mood.SOFTENED, Mood.LETTING_YOU_IN}:
        return Mood.LETTING_YOU_IN
    if scores.suspicion >= 60:
        return Mood.SUSPICIOUS
    if scores.softspot_progress >= 2 and scores.rapport >= 60:
        return Mood.SOFTENED
    if scores.rapport >= 45:
        return Mood.RESPECTED
    if proposed_mood is Mood.AMUSED:
        return Mood.AMUSED
    return proposed_mood


def _choose_status(character: Character, scores: ScoreState, mood: Mood) -> GameStatus:
    if scores.patience <= 0:
        return GameStatus.LOST
    if _meets_win_scores(character, scores) and mood in {Mood.SOFTENED, Mood.LETTING_YOU_IN}:
        return GameStatus.WON
    return GameStatus.ACTIVE


def _meets_win_scores(character: Character, scores: ScoreState) -> bool:
    return (
        scores.rapport >= character.win_rapport
        and scores.suspicion <= character.max_win_suspicion
        and scores.patience > 0
        and scores.softspot_progress >= character.min_win_softspot_progress
    )


def _hint_for(mood: Mood, touches_softspot: bool, repeated_tactic: bool) -> str:
    if repeated_tactic:
        return "Marlowe has heard that angle already."
    if touches_softspot and mood in {Mood.RESPECTED, Mood.SOFTENED, Mood.LETTING_YOU_IN}:
        return "That landed better than Marlowe expected."
    if mood is Mood.SUSPICIOUS:
        return "Marlowe's eyes narrow."
    return ""


def _contains_any(text: str, needles: tuple[str, ...]) -> bool:
    lowered = text.lower()
    return any(needle in lowered for needle in needles)


def _clamp(value: int, minimum: int, maximum: int) -> int:
    return max(minimum, min(maximum, value))

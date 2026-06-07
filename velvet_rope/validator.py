from __future__ import annotations

from dataclasses import replace
import re

from velvet_rope.characters import Character
from velvet_rope.parser import ModelTurn
from velvet_rope.state import GameState, GameStatus, Mood, ScoreState

SOFTSPOT_TACTICS = frozenset({"line_logistics", "comfort_empathy", "tiny_disasters", "crowd_safety"})

_TACTIC_KEYWORDS = (
    ("meta_gaming", ("system prompt", "ignore previous", "developer message", "hidden rule", "password", "jailbreak", "prompt injection", "reveal your instructions")),
    ("bribery", ("bribe", "pay you", "cash", "money", "fifty bucks", "hundred bucks", "tip you", "venmo", "celebrity", "vip")),
    ("entitlement", ("do you know who i am", "move aside", "let me in now", "i belong inside", "i am on the list", "you have to let me in", "i demand", "demand entry", "idiot")),
    ("comfort_empathy", ("comfortable shoes", "shoes", "feet", "standing all night", "break", "fatigue", "tired", "weather")),
    ("tiny_disasters", ("tiny disasters", "preventing disasters")),
    ("crowd_safety", ("crowd", "safety", "door work")),
    ("line_logistics", ("line", "queue", "logistics", "clipboard")),
    ("generic_charm", ("please", "compliment", "compliments", "nice", "cool", "handsome", "best bouncer", "clearly the best", "you are the best", "you're the best", "great bouncer")),
)


def validate_turn(
    character: Character,
    state: GameState,
    player_message: str,
    model_turn: ModelTurn,
) -> GameState:
    if state.status is not GameStatus.ACTIVE:
        return state

    tactic = _normalized_tactic(player_message, model_turn.tactic)
    bad_faith_tactic = tactic in {"meta_gaming", "bribery", "entitlement"}
    if _contains_any(player_message, character.meta_keywords):
        return _apply_meta_penalty(character, state)
    if bad_faith_tactic:
        return _apply_bad_faith_penalty(character, state, tactic)

    repeated_tactic = tactic in state.used_tactics
    touches_softspot = _contains_any(player_message, character.softspot_keywords)
    is_softspot_tactic = tactic in SOFTSPOT_TACTICS
    proposed_mood = Mood.UNIMPRESSED if tactic == "generic_charm" else model_turn.mood
    proposed_winning_mood = proposed_mood in {Mood.SOFTENED, Mood.LETTING_YOU_IN}
    delta = _clamp_delta(model_turn.score_delta, is_softspot_tactic, repeated_tactic, proposed_mood, tactic)
    delta = _close_endgame_delta(character, state, proposed_mood, delta)
    next_scores = _apply_delta(state.scores, delta)
    next_mood = _choose_mood(character, next_scores, proposed_mood)
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
        hint=_hint_for(character.display_name, next_mood, tactic, is_softspot_tactic, repeated_tactic),
    )


def _clamp_delta(
    delta: ScoreState,
    is_softspot_tactic: bool,
    repeated_tactic: bool,
    proposed_mood: Mood,
    tactic: str,
) -> ScoreState:
    if tactic == "generic_charm":
        return ScoreState(rapport=1, suspicion=0, patience=-2, softspot_progress=0)
    if repeated_tactic:
        return ScoreState(rapport=1, suspicion=0, patience=-2, softspot_progress=0)

    clamped = ScoreState(
        rapport=_clamp(delta.rapport, -8, 12),
        suspicion=_clamp(delta.suspicion, -10, 15),
        patience=_clamp(delta.patience, -10, 5),
        softspot_progress=_clamp(delta.softspot_progress, 0, 1) if is_softspot_tactic else 0,
    )
    if not is_softspot_tactic or proposed_mood in {Mood.SUSPICIOUS, Mood.DONE_WITH_YOU}:
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


def _apply_bad_faith_penalty(character: Character, state: GameState, tactic: str) -> GameState:
    if tactic == "bribery":
        delta = ScoreState(rapport=-2, suspicion=15, patience=-6, softspot_progress=0)
        hint = "The rope dislikes transactions. Marlowe dislikes them more."
    elif tactic == "entitlement":
        delta = ScoreState(rapport=-6, suspicion=12, patience=-10, softspot_progress=0)
        hint = "Entitlement makes the clipboard heavier."
    else:
        delta = ScoreState(rapport=0, suspicion=20, patience=-10, softspot_progress=0)
        hint = f"{character.display_name} notices you trying to rules-lawyer the door."

    scores = _apply_delta(state.scores, delta)
    status = GameStatus.LOST if scores.patience <= 0 else GameStatus.ACTIVE
    mood = Mood.DONE_WITH_YOU if status is GameStatus.LOST else Mood.SUSPICIOUS
    return replace(
        state,
        scores=scores,
        mood=mood,
        status=status,
        used_tactics=state.used_tactics | {tactic},
        hint=hint,
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


def _hint_for(
    display_name: str,
    mood: Mood,
    tactic: str,
    is_softspot_tactic: bool,
    repeated_tactic: bool,
) -> str:
    if tactic == "generic_charm":
        return "Marlowe has heard compliments before. Specificity might survive the clipboard."
    if repeated_tactic and is_softspot_tactic:
        return "Good instinct, but the same read twice is starting to sound rehearsed."
    if is_softspot_tactic and mood in {Mood.RESPECTED, Mood.SOFTENED, Mood.LETTING_YOU_IN}:
        return f"That landed. {display_name} noticed you noticed the job."
    if mood is Mood.SUSPICIOUS:
        return f"{display_name}'s eyes narrow."
    return ""


def _contains_any(text: str, needles: tuple[str, ...]) -> bool:
    lowered = text.lower()
    return any(_contains_keyword(lowered, needle.lower()) for needle in needles if needle)


def _normalized_tactic(player_message: str, model_tactic: str) -> str:
    for tactic, keywords in _TACTIC_KEYWORDS:
        if _contains_any(player_message, keywords):
            return tactic
    normalized = re.sub(r"\W+", "_", model_tactic.strip().lower()).strip("_")
    if normalized in {"generic", "unspecified"}:
        return "generic_charm"
    return normalized or "unspecified"


def _contains_keyword(lowered_text: str, needle: str) -> bool:
    pattern = r"(?<!\w)" + re.escape(needle) + r"(?!\w)"
    return re.search(pattern, lowered_text) is not None


def _clamp(value: int, minimum: int, maximum: int) -> int:
    return max(minimum, min(maximum, value))

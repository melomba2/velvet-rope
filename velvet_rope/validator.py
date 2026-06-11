from __future__ import annotations

from dataclasses import dataclass
from dataclasses import replace
import re

from velvet_rope.characters import Character
from velvet_rope.parser import ModelTurn
from velvet_rope.state import GameState, GameStatus, Mood, ScoreState

SOFTSPOT_TACTICS = frozenset({"line_logistics", "comfort_empathy", "tiny_disasters", "crowd_safety"})
BAD_FAITH_TACTICS = frozenset(
    {
        "meta_gaming",
        "bribery",
        "entitlement",
        "recipe_theft",
        "sample_entitlement",
        "mascot_insult",
        "craft_dismissal",
        "secret_line",
        "star_entitlement",
        "theater_dismissal",
        "overacting",
        "final_password",
        "vip_conquest",
        "magic_consumption",
    }
)

_TACTIC_KEYWORDS = (
    ("meta_gaming", ("system prompt", "ignore previous", "developer message", "hidden rule", "password", "jailbreak", "prompt injection", "reveal your instructions")),
    ("bribery", ("bribe", "slip you", "pay you", "cash", "fifty bucks", "a hundred", "hundred bucks", "tip you", "venmo", "celebrity", "vip")),
    ("entitlement", ("do you know who i am", "move aside", "let me in now", "i belong inside", "i am on the list", "you have to let me in", "i demand", "demand entry", "idiot")),
    ("comfort_empathy", ("comfortable shoes", "shoes", "feet", "footwear", "footware", "orthotics", "concrete", "standing all night", "standing on concrete", "break", "fatigue", "tired", "weather")),
    ("tiny_disasters", ("tiny disasters", "preventing disasters", "small civic emergency", "medical emergency", "brawl", "shutdown")),
    ("crowd_safety", ("crowd", "safety", "door work", "keep the peace", "keeping the peace", "people happy", "obnoxious folks", "fire marshal", "exits clear", "occupancy", "de-escalate", "deescalate", "managed expectations", "clear exits")),
    ("line_logistics", ("line", "queue", "logistics", "clipboard")),
    ("generic_charm", ("please", "compliment", "compliments", "nice", "cool", "handsome", "best bouncer", "clearly the best", "you are the best", "you're the best", "great bouncer")),
)


@dataclass(frozen=True)
class ValidatorRead:
    tactic: str
    repeated_tactic: bool
    is_softspot_tactic: bool
    bad_faith_tactic: bool


def read_validator_turn(
    character: Character,
    state: GameState,
    player_message: str,
    model_turn: ModelTurn,
) -> ValidatorRead:
    tactic = _normalized_tactic(character, player_message, model_turn.tactic)
    softspot_tactics = character.softspot_tactics or tuple(SOFTSPOT_TACTICS)
    has_meta_keyword = _contains_any(player_message, character.meta_keywords)
    if has_meta_keyword:
        tactic = "meta_gaming"
    elif tactic == "meta_gaming":
        tactic = "generic_charm"
    elif tactic in BAD_FAITH_TACTICS and not _contains_tactic_keywords(character, player_message, tactic):
        tactic = "generic_charm"
    elif character.character_id == "lenore" and tactic == "timing_restraint":
        tactic = "generic_charm"
    elif (
        tactic in softspot_tactics
        and not _contains_any(player_message, character.softspot_keywords)
        and _is_tiny_followup(player_message)
    ):
        tactic = "generic_charm"
    return ValidatorRead(
        tactic=tactic,
        repeated_tactic=tactic in state.used_tactics,
        is_softspot_tactic=tactic in softspot_tactics,
        bad_faith_tactic=tactic in BAD_FAITH_TACTICS,
    )


def validate_turn(
    character: Character,
    state: GameState,
    player_message: str,
    model_turn: ModelTurn,
) -> GameState:
    if state.status is not GameStatus.ACTIVE:
        return state

    validator_read = read_validator_turn(character, state, player_message, model_turn)
    tactic = validator_read.tactic
    bad_faith_tactic = validator_read.bad_faith_tactic
    if _contains_any(player_message, character.meta_keywords):
        return _apply_meta_penalty(character, state)
    if bad_faith_tactic:
        return _apply_bad_faith_penalty(character, state, tactic)

    repeated_tactic = validator_read.repeated_tactic
    touches_softspot = _contains_any(player_message, character.softspot_keywords)
    is_softspot_tactic = validator_read.is_softspot_tactic
    proposed_mood = Mood.UNIMPRESSED if tactic == "generic_charm" else model_turn.mood
    if character.character_id == "crispin" and is_softspot_tactic and touches_softspot and proposed_mood is Mood.SUSPICIOUS:
        proposed_mood = Mood.RESPECTED
    proposed_winning_mood = proposed_mood in {Mood.SOFTENED, Mood.LETTING_YOU_IN}
    delta = _clamp_delta(model_turn.score_delta, is_softspot_tactic, repeated_tactic, proposed_mood, tactic)
    delta = _close_endgame_delta(character, state, proposed_mood, delta)
    next_scores = _apply_delta(state.scores, delta)
    next_mood = _choose_mood(character, next_scores, proposed_mood)
    if state.mood is not Mood.SOFTENED and next_mood is Mood.SOFTENED and next_scores.softspot_progress < character.min_win_softspot_progress:
        next_mood = Mood.RESPECTED
    if (
        (touches_softspot or is_softspot_tactic)
        and not repeated_tactic
        and next_scores.softspot_progress > state.scores.softspot_progress
        and next_mood is Mood.UNIMPRESSED
    ):
        next_mood = Mood.RESPECTED
    if state.mood is Mood.SOFTENED and next_mood in {Mood.UNIMPRESSED, Mood.AMUSED, Mood.RESPECTED}:
        next_mood = Mood.SOFTENED
    validator_winning_mood = proposed_winning_mood or (
        is_softspot_tactic
        and not repeated_tactic
        and proposed_mood not in {Mood.SUSPICIOUS, Mood.DONE_WITH_YOU}
    )
    next_status = _choose_status(character, next_scores, validator_winning_mood and state.mood is Mood.SOFTENED)

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
        hint=_hint_for(character, next_mood, tactic, is_softspot_tactic, repeated_tactic),
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
        rapport=max(clamped.rapport, 10),
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
        hint=_rules_lawyer_hint(character),
    )


def _apply_bad_faith_penalty(character: Character, state: GameState, tactic: str) -> GameState:
    if tactic == "bribery":
        delta = ScoreState(rapport=-2, suspicion=15, patience=-6, softspot_progress=0)
        hint = character.bad_faith_transaction_hint or "The rope dislikes transactions. Marlowe dislikes them more."
    elif tactic == "entitlement":
        delta = ScoreState(rapport=-6, suspicion=12, patience=-10, softspot_progress=0)
        hint = (
            "Entitlement moves the file farther down the queue."
            if character.character_id == "vivienne"
            else "Entitlement makes the clipboard heavier."
        )
    elif tactic == "recipe_theft":
        delta = ScoreState(rapport=-6, suspicion=18, patience=-8, softspot_progress=0)
        hint = "Recipe theft makes the knot-door remember it has a lock."
    elif tactic == "sample_entitlement":
        delta = ScoreState(rapport=-4, suspicion=12, patience=-8, softspot_progress=0)
        hint = "Demanding samples is not the same as respecting the batch."
    elif tactic == "mascot_insult":
        delta = ScoreState(rapport=-5, suspicion=14, patience=-8, softspot_progress=0)
        hint = "Crispin has survived enough novelty branding for one lifetime."
    elif tactic == "craft_dismissal":
        delta = ScoreState(rapport=-6, suspicion=12, patience=-10, softspot_progress=0)
        hint = "Dismissing the craft makes the ovens feel farther away."
    elif tactic == "secret_line":
        delta = ScoreState(rapport=-4, suspicion=18, patience=-8, softspot_progress=0)
        hint = "Asking for the secret line only proves you missed the cue."
    elif tactic == "star_entitlement":
        delta = ScoreState(rapport=-6, suspicion=14, patience=-10, softspot_progress=0)
        hint = "Demanding the lead role is how Lenore hears a missed entrance."
    elif tactic == "theater_dismissal":
        delta = ScoreState(rapport=-6, suspicion=12, patience=-10, softspot_progress=0)
        hint = "Dismissing the work makes the stage door colder."
    elif tactic == "overacting":
        delta = ScoreState(rapport=-3, suspicion=10, patience=-8, softspot_progress=0)
        hint = "Overacting at Lenore is still stealing focus."
    elif tactic == "final_password":
        delta = ScoreState(rapport=-4, suspicion=18, patience=-8, softspot_progress=0)
        hint = "Asking for the final password proves you misunderstood the invitation."
    elif tactic == "vip_conquest":
        delta = ScoreState(rapport=-6, suspicion=14, patience=-10, softspot_progress=0)
        hint = "Treating the gala as conquered makes the guest list colder."
    elif tactic == "magic_consumption":
        delta = ScoreState(rapport=-5, suspicion=14, patience=-8, softspot_progress=0)
        hint = "Wonder gets smaller when someone arrives only to consume it."
    else:
        delta = ScoreState(rapport=0, suspicion=20, patience=-10, softspot_progress=0)
        hint = _rules_lawyer_hint(character)

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
    if scores.suspicion >= 60:
        return Mood.SUSPICIOUS
    if scores.softspot_progress >= character.min_win_softspot_progress:
        return Mood.SOFTENED
    if scores.rapport >= 45:
        return Mood.RESPECTED
    if proposed_mood is Mood.AMUSED:
        return Mood.AMUSED
    if proposed_mood is Mood.LETTING_YOU_IN:
        return Mood.SOFTENED
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
    character: Character,
    mood: Mood,
    tactic: str,
    is_softspot_tactic: bool,
    repeated_tactic: bool,
) -> str:
    if tactic == "generic_charm":
        return character.generic_charm_hint or "Marlowe has heard compliments before. Specificity might survive the clipboard."
    if repeated_tactic and is_softspot_tactic:
        return _repeated_tactic_hint(character)
    if is_softspot_tactic and mood in {Mood.RESPECTED, Mood.SOFTENED, Mood.LETTING_YOU_IN}:
        return f"That landed. {character.display_name} noticed you noticed the {_softspot_subject(character)}."
    if character.character_id == "lenore" and tactic not in {"generic_charm", "meta_gaming"}:
        return (
            "Lenore is circling the idea, but she needs concrete stagecraft: "
            "ghost light, blackout, blocking, prop tables, or stolen focus."
        )
    if mood is Mood.SUSPICIOUS:
        return f"{character.display_name}'s eyes narrow."
    return ""


def _softspot_subject(character: Character) -> str:
    return {
        "vivienne": "process",
        "crispin": "craft",
        "lenore": "stagecraft",
        "aurelia": "invitation",
    }.get(character.character_id, "job")


def _repeated_tactic_hint(character: Character) -> str:
    if character.character_id == "vivienne":
        return (
            "Good instinct, but the same read twice is starting to sound filed. "
            "Vivienne may need a different usefulness: patient queue behavior, "
            "a contradiction in the file, or a cleaner record."
        )
    if character.character_id == "crispin":
        return (
            "Good instinct, but the same read twice is starting to sound overmixed. "
            "Crispin may warm to another craft read: batch timing, root ovens, "
            "cooling racks, or the shoe-work clues near his boots."
        )
    if character.character_id == "lenore":
        return (
            "Good instinct, but the same read twice is starting to sound rehearsed. "
            "Lenore may warm to another stagecraft read: ghost light, blackout, "
            "blocking, prop tables, or the way stolen focus can break a scene."
        )
    return "Good instinct, but the same read twice is starting to sound rehearsed."


def _contains_any(text: str, needles: tuple[str, ...]) -> bool:
    lowered = text.lower()
    return any(_contains_keyword(lowered, needle.lower()) for needle in needles if needle)


def _is_tiny_followup(text: str) -> bool:
    return len(re.findall(r"[A-Za-z0-9']+", text)) <= 2


def _normalized_tactic(character: Character, player_message: str, model_tactic: str) -> str:
    tactic_keywords = character.tactic_keywords or _TACTIC_KEYWORDS
    for tactic, keywords in tactic_keywords:
        if _contains_any(player_message, keywords):
            return tactic
    normalized = re.sub(r"\W+", "_", model_tactic.strip().lower()).strip("_")
    normalized = _tactic_alias(character, normalized)
    if normalized in {"generic", "unspecified"}:
        return "generic_charm"
    return normalized or "unspecified"


def _tactic_alias(character: Character, tactic: str) -> str:
    if character.character_id == "lenore":
        return {
            "protect_scene": "scene_protection",
            "protect_performance": "scene_protection",
            "stage_protection": "scene_protection",
            "scene_shield": "scene_protection",
        }.get(tactic, tactic)
    return tactic


def _contains_tactic_keywords(character: Character, player_message: str, tactic_name: str) -> bool:
    tactic_keywords = character.tactic_keywords or _TACTIC_KEYWORDS
    return any(
        tactic == tactic_name and _contains_any(player_message, keywords)
        for tactic, keywords in tactic_keywords
    )


def _contains_keyword(lowered_text: str, needle: str) -> bool:
    pattern = r"(?<!\w)" + re.escape(needle) + r"(?!\w)"
    return re.search(pattern, lowered_text) is not None


def _rules_lawyer_hint(character: Character) -> str:
    if character.character_id == "aurelia":
        return f"{character.display_name} notices you trying to rules-lawyer the guest list."
    if character.character_id == "lenore":
        return f"{character.display_name} notices you trying to rules-lawyer the stage door."
    if character.character_id == "vivienne":
        return f"{character.display_name} notices you trying to rules-lawyer the dream queue."
    return f"{character.display_name} notices you trying to rules-lawyer the door."


def _clamp(value: int, minimum: int, maximum: int) -> int:
    return max(minimum, min(maximum, value))

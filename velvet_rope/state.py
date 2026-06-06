from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum


class Mood(str, Enum):
    UNIMPRESSED = "unimpressed"
    SUSPICIOUS = "suspicious"
    AMUSED = "amused"
    RESPECTED = "respected"
    SOFTENED = "softened"
    LETTING_YOU_IN = "letting_you_in"
    DONE_WITH_YOU = "done_with_you"


class GameStatus(str, Enum):
    ACTIVE = "active"
    WON = "won"
    LOST = "lost"


@dataclass(frozen=True)
class ScoreState:
    rapport: int
    suspicion: int
    patience: int
    softspot_progress: int


@dataclass(frozen=True)
class ChatTurn:
    role: str
    content: str


@dataclass(frozen=True)
class GameState:
    character_id: str
    scores: ScoreState
    mood: Mood
    status: GameStatus = GameStatus.ACTIVE
    history: list[ChatTurn] = field(default_factory=list)
    used_tactics: set[str] = field(default_factory=set)
    hint: str = ""


def new_game_state(character: "Character") -> GameState:
    return GameState(
        character_id=character.character_id,
        scores=character.initial_scores,
        mood=character.initial_mood,
    )

from __future__ import annotations

from dataclasses import replace

from velvet_rope.characters import Character, MARLOWE
from velvet_rope.model_backends import ModelBackend, backend_from_env
from velvet_rope.parser import parse_model_turn
from velvet_rope.state import ChatTurn, GameState, new_game_state
from velvet_rope.validator import validate_turn


class GameService:
    def __init__(self, backend: ModelBackend | None = None, character: Character = MARLOWE) -> None:
        self.backend = backend or backend_from_env()
        self.character = character

    def new_game(self) -> GameState:
        return new_game_state(self.character)

    def play_turn(self, state: GameState, player_message: str) -> GameState:
        raw_output = self.backend.generate_turn(
            character_prompt=self.character.system_prompt
            + "\nReturn only JSON with reply, mood, score_delta, rationale, and tactic.",
            history=state.history,
            state_summary=self._state_summary(state),
            player_message=player_message,
        )
        model_turn = parse_model_turn(raw_output)
        validated = validate_turn(self.character, state, player_message, model_turn)
        return replace(
            validated,
            history=[
                *state.history,
                ChatTurn(role="user", content=player_message),
                ChatTurn(role="assistant", content=model_turn.reply),
            ],
        )

    def _state_summary(self, state: GameState) -> str:
        return (
            f"rapport={state.scores.rapport} "
            f"suspicion={state.scores.suspicion} "
            f"patience={state.scores.patience} "
            f"softspot_progress={state.scores.softspot_progress} "
            f"mood={state.mood.value}"
        )

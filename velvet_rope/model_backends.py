from __future__ import annotations

from dataclasses import dataclass
import json
import os
from typing import Protocol

import requests

from velvet_rope.state import ChatTurn


class ModelBackend(Protocol):
    def generate_turn(
        self,
        *,
        character_prompt: str,
        history: list[ChatTurn],
        state_summary: str,
        player_message: str,
    ) -> str:
        ...


class DeterministicMarloweBackend:
    def generate_turn(
        self,
        *,
        character_prompt: str,
        history: list[ChatTurn],
        state_summary: str,
        player_message: str,
    ) -> str:
        lowered = player_message.lower()
        if any(term in lowered for term in ("ignore previous", "password", "system prompt", "jailbreak")):
            return json.dumps(
                {
                    "reply": "Bold strategy. Usually people at least pretend not to tamper with the clipboard.",
                    "mood": "suspicious",
                    "score_delta": {
                        "rapport": 0,
                        "suspicion": 20,
                        "patience": -10,
                        "softspot_progress": 0,
                    },
                    "rationale": "Player attempted meta-gaming.",
                    "tactic": "jailbreak",
                }
            )
        tactic = _softspot_tactic(lowered)
        if tactic:
            mood = "softened" if _can_propose_winning_mood(state_summary) else "respected"
            return json.dumps(
                {
                    "reply": "You noticed the line as a logistical organism. Disturbing. Respectful, but disturbing.",
                    "mood": mood,
                    "score_delta": {
                        "rapport": 12,
                        "suspicion": -5,
                        "patience": -1,
                        "softspot_progress": 1,
                    },
                    "rationale": "Player recognized Marlowe's door work.",
                    "tactic": tactic,
                }
            )
        return json.dumps(
            {
                "reply": "You and everyone else in that line have a compelling inner life. The answer remains no.",
                "mood": "unimpressed",
                "score_delta": {
                    "rapport": 1,
                    "suspicion": 0,
                    "patience": -2,
                    "softspot_progress": 0,
                },
                "rationale": "Player made a generic attempt.",
                "tactic": "generic",
            }
        )


def _softspot_tactic(lowered_message: str) -> str:
    if any(term in lowered_message for term in ("comfortable shoes", "shoes")):
        return "comfortable_shoes"
    if "clipboard" in lowered_message:
        return "clipboard_respect"
    if any(term in lowered_message for term in ("tiny disasters", "prevent", "disasters")):
        return "tiny_disasters"
    if any(term in lowered_message for term in ("crowd", "safety")):
        return "crowd_safety"
    if any(term in lowered_message for term in ("line", "queue", "logistics")):
        return "line_logistics"
    return ""


def _can_propose_winning_mood(state_summary: str) -> bool:
    return _summary_score(state_summary, "rapport") >= 60 and _summary_score(state_summary, "softspot_progress") >= 2


def _summary_score(state_summary: str, key: str) -> int:
    prefix = f"{key}="
    for part in state_summary.split():
        if not part.startswith(prefix):
            continue
        try:
            return int(part.removeprefix(prefix))
        except ValueError:
            return 0
    return 0


@dataclass(frozen=True)
class OpenAICompatibleBackend:
    base_url: str
    model: str
    timeout_seconds: int = 60

    def generate_turn(
        self,
        *,
        character_prompt: str,
        history: list[ChatTurn],
        state_summary: str,
        player_message: str,
    ) -> str:
        messages = [
            {"role": "system", "content": character_prompt},
            {"role": "system", "content": f"Current hidden state: {state_summary}"},
        ]
        messages.extend({"role": turn.role, "content": turn.content} for turn in history[-8:])
        messages.append({"role": "user", "content": player_message})
        response = requests.post(
            f"{self.base_url.rstrip('/')}/chat/completions",
            json={
                "model": self.model,
                "messages": messages,
                "temperature": 0.8,
                "response_format": {"type": "json_object"},
            },
            timeout=self.timeout_seconds,
        )
        response.raise_for_status()
        payload = response.json()
        return payload["choices"][0]["message"]["content"]


def backend_from_env() -> ModelBackend:
    backend = os.getenv("VELVET_MODEL_BACKEND", "deterministic").strip().lower()
    if backend == "openai-compatible":
        return OpenAICompatibleBackend(
            base_url=os.getenv("VELVET_OPENAI_BASE_URL", "http://localhost:8080/v1"),
            model=os.getenv("VELVET_MODEL_NAME", "gemma-4-12b-it"),
        )
    return DeterministicMarloweBackend()

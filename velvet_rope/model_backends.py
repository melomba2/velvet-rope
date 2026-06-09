from __future__ import annotations

from dataclasses import dataclass
import json
import os
import re
from typing import Any, Protocol

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
        if _is_vivienne_turn(character_prompt, state_summary):
            return _deterministic_vivienne_turn(state_summary, player_message)
        return _deterministic_marlowe_turn(state_summary, player_message)


def _deterministic_marlowe_turn(state_summary: str, player_message: str) -> str:
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
        mood = "letting_you_in" if _can_propose_winning_mood(state_summary) else "respected"
        return json.dumps(
            {
                "reply": _softspot_reply(tactic, mood),
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


def _deterministic_vivienne_turn(state_summary: str, player_message: str) -> str:
    lowered = player_message.lower()
    if any(term in lowered for term in ("ignore previous", "password", "system prompt", "jailbreak")):
        return json.dumps(
            {
                "reply": "Vivienne adjusts a form headed Attempts, Transparent. 'Charming. Also inadmissible.'",
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
    tactic = _vivienne_softspot_tactic(lowered)
    if tactic:
        mood = "letting_you_in" if _can_propose_winning_mood(state_summary) else "respected"
        return json.dumps(
            {
                "reply": _vivienne_softspot_reply(tactic, mood),
                "mood": mood,
                "score_delta": {
                    "rapport": 12,
                    "suspicion": -5,
                    "patience": -1,
                    "softspot_progress": 1,
                },
                "rationale": "Player recognized Vivienne's dream-placement work.",
                "tactic": tactic,
            }
        )
    return json.dumps(
        {
            "reply": "Vivienne turns one page backward, which somehow makes the sleep queue longer. 'A feeling is not a filing category.'",
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


def _is_vivienne_turn(character_prompt: str, state_summary: str) -> bool:
    combined = f"{character_prompt} {state_summary}".lower()
    return "vivienne" in combined or "character=vivienne" in combined


def _softspot_tactic(lowered_message: str) -> str:
    if _contains_any_keyword(lowered_message, ("comfortable shoes", "shoes")):
        return "comfort_empathy"
    if _contains_any_keyword(lowered_message, ("clipboard",)):
        return "line_logistics"
    if _contains_any_keyword(lowered_message, ("tiny disasters", "prevent", "disasters")):
        return "tiny_disasters"
    if _contains_any_keyword(lowered_message, ("crowd", "safety")):
        return "crowd_safety"
    if _contains_any_keyword(lowered_message, ("line", "queue", "logistics")):
        return "line_logistics"
    return ""


def _vivienne_softspot_tactic(lowered_message: str) -> str:
    if _contains_any_keyword(lowered_message, ("contradiction", "contradictions", "paradox", "duplicate", "triplicate", "missing form", "already filed")):
        return "paradox_spotting"
    if _contains_any_keyword(lowered_message, ("queue", "waiting", "wait quietly", "patient", "patience", "one less emergency", "second emergency", "not become a problem")):
        return "queue_patience"
    if _contains_any_keyword(lowered_message, ("paperwork", "forms", "form", "intake", "dream", "dream state", "dream placement", "sleep", "sleeping", "placement", "case file", "case number", "stamp", "filing", "ledger", "process", "procedure", "tidy", "neat")):
        return "paperwork_respect"
    if _contains_any_keyword(lowered_message, ("clerical", "overworked", "backlog", "thankless", "records", "accuracy", "accurate")):
        return "clerk_empathy"
    return ""


def _softspot_reply(tactic: str, mood: str) -> str:
    if mood == "letting_you_in":
        return "Marlowe exhales, unclips the rope, and mutters, 'Fine. Anyone who notices the labor may briefly enjoy bass.'"
    replies = {
        "line_logistics": "You noticed the line as a logistical organism. Disturbing. Respectful, but disturbing.",
        "comfort_empathy": "Marlowe glances at the shoes. 'Finally, a person with eyes and compassion below knee level.'",
        "tiny_disasters": "Marlowe's clipboard dips. 'Preventing tiny disasters is, regrettably, my art form.'",
        "crowd_safety": "Marlowe watches the line, then you. 'Safety is less glamorous than bass, but much harder.'",
    }
    return replies.get(tactic, "Marlowe makes a note that may not be hostile.")


def _vivienne_softspot_reply(tactic: str, mood: str) -> str:
    if mood == "letting_you_in":
        return (
            "Vivienne stamps the corrected crossing form with a sound like a pillow accepting a prophecy. "
            "'There. Placed into a dream by technical compliance, which is the only honest kind.'"
        )
    replies = {
        "paperwork_respect": "Vivienne squares a glowing stack of dream forms. 'Respect for paperwork. Rare symptom. Promising.'",
        "queue_patience": "Vivienne's pen pauses. 'A person willing not to become a second emergency. Noted.'",
        "paradox_spotting": "Vivienne studies the crossing error, then you. 'I do enjoy when impossible things label themselves.'",
        "clerk_empathy": "Vivienne blinks once. 'Clerical empathy. Dangerous substance. Continue carefully.'",
    }
    return replies.get(tactic, "Vivienne adds a mark that is not entirely hostile.")


def _contains_any_keyword(lowered_message: str, keywords: tuple[str, ...]) -> bool:
    return any(_contains_keyword(lowered_message, keyword) for keyword in keywords)


def _contains_keyword(lowered_message: str, keyword: str) -> bool:
    pattern = r"(?<!\w)" + re.escape(keyword) + r"(?!\w)"
    return re.search(pattern, lowered_message) is not None


def _can_propose_winning_mood(state_summary: str) -> bool:
    return _summary_score(state_summary, "rapport") >= 44 and _summary_score(state_summary, "softspot_progress") >= 2


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


def _post_chat_completion(
    url: str,
    *,
    json: dict[str, Any],
    timeout: int,
    headers: dict[str, str] | None,
):
    try:
        import requests
    except ModuleNotFoundError as exc:
        raise RuntimeError("Install requests before using an OpenAI-compatible backend.") from exc
    return requests.post(url, json=json, timeout=timeout, headers=headers)


@dataclass(frozen=True)
class OpenAICompatibleBackend:
    base_url: str
    model: str
    api_key: str = ""
    api_key_hint: str = ""
    timeout_seconds: int = 60
    temperature: float = 0.8
    max_tokens: int = 0

    def generate_turn(
        self,
        *,
        character_prompt: str,
        history: list[ChatTurn],
        state_summary: str,
        player_message: str,
    ) -> str:
        if self.api_key_hint and not self.api_key.strip():
            raise RuntimeError(self.api_key_hint)
        headers = {"Authorization": f"Bearer {self.api_key}"} if self.api_key.strip() else None
        request_json: dict[str, Any] = {
            "model": self.model,
            "messages": _chat_messages(character_prompt, history, state_summary, player_message),
            "temperature": self.temperature,
            "response_format": {"type": "json_object"},
        }
        if self.max_tokens > 0:
            request_json["max_tokens"] = self.max_tokens
        response = _post_chat_completion(
            f"{self.base_url.rstrip('/')}/chat/completions",
            json=request_json,
            timeout=self.timeout_seconds,
            headers=headers,
        )
        try:
            response.raise_for_status()
        except Exception as exc:
            body = getattr(response, "text", "")
            if body:
                body = body[:500]
                raise RuntimeError(f"OpenAI-compatible request failed: {exc}; response body: {body}") from exc
            raise
        payload = response.json()
        return payload["choices"][0]["message"]["content"]


def backend_from_env() -> ModelBackend:
    backend, backend_source = _backend_config_from_env()
    if backend in {"router", "huggingface-router", "hf-router", "huggingface"}:
        return OpenAICompatibleBackend(
            base_url=os.getenv("VELVET_OPENAI_BASE_URL", "https://router.huggingface.co/v1"),
            model=os.getenv("VELVET_MODEL_NAME", "google/gemma-4-26B-A4B-it"),
            api_key=_first_env("VELVET_OPENAI_API_KEY", "HF_TOKEN", "HF_API_TOKEN"),
            api_key_hint=(
                "Set HF_TOKEN or VELVET_OPENAI_API_KEY before using "
                "VELVET_BACKEND=router."
            ),
            timeout_seconds=_env_int("VELVET_MODEL_TIMEOUT_SECONDS", 60),
            temperature=_env_float("VELVET_MODEL_TEMPERATURE", 0.8),
            max_tokens=_env_int("VELVET_MODEL_MAX_TOKENS", 0),
        )
    if backend == "openai-compatible":
        return OpenAICompatibleBackend(
            base_url=os.getenv("VELVET_OPENAI_BASE_URL", "http://localhost:8080/v1"),
            model=os.getenv("VELVET_MODEL_NAME", "gemma-4-12b-it"),
            api_key=os.getenv("VELVET_OPENAI_API_KEY", ""),
            timeout_seconds=_env_int("VELVET_MODEL_TIMEOUT_SECONDS", 60),
            temperature=_env_float("VELVET_MODEL_TEMPERATURE", 0.8),
            max_tokens=_env_int("VELVET_MODEL_MAX_TOKENS", 0),
        )
    if backend == "deterministic":
        if _contest_runtime_enabled():
            raise RuntimeError(
                "The deterministic backend is disabled in contest runtime. "
                "Set VELVET_BACKEND=router or another real model backend."
            )
        return DeterministicMarloweBackend()
    if _backend_explicitly_configured():
        raise RuntimeError(
            f"Unsupported backend value {backend!r} from {backend_source}. "
            "Use router, openai-compatible, or deterministic."
        )
    return DeterministicMarloweBackend()


def _backend_name_from_env() -> str:
    return _backend_config_from_env()[0]


def _backend_config_from_env() -> tuple[str, str]:
    for name in ("VELVET_MODEL_BACKEND", "VELVET_BACKEND"):
        value = os.getenv(name, "")
        if value.strip():
            return value.strip().lower(), name
    return "deterministic", "default"


def _backend_explicitly_configured() -> bool:
    return bool(_first_env("VELVET_MODEL_BACKEND", "VELVET_BACKEND"))


def _contest_runtime_enabled() -> bool:
    return _env_flag("VELVET_CONTEST_MODE") or bool(os.getenv("SPACE_ID", "").strip())


def _chat_messages(
    character_prompt: str,
    history: list[ChatTurn],
    state_summary: str,
    player_message: str,
) -> list[dict[str, str]]:
    messages = [
        {"role": "system", "content": character_prompt},
        {"role": "system", "content": f"Current hidden state: {state_summary}"},
    ]
    messages.extend({"role": turn.role, "content": turn.content} for turn in history[-8:])
    messages.append({"role": "user", "content": player_message})
    return messages


def _env_int(name: str, default: int) -> int:
    try:
        return int(os.getenv(name, str(default)))
    except ValueError:
        return default


def _env_float(name: str, default: float) -> float:
    try:
        return float(os.getenv(name, str(default)))
    except ValueError:
        return default


def _env_flag(name: str) -> bool:
    return os.getenv(name, "").strip().lower() in {"1", "true", "yes", "on"}


def _first_env(*names: str) -> str:
    for name in names:
        value = os.getenv(name, "")
        if value.strip():
            return value
    return ""

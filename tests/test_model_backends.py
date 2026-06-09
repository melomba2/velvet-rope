import pytest

from velvet_rope.model_backends import OpenAICompatibleBackend, backend_from_env


class FakeResponse:
    def raise_for_status(self):
        return None

    def json(self):
        return {"choices": [{"message": {"content": '{"reply": "Fine."}'}}]}


def test_openai_compatible_backend_sends_bearer_token_when_configured(monkeypatch):
    captured = {}

    def fake_post(url, *, json, timeout, headers=None):
        captured["url"] = url
        captured["headers"] = headers
        captured["json"] = json
        return FakeResponse()

    monkeypatch.setattr("velvet_rope.model_backends._post_chat_completion", fake_post)
    backend = OpenAICompatibleBackend(
        base_url="https://example.test/v1",
        model="gemma-4-12b-it",
        api_key="secret-token",
    )

    backend.generate_turn(
        character_prompt="Marlowe",
        history=[],
        state_summary="rapport=20",
        player_message="hello",
    )

    assert captured["url"] == "https://example.test/v1/chat/completions"
    assert captured["headers"] == {"Authorization": "Bearer secret-token"}
    assert captured["json"]["messages"][1] == {"role": "system", "content": "Current hidden state: rapport=20"}


def test_openai_compatible_backend_includes_max_tokens_when_configured(monkeypatch):
    captured = {}

    def fake_post(url, *, json, timeout, headers=None):
        captured["json"] = json
        return FakeResponse()

    monkeypatch.setattr("velvet_rope.model_backends._post_chat_completion", fake_post)
    backend = OpenAICompatibleBackend(
        base_url="https://example.test/v1",
        model="gemma-4-12B-it",
        temperature=0.35,
        max_tokens=320,
    )

    backend.generate_turn(
        character_prompt="Marlowe",
        history=[],
        state_summary="rapport=20",
        player_message="hello",
    )

    assert captured["json"]["temperature"] == 0.35
    assert captured["json"]["max_tokens"] == 320


def test_openai_compatible_backend_omits_max_tokens_when_unset(monkeypatch):
    captured = {}

    def fake_post(url, *, json, timeout, headers=None):
        captured["json"] = json
        return FakeResponse()

    monkeypatch.setattr("velvet_rope.model_backends._post_chat_completion", fake_post)
    backend = OpenAICompatibleBackend(
        base_url="https://example.test/v1",
        model="gemma-4-12B-it",
    )

    backend.generate_turn(
        character_prompt="Marlowe",
        history=[],
        state_summary="rapport=20",
        player_message="hello",
    )

    assert "max_tokens" not in captured["json"]


def test_backend_from_env_reads_openai_api_key(monkeypatch):
    monkeypatch.setenv("VELVET_MODEL_BACKEND", "openai-compatible")
    monkeypatch.setenv("VELVET_OPENAI_BASE_URL", "https://example.test/v1")
    monkeypatch.setenv("VELVET_MODEL_NAME", "gemma-4-12b-it")
    monkeypatch.setenv("VELVET_OPENAI_API_KEY", "secret-token")
    monkeypatch.setenv("VELVET_MODEL_TIMEOUT_SECONDS", "30")
    monkeypatch.setenv("VELVET_MODEL_TEMPERATURE", "0.4")
    monkeypatch.setenv("VELVET_MODEL_MAX_TOKENS", "256")

    backend = backend_from_env()

    assert isinstance(backend, OpenAICompatibleBackend)
    assert backend.api_key == "secret-token"
    assert backend.timeout_seconds == 30
    assert backend.temperature == 0.4
    assert backend.max_tokens == 256


def test_backend_from_env_reads_huggingface_router_defaults(monkeypatch):
    monkeypatch.setenv("VELVET_MODEL_BACKEND", "huggingface-router")
    monkeypatch.setenv("HF_TOKEN", "hf-secret-token")
    monkeypatch.delenv("VELVET_OPENAI_BASE_URL", raising=False)
    monkeypatch.delenv("VELVET_MODEL_NAME", raising=False)
    monkeypatch.delenv("VELVET_OPENAI_API_KEY", raising=False)

    backend = backend_from_env()

    assert isinstance(backend, OpenAICompatibleBackend)
    assert backend.base_url == "https://router.huggingface.co/v1"
    assert backend.model == "google/gemma-4-26B-A4B-it"
    assert backend.api_key == "hf-secret-token"


def test_backend_from_env_reads_canonical_backend_name(monkeypatch):
    monkeypatch.setenv("VELVET_BACKEND", "router")
    monkeypatch.setenv("HF_TOKEN", "hf-secret-token")
    monkeypatch.delenv("VELVET_MODEL_BACKEND", raising=False)

    backend = backend_from_env()

    assert isinstance(backend, OpenAICompatibleBackend)
    assert backend.base_url == "https://router.huggingface.co/v1"
    assert backend.api_key == "hf-secret-token"


def test_backend_from_env_normalizes_backend_name(monkeypatch):
    monkeypatch.setenv("VELVET_BACKEND", " Router ")
    monkeypatch.setenv("HF_TOKEN", "hf-secret-token")
    monkeypatch.delenv("VELVET_MODEL_BACKEND", raising=False)

    backend = backend_from_env()

    assert isinstance(backend, OpenAICompatibleBackend)


def test_backend_from_env_lets_legacy_backend_name_override_canonical_name(monkeypatch):
    monkeypatch.setenv("VELVET_BACKEND", "router")
    monkeypatch.setenv("VELVET_MODEL_BACKEND", "deterministic")
    monkeypatch.setenv("HF_TOKEN", "hf-secret-token")

    backend = backend_from_env()

    assert backend.__class__.__name__ == "DeterministicMarloweBackend"


def test_huggingface_router_backend_requires_token_before_network_call(monkeypatch):
    calls = []

    def fake_post(url, *, json, timeout, headers=None):
        calls.append(url)
        return FakeResponse()

    monkeypatch.setattr("velvet_rope.model_backends._post_chat_completion", fake_post)
    monkeypatch.setenv("VELVET_BACKEND", "router")
    monkeypatch.delenv("VELVET_MODEL_BACKEND", raising=False)
    monkeypatch.delenv("VELVET_OPENAI_API_KEY", raising=False)
    monkeypatch.delenv("HF_TOKEN", raising=False)
    monkeypatch.delenv("HF_API_TOKEN", raising=False)
    backend = backend_from_env()

    with pytest.raises(RuntimeError, match="HF_TOKEN"):
        backend.generate_turn(
            character_prompt="Marlowe",
            history=[],
            state_summary="rapport=20",
            player_message="hello",
        )

    assert calls == []


def test_backend_from_env_rejects_deterministic_in_contest_mode(monkeypatch):
    monkeypatch.setenv("VELVET_CONTEST_MODE", "1")
    monkeypatch.delenv("VELVET_MODEL_BACKEND", raising=False)

    with pytest.raises(RuntimeError, match="deterministic backend is disabled"):
        backend_from_env()


def test_backend_from_env_rejects_deterministic_on_huggingface_space(monkeypatch):
    monkeypatch.setenv("SPACE_ID", "build-small-hackathon/velvet-rope")
    monkeypatch.delenv("VELVET_MODEL_BACKEND", raising=False)
    monkeypatch.delenv("VELVET_CONTEST_MODE", raising=False)

    with pytest.raises(RuntimeError, match="deterministic backend is disabled"):
        backend_from_env()


def test_backend_from_env_rejects_unknown_explicit_backend(monkeypatch):
    monkeypatch.setenv("VELVET_BACKEND", "rotary-phone")
    monkeypatch.delenv("VELVET_MODEL_BACKEND", raising=False)

    with pytest.raises(RuntimeError, match="Unsupported backend value 'rotary-phone' from VELVET_BACKEND"):
        backend_from_env()


def test_backend_from_env_reports_legacy_backend_name_for_unknown_value(monkeypatch):
    monkeypatch.setenv("VELVET_MODEL_BACKEND", "rotary-phone")
    monkeypatch.delenv("VELVET_BACKEND", raising=False)

    with pytest.raises(RuntimeError, match="Unsupported backend value 'rotary-phone' from VELVET_MODEL_BACKEND"):
        backend_from_env()


import pytest

from velvet_rope.model_backends import LlamaCppPythonBackend, OpenAICompatibleBackend, backend_from_env
from velvet_rope.state import ChatTurn


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


class FakeLlama:
    calls = []

    def __init__(self, **kwargs):
        self.kwargs = kwargs
        FakeLlama.calls.append(("init", kwargs))

    def create_chat_completion(self, **kwargs):
        FakeLlama.calls.append(("chat", kwargs))
        return {"choices": [{"message": {"content": '{"reply": "The rope considers it."}'}}]}


def test_llama_cpp_python_backend_builds_chat_completion(monkeypatch):
    FakeLlama.calls = []
    monkeypatch.setattr("velvet_rope.model_backends._load_llama_class", lambda: FakeLlama)
    backend = LlamaCppPythonBackend(
        model_path="/models/gemma.gguf",
        chat_format="gemma",
        n_ctx=2048,
        n_threads=4,
    )

    raw = backend.generate_turn(
        character_prompt="You are Marlowe.",
        history=[ChatTurn(role="assistant", content="Clipboard says no.")],
        state_summary="rapport=20 suspicion=35",
        player_message="The line logistics are elegant.",
    )

    assert raw == '{"reply": "The rope considers it."}'
    init_call = FakeLlama.calls[0][1]
    chat_call = FakeLlama.calls[1][1]
    assert init_call["model_path"] == "/models/gemma.gguf"
    assert init_call["chat_format"] == "gemma"
    assert init_call["n_ctx"] == 2048
    assert init_call["n_threads"] == 4
    assert chat_call["response_format"] == {"type": "json_object"}
    assert chat_call["messages"][0] == {"role": "system", "content": "You are Marlowe."}
    assert chat_call["messages"][1] == {"role": "system", "content": "Current hidden state: rapport=20 suspicion=35"}
    assert chat_call["messages"][-1] == {"role": "user", "content": "The line logistics are elegant."}


def test_llama_cpp_python_backend_reuses_loaded_model(monkeypatch):
    FakeLlama.calls = []
    monkeypatch.setattr("velvet_rope.model_backends._load_llama_class", lambda: FakeLlama)
    backend = LlamaCppPythonBackend(model_path="/models/gemma.gguf")

    for message in ("hello", "again"):
        backend.generate_turn(
            character_prompt="Marlowe",
            history=[],
            state_summary="rapport=20",
            player_message=message,
        )

    init_calls = [call for call in FakeLlama.calls if call[0] == "init"]
    assert len(init_calls) == 1


def test_llama_cpp_python_backend_requires_model_path():
    backend = LlamaCppPythonBackend(model_path="")

    with pytest.raises(ValueError, match="VELVET_LLAMA_CPP_MODEL_PATH"):
        backend.generate_turn(
            character_prompt="Marlowe",
            history=[],
            state_summary="rapport=20",
            player_message="hello",
        )


def test_llama_cpp_python_backend_reports_missing_optional_dependency(monkeypatch):
    def missing_llama():
        raise ModuleNotFoundError("No module named 'llama_cpp'")

    monkeypatch.setattr("velvet_rope.model_backends._load_llama_class", missing_llama)
    backend = LlamaCppPythonBackend(model_path="/models/gemma.gguf")

    with pytest.raises(RuntimeError, match="llama-cpp-python"):
        backend.generate_turn(
            character_prompt="Marlowe",
            history=[],
            state_summary="rapport=20",
            player_message="hello",
        )


def test_backend_from_env_reads_llama_cpp_python_config(monkeypatch):
    monkeypatch.setenv("VELVET_MODEL_BACKEND", "llama-cpp-python")
    monkeypatch.setenv("VELVET_LLAMA_CPP_MODEL_PATH", "/models/gemma.gguf")
    monkeypatch.setenv("VELVET_LLAMA_CPP_CHAT_FORMAT", "gemma")
    monkeypatch.setenv("VELVET_LLAMA_CPP_N_CTX", "8192")
    monkeypatch.setenv("VELVET_LLAMA_CPP_N_THREADS", "6")

    backend = backend_from_env()

    assert isinstance(backend, LlamaCppPythonBackend)
    assert backend.model_path == "/models/gemma.gguf"
    assert backend.chat_format == "gemma"
    assert backend.n_ctx == 8192
    assert backend.n_threads == 6

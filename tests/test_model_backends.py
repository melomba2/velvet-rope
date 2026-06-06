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
        return FakeResponse()

    monkeypatch.setattr("velvet_rope.model_backends.requests.post", fake_post)
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


def test_backend_from_env_reads_openai_api_key(monkeypatch):
    monkeypatch.setenv("VELVET_MODEL_BACKEND", "openai-compatible")
    monkeypatch.setenv("VELVET_OPENAI_BASE_URL", "https://example.test/v1")
    monkeypatch.setenv("VELVET_MODEL_NAME", "gemma-4-12b-it")
    monkeypatch.setenv("VELVET_OPENAI_API_KEY", "secret-token")

    backend = backend_from_env()

    assert isinstance(backend, OpenAICompatibleBackend)
    assert backend.api_key == "secret-token"

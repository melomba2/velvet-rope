# HF Router Gemma Backend Design

## Summary

Velvet Rope should start real-model deployment through Hugging Face infrastructure. The contest requires a Gradio app hosted as a Hugging Face Space, and the Thousand Token Wood track judges whether AI is load-bearing for the experience. Deterministic mode remains useful for local development and fallback behavior, but it should not be the intended final backend.

## Approved Direction

- Use Hugging Face Router / Inference Providers as the first real Gemma path.
- Keep the app a normal Gradio Space.
- Preserve `deterministic` as the default local/demo fallback until the Space is intentionally flipped.
- Add a clear backend alias for HF Router instead of requiring users to remember the generic OpenAI-compatible env combination.
- Keep `llama-cpp-python` available as a later local-first or bonus-badge experiment.

## Runtime Design

Add a `huggingface-router` backend option that constructs `OpenAICompatibleBackend` with:

- `base_url=https://router.huggingface.co/v1`
- `model=google/gemma-4-26B-A4B-it` unless `VELVET_MODEL_NAME` overrides it
- `api_key` from `VELVET_OPENAI_API_KEY`, then `HF_TOKEN`, then `HF_API_TOKEN`

The generic `openai-compatible` backend remains for local servers and custom providers. Both OpenAI-compatible paths should support optional sampling controls through environment variables:

- `VELVET_MODEL_TEMPERATURE`
- `VELVET_MODEL_MAX_TOKENS`
- `VELVET_MODEL_TIMEOUT_SECONDS`

## Testing

Tests should prove:

- HF Router aliases create `OpenAICompatibleBackend`.
- HF Router defaults to the Hugging Face Router base URL and working Gemma chat model.
- HF token fallback works without requiring a duplicate `VELVET_OPENAI_API_KEY`.
- OpenAI-compatible requests include optional `max_tokens` only when configured.

## Documentation

Update `README.md` so the recommended contest path is HF Router first, with deterministic explicitly labeled as a fallback and `llama-cpp-python` as a later experiment.

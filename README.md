---
title: Velvet Rope
emoji: 🚪
colorFrom: red
colorTo: yellow
sdk: gradio
sdk_version: 5.49.1
app_file: app.py
pinned: false
---

# Velvet Rope

Velvet Rope is a whimsical Gradio game where you talk your way past AI gatekeepers by reading their moods and discovering each character's soft spot.

The MVP features Marlowe, an exhausted nightclub bouncer guarding a literal velvet rope. The player wins by recognizing Marlowe's pride in door work, line logistics, and tiny disasters prevented before anyone notices.

## Runtime

The default backend is deterministic so local development remains demoable while model runtime work continues. The contest deployment should use a real small model backend so Marlowe's voice, mood shifts, and persuasion scoring are load-bearing AI behavior.

Backend selection in the Space uses `VELVET_MODEL_BACKEND`. Supported values are:

- `router`
- `openai-compatible`
- `llamacpp`
- `deterministic`

`VELVET_BACKEND` is also accepted as a shorter alias, but do not set both in the Space. If both env vars are set, `VELVET_MODEL_BACKEND` wins so the current Space config remains the source of truth.

### Hugging Face Router / Inference Providers

Recommended starting point for the Build Small Hackathon deployment. This keeps Velvet Rope as a normal Gradio Space while using Hugging Face infrastructure and credits for real Gemma inference. HF Router currently exposes Gemma 4 26B A4B as a chat model; it stays under the contest's 32B total-parameter cap and is the working Router default while Gemma 4 12B remains the local/llama.cpp target.

```bash
export VELVET_CONTEST_MODE=1
export VELVET_MODEL_BACKEND=router
export HF_TOKEN=...
export VELVET_MODEL_NAME=google/gemma-4-26B-A4B-it
export VELVET_MODEL_TEMPERATURE=0.8
export VELVET_MODEL_MAX_TOKENS=512
python app.py
```

You can also set `VELVET_OPENAI_API_KEY` instead of `HF_TOKEN`. If both are present, `VELVET_OPENAI_API_KEY` wins. The HF Router backend defaults to `https://router.huggingface.co/v1`, but `VELVET_OPENAI_BASE_URL` can override it for testing. Router mode requires one of those tokens before it makes a network call, so a missing Space secret becomes a clear model-unavailable turn instead of a silent fallback.

`VELVET_CONTEST_MODE=1` disables the deterministic backend and prevents silent deterministic fallback when model calls fail. In contest mode, a model outage is shown as an unavailable-model message instead of pretending the AI completed the turn.

### Deterministic fallback

No model server is required. Use this for local development, UI work, and fallback smoke tests, not as the intended final contest backend:

```bash
export VELVET_MODEL_BACKEND=deterministic
python app.py
```

### Playtest transcripts

Running `python app.py` captures one JSONL transcript file per play session in `.playtests/transcripts/`.
The folder is git-ignored. Set `VELVET_CAPTURE_TRANSCRIPTS=0` to disable capture, or set
`VELVET_TRANSCRIPT_DIR=/path/to/transcripts` to write somewhere else.

### External OpenAI-compatible endpoint

Use this for hosted llama.cpp, Modal, vLLM, Hugging Face Inference Endpoints, or any other OpenAI-compatible chat-completions server:

```bash
export VELVET_MODEL_BACKEND=openai-compatible
export VELVET_OPENAI_BASE_URL=https://your-endpoint.example/v1
export VELVET_MODEL_NAME=gemma-4-12b-it
export VELVET_OPENAI_API_KEY=...
export VELVET_MODEL_TEMPERATURE=0.8
export VELVET_MODEL_MAX_TOKENS=512
python app.py
```

For local development with a llama.cpp server running on the same machine, set `VELVET_OPENAI_BASE_URL=http://localhost:8080/v1`.
Inside a Hugging Face Space, `localhost` means the Space container, not your laptop.

### In-Space llama.cpp

Use this for direct `llama-cpp-python` inference inside the Gradio Space. This keeps the app as a normal Gradio Space, but requires installing `llama-cpp-python` and providing a GGUF model file path.

```bash
export VELVET_MODEL_BACKEND=llamacpp
export VELVET_LLAMA_CPP_MODEL_PATH=/path/to/model.gguf
export VELVET_LLAMA_CPP_CHAT_FORMAT=gemma
export VELVET_LLAMA_CPP_N_CTX=4096
export VELVET_LLAMA_CPP_N_THREADS=4
python app.py
```

`llama-cpp-python` is intentionally not installed by the default `requirements.txt` so the private demo Space remains quick and stable. Use `requirements-llamacpp.txt` as the deployment starting point when enabling the in-Space llama.cpp mode.

### Model accounting

The judging story should stay simple and conservative:

- Primary planned model: [`google/gemma-4-12B-it`](https://huggingface.co/google/gemma-4-12B-it), whose model card lists Gemma 4 12B Unified at 11.95B total parameters.
- Current reliable Router fallback: [`google/gemma-4-26B-A4B-it`](https://huggingface.co/google/gemma-4-26B-A4B-it), whose model card lists 25.2B total parameters and 3.8B active parameters.
- Character specialization should use small LoRA adapter deltas over one shared base model, not one merged full model per character.

For deployment strategy, keep these paths distinct:

- Gradio SDK + Router is the current judge-reliable path.
- Gradio SDK + ZeroGPU is the HF shared GPU path, but it needs a PyTorch/Transformers-style backend.
- Docker + Gradio + llama.cpp is the local-first GGUF path; it is not the ZeroGPU/user-quota path.

## Development

On machines without bare `python`, use `python3` for the Python commands below.

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements-dev.txt
python -m pytest -v
python app.py
```

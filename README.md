---
title: Velvet Rope
emoji: 🚪
colorFrom: red
colorTo: yellow
sdk: gradio
sdk_version: 5.49.1
python_version: "3.11"
app_file: app.py
pinned: false
license: mit
short_description: Read AI gatekeepers' moods and talk your way past.
tags:
  - build-small-hackathon
  - thousand-token-wood
  - well-tuned
  - sharing-is-caring
  - llama-champion
  - off-brand
  - custom-ui
  - gradio
  - modal
  - lora
  - gemma
  - game
  - conversational
models:
  - unsloth/gemma-4-12b-it-qat-GGUF
  - build-small-hackathon/velvet-rope-marlowe-lora
  - build-small-hackathon/velvet-rope-vivienne-lora
  - build-small-hackathon/velvet-rope-crispin-lora
  - build-small-hackathon/velvet-rope-lenore-lora
  - build-small-hackathon/velvet-rope-aurelia-lora
  - google/gemma-4-26B-A4B-it
---

## 🏆 Build Small Hackathon Submission
- **Track:** Thousand Token Wood
- **Demo video:** https://youtu.be/ilyFFChfPFE
- **Social post:** https://x.com/lombard258/status/2065953865581596846
- **Models (all ≤32B):** Gemma 4 12B (`unsloth/gemma-4-12b-it-qat-GGUF`, served via
  llama.cpp on Modal with one small LoRA adapter per character) + Gemma 4 26B-A4B
  (`google/gemma-4-26B-A4B-it`, 25.2B total / 3.8B active, Router fallback).
- **Public artifacts:** LoRA adapters for [Marlowe](https://huggingface.co/build-small-hackathon/velvet-rope-marlowe-lora),
  [Vivienne](https://huggingface.co/build-small-hackathon/velvet-rope-vivienne-lora),
  [Crispin](https://huggingface.co/build-small-hackathon/velvet-rope-crispin-lora),
  [Lenore](https://huggingface.co/build-small-hackathon/velvet-rope-lenore-lora), and
  [Aurelia](https://huggingface.co/build-small-hackathon/velvet-rope-aurelia-lora), plus
  [cleaned playtest transcripts](https://huggingface.co/datasets/build-small-hackathon/velvet-rope-playtest-transcripts).
- **Why it fits:** A delightful, AI-load-bearing game — each gatekeeper's voice, mood
  shifts, and persuasion scoring come from the small model; you win by reading their
  soft spot, not by prompt injection.

## Idea & Tech

Velvet Rope is a small, character-driven persuasion game where you talk your way
past a cast of moody AI gatekeepers by reading each character's voice, mood, and
soft spot. It is a playful homage to Gandalf-style "guess the wizard's password"
games, but flips the challenge from extracting a secret into understanding a
character. It is built as a custom Gradio app for Hugging Face Spaces, with real
model turns served by a Modal-hosted llama.cpp runtime using Gemma 4 12B plus one
LoRA adapter per character; a Gemma 4 26B-A4B Hugging Face Router backend is
available as a demo fallback, and all model paths stay under the 32B contest
limit.

# Velvet Rope

Velvet Rope is a whimsical Gradio game where you talk your way past AI gatekeepers by reading their moods and discovering each character's soft spot.

The MVP starts with Marlowe, an exhausted nightclub bouncer guarding a literal velvet rope. Level 2 adds Vivienne Quill, a dream placement clerk in a cosmic bureaucracy where a crossing error leaves the player waiting in line to be placed into a dream. Level 3 adds Crispin Crumbwell, a Hollow Tree Cookie Works gatekeeper who cares about craft, batch discipline, and his carefully hidden cobbler clues. Level 4 adds Lenore Cue, a spectral stage manager guarding a haunted theater stage door at The Last Curtain. Level 5 adds Aurelia Vane, Mistress of the Impossible Guest List, hosting The Grand Threshold as a triumphant magical finale about hospitality, invitation, and leaving the room more enchanted than you found it. The player wins by reading each gatekeeper's specific soft spot instead of relying on generic charm.

## Runtime

The default backend is deterministic so local development remains demoable while model runtime work continues. The contest deployment should use a real small model backend so Marlowe's voice, mood shifts, and persuasion scoring are load-bearing AI behavior.

Backend selection in the Space uses `VELVET_MODEL_BACKEND`. Supported values are:

- `router`
- `openai-compatible`
- `deterministic`

`VELVET_BACKEND` is also accepted as a shorter alias, but do not set both in the Space. If both env vars are set, `VELVET_MODEL_BACKEND` wins so the current Space config remains the source of truth.

### Modal 12B LoRA Runtime

The current 12B deployment path is a Modal-hosted OpenAI-compatible endpoint
with one trained LoRA adapter per character. The app sends a per-character model
name such as `velvet-marlowe` or `velvet-vivienne`; the Modal proxy applies the
matching adapter and falls back to the base model for unknown names.
The Hugging Face Space stays lightweight and calls Modal for inference, which
avoids trying to run a 12B GGUF on Space CPU.

```bash
export VELVET_CONTEST_MODE=1
export VELVET_MODEL_BACKEND=openai-compatible
export VELVET_OPENAI_BASE_URL=https://melomba2--velvet-llamacpp-lora-serve.modal.run/v1
export VELVET_MODEL_NAME='velvet-{character_id}'
export VELVET_OPENAI_API_KEY=...
export VELVET_MODEL_TEMPERATURE=0.8
export VELVET_MODEL_MAX_TOKENS=384
python app.py
```

Inside the Hugging Face Space, store `VELVET_OPENAI_API_KEY` as a secret and
the other values as Space variables. Store the literal value
`velvet-{character_id}` for `VELVET_MODEL_NAME`; the app substitutes each
playable character id when it creates that character's game service. The Modal
service is responsible for model loading, GPU selection, llama.cpp, and LoRA
adapter routing.

### Hugging Face Router / Inference Providers

Router is the fast fallback path for demos when Modal is unavailable. HF Router
currently exposes Gemma 4 26B A4B as a chat model; it stays under the contest's
32B total-parameter cap, but it is not the current 12B Modal experiment.

```bash
export VELVET_CONTEST_MODE=1
export VELVET_MODEL_BACKEND=router
export HF_TOKEN=...
export VELVET_MODEL_NAME=google/gemma-4-26B-A4B-it
export VELVET_MODEL_TEMPERATURE=0.8
export VELVET_MODEL_MAX_TOKENS=384
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

### Other OpenAI-compatible endpoint

Use this for vLLM, Hugging Face Inference Endpoints, or any other
OpenAI-compatible chat-completions server:

```bash
export VELVET_MODEL_BACKEND=openai-compatible
export VELVET_OPENAI_BASE_URL=https://your-endpoint.example/v1
export VELVET_MODEL_NAME=your-model-name
export VELVET_OPENAI_API_KEY=...
export VELVET_MODEL_TEMPERATURE=0.8
export VELVET_MODEL_MAX_TOKENS=384
python app.py
```

### Model accounting

The judging story should stay simple and conservative:

- Current Modal model: [`unsloth/gemma-4-12b-it-qat-GGUF`](https://huggingface.co/unsloth/gemma-4-12b-it-qat-GGUF), serving `gemma-4-12B-it-qat-UD-Q4_K_XL.gguf` with one small character LoRA adapter selected per turn.
- Current reliable Router fallback: [`google/gemma-4-26B-A4B-it`](https://huggingface.co/google/gemma-4-26B-A4B-it), whose model card lists 25.2B total parameters and 3.8B active parameters.
- Character specialization should use small LoRA adapter deltas over one shared base model, not one merged full model per character.

For deployment strategy, keep these paths distinct:

- Gradio SDK + Modal is the current 12B test path.
- Gradio SDK + Router is the fast 26B fallback path.
- The Hugging Face Space should not install or run llama.cpp locally.

## Development

On machines without bare `python`, use `python3` for the Python commands below.

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements-dev.txt
python -m pytest -v
python app.py
```

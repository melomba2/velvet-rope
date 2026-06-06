---
title: Velvet Rope
emoji: 🚪
colorFrom: red
colorTo: yellow
sdk: gradio
sdk_version: 5.0.0
app_file: app.py
pinned: false
---

# Velvet Rope

Velvet Rope is a whimsical Gradio game where you talk your way past AI gatekeepers by reading their moods and discovering each character's soft spot.

The MVP features Marlowe, an exhausted nightclub bouncer guarding a literal velvet rope. The player wins by recognizing Marlowe's pride in door work, line logistics, and tiny disasters prevented before anyone notices.

## Runtime

The default backend is deterministic so the Space remains demoable while model runtime work continues.

For a local OpenAI-compatible llama.cpp server:

```bash
export VELVET_MODEL_BACKEND=openai-compatible
export VELVET_OPENAI_BASE_URL=http://localhost:8080/v1
export VELVET_MODEL_NAME=gemma-4-12b-it
python app.py
```

## Development

On machines without bare `python`, use `python3` for the Python commands below.

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements-dev.txt
python -m pytest -v
python app.py
```

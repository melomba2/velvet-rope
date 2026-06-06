# Velvet Rope Agent Notes

## Project Shape

Velvet Rope is a Build Small Hackathon project: a whimsical Gradio game where the player talks past AI gatekeepers by reading their moods and discovering each character's soft spot.

Core constraints:

- Build as a Gradio app suitable for Hugging Face Spaces.
- Keep total model parameters at or below 32B.
- Favor local/offline inference paths, especially llama.cpp-compatible models, when practical.
- The AI should be load-bearing for the experience: character voice, mood shifts, and persuasion mechanics are the point.
- Preserve a custom, polished UI rather than relying on default Gradio styling.

## Product Priorities

- The gatekeeper must visibly emote; mood is the main feedback loop.
- Persuasion should be character-reading, not prompt-injection or password extraction.
- A small cast of distinct personalities is preferred over one generic guard.
- Comedy, charm, and fast interactions matter more than broad general intelligence.
- MVP target: 1-3 characters working end to end with conversation, mood, win detection, and custom UI.

## Engineering Guidelines

- Keep project-local planning files ignored; do not commit private brief/readme notes.
- Do not commit model weights, checkpoints, generated datasets, Gradio flagging logs, or experiment outputs.
- Prefer reproducible dependency files once a Python toolchain is introduced.
- Keep app code Space-friendly: clear entry point, minimal startup assumptions, and documented runtime requirements.
- Add tests or lightweight validation around game-state logic, mood parsing, and win detection as those pieces appear.

## Current State

The repo is currently initialized but has no application source yet. Existing tracked/important files are:

- `LICENSE`
- `.gitignore`
- `AGENTS.md`


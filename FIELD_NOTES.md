# Field Notes: Velvet Rope

Velvet Rope is a Build Small hackathon entry for the Thousand Token Wood track. It is a
small, character-driven persuasion game where the fun depends on the model doing the
character work: voice, mood shifts, clues, refusal, and the final decision to let the
player through.

## The Bet

The original product bet was simple: make the player read a character, not jailbreak a
password. Each gatekeeper has a specific soft spot and a visible emotional state. The
player wins by responding to that character with the right kind of respect, humor, craft,
or hospitality.

That makes the model load-bearing. A deterministic rules engine can track state, but the
experience only works if the gatekeeper sounds distinct and reacts believably to the
player's language.

## What Shipped

- Five playable gatekeepers: Marlowe, Vivienne, Crispin, Lenore, and Aurelia.
- A custom pixel-art Gradio interface with sprites, mood badges, stamped outcomes, and
  level-specific backgrounds.
- A real small-model runtime path: Gemma 4 12B via llama.cpp on Modal, with one LoRA
  adapter per character.
- A Hugging Face Router fallback using Gemma 4 26B-A4B for demos when the Modal runtime is
  unavailable.
- Public LoRA adapter repos and a public cleaned playtest transcript dataset.

## Small-Model Shape

The primary model is `unsloth/gemma-4-12b-it-qat-GGUF`, served with llama.cpp. Character
specialization lives in small LoRA adapters rather than in separate full model copies. The
fallback model is `google/gemma-4-26B-A4B-it`, whose model card lists 25.2B total
parameters and 3.8B active parameters. Both paths stay under the hackathon's 32B total
parameter cap.

## What Codex Did

OpenAI Codex was used throughout the project, not just for a small cleanup pass. It helped
build the Gradio app, add game-state tests, tune prompt and parser behavior, wire the
Modal/OpenAI-compatible runtime, debug local and hosted submission issues, prepare
Hugging Face metadata, and keep the documentation aligned with the hackathon judging
tags.

The repo keeps Codex visible in `CONTRIBUTORS.md`, and Codex-attributed commits in the
linked GitHub/Hugging Face history document the final submission preparation.

## What Is Shared

- Character LoRA adapters:
  - `build-small-hackathon/velvet-rope-marlowe-lora`
  - `build-small-hackathon/velvet-rope-vivienne-lora`
  - `build-small-hackathon/velvet-rope-crispin-lora`
  - `build-small-hackathon/velvet-rope-lenore-lora`
  - `build-small-hackathon/velvet-rope-aurelia-lora`
- Cleaned playtest transcripts:
  - `build-small-hackathon/velvet-rope-playtest-transcripts`

## Submission Tags

The final README uses the field-guide tag format:

- `track:wood`
- `sponsor:openai`
- `sponsor:modal`
- `achievement:welltuned`
- `achievement:offbrand`
- `achievement:llama`
- `achievement:sharing`
- `achievement:fieldnotes`

The project deliberately does not claim `achievement:offgrid`, `sponsor:openbmb`,
`sponsor:nvidia`, or Tiny Titan.

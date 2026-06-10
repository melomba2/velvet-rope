# Lenore Stage Door Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add Level 4 as a playable haunted theater stage-door encounter with Lenore Cue.

**Architecture:** Reuse the existing character-driven game architecture. Lenore is mostly data in `characters.py`; validator changes are limited to theater-specific bad-faith tactics; art is wired through `manifest.json`.

**Tech Stack:** Python, Gradio, pytest, project-local PNG assets.

---

### Task 1: Character And Validator Behavior

**Files:**
- Modify: `velvet_rope/characters.py`
- Modify: `velvet_rope/validator.py`
- Test: `tests/test_validator.py`
- Test: `tests/test_game.py`

- [ ] Add failing tests importing `LENORE`, checking a backstage soft spot, a repeated soft spot, and a star-entitlement penalty.
- [ ] Run `python -m pytest tests/test_validator.py tests/test_game.py -q` and confirm the tests fail because `LENORE` is missing.
- [ ] Add the `LENORE` character and include it in `PLAYABLE_CHARACTERS`.
- [ ] Add theater-specific bad-faith tactics to `BAD_FAITH_TACTICS` and bad-faith reply handling.
- [ ] Run the focused tests again and confirm they pass.

### Task 2: Art Manifest And Assets

**Files:**
- Modify: `velvet_rope/static/art/manifest.json`
- Create: `velvet_rope/static/art/sprites/lenore_*.png`
- Create: `velvet_rope/static/art/assets/stage_door_*.png`
- Test: `tests/test_ui_assets.py`

- [ ] Add failing UI asset tests for Lenore mood sprites, scene copy, win overlay, and stamps.
- [ ] Run `python -m pytest tests/test_ui_assets.py -q` and confirm the tests fail because Lenore art is unmapped.
- [ ] Create Lenore pixel assets and wire them into the manifest.
- [ ] Run the focused UI tests and confirm they pass.

### Task 3: Full Verification And Local Server

**Files:**
- Verify only.

- [ ] Run `python -m pytest -q`.
- [ ] Check whether a local app server is reachable on common Gradio ports.
- [ ] If no server is reachable, start `python app.py` locally and report the URL.

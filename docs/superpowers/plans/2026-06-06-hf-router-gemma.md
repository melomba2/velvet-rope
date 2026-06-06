# HF Router Gemma Backend Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a Hugging Face Router backend alias for Gemma so Velvet Rope can start contest playtesting on HF infrastructure.

**Architecture:** Reuse the existing `OpenAICompatibleBackend` rather than adding another HTTP client. The backend factory will map `huggingface-router` aliases to Hugging Face Router defaults, while the request adapter gains small sampling controls used by both HF Router and generic OpenAI-compatible endpoints.

**Tech Stack:** Python, requests, pytest, Hugging Face Router OpenAI-compatible chat completions.

---

## File Structure

- Modify `velvet_rope/model_backends.py`: add HF Router env mapping and optional request controls.
- Modify `tests/test_model_backends.py`: add TDD coverage for HF Router defaults and request payloads.
- Modify `README.md`: document the HF-first contest runtime path.

## Task 1: HF Router Backend Alias

**Files:**
- Modify: `tests/test_model_backends.py`
- Modify: `velvet_rope/model_backends.py`

- [ ] **Step 1: Write a failing test**

Add a test proving `VELVET_MODEL_BACKEND=huggingface-router` creates an `OpenAICompatibleBackend` with HF Router defaults and `HF_TOKEN` fallback.

- [ ] **Step 2: Run the focused test**

Run `python3 -m pytest tests/test_model_backends.py::test_backend_from_env_reads_huggingface_router_defaults -q`.
Expected: fail because the alias is not implemented.

- [ ] **Step 3: Implement the alias**

Update `backend_from_env()` to map `huggingface-router`, `hf-router`, and `huggingface` to the OpenAI-compatible backend with HF defaults.

- [ ] **Step 4: Run the focused test**

Run `python3 -m pytest tests/test_model_backends.py::test_backend_from_env_reads_huggingface_router_defaults -q`.
Expected: pass.

## Task 2: Sampling Controls

**Files:**
- Modify: `tests/test_model_backends.py`
- Modify: `velvet_rope/model_backends.py`

- [ ] **Step 1: Write a failing test**

Add a test proving `max_tokens` appears in the request payload only when configured.

- [ ] **Step 2: Run the focused test**

Run `python3 -m pytest tests/test_model_backends.py::test_openai_compatible_backend_includes_max_tokens_when_configured -q`.
Expected: fail because the backend has no `max_tokens` field.

- [ ] **Step 3: Implement request controls**

Add `temperature`, `max_tokens`, and timeout env parsing to `OpenAICompatibleBackend` construction.

- [ ] **Step 4: Run focused and full backend tests**

Run `python3 -m pytest tests/test_model_backends.py -q`.
Expected: pass.

## Task 3: Runtime Documentation

**Files:**
- Modify: `README.md`

- [ ] **Step 1: Update README runtime section**

Describe HF Router as the recommended contest starting point and deterministic as fallback/dev mode.

- [ ] **Step 2: Verify all tests**

Run `python3 -m pytest -q` and `python3 -m compileall -q velvet_rope tests app.py`.
Expected: all pass.

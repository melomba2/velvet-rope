# Retro Bottom HUD Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build the approved full-width bottom HUD with Read the Room, a level-specific velvet-rope status bar, and retro pixel UI polish without creating new image assets.

**Architecture:** Keep the change local to the existing Gradio UI layer. Add a status-bar HTML renderer beside the existing scene and read-room renderers, move input controls into a new bottom HUD row, and update CSS/tests to lock in the layout.

**Tech Stack:** Python, Gradio Blocks, HTML string renderers, CSS, pytest.

---

## File Structure

- Modify `velvet_rope/ui.py`: add the bottom HUD layout, status bar renderer, and retro CSS updates.
- Modify `tests/test_ui_assets.py`: add regression coverage for the HUD markup, status bar, and CSS.
- Keep `velvet_rope/static/art/manifest.json` unchanged because the requested assets do not exist yet.

### Task 1: Add HUD Renderer Tests

**Files:**
- Modify: `tests/test_ui_assets.py`

- [ ] **Step 1: Write failing tests for the bottom HUD helpers**

Add imports and tests that assert `_status_bar_html` exists, contains the current status copy, exposes character/mood/state classes, and documents future asset filenames in CSS.

```python
from velvet_rope.ui import CSS, _header_html, _read_room_html, _scene_html, _status_bar_html


def test_status_bar_html_uses_character_status_and_classes():
    game_state = replace(
        new_game_state(VIVIENNE),
        mood=Mood.RESPECTED,
    )

    status_bar = _status_bar_html(game_state)

    assert "velvet-status-bar" in status_bar
    assert "character-vivienne" in status_bar
    assert "mood-respected" in status_bar
    assert "is-active" in status_bar
    assert "The forms align by half an inch" in status_bar
    assert "Somnolent Bureau" in status_bar


def test_css_defines_full_width_retro_bottom_hud():
    assert ".hud-console" in CSS
    assert ".hud-read-room" in CSS
    assert ".velvet-status-bar" in CSS
    assert ".hud-input-row" in CSS
    assert "grid-column: 1 / -1;" in CSS
    assert "image-rendering: pixelated;" in CSS
    assert "status_marlowe_rope.png" in CSS
    assert "status_vivienne_rope.png" in CSS
    assert "status_crispin_rope.png" in CSS
    assert "status_lenore_rope.png" in CSS
    assert "status_aurelia_rope.png" in CSS
```

- [ ] **Step 2: Run tests and verify failure**

Run:

```bash
python -m pytest tests/test_ui_assets.py::test_status_bar_html_uses_character_status_and_classes tests/test_ui_assets.py::test_css_defines_full_width_retro_bottom_hud -q
```

Expected: import or assertion failure because `_status_bar_html` and the HUD CSS do not exist yet.

### Task 2: Implement Bottom HUD Layout

**Files:**
- Modify: `velvet_rope/ui.py`

- [ ] **Step 1: Add `_status_bar_html`**

Create a renderer that uses existing `_status_line`, `character_for_id`, and game-state classes.

```python
def _status_bar_html(state: GameState) -> str:
    character = character_for_id(state.character_id)
    status_line = _status_line(state)
    return f"""
    <section class="velvet-status-bar character-{html.escape(state.character_id)} mood-{html.escape(state.mood.value)} is-{html.escape(state.status.value)}" aria-label="Gate status">
      <div class="status-bar-frame">
        <div class="rail-label">{html.escape(character.scene_name)}</div>
        <p>{html.escape(status_line)}</p>
      </div>
    </section>
    """
```

- [ ] **Step 2: Move Gradio controls into a full-width HUD row**

Change `build_app` so `scene` and `chatbot` remain in `play-shell`, while `read_room`, `status_bar`, `player_input`, `send`, and `reset` sit below in `hud-console`.

```python
with gr.Row(equal_height=False, elem_classes=["play-shell"]):
    with gr.Column(scale=7, min_width=470, elem_classes=["velvet-stage"]):
        scene = gr.HTML()
    with gr.Column(scale=4, min_width=340, elem_classes=["chat-panel"]):
        chatbot = gr.Chatbot(...)

with gr.Row(equal_height=False, elem_classes=["hud-console"]):
    with gr.Column(scale=4, min_width=270, elem_classes=["hud-read-room"]):
        read_room = gr.HTML()
    with gr.Column(scale=5, min_width=320, elem_classes=["hud-status-slot"]):
        status_bar = gr.HTML()
    with gr.Column(scale=5, min_width=360, elem_classes=["hud-input-stack"]):
        player_input = gr.Textbox(...)
        with gr.Row(elem_classes=["hud-input-row"]):
            send = gr.Button("Send", variant="primary", scale=2)
            reset = gr.Button("Reset", variant="secondary", scale=1)
```

- [ ] **Step 3: Update render callbacks**

Return and update `status_bar` alongside the existing scene, read-room, and chatbot outputs.

```python
def render(current: GameState) -> tuple[str, str, str, list[dict[str, str]]]:
    return _scene_html(current), _read_room_html(current), _status_bar_html(current), _chat_messages(current)
```

Then update `submit`, `restart`, `select_level`, `app.load`, `level.change`, `send.click`, `player_input.submit`, and `reset.click` outputs to include `status_bar`.

- [ ] **Step 4: Run targeted tests**

Run:

```bash
python -m pytest tests/test_ui_assets.py::test_status_bar_html_uses_character_status_and_classes -q
```

Expected: PASS.

### Task 3: Apply Retro HUD CSS

**Files:**
- Modify: `velvet_rope/ui.py`
- Modify: `tests/test_ui_assets.py`

- [ ] **Step 1: Replace chat-rail read-room styling with HUD styling**

Update CSS so `.chat-panel` is conversation-only and `.hud-console` owns the control surface. Keep existing Gradio component selectors scoped to the new HUD where possible.

- [ ] **Step 2: Add status-bar fallback designs**

Use CSS custom properties and character classes for the fallback status bars. Include commented asset filenames so future image files have clear hooks without requiring missing files.

```css
.velvet-status-bar.character-marlowe { --status-asset: url("assets/status_marlowe_rope.png"); }
.velvet-status-bar.character-vivienne { --status-asset: url("assets/status_vivienne_rope.png"); }
.velvet-status-bar.character-crispin { --status-asset: url("assets/status_crispin_rope.png"); }
.velvet-status-bar.character-lenore { --status-asset: url("assets/status_lenore_rope.png"); }
.velvet-status-bar.character-aurelia { --status-asset: url("assets/status_aurelia_rope.png"); }
```

Do not use these URLs as loaded backgrounds until files exist; use gradients and borders for the runtime fallback.

- [ ] **Step 3: Update old tests that expected scene-bottom status**

Replace `test_css_places_status_at_scene_bottom` with coverage for status staying out of the scene and appearing in the HUD.

- [ ] **Step 4: Run UI asset tests**

Run:

```bash
python -m pytest tests/test_ui_assets.py -q
```

Expected: PASS.

### Task 4: Visual Verification

**Files:**
- No code files; run the app.

- [ ] **Step 1: Start the local Gradio app**

Run:

```bash
python app.py
```

Expected: app starts and prints a local URL.

- [ ] **Step 2: Open the app in the in-app browser**

Navigate to the printed local URL and inspect desktop layout. Verify the stage and chat remain side by side, the HUD spans both columns, Read the Room is in the HUD, the status bar sits between Read the Room and input controls, and text does not overlap.

- [ ] **Step 3: Check mobile width**

Set a narrow viewport or resize the browser. Verify the layout stacks stage, chat, Read the Room, status bar, and controls.

- [ ] **Step 4: Stop the local server**

Stop the running app process once verification is complete.

### Task 5: Final Verification

**Files:**
- No code files.

- [ ] **Step 1: Run targeted tests**

Run:

```bash
python -m pytest tests/test_ui_assets.py tests/test_ui_services.py -q
```

Expected: PASS.

- [ ] **Step 2: Review git diff**

Run:

```bash
git diff -- velvet_rope/ui.py tests/test_ui_assets.py docs/superpowers/specs/2026-06-11-retro-bottom-hud-design.md docs/superpowers/plans/2026-06-11-retro-bottom-hud.md
```

Expected: only the UI, UI tests, and docs changed.

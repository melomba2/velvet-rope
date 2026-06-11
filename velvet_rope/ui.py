from __future__ import annotations

from dataclasses import replace
import html

import gradio as gr

from velvet_rope.art import (
    configure_gradio_static_paths,
    mood_sprite_url,
    scene_asset_url,
    scene_background_url,
    state_rope_url,
    state_stamp_url,
)
from velvet_rope.characters import MARLOWE, PLAYABLE_CHARACTERS, character_for_id
from velvet_rope.game import GameService
from velvet_rope.state import GameState, GameStatus, Mood


CSS = """
:root {
  --vr-bg: #09090b;
  --vr-panel: #120d14;
  --vr-panel-2: #101014;
  --vr-rope: #b32735;
  --vr-rope-hot: #e3424f;
  --vr-gold: #d6b15e;
  --vr-text-gold: #f7e4a8;
  --vr-muted: #b7ad92;
  --vr-danger: #b32735;
  --vr-success: #4f8f73;
  --vr-border: #2c2430;
}

.gradio-container {
  background:
    radial-gradient(circle at 18% 12%, rgba(214, 177, 94, 0.12), transparent 24rem),
    linear-gradient(180deg, #09090b 0%, #0e080d 58%, #09090b 100%);
  color: var(--vr-text-gold);
  font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
}

.gradio-container .main {
  background: transparent;
}

#velvet-app {
  max-width: 1240px;
  margin: 0 auto;
  padding: 8px 16px 8px;
}

.velvet-header {
  display: flex;
  justify-content: space-between;
  gap: 14px;
  align-items: end;
  margin-bottom: 8px;
}

.rail-label {
  color: var(--vr-gold);
  font-size: 0.72rem;
  font-weight: 800;
  letter-spacing: 0;
  text-transform: uppercase;
}

.velvet-header h1 {
  color: var(--vr-text-gold);
  font-size: clamp(2.2rem, 4.2vw, 3.65rem);
  line-height: 0.92;
  margin: 0 0 4px;
}

.velvet-header p {
  color: var(--vr-muted);
  font-size: 0.94rem;
  line-height: 1.28;
  max-width: 620px;
  margin: 0;
}

.level-select-card {
  position: relative;
  flex: 0 0 340px !important;
  width: 340px;
  max-width: 340px;
  margin-left: auto;
  padding: 8px 10px;
  border: 1px solid rgba(214, 177, 94, 0.58);
  border-radius: 8px;
  background:
    linear-gradient(180deg, rgba(18, 13, 20, 0.9), rgba(16, 16, 20, 0.86)),
    radial-gradient(circle at 92% 18%, rgba(214, 177, 94, 0.16), transparent 8rem);
  box-shadow: 0 14px 48px rgba(0, 0, 0, 0.24);
}

.level-select-card > .gap {
  justify-content: flex-end;
}

.level-select-card .wrap,
.level-select-card .secondary-wrap,
.level-select-card .form {
  background: transparent !important;
  border: 0 !important;
  box-shadow: none !important;
}

.level-select-card label {
  margin: 0 !important;
}

.velvet-stage,
.chat-panel {
  border: 1px solid var(--vr-border);
  border-radius: 8px;
  background: rgba(18, 13, 20, 0.94);
  box-shadow: 0 22px 80px rgba(0, 0, 0, 0.32);
  overflow: hidden;
}

.velvet-stage {
  min-height: 0;
}

.nightclub-scene {
  position: relative;
  min-height: min(54vh, 500px);
  height: calc(100vh - 150px);
  max-height: 500px;
  padding: 14px 14px 0;
  isolation: isolate;
  background:
    linear-gradient(90deg, rgba(179, 39, 53, 0.22), transparent 26%, transparent 74%, rgba(214, 177, 94, 0.2)),
    linear-gradient(180deg, rgba(9, 9, 11, 0.08), rgba(9, 9, 11, 0.58)),
    var(--stage-bg, url("__DOOR_BG_URL__"));
  background-position: center;
  background-size: cover;
  image-rendering: pixelated;
  overflow: hidden;
}

.nightclub-scene::before {
  content: "";
  position: absolute;
  inset: 0;
  z-index: 0;
  background: rgba(9, 9, 11, 0.2);
  pointer-events: none;
}

.scene-bg-image {
  position: absolute;
  inset: 0;
  z-index: 0;
  width: 100%;
  height: 100%;
  object-fit: cover;
  image-rendering: pixelated;
  image-rendering: crisp-edges;
}

.nightclub-scene.is-won::before {
  background: rgba(30, 18, 10, 0.1);
}

.nightclub-scene.is-won {
  background:
    linear-gradient(90deg, rgba(79, 143, 115, 0.2), transparent 30%, transparent 70%, rgba(214, 177, 94, 0.18)),
    linear-gradient(180deg, rgba(9, 9, 11, 0.02), rgba(9, 9, 11, 0.38)),
    var(--stage-bg, url("__WIN_BG_URL__"));
  background-position: center;
  background-size: cover;
}

.nightclub-scene.is-lost::before {
  background: rgba(9, 9, 11, 0.36);
}

.nightclub-scene.is-lost {
  background:
    linear-gradient(90deg, rgba(179, 39, 53, 0.22), transparent 30%, transparent 70%, rgba(9, 9, 11, 0.32)),
    linear-gradient(180deg, rgba(9, 9, 11, 0.14), rgba(9, 9, 11, 0.62)),
    var(--stage-bg, url("__LOSS_BG_URL__"));
  background-position: center;
  background-size: cover;
}

.door-sign {
  position: relative;
  z-index: 2;
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 12px;
  margin-bottom: 8px;
}

.door-plaque {
  max-width: min(62%, 440px);
  padding: 8px 10px;
  border: 2px solid rgba(214, 177, 94, 0.52);
  border-radius: 8px;
  background:
    linear-gradient(180deg, rgba(9, 9, 11, 0.82), rgba(18, 13, 20, 0.74)),
    radial-gradient(circle at 12% 18%, rgba(214, 177, 94, 0.12), transparent 8rem);
  box-shadow:
    inset 0 0 0 2px rgba(9, 9, 11, 0.42),
    0 10px 0 rgba(9, 9, 11, 0.18),
    0 18px 36px rgba(0, 0, 0, 0.22);
}

.door-sign h2 {
  color: var(--vr-text-gold);
  font-size: 1.3rem;
  line-height: 1.1;
  margin: 0;
  text-shadow: 0 2px 0 #09090b;
}

.door-sign p {
  color: var(--vr-muted);
  margin: 4px 0 0;
  font-size: 0.92rem;
  line-height: 1.22;
  text-shadow: 0 1px 0 #09090b;
}

.mood-badge {
  border: 2px solid var(--vr-gold);
  border-radius: 8px;
  color: var(--vr-text-gold);
  background: rgba(16, 16, 20, 0.88);
  padding: 7px 9px;
  font-size: 0.84rem;
  font-weight: 800;
  white-space: nowrap;
  box-shadow: 0 0 0 2px rgba(9, 9, 11, 0.62);
}

.mood-badge.suspicious,
.mood-badge.done_with_you {
  border-color: var(--vr-danger);
}

.mood-badge.respected,
.mood-badge.softened,
.mood-badge.letting_you_in {
  border-color: var(--vr-success);
}

.scene-composition {
  position: relative;
  z-index: 1;
  min-height: 0;
  height: calc(100% - 52px);
  margin-top: 6px;
}

.scene-composition::after {
  content: "";
  position: absolute;
  inset: auto -18px 0;
  height: 34%;
  z-index: 1;
  background: linear-gradient(180deg, transparent, rgba(9, 9, 11, 0.42));
  pointer-events: none;
}

.marlowe-box {
  position: absolute;
  left: 0;
  bottom: 0;
  z-index: 2;
  width: clamp(224px, 38%, 340px);
  max-height: 96%;
  padding: 8px 8px 0;
  border: 2px solid rgba(214, 177, 94, 0.5);
  border-radius: 8px 8px 0 0;
  background: linear-gradient(180deg, rgba(9, 9, 11, 0.58), rgba(9, 9, 11, 0.72));
  box-shadow: inset 0 0 0 2px rgba(9, 9, 11, 0.32), 0 16px 0 rgba(9, 9, 11, 0.18);
  overflow: hidden;
}

.marlowe-figure {
  display: block;
  width: 100%;
  height: auto;
  object-fit: contain;
  image-rendering: pixelated;
  image-rendering: crisp-edges;
  filter: drop-shadow(0 10px 0 rgba(9, 9, 11, 0.2));
}

.stage-status {
  color: var(--vr-muted);
  line-height: 1.45;
  position: absolute;
  right: 18px;
  bottom: 48px;
  z-index: 5;
  max-width: min(46ch, 52%);
  text-shadow: 0 2px 0 #09090b, 0 0 12px #09090b;
  border-left: 3px solid var(--vr-rope);
  padding-left: 12px;
}

.state-stamp {
  position: absolute;
  right: 28px;
  top: 72px;
  z-index: 6;
  width: clamp(112px, 18vw, 166px);
  aspect-ratio: 1;
  object-fit: contain;
  image-rendering: pixelated;
  image-rendering: crisp-edges;
  filter: drop-shadow(0 8px 0 rgba(9, 9, 11, 0.34));
}

.velvet-rope-layer {
  position: absolute;
  left: 50%;
  bottom: -125px;
  z-index: 4;
  width: min(106%, 800px);
  transform: translateX(-50%);
  pointer-events: none;
}

.velvet-rope-sprite {
  display: block;
  width: 100%;
  height: auto;
  image-rendering: pixelated;
  image-rendering: crisp-edges;
  filter: drop-shadow(0 12px 0 rgba(9, 9, 11, 0.24));
}

.chat-panel {
  display: flex;
  flex-direction: column;
  flex-wrap: nowrap !important;
  gap: 8px;
  padding: 10px;
  min-height: 0;
  height: calc(100vh - 150px);
  max-height: 680px;
  background:
    linear-gradient(180deg, rgba(18, 13, 20, 0.96), rgba(9, 9, 11, 0.98)),
    radial-gradient(circle at 94% 8%, rgba(214, 177, 94, 0.12), transparent 10rem);
}

.chat-panel .bubble-wrap,
.chat-panel .message,
.chat-panel .chatbot,
.chat-panel .chatbot-container {
  border-radius: 8px;
}

#conversation-chatbot {
  flex: 1 1 auto !important;
  min-height: 245px !important;
  height: auto !important;
}

#conversation-chatbot .wrapper,
#conversation-chatbot .bubble-wrap {
  height: 100% !important;
  min-height: 0 !important;
}

#conversation-chatbot .bubble-wrap {
  overflow-y: auto !important;
}

.chat-panel .form {
  flex: 0 0 auto;
}

.read-room-panel {
  display: grid;
  grid-template-columns: 1fr;
  align-items: center;
  min-height: 64px;
  padding: 8px;
  border: 1px solid rgba(214, 177, 94, 0.28);
  border-radius: 8px;
  background: rgba(16, 16, 20, 0.78);
}

.read-room-panel h3 {
  color: var(--vr-text-gold);
  margin: 1px 0 2px;
  font-size: 0.92rem;
  line-height: 1.15;
}

.read-room-panel p {
  color: var(--vr-muted);
  margin: 0;
  font-size: 0.82rem;
  line-height: 1.25;
}

.gradio-container textarea,
.gradio-container input {
  background: #101014 !important;
  color: var(--vr-text-gold) !important;
  border-color: var(--vr-border) !important;
}

.gradio-container label,
.gradio-container .block-title,
.gradio-container .label-wrap span {
  color: var(--vr-muted) !important;
}

.gradio-container button.primary {
  background: var(--vr-rope) !important;
  border-color: var(--vr-rope-hot) !important;
  color: white !important;
}

.gradio-container button.secondary {
  background: #101014 !important;
  border-color: var(--vr-border) !important;
  color: var(--vr-text-gold) !important;
}

.gradio-container footer {
  display: none !important;
}

.mood-dot {
  display: inline-block;
  width: 9px;
  height: 9px;
  border-radius: 99px;
  margin-right: 7px;
  background: var(--vr-gold);
  box-shadow: 0 0 12px currentColor;
}

.mood-dot.suspicious,
.mood-dot.done_with_you {
  background: var(--vr-danger);
}

.mood-dot.softened,
.mood-dot.letting_you_in {
  background: var(--vr-success);
}

@media (max-width: 780px) {
  #velvet-app {
    padding: 18px 10px 28px;
  }

  .velvet-header {
    align-items: start;
    flex-direction: column;
    justify-content: flex-start;
  }

  .level-select-card {
    flex: 1 1 auto;
    margin-left: 0;
    width: 100%;
  }

  .nightclub-scene {
    min-height: 470px;
    height: auto;
    max-height: none;
  }

  .chat-panel {
    height: auto;
    max-height: none;
  }

  #conversation-chatbot {
    min-height: 300px !important;
  }

  .scene-composition {
    min-height: 430px;
    height: auto;
  }

  .marlowe-box {
    left: 0;
    bottom: 0;
    width: min(76%, 290px);
  }

  .stage-status {
    right: 8px;
    bottom: 36px;
    max-width: calc(100% - 16px);
    font-size: 0.88rem;
  }

  .velvet-rope-layer {
    bottom: -96px;
    width: 148%;
  }

  .state-stamp {
    right: 10px;
    top: 76px;
    width: 112px;
  }

  .door-sign {
    align-items: start;
    flex-direction: column;
  }

  .door-plaque {
    max-width: 100%;
  }
}
""".replace("__DOOR_BG_URL__", scene_asset_url("door_background"))
CSS = CSS.replace("__WIN_BG_URL__", scene_asset_url("win_background"))
CSS = CSS.replace("__LOSS_BG_URL__", scene_asset_url("loss_background"))


def build_app(service: GameService | None = None) -> gr.Blocks:
    service = service or GameService()
    services = _services_for_levels(service)
    configure_gradio_static_paths(gr)

    with gr.Blocks(css=CSS, title="Velvet Rope", theme=gr.themes.Base()) as app:
        state = gr.State(services[MARLOWE.character_id].new_game())

        with gr.Column(elem_id="velvet-app"):
            with gr.Row(equal_height=False, elem_classes=["velvet-header"]):
                gr.HTML(_header_html())
                with gr.Column(min_width=230, elem_classes=["level-select-card"]):
                    level = gr.Dropdown(
                        label="Level",
                        choices=[character.level_label for character in PLAYABLE_CHARACTERS],
                        value=MARLOWE.level_label,
                        interactive=True,
                    )
            with gr.Row(equal_height=False, elem_classes=["play-shell"]):
                with gr.Column(scale=7, min_width=470, elem_classes=["velvet-stage"]):
                    scene = gr.HTML()
                with gr.Column(scale=4, min_width=340, elem_classes=["chat-panel"]):
                    read_room = gr.HTML()
                    chatbot = gr.Chatbot(
                        label="Conversation",
                        type="messages",
                        height=None,
                        elem_id="conversation-chatbot",
                        show_copy_button=False,
                        avatar_images=(None, None),
                    )
                    player_input = gr.Textbox(
                        label=MARLOWE.input_label,
                        placeholder=MARLOWE.input_placeholder,
                        lines=1,
                        max_lines=1,
                    )
                    with gr.Row():
                        send = gr.Button("Send", variant="primary", scale=2)
                        reset = gr.Button("Reset", variant="secondary", scale=1)

        def render(current: GameState) -> tuple[str, str, list[dict[str, str]]]:
            return _scene_html(current), _read_room_html(current), _chat_messages(current)

        def submit(
            message: str,
            current: GameState,
        ) -> tuple[GameState, str, str, list[dict[str, str]], str]:
            cleaned = message.strip()
            if not cleaned:
                scene_html, hint_html, messages = render(current)
                return current, scene_html, hint_html, messages, ""
            updated = _service_for_state(services, current).play_turn(current, cleaned)
            scene_html, hint_html, messages = render(updated)
            return updated, scene_html, hint_html, messages, ""

        def restart(current: GameState) -> tuple[GameState, str, str, list[dict[str, str]], str]:
            fresh = _service_for_state(services, current).new_game()
            scene_html, hint_html, messages = render(fresh)
            return fresh, scene_html, hint_html, messages, ""

        def select_level(level_label: str) -> tuple[GameState, str, str, list[dict[str, str]], dict]:
            character = _character_for_level_label(level_label)
            fresh = services[character.character_id].new_game()
            scene_html, hint_html, messages = render(fresh)
            input_update = gr.update(
                label=character.input_label,
                placeholder=character.input_placeholder,
                value="",
            )
            return fresh, scene_html, hint_html, messages, input_update

        app.load(render, inputs=state, outputs=[scene, read_room, chatbot])
        level.change(
            select_level,
            inputs=level,
            outputs=[state, scene, read_room, chatbot, player_input],
        )
        send.click(
            submit,
            inputs=[player_input, state],
            outputs=[state, scene, read_room, chatbot, player_input],
        )
        player_input.submit(
            submit,
            inputs=[player_input, state],
            outputs=[state, scene, read_room, chatbot, player_input],
        )
        reset.click(restart, inputs=state, outputs=[state, scene, read_room, chatbot, player_input])

    return app


def _services_for_levels(service: GameService) -> dict[str, GameService]:
    return {
        character.character_id: GameService(
            backend=_backend_for_character(service.backend, character),
            character=character,
            allow_backend_fallback=service.allow_backend_fallback,
            transcript_recorder=service.transcript_recorder,
        )
        for character in PLAYABLE_CHARACTERS
    }


def _backend_for_character(backend, character):
    model = getattr(backend, "model", None)
    if isinstance(model, str) and "{character_id}" in model:
        return replace(backend, model=model.format(character_id=character.character_id))
    return backend


def _service_for_state(services: dict[str, GameService], state: GameState) -> GameService:
    return services.get(state.character_id, services[MARLOWE.character_id])


def _character_for_level_label(level_label: str):
    for character in PLAYABLE_CHARACTERS:
        if character.level_label == level_label:
            return character
    return MARLOWE


def _header_html() -> str:
    return """
    <div class="velvet-title">
      <h1>Velvet Rope</h1>
      <p>Read the room, charm the gatekeeper, and talk your way past.</p>
    </div>
    """


def _scene_html(state: GameState) -> str:
    character = character_for_id(state.character_id)
    mood_label = _mood_label(state.mood)
    status_line = _status_line(state)
    mood_value = html.escape(state.mood.value)
    background_url = html.escape(scene_background_url(state), quote=True)
    sprite_url = html.escape(mood_sprite_url(state.mood, character.character_id), quote=True)
    stamp_html = _stamp_html(state)
    rope_html = _rope_html(state)
    return f"""
    <section class="nightclub-scene {_scene_class(state)}" data-stage-bg="{background_url}" style="--stage-bg: url('{background_url}')">
      <img class="scene-bg-image" src="{background_url}" alt="" aria-hidden="true">
      <div class="door-sign">
        <div class="door-plaque">
          <h2>{html.escape(character.display_name)}</h2>
          <p>{html.escape(character.title)} at {html.escape(character.scene_name)}</p>
        </div>
        <div class="mood-badge {mood_value}">Mood: {html.escape(mood_label)}</div>
      </div>
      <div class="scene-composition">
        <div class="marlowe-box">
          <img class="marlowe-figure" src="{sprite_url}" alt="{html.escape(character.display_name)} looks {html.escape(mood_label)}">
        </div>
        {stamp_html}
        <div class="stage-status">{html.escape(status_line)}</div>
        {rope_html}
      </div>
    </section>
    """


def _read_room_html(state: GameState) -> str:
    mood_value = state.mood.value
    return f"""
    <section class="read-room-panel">
      <div>
        <div class="rail-label">Read the room</div>
        <h3><span class="mood-dot {html.escape(mood_value)}"></span>Current mood: {html.escape(_mood_label(state.mood))}</h3>
        <p>{html.escape(_hint_text(state))}</p>
      </div>
    </section>
    """


def _chat_messages(state: GameState) -> list[dict[str, str]]:
    character = character_for_id(state.character_id)
    messages = [
        {
            "role": "assistant",
            "content": character.opening_line,
        }
    ]
    messages.extend({"role": turn.role, "content": turn.content} for turn in state.history)
    return messages


def _hint_text(state: GameState) -> str:
    character = character_for_id(state.character_id)
    if state.status is GameStatus.WON:
        return character.won_hint
    if state.status is GameStatus.LOST:
        return character.lost_hint
    if state.hint:
        return state.hint
    return character.default_hint


def _status_line(state: GameState) -> str:
    character = character_for_id(state.character_id)
    if state.status is GameStatus.WON:
        return character.won_status_line
    if state.status is GameStatus.LOST:
        return character.lost_status_line
    if state.mood is Mood.SUSPICIOUS:
        return character.suspicious_status_line
    if state.mood in {Mood.RESPECTED, Mood.SOFTENED}:
        return character.respected_status_line
    return character.active_status_line


def _mood_label(mood: Mood) -> str:
    return mood.value.replace("_", " ")


def _scene_class(state: GameState) -> str:
    return f"is-{state.status.value} mood-{state.mood.value}"


def _stamp_html(state: GameState) -> str:
    stamp_url = state_stamp_url(state)
    if stamp_url is None:
        return ""
    label = _stamp_label(state)
    return f'<img class="state-stamp" src="{html.escape(stamp_url, quote=True)}" alt="{label}">'


def _stamp_label(state: GameState) -> str:
    if state.character_id == "aurelia":
        return "Invited" if state.status is GameStatus.WON else "Uninvited"
    if state.character_id == "lenore":
        return "Places called" if state.status is GameStatus.WON else "Blackout"
    if state.character_id == "crispin":
        return "Cookie crowned" if state.status is GameStatus.WON else "Crumbled"
    if state.character_id == "vivienne":
        return "Dream placed" if state.status is GameStatus.WON else "Misfiled"
    return "Admitted" if state.status is GameStatus.WON else "Denied"


def _rope_html(state: GameState) -> str:
    rope_url = state_rope_url(state)
    if rope_url is None:
        return ""
    if state.character_id == "aurelia":
        label = "the grand threshold opens"
    elif state.character_id == "crispin":
        label = "the knot-door opens"
    elif state.character_id == "lenore":
        label = "the stage door opens"
    elif state.character_id == "vivienne":
        label = "the dream gate opens"
    else:
        label = "the velvet rope opens"
    return (
        '<div class="velvet-rope-layer">'
        f'<img class="velvet-rope-sprite" src="{html.escape(rope_url, quote=True)}" alt="{label}">'
        "</div>"
    )

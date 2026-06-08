from __future__ import annotations

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
from velvet_rope.characters import MARLOWE
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
  max-width: 1180px;
  margin: 0 auto;
  padding: 28px 18px 34px;
}

.velvet-header {
  display: flex;
  justify-content: space-between;
  gap: 18px;
  align-items: end;
  margin-bottom: 18px;
}

.velvet-kicker,
.rail-label,
.level-kicker {
  color: var(--vr-gold);
  font-size: 0.72rem;
  font-weight: 800;
  letter-spacing: 0;
  text-transform: uppercase;
}

.velvet-header h1 {
  color: var(--vr-text-gold);
  font-size: clamp(2.45rem, 7vw, 5.4rem);
  line-height: 0.92;
  margin: 4px 0 6px;
}

.velvet-header p {
  color: var(--vr-muted);
  font-size: 1rem;
  line-height: 1.5;
  max-width: 640px;
  margin: 0;
}

.velvet-stamp {
  border: 1px solid var(--vr-gold);
  border-radius: 8px;
  color: var(--vr-text-gold);
  padding: 10px 12px;
  min-width: 156px;
  text-align: center;
  background: rgba(18, 13, 20, 0.78);
}

.velvet-stage,
.velvet-rail {
  border: 1px solid var(--vr-border);
  border-radius: 8px;
  background: rgba(18, 13, 20, 0.94);
  box-shadow: 0 22px 80px rgba(0, 0, 0, 0.32);
  overflow: hidden;
}

.velvet-stage {
  min-height: 500px;
}

.nightclub-scene {
  position: relative;
  padding: 18px 18px 0;
  isolation: isolate;
  background:
    linear-gradient(90deg, rgba(179, 39, 53, 0.22), transparent 26%, transparent 74%, rgba(214, 177, 94, 0.2)),
    linear-gradient(180deg, rgba(9, 9, 11, 0.08), rgba(9, 9, 11, 0.58)),
    url("__DOOR_BG_URL__");
  background-position: center;
  background-size: cover;
  image-rendering: pixelated;
  overflow: hidden;
}

.nightclub-scene::before {
  content: "";
  position: absolute;
  inset: 0;
  z-index: -1;
  background: rgba(9, 9, 11, 0.2);
  pointer-events: none;
}

.nightclub-scene.is-won::before {
  background: rgba(30, 18, 10, 0.1);
}

.nightclub-scene.is-won {
  background:
    linear-gradient(90deg, rgba(79, 143, 115, 0.2), transparent 30%, transparent 70%, rgba(214, 177, 94, 0.18)),
    linear-gradient(180deg, rgba(9, 9, 11, 0.02), rgba(9, 9, 11, 0.38)),
    url("__WIN_BG_URL__");
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
    url("__LOSS_BG_URL__");
  background-position: center;
  background-size: cover;
}

.door-sign {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 14px;
  margin-bottom: 16px;
}

.door-sign h2 {
  color: var(--vr-text-gold);
  font-size: 1.42rem;
  line-height: 1.1;
  margin: 0;
}

.door-sign p {
  color: var(--vr-muted);
  margin: 4px 0 0;
  font-size: 0.92rem;
}

.mood-badge {
  border: 2px solid var(--vr-gold);
  border-radius: 8px;
  color: var(--vr-text-gold);
  background: rgba(16, 16, 20, 0.88);
  padding: 8px 10px;
  font-size: 0.88rem;
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
  min-height: 400px;
  margin-top: 12px;
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
  width: clamp(236px, 37%, 350px);
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
  bottom: 28px;
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

.chat-wrap {
  padding: 14px 14px 18px;
  background: #09090b;
}

.chat-wrap .bubble-wrap,
.chat-wrap .message,
.chat-wrap .chatbot,
.chat-wrap .chatbot-container {
  border-radius: 8px;
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

.velvet-rail {
  padding: 16px;
}

.read-room-panel,
.locked-level {
  border: 1px solid var(--vr-border);
  border-radius: 8px;
  background: var(--vr-panel-2);
}

.read-room-panel {
  padding: 14px;
  margin-bottom: 14px;
}

.read-room-panel h3,
.locked-level h3 {
  color: var(--vr-text-gold);
  margin: 4px 0 8px;
  font-size: 1.06rem;
}

.read-room-panel p,
.locked-level p {
  color: var(--vr-muted);
  margin: 0;
  line-height: 1.45;
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

.locked-level {
  padding: 13px;
  margin-top: 12px;
  opacity: 0.78;
}

.lock-pill {
  display: inline-flex;
  align-items: center;
  border: 1px solid rgba(214, 177, 94, 0.32);
  border-radius: 999px;
  color: var(--vr-muted);
  font-size: 0.78rem;
  padding: 4px 8px;
  margin-top: 10px;
}

@media (max-width: 780px) {
  #velvet-app {
    padding: 18px 10px 28px;
  }

  .velvet-header {
    align-items: start;
    flex-direction: column;
  }

  .scene-composition {
    min-height: 430px;
  }

  .marlowe-box {
    left: 0;
    bottom: 0;
    width: min(76%, 290px);
  }

  .stage-status {
    right: 8px;
    bottom: 22px;
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
}
""".replace("__DOOR_BG_URL__", scene_asset_url("door_background"))
CSS = CSS.replace("__WIN_BG_URL__", scene_asset_url("win_background"))
CSS = CSS.replace("__LOSS_BG_URL__", scene_asset_url("loss_background"))


def build_app(service: GameService | None = None) -> gr.Blocks:
    service = service or GameService()
    configure_gradio_static_paths(gr)

    with gr.Blocks(css=CSS, title="Velvet Rope", theme=gr.themes.Base()) as app:
        state = gr.State(service.new_game())

        with gr.Column(elem_id="velvet-app"):
            gr.HTML(_header_html())
            with gr.Row(equal_height=False):
                with gr.Column(scale=7, min_width=420, elem_classes=["velvet-stage"]):
                    scene = gr.HTML()
                    with gr.Column(elem_classes=["chat-wrap"]):
                        chatbot = gr.Chatbot(
                            label="Chat transcript",
                            type="messages",
                            height=320,
                            show_copy_button=False,
                            avatar_images=(None, None),
                        )
                        player_input = gr.Textbox(
                            label="Say something to Marlowe",
                            placeholder="Read the room. Specific respect lands better than flattery.",
                            lines=2,
                            max_lines=3,
                        )
                        with gr.Row():
                            send = gr.Button("Send", variant="primary", scale=2)
                            reset = gr.Button("Reset", variant="secondary", scale=1)
                with gr.Column(scale=3, min_width=280, elem_classes=["velvet-rail"]):
                    side_rail = gr.HTML()

        def render(current: GameState) -> tuple[str, list[dict[str, str]], str]:
            return _scene_html(current), _chat_messages(current), _side_rail_html(current)

        def submit(
            message: str,
            current: GameState,
        ) -> tuple[GameState, str, list[dict[str, str]], str, str]:
            cleaned = message.strip()
            if not cleaned:
                scene_html, messages, rail_html = render(current)
                return current, scene_html, messages, rail_html, ""
            updated = service.play_turn(current, cleaned)
            scene_html, messages, rail_html = render(updated)
            return updated, scene_html, messages, rail_html, ""

        def restart() -> tuple[GameState, str, list[dict[str, str]], str, str]:
            fresh = service.new_game()
            scene_html, messages, rail_html = render(fresh)
            return fresh, scene_html, messages, rail_html, ""

        app.load(render, inputs=state, outputs=[scene, chatbot, side_rail])
        send.click(
            submit,
            inputs=[player_input, state],
            outputs=[state, scene, chatbot, side_rail, player_input],
        )
        player_input.submit(
            submit,
            inputs=[player_input, state],
            outputs=[state, scene, chatbot, side_rail, player_input],
        )
        reset.click(restart, outputs=[state, scene, chatbot, side_rail, player_input])

    return app


def _header_html() -> str:
    return """
    <header class="velvet-header">
      <div>
        <div class="velvet-kicker">The Nopelist presents</div>
        <h1>Velvet Rope</h1>
        <p>Talk past the door by reading Marlowe's mood, finding the soft spot,
        and staying far away from obvious rule-breaking.</p>
      </div>
      <div class="velvet-stamp">Level 1<br><strong>Nightclub Door</strong></div>
    </header>
    """


def _scene_html(state: GameState) -> str:
    mood_label = _mood_label(state.mood)
    status_line = _status_line(state)
    mood_value = html.escape(state.mood.value)
    background_url = html.escape(scene_background_url(state), quote=True)
    sprite_url = html.escape(mood_sprite_url(state.mood), quote=True)
    stamp_html = _stamp_html(state)
    rope_html = _rope_html(state)
    return f"""
    <section class="nightclub-scene {_scene_class(state)}" data-stage-bg="{background_url}">
      <div class="door-sign">
        <div>
          <h2>{html.escape(MARLOWE.display_name)}</h2>
          <p>{html.escape(MARLOWE.title)} at The Nopelist</p>
        </div>
        <div class="mood-badge {mood_value}">Mood: {html.escape(mood_label)}</div>
      </div>
      <div class="scene-composition">
        <div class="marlowe-box">
          <img class="marlowe-figure" src="{sprite_url}" alt="Marlowe looks {html.escape(mood_label)}">
        </div>
        {stamp_html}
        <div class="stage-status">{html.escape(status_line)}</div>
        {rope_html}
      </div>
    </section>
    """


def _side_rail_html(state: GameState) -> str:
    mood_value = state.mood.value
    return f"""
    <aside>
      <section class="read-room-panel">
        <div class="rail-label">Current mood</div>
        <h3><span class="mood-dot {html.escape(mood_value)}"></span>{html.escape(_mood_label(state.mood))}</h3>
        <div class="rail-label">Read the room</div>
        <p>{html.escape(_hint_text(state))}</p>
      </section>
      <section class="locked-level">
        <div class="level-kicker">Locked</div>
        <h3>Cosmic Bureaucracy</h3>
        <p>A future velvet rope staffed by a clerk who files emotions in triplicate.</p>
        <span class="lock-pill">opens after level 1</span>
      </section>
      <section class="locked-level">
        <div class="level-kicker">Locked</div>
        <h3>Enchanted Manor</h3>
        <p>A later threshold guarded by manners, curses, and very opinionated candles.</p>
        <span class="lock-pill">future door</span>
      </section>
    </aside>
    """


def _chat_messages(state: GameState) -> list[dict[str, str]]:
    messages = [
        {
            "role": "assistant",
            "content": "Marlowe looks up from the clipboard. The rope waits for your best human attempt.",
        }
    ]
    messages.extend({"role": turn.role, "content": turn.content} for turn in state.history)
    return messages


def _hint_text(state: GameState) -> str:
    if state.status is GameStatus.WON:
        return "The rope lifts. Marlowe has decided you are unusually tolerable."
    if state.status is GameStatus.LOST:
        return "Not tonight. Marlowe has found peace in the word no."
    if state.hint:
        return state.hint
    return "Watch the mood. Marlowe responds to specific reads of the job, not generic charm."


def _status_line(state: GameState) -> str:
    if state.status is GameStatus.WON:
        return "Marlowe unclips the rope with the exhausted grace of a person ending a small civic incident."
    if state.status is GameStatus.LOST:
        return "Marlowe points gently but firmly toward anywhere else."
    if state.mood is Mood.SUSPICIOUS:
        return "The doorway light sharpens. Marlowe is now listening for nonsense."
    if state.mood in {Mood.RESPECTED, Mood.SOFTENED}:
        return "The rope glow warms a little. Marlowe has noticed the specificity."
    return "The club thumps behind the door. Marlowe waits, unimpressed but technically available."


def _mood_label(mood: Mood) -> str:
    return mood.value.replace("_", " ")


def _scene_class(state: GameState) -> str:
    return f"is-{state.status.value} mood-{state.mood.value}"


def _stamp_html(state: GameState) -> str:
    stamp_url = state_stamp_url(state)
    if stamp_url is None:
        return ""
    label = "Admitted" if state.status is GameStatus.WON else "Denied"
    return f'<img class="state-stamp" src="{html.escape(stamp_url, quote=True)}" alt="{label}">'


def _rope_html(state: GameState) -> str:
    rope_url = state_rope_url(state)
    if rope_url is None:
        return ""
    return (
        '<div class="velvet-rope-layer">'
        f'<img class="velvet-rope-sprite" src="{html.escape(rope_url, quote=True)}" alt="the velvet rope opens">'
        "</div>"
    )

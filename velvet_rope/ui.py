from __future__ import annotations

import html

import gradio as gr

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
  padding: 18px;
  background:
    linear-gradient(90deg, rgba(179, 39, 53, 0.12), transparent 24%, transparent 76%, rgba(214, 177, 94, 0.12)),
    linear-gradient(160deg, #120d14 0%, #1f101b 52%, #070708 100%);
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
  border: 1px solid var(--vr-gold);
  border-radius: 8px;
  color: var(--vr-text-gold);
  background: rgba(16, 16, 20, 0.92);
  padding: 8px 10px;
  font-size: 0.88rem;
  font-weight: 800;
  white-space: nowrap;
}

.doorway-frame {
  border: 1px solid rgba(214, 177, 94, 0.44);
  border-radius: 8px;
  background:
    linear-gradient(90deg, rgba(214, 177, 94, 0.1), transparent 18%, transparent 82%, rgba(214, 177, 94, 0.1)),
    #101014;
  min-height: 284px;
  display: grid;
  grid-template-columns: minmax(160px, 0.62fr) minmax(180px, 1fr);
  gap: 18px;
  align-items: end;
  padding: 20px;
}

.marlowe-card {
  border: 1px solid rgba(214, 177, 94, 0.35);
  border-radius: 8px;
  background: linear-gradient(180deg, #191018 0%, #0b0b0d 100%);
  padding: 16px;
  min-height: 226px;
  display: flex;
  flex-direction: column;
  justify-content: end;
}

.marlowe-portrait {
  width: 132px;
  aspect-ratio: 1;
  border-radius: 8px;
  border: 1px solid rgba(214, 177, 94, 0.46);
  background:
    radial-gradient(circle at 50% 28%, #d6b15e 0 11%, transparent 12%),
    radial-gradient(circle at 37% 42%, #f7e4a8 0 3%, transparent 4%),
    radial-gradient(circle at 63% 42%, #f7e4a8 0 3%, transparent 4%),
    linear-gradient(180deg, #301622 0%, #130d14 100%);
  color: var(--vr-text-gold);
  font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace;
  font-size: 1.25rem;
  display: grid;
  place-items: center;
  margin-bottom: 14px;
  box-shadow: 0 0 34px rgba(179, 39, 53, 0.18);
}

.marlowe-name {
  color: var(--vr-text-gold);
  font-size: 1.1rem;
  font-weight: 850;
}

.marlowe-title,
.door-copy,
.stage-status {
  color: var(--vr-muted);
  line-height: 1.45;
}

.door-copy {
  align-self: stretch;
  display: flex;
  flex-direction: column;
  justify-content: end;
  gap: 14px;
}

.club-door {
  min-height: 172px;
  border: 1px solid rgba(214, 177, 94, 0.36);
  border-radius: 8px 8px 4px 4px;
  background:
    linear-gradient(90deg, transparent 48%, rgba(214, 177, 94, 0.35) 49%, rgba(214, 177, 94, 0.35) 51%, transparent 52%),
    radial-gradient(circle at 50% 38%, rgba(227, 66, 79, 0.2), transparent 36%),
    linear-gradient(180deg, #0e0e12 0%, #050506 100%);
}

.stage-status {
  border-left: 3px solid var(--vr-rope);
  padding-left: 12px;
}

.velvet-rope-bar {
  height: 9px;
  border-radius: 999px;
  background: linear-gradient(90deg, #711421, var(--vr-rope-hot), #711421);
  box-shadow: 0 0 22px rgba(227, 66, 79, 0.62);
  margin: 18px 8px 4px;
}

.rope-posts {
  display: flex;
  justify-content: space-between;
  margin: 0 0 8px;
}

.rope-posts span {
  width: 14px;
  height: 42px;
  border-radius: 999px 999px 4px 4px;
  background: linear-gradient(180deg, var(--vr-gold), #694b1c);
  box-shadow: 0 0 16px rgba(214, 177, 94, 0.3);
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

  .doorway-frame {
    grid-template-columns: 1fr;
  }

  .door-sign {
    align-items: start;
    flex-direction: column;
  }
}
"""


def build_app(service: GameService | None = None) -> gr.Blocks:
    service = service or GameService()

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
    portrait = html.escape(_portrait_for(state.mood))
    return f"""
    <section class="nightclub-scene">
      <div class="door-sign">
        <div>
          <h2>{html.escape(MARLOWE.display_name)}</h2>
          <p>{html.escape(MARLOWE.title)} at The Nopelist</p>
        </div>
        <div class="mood-badge">Mood: {html.escape(mood_label)}</div>
      </div>
      <div class="doorway-frame">
        <div class="marlowe-card">
          <div class="marlowe-portrait" aria-label="Marlowe portrait">{portrait}</div>
          <div class="marlowe-name">{html.escape(MARLOWE.display_name)}</div>
          <div class="marlowe-title">Clipboard sovereign. Shoe survivor. Door philosopher.</div>
        </div>
        <div class="door-copy">
          <div class="club-door" aria-hidden="true"></div>
          <div class="stage-status">{html.escape(status_line)}</div>
        </div>
      </div>
      <div class="rope-posts"><span></span><span></span></div>
      <div class="velvet-rope-bar" aria-label="literal velvet rope"></div>
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


def _portrait_for(mood: Mood) -> str:
    portraits = {
        Mood.UNIMPRESSED: "-_-",
        Mood.SUSPICIOUS: "o_O",
        Mood.AMUSED: ":-]",
        Mood.RESPECTED: ":-)",
        Mood.SOFTENED: ":')",
        Mood.LETTING_YOU_IN: ":-D",
        Mood.DONE_WITH_YOU: ">:|",
    }
    return portraits[mood]

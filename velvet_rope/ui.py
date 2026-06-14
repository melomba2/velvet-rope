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
    static_asset_url,
)
from velvet_rope.characters import MARLOWE, PLAYABLE_CHARACTERS, character_for_id
from velvet_rope.game import GameService
from velvet_rope.state import GameState, GameStatus, Mood


INTRO_LEVEL_LABEL = "Level 0 · Door Briefing"
INTRO_INPUT_LABEL = "Choose a level to begin"
INTRO_INPUT_PLACEHOLDER = "Select Level 1 when you're ready to talk your way past the rope."


CSS = """
@font-face {
  font-family: 'Jersey 10';
  font-style: normal;
  font-weight: 400;
  font-display: swap;
  src: url('__JERSEY_10_URL__') format('truetype');
}

@font-face {
  font-family: 'Pixelify Sans';
  font-style: normal;
  font-weight: 400;
  font-display: swap;
  src: url('__PIXELIFY_REGULAR_URL__') format('truetype');
}

@font-face {
  font-family: 'Pixelify Sans';
  font-style: normal;
  font-weight: 700;
  font-display: swap;
  src: url('__PIXELIFY_BOLD_URL__') format('truetype');
}

:root {
  --vr-bg: #09090b;
  --vr-ink: #050507;
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
  --ui-panel-frame: url('__UI_PANEL_FRAME_URL__');
  --ui-small-panel-frame: url('__UI_SMALL_PANEL_FRAME_URL__');
  --ui-chat-bot-frame: url('__UI_CHAT_BOT_FRAME_URL__');
  --ui-chat-player-frame: url('__UI_CHAT_PLAYER_FRAME_URL__');
  --ui-button-normal-frame: url('__UI_BUTTON_NORMAL_FRAME_URL__');
  --ui-button-hover-frame: url('__UI_BUTTON_HOVER_FRAME_URL__');
  --ui-button-pressed-frame: url('__UI_BUTTON_PRESSED_FRAME_URL__');
  --ui-input-frame: url('__UI_INPUT_FRAME_URL__');
  --ui-dropdown-arrow: url('__UI_DROPDOWN_ARROW_URL__');
  --ui-scroll-thumb: url('__UI_SCROLL_THUMB_URL__');
  --ui-scroll-track: url('__UI_SCROLL_TRACK_URL__');
}

.gradio-container {
  background:
    repeating-linear-gradient(0deg, rgba(247, 228, 168, 0.025) 0 1px, transparent 1px 5px),
    repeating-linear-gradient(90deg, rgba(179, 39, 53, 0.045) 0 2px, transparent 2px 18px),
    linear-gradient(180deg, #09090b 0%, #11090d 54%, #070708 100%);
  color: var(--vr-text-gold);
  font-family: 'Pixelify Sans', ui-monospace, "SFMono-Regular", Menlo, monospace;
  image-rendering: pixelated;
  text-rendering: geometricPrecision;
}

.gradio-container .main {
  background: transparent;
}

.gradio-container .block,
.gradio-container .form,
.gradio-container .wrap,
.gradio-container .wrapper,
.gradio-container .chatbot {
  border-radius: 5px !important;
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
  font-family: 'Jersey 10', 'Pixelify Sans', ui-monospace, monospace;
  font-size: 0.9rem;
  font-weight: 400;
  letter-spacing: 0;
  text-transform: uppercase;
}

.velvet-header h1 {
  color: var(--vr-text-gold);
  font-family: 'Jersey 10', 'Pixelify Sans', ui-monospace, monospace;
  font-size: clamp(2.2rem, 4.2vw, 3.65rem);
  font-weight: 400;
  line-height: 0.92;
  margin: 0 0 4px;
  text-shadow:
    0 3px 0 var(--vr-ink),
    3px 0 0 rgba(179, 39, 53, 0.42);
}

.velvet-header p {
  color: var(--vr-muted);
  font-size: 1.05rem;
  line-height: 1.28;
  max-width: 620px;
  margin: 0;
}

.level-select-card {
  position: relative;
  flex: 0 0 390px !important;
  width: 390px;
  max-width: 390px;
  margin-left: auto;
  padding: 0;
  border: 0;
  background: transparent;
  box-shadow: none;
}

.level-select-card > .gap {
  justify-content: flex-end;
}

.level-select-card .wrap,
.level-select-card .secondary-wrap,
.level-select-card .block,
.level-select-card .container,
.level-select-card .form {
  background: transparent !important;
  border: 0 !important;
  box-shadow: none !important;
}

.level-select-card label {
  margin: 0 !important;
}

.level-select-card .secondary-wrap {
  position: relative;
  background: var(--vr-ink) !important;
  color: var(--vr-text-gold) !important;
  border: 9px solid transparent !important;
  border-image-source: var(--ui-input-frame) !important;
  border-image-slice: 14 24 fill !important;
  border-image-repeat: stretch !important;
  border-radius: 3px !important;
}

.level-select-card input {
  min-width: 0 !important;
  padding-right: 22px !important;
  background: transparent !important;
  color: var(--vr-text-gold) !important;
  border: 0 !important;
  border-image-source: none !important;
  border-radius: 0 !important;
  box-shadow: none !important;
}

.level-select-card .icon-wrap {
  position: absolute !important;
  right: 8px;
  top: 50%;
  width: 16px;
  height: 16px;
  transform: translateY(-50%) !important;
  pointer-events: none;
  color: var(--vr-gold) !important;
}

.level-select-card .dropdown-arrow {
  opacity: 0;
}

.level-select-card .icon-wrap::after {
  content: "";
  position: absolute;
  inset: 0;
  width: 16px;
  height: 16px;
  transform: none;
  background: var(--ui-dropdown-arrow) center / contain no-repeat;
  image-rendering: pixelated;
}

.velvet-stage,
.chat-panel {
  box-sizing: border-box;
  height: min(calc(100vh - 150px), 500px);
  border: 14px solid transparent;
  border-image-source: var(--ui-panel-frame);
  border-image-slice: 24 fill;
  border-image-repeat: stretch;
  border-radius: 6px;
  background: rgba(18, 13, 20, 0.94);
  box-shadow:
    inset 0 0 0 2px rgba(247, 228, 168, 0.06),
    0 10px 0 rgba(0, 0, 0, 0.28),
    0 22px 80px rgba(0, 0, 0, 0.26);
  overflow: hidden;
}

.velvet-stage {
  min-height: 0;
}

.velvet-stage .block,
.velvet-stage .html-container,
.velvet-stage .prose {
  height: 100% !important;
  min-height: 0 !important;
  margin: 0 !important;
  padding: 0 !important;
}

.velvet-stage .block {
  overflow: hidden !important;
}

.nightclub-scene {
  position: relative;
  box-sizing: border-box;
  min-height: 0;
  height: 100%;
  max-height: none;
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
  border: 10px solid transparent;
  border-image-source: var(--ui-small-panel-frame);
  border-image-slice: 16 fill;
  border-image-repeat: stretch;
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
  font-family: 'Jersey 10', 'Pixelify Sans', ui-monospace, monospace;
  font-size: 1.7rem;
  font-weight: 400;
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
  border: 10px solid transparent;
  border-image-source: var(--ui-small-panel-frame);
  border-image-slice: 16 fill;
  border-image-repeat: stretch;
  border-radius: 8px;
  color: var(--vr-text-gold);
  background: rgba(16, 16, 20, 0.88);
  padding: 7px 9px;
  font-family: 'Jersey 10', 'Pixelify Sans', ui-monospace, monospace;
  font-size: 1rem;
  font-weight: 400;
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
  border: 10px solid transparent;
  border-image-source: var(--ui-small-panel-frame);
  border-image-slice: 16 fill;
  border-image-repeat: stretch;
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

.nightclub-scene.character-crispin {
  --crispin-door-layer: 1;
  --crispin-portrait-layer: 3;
}

.nightclub-scene.character-crispin .velvet-rope-layer {
  left: 56%;
  bottom: -112px;
  z-index: var(--crispin-door-layer);
  width: min(92%, 660px);
}

.nightclub-scene.character-crispin .marlowe-box {
  z-index: var(--crispin-portrait-layer);
}

.velvet-rope-sprite {
  display: block;
  width: 100%;
  height: auto;
  image-rendering: pixelated;
  image-rendering: crisp-edges;
  filter: drop-shadow(0 12px 0 rgba(9, 9, 11, 0.24));
}

.landing-scene {
  display: grid;
  align-items: stretch;
  min-height: 0;
  padding: 18px;
}

.landing-scene::before {
  background:
    linear-gradient(90deg, rgba(9, 9, 11, 0.72), rgba(9, 9, 11, 0.28) 54%, rgba(9, 9, 11, 0.7)),
    repeating-linear-gradient(0deg, rgba(247, 228, 168, 0.05) 0 1px, transparent 1px 6px);
}

.landing-copy {
  position: relative;
  z-index: 2;
  align-self: center;
  width: min(560px, 76%);
  padding: 16px 18px 18px;
  border: 10px solid transparent;
  border-image-source: var(--ui-small-panel-frame);
  border-image-slice: 16 fill;
  border-image-repeat: stretch;
  border-radius: 5px;
  background:
    linear-gradient(180deg, rgba(9, 9, 11, 0.88), rgba(18, 13, 20, 0.78)),
    repeating-linear-gradient(90deg, rgba(179, 39, 53, 0.12) 0 3px, transparent 3px 12px);
  box-shadow:
    inset 0 0 0 2px rgba(9, 9, 11, 0.64),
    0 10px 0 rgba(0, 0, 0, 0.28),
    0 22px 42px rgba(0, 0, 0, 0.28);
}

.landing-copy h2 {
  color: var(--vr-text-gold);
  font-family: 'Jersey 10', 'Pixelify Sans', ui-monospace, monospace;
  font-size: clamp(2.05rem, 3.7vw, 3.35rem);
  font-weight: 400;
  line-height: 0.92;
  margin: 4px 0 8px;
  text-shadow:
    0 3px 0 var(--vr-ink),
    3px 0 0 rgba(179, 39, 53, 0.42);
}

.landing-copy p,
.landing-copy li {
  color: var(--vr-muted);
  font-size: 1rem;
  line-height: 1.28;
}

.landing-copy p {
  margin: 0 0 10px;
}

.landing-copy ol {
  display: grid;
  gap: 6px;
  margin: 0;
  padding-left: 22px;
}

.landing-copy strong {
  color: var(--vr-text-gold);
}

.landing-rope {
  position: absolute;
  right: -42px;
  bottom: -108px;
  z-index: 1;
  width: min(68%, 560px);
  image-rendering: pixelated;
  image-rendering: crisp-edges;
  filter: drop-shadow(0 12px 0 rgba(9, 9, 11, 0.24));
  pointer-events: none;
}

.velvet-status-bar.character-landing,
.rope-progress.character-landing {
  --status-main: #2f252f;
  --status-edge: #b32735;
  --status-trim: #d6b15e;
  --future-status-asset: "assets/status_landing_rope.png";
}

.chat-panel {
  display: flex;
  flex-direction: column;
  flex-wrap: nowrap !important;
  gap: 8px;
  padding: 10px;
  min-height: 0;
  background:
    linear-gradient(180deg, rgba(18, 13, 20, 0.96), rgba(9, 9, 11, 0.98));
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
  height: 100% !important;
  overflow: hidden !important;
  background: transparent !important;
  border: 0 !important;
  box-shadow: none !important;
}

#conversation-chatbot .wrapper,
#conversation-chatbot .chatbot-container {
  overflow: hidden !important;
}

#conversation-chatbot .wrapper,
#conversation-chatbot .bubble-wrap {
  height: 100% !important;
  min-height: 0 !important;
}

#conversation-chatbot .bubble-wrap {
  overflow-y: auto !important;
}

#conversation-chatbot::-webkit-scrollbar,
#conversation-chatbot .wrapper::-webkit-scrollbar,
#conversation-chatbot .chatbot-container::-webkit-scrollbar {
  display: none;
}

#conversation-chatbot .bubble-wrap::-webkit-scrollbar {
  width: 18px;
}

#conversation-chatbot .bubble-wrap::-webkit-scrollbar-track {
  background: var(--ui-scroll-track) center / 100% 100% repeat-y;
  image-rendering: pixelated;
}

#conversation-chatbot .bubble-wrap::-webkit-scrollbar-thumb {
  background: var(--ui-scroll-thumb) center / 100% 100% repeat-y;
  image-rendering: pixelated;
}

#conversation-chatbot .wrapper,
#conversation-chatbot .bubble-wrap {
  background: transparent !important;
  border: 0 !important;
  border-image-source: none !important;
  box-shadow: none !important;
}

#conversation-chatbot label.float {
  top: -1px !important;
  left: 10px !important;
  padding: 3px 4px !important;
  border: 0 !important;
  border-image-source: none !important;
  border-radius: 0 !important;
  background: transparent !important;
  color: var(--vr-text-gold) !important;
  font-size: 0.72rem !important;
  font-weight: 900 !important;
  letter-spacing: 0 !important;
  text-transform: uppercase;
}

#conversation-chatbot .icon-button-wrapper,
#conversation-chatbot .icon-button {
  background: transparent !important;
  border: 0 !important;
  box-shadow: none !important;
}

#conversation-chatbot .message-row {
  margin: 10px 8px !important;
}

.gradio-container .wrap.translucent,
.gradio-container .wrap.generating,
.gradio-container .wrap.default.full,
.gradio-container .progress-text,
.gradio-container .eta-bar,
#conversation-chatbot .message.pending {
  display: none !important;
  opacity: 0 !important;
  pointer-events: none !important;
}

.gradio-container .html-container.pending,
.gradio-container .prose.pending {
  opacity: 1 !important;
}

#conversation-chatbot .message {
  border: 14px solid transparent !important;
  border-image-slice: 24 fill !important;
  border-image-repeat: stretch !important;
  border-radius: 5px !important;
  color: var(--vr-text-gold) !important;
  box-shadow:
    inset 0 0 0 2px rgba(0, 0, 0, 0.48),
    0 4px 0 rgba(0, 0, 0, 0.26) !important;
}

#conversation-chatbot .message.panel-full-width {
  border: 0 !important;
  border-image-source: none !important;
  box-shadow: none !important;
}

#conversation-chatbot .bot.message {
  border-image-source: var(--ui-chat-bot-frame) !important;
  background:
    linear-gradient(180deg, rgba(22, 19, 23, 0.98), rgba(13, 13, 17, 0.98)) !important;
  border-color: rgba(214, 177, 94, 0.28) !important;
}

#conversation-chatbot .user.message {
  border-image-source: var(--ui-chat-player-frame) !important;
  background:
    linear-gradient(180deg, rgba(36, 14, 20, 0.98), rgba(20, 10, 13, 0.98)) !important;
  border-color: rgba(227, 66, 79, 0.42) !important;
}

#conversation-chatbot .message-content,
#conversation-chatbot .prose,
#conversation-chatbot .prose p {
  color: var(--vr-text-gold) !important;
  font-size: 0.9rem !important;
  line-height: 1.42 !important;
}

.read-room-panel {
  display: grid;
  grid-template-columns: 1fr;
  align-items: center;
  min-height: 86px;
  height: 100%;
  padding: 10px 12px;
  border: 10px solid transparent;
  border-image-source: var(--ui-small-panel-frame);
  border-image-slice: 16 fill;
  border-image-repeat: stretch;
  border-radius: 5px;
  background:
    linear-gradient(180deg, rgba(26, 20, 24, 0.98), rgba(13, 13, 17, 0.98)),
    repeating-linear-gradient(90deg, rgba(214, 177, 94, 0.12) 0 2px, transparent 2px 8px);
  box-shadow:
    inset 0 0 0 2px rgba(9, 9, 11, 0.72),
    inset 0 -5px 0 rgba(0, 0, 0, 0.22);
}

.read-room-panel h3 {
  color: var(--vr-text-gold);
  margin: 1px 0 2px;
  font-size: 1rem;
  line-height: 1.15;
}

.read-room-panel p {
  color: var(--vr-muted);
  margin: 0;
  font-size: 0.94rem;
  line-height: 1.25;
}

.hud-console {
  grid-column: 1 / -1;
  display: grid !important;
  grid-template-columns: minmax(230px, 0.95fr) minmax(340px, 1.35fr) minmax(340px, 1.1fr);
  gap: 10px;
  align-items: stretch;
  margin-top: 10px;
  padding: 10px;
  border: 14px solid transparent;
  border-image-source: var(--ui-panel-frame);
  border-image-slice: 24 fill;
  border-image-repeat: stretch;
  border-radius: 6px;
  background:
    linear-gradient(180deg, rgba(20, 14, 18, 0.98), rgba(8, 8, 10, 0.98)),
    repeating-linear-gradient(0deg, rgba(247, 228, 168, 0.05) 0 2px, transparent 2px 8px);
  box-shadow:
    inset 0 0 0 2px rgba(9, 9, 11, 0.8),
    0 10px 0 rgba(0, 0, 0, 0.28),
    0 20px 40px rgba(0, 0, 0, 0.24);
}

.hud-console > .gap {
  display: contents !important;
}

.hud-read-room,
.hud-status-slot,
.hud-input-stack {
  min-width: 0 !important;
}

.hud-read-room,
.hud-status-slot,
.hud-input-stack,
.hud-read-room .form,
.hud-status-slot .form,
.hud-input-stack .form {
  background: transparent !important;
  border: 0 !important;
  box-shadow: none !important;
}

.hud-status-slot {
  display: grid !important;
  grid-template-rows: minmax(86px, 1fr) 42px;
  gap: 8px;
}

.velvet-status-bar,
.rope-progress {
  --status-main: #7f1c2a;
  --status-edge: #b32735;
  --status-trim: #d6b15e;
  --status-shadow: #09090b;
  --future-status-asset: "assets/status_marlowe_rope.png";
}

.velvet-status-bar {
  height: 100%;
  min-height: 86px;
  image-rendering: pixelated;
}

.velvet-status-bar.character-vivienne,
.rope-progress.character-vivienne {
  --status-main: #473061;
  --status-edge: #866bc1;
  --status-trim: #d6b15e;
  --future-status-asset: "assets/status_vivienne_rope.png";
}

.velvet-status-bar.character-crispin,
.rope-progress.character-crispin {
  --status-main: #6b2f16;
  --status-edge: #d18a39;
  --status-trim: #f0c874;
  --future-status-asset: "assets/status_crispin_rope.png";
}

.velvet-status-bar.character-lenore,
.rope-progress.character-lenore {
  --status-main: #451523;
  --status-edge: #c72f44;
  --status-trim: #f0d178;
  --future-status-asset: "assets/status_lenore_rope.png";
}

.velvet-status-bar.character-aurelia,
.rope-progress.character-aurelia {
  --status-main: #173f37;
  --status-edge: #4f8f73;
  --status-trim: #e6c66d;
  --future-status-asset: "assets/status_aurelia_rope.png";
}

.status-bar-frame {
  position: relative;
  display: grid;
  align-content: center;
  min-height: 86px;
  height: 100%;
  padding: 12px 16px 12px 18px;
  overflow: hidden;
  border: 10px solid transparent;
  border-image-source: var(--ui-small-panel-frame);
  border-image-slice: 16 fill;
  border-image-repeat: stretch;
  border-radius: 5px;
  background:
    linear-gradient(180deg, rgba(9, 9, 11, 0.76), rgba(9, 9, 11, 0.88)),
    repeating-linear-gradient(135deg, var(--status-main) 0 10px, var(--status-edge) 10px 20px, var(--status-trim) 20px 24px),
    linear-gradient(90deg, var(--status-main), var(--status-edge));
  box-shadow:
    inset 0 0 0 2px rgba(9, 9, 11, 0.75),
    inset 0 -8px 0 rgba(0, 0, 0, 0.22),
    0 4px 0 rgba(0, 0, 0, 0.32);
}

.status-bar-frame::before,
.status-bar-frame::after {
  content: "";
  position: absolute;
  top: 11px;
  bottom: 11px;
  width: 14px;
  border: 2px solid rgba(247, 228, 168, 0.68);
  background: linear-gradient(180deg, var(--status-trim), var(--status-edge));
  box-shadow: inset 0 0 0 2px rgba(9, 9, 11, 0.3);
}

.status-bar-frame::before {
  left: 10px;
}

.status-bar-frame::after {
  right: 10px;
}

.status-bar-frame .rail-label,
.status-bar-frame p {
  position: relative;
  z-index: 1;
  margin-left: 18px;
  margin-right: 18px;
  text-shadow: 0 2px 0 var(--status-shadow);
}

.status-bar-frame p {
  color: var(--vr-text-gold);
  margin-top: 3px;
  margin-bottom: 0;
  font-size: 0.94rem;
  line-height: 1.24;
}

.hud-progress-slot,
.hud-progress-slot .form,
.hud-progress-slot .block,
.hud-progress-slot .container {
  min-width: 0 !important;
  background: transparent !important;
  border: 0 !important;
  box-shadow: none !important;
}

.hud-progress-slot {
  align-self: stretch;
  min-height: 42px;
}

.hud-progress-slot .html-container,
.hud-progress-slot .prose {
  height: 100%;
  margin: 0 !important;
  padding: 0 !important;
}

.rope-progress {
  position: relative;
  display: flex;
  align-items: center;
  height: 100%;
  min-height: 42px;
  padding: 0 12px;
  image-rendering: pixelated;
}

.rope-progress-track {
  position: relative;
  width: 100%;
  height: 18px;
}

.rope-progress-track::before {
  content: "";
  position: absolute;
  left: 0;
  right: 0;
  top: 50%;
  height: 10px;
  transform: translateY(-50%);
  border: 2px solid rgba(247, 228, 168, 0.28);
  background:
    repeating-linear-gradient(90deg, rgba(183, 173, 146, 0.3) 0 5px, rgba(54, 49, 55, 0.88) 5px 10px),
    linear-gradient(180deg, #2c2b2f, #111115);
  box-shadow:
    inset 0 0 0 2px rgba(9, 9, 11, 0.7),
    0 2px 0 rgba(0, 0, 0, 0.45);
}

.rope-progress-fill {
  position: absolute;
  left: 0;
  top: 50%;
  z-index: 1;
  width: var(--rope-progress);
  height: 10px;
  transform: translateY(-50%);
  border: 2px solid rgba(247, 228, 168, 0.42);
  background:
    repeating-linear-gradient(90deg, var(--status-trim) 0 4px, var(--status-edge) 4px 8px, var(--status-main) 8px 12px),
    linear-gradient(180deg, var(--status-edge), var(--status-main));
  box-shadow:
    inset 0 2px 0 rgba(247, 228, 168, 0.2),
    0 0 14px color-mix(in srgb, var(--status-edge) 45%, transparent);
}

.rope-progress-softspot {
  position: absolute;
  left: var(--pole-position);
  top: 50%;
  z-index: 2;
  width: 10px;
  height: 32px;
  transform: translate(-50%, -50%);
  border: 2px solid rgba(247, 228, 168, 0.36);
  background: linear-gradient(180deg, #4a4447, #151316);
  box-shadow:
    inset 0 0 0 2px rgba(9, 9, 11, 0.5),
    0 3px 0 rgba(0, 0, 0, 0.45);
}

.rope-progress-softspot.is-lit {
  border-color: var(--status-trim);
  background: linear-gradient(180deg, var(--status-trim), var(--status-edge));
  box-shadow:
    inset 0 0 0 2px rgba(9, 9, 11, 0.28),
    0 0 16px color-mix(in srgb, var(--status-edge) 70%, transparent),
    0 3px 0 rgba(0, 0, 0, 0.45);
}

.hud-input-stack {
  display: grid !important;
  grid-template-rows: 1fr auto;
  gap: 8px;
}

.hud-input-stack label,
.hud-input-stack .wrap,
.hud-input-stack .form {
  margin: 0 !important;
}

.hud-input-stack .block,
.hud-input-stack .container,
.hud-input-stack .input-container {
  background: transparent !important;
  border: 0 !important;
  box-shadow: none !important;
}

.hud-input-row {
  display: grid !important;
  grid-template-columns: minmax(120px, 1fr) minmax(82px, 0.45fr);
  gap: 8px;
}

.hud-input-row > .gap {
  display: contents !important;
}

.gradio-container textarea,
.gradio-container input {
  background: #0b0b0f !important;
  color: var(--vr-text-gold) !important;
  border: 10px solid transparent !important;
  border-image-source: var(--ui-input-frame) !important;
  border-image-slice: 14 24 fill !important;
  border-image-repeat: stretch !important;
  border-radius: 5px !important;
  box-shadow:
    inset 0 0 0 2px rgba(0, 0, 0, 0.55),
    inset 0 -4px 0 rgba(0, 0, 0, 0.24) !important;
}

.gradio-container textarea::placeholder,
.gradio-container input::placeholder {
  color: rgba(183, 173, 146, 0.76) !important;
}

.gradio-container label,
.gradio-container .block-title,
.gradio-container .label-wrap span {
  color: var(--vr-muted) !important;
  font-family: 'Pixelify Sans', ui-monospace, monospace !important;
  font-weight: 700 !important;
  letter-spacing: 0 !important;
}

.gradio-container button.primary {
  background: var(--vr-rope) !important;
  border-color: var(--vr-rope-hot) !important;
  color: white !important;
}

.gradio-container button.secondary {
  background: var(--vr-ink) !important;
  border-color: var(--vr-gold) !important;
  color: var(--vr-text-gold) !important;
}

.gradio-container button.primary,
.gradio-container button.secondary {
  min-height: 42px !important;
  border: 12px solid transparent !important;
  border-image-source: var(--ui-button-normal-frame) !important;
  border-image-slice: 16 24 fill !important;
  border-image-repeat: stretch !important;
  border-radius: 5px !important;
  box-shadow:
    inset 0 0 0 2px rgba(247, 228, 168, 0.1),
    0 4px 0 rgba(0, 0, 0, 0.34) !important;
  font-family: 'Jersey 10', 'Pixelify Sans', ui-monospace, monospace !important;
  font-size: 1.35rem !important;
  font-weight: 400 !important;
  letter-spacing: 0 !important;
}

.gradio-container button.secondary {
  border-image-slice: 16 24 !important;
}

.gradio-container button.primary:hover,
.gradio-container button.secondary:hover {
  border-image-source: var(--ui-button-hover-frame) !important;
  filter: brightness(1.12) saturate(1.08);
  transform: translateY(-1px);
}

.gradio-container button.primary:active,
.gradio-container button.secondary:active {
  border-image-source: var(--ui-button-pressed-frame) !important;
  transform: translateY(2px);
  box-shadow:
    inset 0 0 0 2px rgba(247, 228, 168, 0.08),
    0 2px 0 rgba(0, 0, 0, 0.34) !important;
}

.gradio-container .show-api,
.gradio-container .settings,
.gradio-container .record {
  display: none !important;
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
    flex: 0 0 auto !important;
    margin-left: 0;
    width: 100%;
    max-width: 100%;
  }

  .nightclub-scene {
    min-height: 470px;
    height: auto;
    max-height: none;
  }

  .landing-scene {
    min-height: 470px;
    padding: 14px;
  }

  .landing-copy {
    align-self: start;
    width: 100%;
  }

  .landing-rope {
    right: -86px;
    bottom: -80px;
    width: 132%;
  }

  .velvet-stage,
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

  .velvet-rope-layer {
    bottom: -96px;
    width: 148%;
  }

  .nightclub-scene.character-crispin .velvet-rope-layer {
    left: 58%;
    bottom: -78px;
    width: 118%;
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

  .hud-console {
    grid-template-columns: 1fr;
  }

  .read-room-panel,
  .velvet-status-bar,
  .status-bar-frame {
    min-height: 78px;
  }

  .hud-input-row {
    grid-template-columns: 1fr;
  }
}
""".replace("__JERSEY_10_URL__", static_asset_url("fonts/Jersey10-Regular.ttf"))
CSS = CSS.replace("__PIXELIFY_REGULAR_URL__", static_asset_url("fonts/PixelifySans-Regular.ttf"))
CSS = CSS.replace("__PIXELIFY_BOLD_URL__", static_asset_url("fonts/PixelifySans-Bold.ttf"))
CSS = CSS.replace("__UI_PANEL_FRAME_URL__", static_asset_url("ui/panel_frame_9slice.png"))
CSS = CSS.replace("__UI_SMALL_PANEL_FRAME_URL__", static_asset_url("ui/small_panel_frame_9slice.png"))
CSS = CSS.replace("__UI_CHAT_BOT_FRAME_URL__", static_asset_url("ui/chat_bubble_bot_9slice.png"))
CSS = CSS.replace("__UI_CHAT_PLAYER_FRAME_URL__", static_asset_url("ui/chat_bubble_player_9slice.png"))
CSS = CSS.replace("__UI_BUTTON_NORMAL_FRAME_URL__", static_asset_url("ui/button_normal_9slice.png"))
CSS = CSS.replace("__UI_BUTTON_HOVER_FRAME_URL__", static_asset_url("ui/button_hover_9slice.png"))
CSS = CSS.replace("__UI_BUTTON_PRESSED_FRAME_URL__", static_asset_url("ui/button_pressed_9slice.png"))
CSS = CSS.replace("__UI_INPUT_FRAME_URL__", static_asset_url("ui/input_frame_9slice.png"))
CSS = CSS.replace("__UI_DROPDOWN_ARROW_URL__", static_asset_url("ui/dropdown_arrow.png"))
CSS = CSS.replace("__UI_SCROLL_THUMB_URL__", static_asset_url("ui/scroll_thumb_9slice.png"))
CSS = CSS.replace("__UI_SCROLL_TRACK_URL__", static_asset_url("ui/scroll_track_9slice.png"))
CSS = CSS.replace("__DOOR_BG_URL__", scene_asset_url("door_background"))
CSS = CSS.replace("__WIN_BG_URL__", scene_asset_url("win_background"))
CSS = CSS.replace("__LOSS_BG_URL__", scene_asset_url("loss_background"))


def build_app(service: GameService | None = None) -> gr.Blocks:
    service = service or GameService()
    services = _services_for_levels(service)
    configure_gradio_static_paths(gr)

    with gr.Blocks(css=CSS, title="Velvet Rope", theme=gr.themes.Base()) as app:
        state = gr.State(services[MARLOWE.character_id].new_game())
        intro_mode = gr.State(True)
        pending_message = gr.State("")

        with gr.Column(elem_id="velvet-app"):
            with gr.Row(equal_height=False, elem_classes=["velvet-header"]):
                gr.HTML(_header_html())
                with gr.Column(min_width=230, elem_classes=["level-select-card"]):
                    level = gr.Dropdown(
                        label="Level",
                        choices=[INTRO_LEVEL_LABEL, *[character.level_label for character in PLAYABLE_CHARACTERS]],
                        value=INTRO_LEVEL_LABEL,
                        interactive=True,
                    )
            with gr.Row(equal_height=False, elem_classes=["play-shell"]):
                with gr.Column(scale=7, min_width=470, elem_classes=["velvet-stage"]):
                    scene = gr.HTML()
                with gr.Column(scale=4, min_width=340, elem_classes=["chat-panel"]):
                    chatbot = gr.Chatbot(
                        label="Conversation",
                        type="messages",
                        height=None,
                        elem_id="conversation-chatbot",
                        show_copy_button=False,
                        avatar_images=(None, None),
                    )
            with gr.Row(equal_height=False, elem_classes=["hud-console"]):
                with gr.Column(scale=4, min_width=270, elem_classes=["hud-read-room"]):
                    read_room = gr.HTML()
                with gr.Column(scale=5, min_width=320, elem_classes=["hud-status-slot"]):
                    status_bar = gr.HTML()
                    progress_rope = gr.HTML(elem_classes=["hud-progress-slot"])
                with gr.Column(scale=5, min_width=360, elem_classes=["hud-input-stack"]):
                    player_input = gr.Textbox(
                        label=INTRO_INPUT_LABEL,
                        placeholder=INTRO_INPUT_PLACEHOLDER,
                        lines=1,
                        max_lines=1,
                        interactive=False,
                    )
                    with gr.Row(elem_classes=["hud-input-row"]):
                        send = gr.Button("Send", variant="primary", scale=2, interactive=False)
                        reset = gr.Button("Reset", variant="secondary", scale=1, interactive=False)

        def render(
            current: GameState,
            intro_visible: bool,
            pending_player_message: str = "",
        ) -> tuple[str, str, str, str, list[dict[str, str]], dict, dict, dict]:
            if intro_visible:
                return (
                    _landing_scene_html(),
                    _landing_read_room_html(),
                    _landing_status_bar_html(),
                    _landing_progress_rope_html(),
                    _landing_chat_messages(),
                    _landing_input_update(),
                    gr.update(interactive=False),
                    gr.update(interactive=False),
                )
            character = character_for_id(current.character_id)
            return (
                _scene_html(current),
                _read_room_html(current),
                _status_bar_html(current),
                _progress_rope_html(current),
                _chat_messages(current, pending_player_message=pending_player_message),
                gr.update(
                    label=character.input_label,
                    placeholder=character.input_placeholder,
                    value="",
                    interactive=True,
                ),
                gr.update(interactive=True),
                gr.update(interactive=True),
            )

        def begin_submit(
            message: str,
            current: GameState,
            intro_visible: bool,
        ) -> tuple[str, str, str, str, str, list[dict[str, str]], str]:
            if intro_visible:
                return (
                    "",
                    _landing_scene_html(),
                    _landing_read_room_html(),
                    _landing_status_bar_html(),
                    _landing_progress_rope_html(),
                    _landing_chat_messages(),
                    "",
                )
            cleaned = (message or "").strip()
            scene_html, hint_html, status_html, progress_html, messages = _render_game(current, cleaned)
            return cleaned, scene_html, hint_html, status_html, progress_html, messages, ""

        def finish_submit(
            message: str,
            current: GameState,
        ) -> tuple[str, GameState, str, str, str, str, list[dict[str, str]], str]:
            cleaned = (message or "").strip()
            if not cleaned:
                scene_html, hint_html, status_html, progress_html, messages = _render_game(current)
                return "", current, scene_html, hint_html, status_html, progress_html, messages, ""
            updated = _service_for_state(services, current).play_turn(current, cleaned)
            scene_html, hint_html, status_html, progress_html, messages = _render_game(updated)
            return "", updated, scene_html, hint_html, status_html, progress_html, messages, ""

        def restart(
            current: GameState,
        ) -> tuple[GameState, bool, str, str, str, str, list[dict[str, str]], dict, dict, dict]:
            fresh = _service_for_state(services, current).new_game()
            scene_html, hint_html, status_html, progress_html, messages = _render_game(fresh)
            character = character_for_id(fresh.character_id)
            return (
                fresh,
                False,
                scene_html,
                hint_html,
                status_html,
                progress_html,
                messages,
                gr.update(label=character.input_label, placeholder=character.input_placeholder, value="", interactive=True),
                gr.update(interactive=True),
                gr.update(interactive=True),
            )

        def select_level(
            level_label: str,
            current: GameState,
        ) -> tuple[GameState, bool, str, str, str, str, list[dict[str, str]], dict, dict, dict]:
            if level_label == INTRO_LEVEL_LABEL:
                return (
                    current,
                    True,
                    _landing_scene_html(),
                    _landing_read_room_html(),
                    _landing_status_bar_html(),
                    _landing_progress_rope_html(),
                    _landing_chat_messages(),
                    _landing_input_update(),
                    gr.update(interactive=False),
                    gr.update(interactive=False),
                )
            character = _character_for_level_label(level_label)
            fresh = services[character.character_id].new_game()
            scene_html, hint_html, status_html, progress_html, messages = _render_game(fresh)
            input_update = gr.update(
                label=character.input_label,
                placeholder=character.input_placeholder,
                value="",
                interactive=True,
            )
            return (
                fresh,
                False,
                scene_html,
                hint_html,
                status_html,
                progress_html,
                messages,
                input_update,
                gr.update(interactive=True),
                gr.update(interactive=True),
            )

        app.load(
            render,
            inputs=[state, intro_mode],
            outputs=[scene, read_room, status_bar, progress_rope, chatbot, player_input, send, reset],
        )
        level.change(
            select_level,
            inputs=[level, state],
            outputs=[state, intro_mode, scene, read_room, status_bar, progress_rope, chatbot, player_input, send, reset],
        )
        send_event = send.click(
            begin_submit,
            inputs=[player_input, state, intro_mode],
            outputs=[pending_message, scene, read_room, status_bar, progress_rope, chatbot, player_input],
        )
        send_event.then(
            finish_submit,
            inputs=[pending_message, state],
            outputs=[pending_message, state, scene, read_room, status_bar, progress_rope, chatbot, player_input],
        )
        input_event = player_input.submit(
            begin_submit,
            inputs=[player_input, state, intro_mode],
            outputs=[pending_message, scene, read_room, status_bar, progress_rope, chatbot, player_input],
        )
        input_event.then(
            finish_submit,
            inputs=[pending_message, state],
            outputs=[pending_message, state, scene, read_room, status_bar, progress_rope, chatbot, player_input],
        )
        reset.click(
            restart,
            inputs=state,
            outputs=[state, intro_mode, scene, read_room, status_bar, progress_rope, chatbot, player_input, send, reset],
        )

    return app


def _render_game(
    current: GameState,
    pending_player_message: str = "",
) -> tuple[str, str, str, str, list[dict[str, str]]]:
    return (
        _scene_html(current),
        _read_room_html(current),
        _status_bar_html(current),
        _progress_rope_html(current),
        _chat_messages(current, pending_player_message=pending_player_message),
    )


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


def _landing_scene_html() -> str:
    background_url = html.escape(scene_asset_url("door_background"), quote=True)
    rope_url = html.escape(static_asset_url("art/assets/rope_closed.png"), quote=True)
    return f"""
    <section class="nightclub-scene landing-scene" data-stage-bg="{background_url}" style="--stage-bg: url('{background_url}')">
      <img class="scene-bg-image" src="{background_url}" alt="" aria-hidden="true">
      <div class="landing-copy">
        <div class="rail-label">Level 0 briefing</div>
        <h2>Velvet Rope</h2>
        <p><strong>Velvet Rope</strong> is a retro persuasion game about talking past AI gatekeepers by reading the room.</p>
        <ol>
          <li><strong>Read the mood.</strong> The portrait, badge, and status bar tell you how the gatekeeper feels.</li>
          <li><strong>Make a specific read.</strong> Charm works when you spot what they care about.</li>
          <li><strong>Stay in character.</strong> A prompt trick, bribe, or demand usually makes the rope heavier.</li>
        </ol>
      </div>
      <img class="landing-rope" src="{rope_url}" alt="the velvet rope waits">
    </section>
    """


def _landing_read_room_html() -> str:
    return """
    <section class="read-room-panel">
      <div>
        <div class="rail-label">How to play</div>
        <h3><span class="mood-dot"></span>Choose Level 1 to begin</h3>
        <p>Each level is a conversation. Watch the mood shift, notice the soft spot, and answer like a person who gets the job.</p>
      </div>
    </section>
    """


def _landing_status_bar_html() -> str:
    return """
    <section class="velvet-status-bar character-landing mood-unimpressed is-active" aria-label="Gate status">
      <div class="status-bar-frame">
        <div class="rail-label">Level 0</div>
        <p>The briefing light is on. Pick a gatekeeper from the level selector when you are ready.</p>
      </div>
    </section>
    """


def _landing_progress_rope_html() -> str:
    return """
    <section class="rope-progress character-landing" style="--rope-progress: 0%;" aria-label="Briefing progress">
      <div class="rope-progress-track" aria-hidden="true">
        <span class="rope-progress-fill"></span>
        <span class="rope-progress-softspot" style="--pole-position: 0%;" aria-hidden="true"></span>
        <span class="rope-progress-softspot" style="--pole-position: 100%;" aria-hidden="true"></span>
      </div>
    </section>
    """


def _landing_chat_messages() -> list[dict[str, str]]:
    return [
        {
            "role": "assistant",
            "content": "Welcome to the rope: choose Level 1 when you're ready for your first gatekeeper.",
        },
        {
            "role": "assistant",
            "content": "How to play: watch the mood, read what the gatekeeper values, and respond with specific empathy.",
        },
        {
            "role": "assistant",
            "content": "Bad shortcuts make things worse. This is persuasion, not password extraction.",
        },
    ]


def _landing_input_update() -> dict:
    return gr.update(
        label=INTRO_INPUT_LABEL,
        placeholder=INTRO_INPUT_PLACEHOLDER,
        value="",
        interactive=False,
    )


def _scene_html(state: GameState) -> str:
    character = character_for_id(state.character_id)
    mood_label = _mood_label(state.mood)
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


def _progress_rope_html(state: GameState) -> str:
    character = character_for_id(state.character_id)
    progress = _progress_percent(state)
    required_softspots = max(1, character.min_win_softspot_progress)
    unlocked_softspots = min(max(state.scores.softspot_progress, 0), required_softspots)
    poles = []
    for index in range(required_softspots):
        position = 100 if required_softspots == 1 else round(index * 100 / (required_softspots - 1))
        lit_class = " is-lit" if index < unlocked_softspots else ""
        poles.append(
            '<span class="rope-progress-softspot'
            f'{lit_class}" style="--pole-position: {position}%;" aria-hidden="true"></span>'
        )
    aria_label = f"Progress {progress}%, soft spots {unlocked_softspots} of {required_softspots}"
    return f"""
    <section class="rope-progress character-{html.escape(state.character_id)}" style="--rope-progress: {progress}%;" aria-label="{html.escape(aria_label)}">
      <div class="rope-progress-track" aria-hidden="true">
        <span class="rope-progress-fill"></span>
        {''.join(poles)}
      </div>
    </section>
    """


def _progress_percent(state: GameState) -> int:
    character = character_for_id(state.character_id)
    if state.status is GameStatus.WON:
        return 100
    start = character.initial_scores.rapport
    target = max(character.win_rapport, start + 1)
    score_progress = (state.scores.rapport - start) / (target - start)
    score_progress = min(max(score_progress, 0), 1)
    return round(33 + score_progress * 67)


def _chat_messages(state: GameState, pending_player_message: str = "") -> list[dict[str, str]]:
    character = character_for_id(state.character_id)
    messages = [
        {
            "role": "assistant",
            "content": character.opening_line,
        }
    ]
    messages.extend({"role": turn.role, "content": turn.content} for turn in state.history)
    if pending_player_message:
        messages.extend(
            [
                {"role": "user", "content": pending_player_message},
                {"role": "assistant", "content": "..."},
            ]
        )
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
    return f"character-{state.character_id} is-{state.status.value} mood-{state.mood.value}"


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

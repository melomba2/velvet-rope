from dataclasses import replace

from velvet_rope.art import (
    ART_ROOT,
    STATIC_ROOT,
    manifest_asset_paths,
    mood_sprite_url,
    scene_background_url,
    static_asset_url,
    state_rope_url,
    state_stamp_url,
)
from velvet_rope.characters import CRISPIN, LENORE, MARLOWE, PLAYABLE_CHARACTERS, VIVIENNE, character_for_id
from velvet_rope.state import GameStatus, Mood, new_game_state
from velvet_rope.ui import CSS, _header_html, _read_room_html, _scene_html, _status_bar_html


def test_manifest_assets_are_local_to_runtime_art_root():
    paths = manifest_asset_paths()

    assert paths
    assert all(path.is_file() for path in paths)
    assert all(path.is_relative_to(ART_ROOT) for path in paths)


def test_local_font_assets_are_served_from_static_root():
    font_paths = [
        STATIC_ROOT / "fonts" / "Jersey10-Regular.ttf",
        STATIC_ROOT / "fonts" / "PixelifySans-Regular.ttf",
        STATIC_ROOT / "fonts" / "PixelifySans-Bold.ttf",
    ]

    assert all(path.is_file() for path in font_paths)
    assert "velvet_rope/static/fonts/Jersey10-Regular.ttf" in static_asset_url("fonts/Jersey10-Regular.ttf")
    assert "velvet_rope/static/fonts/PixelifySans-Regular.ttf" in static_asset_url("fonts/PixelifySans-Regular.ttf")
    assert "velvet_rope/static/fonts/PixelifySans-Bold.ttf" in static_asset_url("fonts/PixelifySans-Bold.ttf")


def test_local_ui_frame_assets_are_served_from_static_root():
    ui_asset_names = [
        "panel_frame_9slice.png",
        "small_panel_frame_9slice.png",
        "chat_bubble_bot_9slice.png",
        "chat_bubble_player_9slice.png",
        "button_normal_9slice.png",
        "button_hover_9slice.png",
        "button_pressed_9slice.png",
        "input_frame_9slice.png",
        "dropdown_arrow.png",
        "scroll_thumb_9slice.png",
        "scroll_track_9slice.png",
    ]

    assert all((STATIC_ROOT / "ui" / name).is_file() for name in ui_asset_names)
    for name in ui_asset_names:
        assert f"velvet_rope/static/ui/{name}" in static_asset_url(f"ui/{name}")


def test_each_mood_maps_to_curated_marlowe_sprite_url():
    for mood in Mood:
        url = mood_sprite_url(mood)

        assert url.startswith("/gradio_api/file=")
        assert f"marlowe_{mood.value}.png" in url
        assert "art/comfyui" not in url


def test_each_mood_maps_to_curated_vivienne_sprite_url():
    for mood in Mood:
        url = mood_sprite_url(mood, VIVIENNE.character_id)

        assert url.startswith("/gradio_api/file=")
        assert f"vivienne_{mood.value}.png" in url
        assert "art/comfyui" not in url


def test_each_mood_maps_to_curated_crispin_sprite_url():
    for mood in Mood:
        url = mood_sprite_url(mood, CRISPIN.character_id)

        assert url.startswith("/gradio_api/file=")
        assert f"crispin_{mood.value}.png" in url
        assert "art/comfyui" not in url


def test_each_mood_maps_to_curated_lenore_sprite_url():
    for mood in Mood:
        url = mood_sprite_url(mood, LENORE.character_id)

        assert url.startswith("/gradio_api/file=")
        assert f"lenore_{mood.value}.png" in url
        assert "art/comfyui" not in url


def test_each_mood_maps_to_curated_aurelia_sprite_url():
    aurelia = character_for_id("aurelia")

    for mood in Mood:
        url = mood_sprite_url(mood, aurelia.character_id)

        assert url.startswith("/gradio_api/file=")
        assert f"aurelia_{mood.value}.png" in url
        assert "art/comfyui" not in url


def test_level_three_scene_uses_hollow_tree_assets_and_crispin_copy():
    game_state = replace(
        new_game_state(CRISPIN),
        mood=Mood.RESPECTED,
    )
    scene = _scene_html(game_state)
    hint = _read_room_html(game_state)

    assert CRISPIN in PLAYABLE_CHARACTERS
    assert scene_background_url(game_state) in scene
    assert mood_sprite_url(Mood.RESPECTED, CRISPIN.character_id) in scene
    assert "hollow_tree_factory_bg.png" in scene
    assert "crispin_respected.png" in scene
    assert "Crispin Crumbwell" in scene
    assert "Hollow Tree Cookie Works" in scene
    assert "Crispin warms to careful factory reads" in hint


def test_level_four_scene_uses_stage_door_assets_and_lenore_copy():
    game_state = replace(
        new_game_state(LENORE),
        mood=Mood.RESPECTED,
    )
    scene = _scene_html(game_state)
    hint = _read_room_html(game_state)

    assert LENORE in PLAYABLE_CHARACTERS
    assert scene_background_url(game_state) in scene
    assert mood_sprite_url(Mood.RESPECTED, LENORE.character_id) in scene
    assert "stage_door_bg.png" in scene
    assert "lenore_respected.png" in scene
    assert "Lenore Cue" in scene
    assert "The Last Curtain" in scene
    assert "Lenore warms to haunted stagecraft" in hint


def test_level_five_scene_uses_grand_threshold_assets_and_aurelia_copy():
    aurelia = character_for_id("aurelia")
    game_state = replace(
        new_game_state(aurelia),
        mood=Mood.RESPECTED,
    )
    scene = _scene_html(game_state)
    hint = _read_room_html(game_state)

    assert aurelia in PLAYABLE_CHARACTERS
    assert scene_background_url(game_state) in scene
    assert mood_sprite_url(Mood.RESPECTED, aurelia.character_id) in scene
    assert "grand_threshold_bg.png" in scene
    assert "aurelia_respected.png" in scene
    assert "Aurelia Vane" in scene
    assert "The Grand Threshold" in scene
    assert "Aurelia warms to hospitality" in hint


def test_scene_uses_curated_assets_for_active_mood():
    game_state = replace(
        new_game_state(MARLOWE),
        mood=Mood.SUSPICIOUS,
    )
    scene = _scene_html(game_state)

    assert scene_background_url(game_state) in scene
    assert mood_sprite_url(Mood.SUSPICIOUS) in scene
    assert "marlowe_suspicious.png" in scene
    assert "velvet-rope-layer" not in scene
    assert "rope_" not in scene
    assert "marlowe-portrait" not in scene
    assert "-_-" not in scene


def test_level_two_scene_uses_cosmic_assets_and_vivienne_copy():
    game_state = replace(
        new_game_state(VIVIENNE),
        mood=Mood.RESPECTED,
    )
    scene = _scene_html(game_state)
    hint = _read_room_html(game_state)

    assert scene_background_url(game_state) in scene
    assert mood_sprite_url(Mood.RESPECTED, VIVIENNE.character_id) in scene
    assert "cosmic_bureaucracy_bg.png" in scene
    assert "vivienne_respected.png" in scene
    assert "Vivienne Quill" in scene
    assert "Somnolent Bureau" in scene
    assert "Vivienne warms to tidy dream-placement process" in hint


def test_scene_uses_win_assets_and_admitted_stamp():
    game_state = replace(
        new_game_state(MARLOWE),
        mood=Mood.LETTING_YOU_IN,
        status=GameStatus.WON,
    )
    scene = _scene_html(game_state)

    assert scene_background_url(game_state) in scene
    assert state_stamp_url(game_state) in scene
    assert "state_win_bg.png" in scene
    assert "velvet-rope-layer" in scene
    assert "rope_open_anim.gif" in scene
    assert "stamp_admitted.png" in scene


def test_level_two_win_uses_cosmic_gate_overlay():
    game_state = replace(
        new_game_state(VIVIENNE),
        mood=Mood.LETTING_YOU_IN,
        status=GameStatus.WON,
    )
    scene = _scene_html(game_state)

    assert state_rope_url(game_state) in scene
    assert state_stamp_url(game_state) in scene
    assert "cosmic_gate_open.png" in scene
    assert "stamp_dream_placed.png" in scene
    assert 'alt="Dream placed"' in scene
    assert 'alt="the dream gate opens"' in scene
    assert "stamp_admitted.png" not in scene
    assert "rope_open_anim.gif" not in scene


def test_level_two_loss_uses_misfiled_stamp():
    game_state = replace(
        new_game_state(VIVIENNE),
        mood=Mood.DONE_WITH_YOU,
        status=GameStatus.LOST,
    )
    scene = _scene_html(game_state)

    assert state_stamp_url(game_state) in scene
    assert "stamp_misfiled.png" in scene
    assert 'alt="Misfiled"' in scene
    assert "stamp_denied.png" not in scene


def test_level_three_win_and_loss_use_cookie_labels():
    won_state = replace(
        new_game_state(CRISPIN),
        mood=Mood.LETTING_YOU_IN,
        status=GameStatus.WON,
    )
    lost_state = replace(
        new_game_state(CRISPIN),
        mood=Mood.DONE_WITH_YOU,
        status=GameStatus.LOST,
    )

    won_scene = _scene_html(won_state)
    lost_scene = _scene_html(lost_state)

    assert "character-crispin" in won_scene
    assert 'alt="Cookie crowned"' in won_scene
    assert 'alt="the knot-door opens"' in won_scene
    assert "hollow_tree_factory_win_bg.png" in won_scene
    assert "tree_knot_door_open.png" in won_scene
    assert "stamp_cookie_crowned.png" in won_scene
    assert 'alt="Crumbled"' in lost_scene
    assert "hollow_tree_factory_loss_bg.png" in lost_scene
    assert "stamp_crumbled.png" in lost_scene
    assert "stamp_admitted.png" not in won_scene
    assert "stamp_denied.png" not in lost_scene


def test_level_four_win_and_loss_use_stage_labels():
    won_state = replace(
        new_game_state(LENORE),
        mood=Mood.LETTING_YOU_IN,
        status=GameStatus.WON,
    )
    lost_state = replace(
        new_game_state(LENORE),
        mood=Mood.DONE_WITH_YOU,
        status=GameStatus.LOST,
    )

    won_scene = _scene_html(won_state)
    lost_scene = _scene_html(lost_state)

    assert 'alt="Places called"' in won_scene
    assert 'alt="the stage door opens"' in won_scene
    assert "stage_door_win_bg.png" in won_scene
    assert "stage_door_open.png" in won_scene
    assert "stamp_places_called.png" in won_scene
    assert 'alt="Blackout"' in lost_scene
    assert "stage_door_loss_bg.png" in lost_scene
    assert "stamp_blackout.png" in lost_scene


def test_level_five_win_and_loss_use_threshold_labels():
    aurelia = character_for_id("aurelia")
    won_state = replace(
        new_game_state(aurelia),
        mood=Mood.LETTING_YOU_IN,
        status=GameStatus.WON,
    )
    lost_state = replace(
        new_game_state(aurelia),
        mood=Mood.DONE_WITH_YOU,
        status=GameStatus.LOST,
    )

    won_scene = _scene_html(won_state)
    lost_scene = _scene_html(lost_state)

    assert 'alt="Invited"' in won_scene
    assert "grand_threshold_win_bg.png" in won_scene
    assert "grand_threshold_open.png" not in won_scene
    assert "velvet-rope-layer" not in won_scene
    assert "stamp_invited.png" in won_scene
    assert 'alt="Uninvited"' in lost_scene
    assert "grand_threshold_loss_bg.png" in lost_scene
    assert "stamp_uninvited.png" in lost_scene


def test_scene_uses_loss_assets_and_denied_stamp():
    game_state = replace(
        new_game_state(MARLOWE),
        mood=Mood.DONE_WITH_YOU,
        status=GameStatus.LOST,
    )
    scene = _scene_html(game_state)

    assert scene_background_url(game_state) in scene
    assert state_stamp_url(game_state) in scene
    assert "state_loss_bg.png" in scene
    assert "velvet-rope-layer" not in scene
    assert "rope_" not in scene
    assert "stamp_denied.png" in scene


def test_scene_uses_single_background_stage_without_nested_visual_boxes():
    game_state = new_game_state(MARLOWE)

    scene = _scene_html(game_state)

    assert "scene-composition" in scene
    assert "marlowe-box" in scene
    assert "marlowe-figure" in scene
    assert "velvet-rope-layer" not in scene
    assert "doorway-frame" not in scene
    assert "marlowe-card" not in scene
    assert "marlowe-sprite-frame" not in scene
    assert "club-door-pixel" not in scene


def test_css_positions_victory_rope_animation_as_foreground_overlay():
    assert ".scene-composition" in CSS
    assert "height: calc(100% - 52px);" in CSS
    assert ".velvet-rope-layer" in CSS
    assert "position: absolute;" in CSS
    assert "bottom: -125px;" in CSS


def test_css_layers_crispin_knot_door_behind_his_portrait():
    assert ".nightclub-scene.character-crispin .velvet-rope-layer" in CSS
    assert ".nightclub-scene.character-crispin .marlowe-box" in CSS
    assert "--crispin-door-layer: 1;" in CSS
    assert "--crispin-portrait-layer: 3;" in CSS


def test_css_places_marlowe_box_in_bottom_left_corner():
    assert ".marlowe-box" in CSS
    assert "left: 0;" in CSS
    assert "bottom: 0;" in CSS


def test_css_marlowe_box_is_dark_but_visibly_transparent():
    assert "rgba(9, 9, 11, 0.58)" in CSS
    assert "rgba(9, 9, 11, 0.72)" in CSS


def test_status_copy_moves_from_scene_to_bottom_hud():
    scene = _scene_html(new_game_state(MARLOWE))
    status_bar = _status_bar_html(new_game_state(MARLOWE))

    assert ".marlowe-figure" in CSS
    assert ".stage-status" not in CSS
    assert "stage-status" not in scene
    assert "velvet-status-bar" in status_bar
    assert "The club thumps behind the door" in status_bar


def test_css_references_stage_background_assets_directly():
    assert "door_bg.png" in CSS
    assert "state_win_bg.png" in CSS
    assert "state_loss_bg.png" in CSS


def test_header_uses_general_game_pitch_without_presenter_or_level_stamp():
    header = _header_html()

    assert "The Nopelist presents" not in header
    assert "Marlowe" not in header
    assert "Level 1" not in header
    assert "Read the room" in header
    assert "talk your way past." in header
    assert "talk your way past the rope" not in header


def test_compact_play_layout_removes_side_rail_and_decorative_hint_assets():
    hint = _read_room_html(new_game_state(MARLOWE))

    assert "speech_bubble.png" not in hint
    assert "Current mood" in hint
    assert "Read the room" in hint
    assert ".chat-panel" in CSS
    assert ".velvet-rail" not in CSS
    assert ".locked-level" not in CSS
    assert "__ROPE_ICON_URL__" not in CSS
    assert "level-select-card::before" not in CSS
    assert "justify-content: flex-end;" in CSS
    assert "flex: 0 0 340px !important;" in CSS
    assert "max-width: 340px;" in CSS


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


def test_css_skins_gradio_native_surfaces_as_retro_game_ui():
    assert "font-family: 'Pixelify Sans'" in CSS
    assert "font-family: 'Jersey 10'" in CSS
    assert "#conversation-chatbot .bot.message" in CSS
    assert "#conversation-chatbot .user.message" in CSS
    assert "#conversation-chatbot label.float" in CSS
    assert ".level-select-card input" in CSS
    assert ".hud-input-stack .input-container" in CSS
    assert ".gradio-container button.primary:hover" in CSS
    assert ".gradio-container .show-api" in CSS
    assert "text-transform: uppercase;" in CSS


def test_css_uses_local_font_faces_without_remote_imports():
    assert "@font-face" in CSS
    assert "Jersey10-Regular.ttf" in CSS
    assert "PixelifySans-Regular.ttf" in CSS
    assert "PixelifySans-Bold.ttf" in CSS
    assert "fonts.googleapis.com" not in CSS
    assert "fonts.gstatic.com" not in CSS


def test_css_applies_local_9slice_ui_frame_assets():
    assert "panel_frame_9slice.png" in CSS
    assert "small_panel_frame_9slice.png" in CSS
    assert "chat_bubble_bot_9slice.png" in CSS
    assert "chat_bubble_player_9slice.png" in CSS
    assert "button_normal_9slice.png" in CSS
    assert "button_hover_9slice.png" in CSS
    assert "button_pressed_9slice.png" in CSS
    assert "input_frame_9slice.png" in CSS
    assert "dropdown_arrow.png" in CSS
    assert "scroll_thumb_9slice.png" in CSS
    assert "scroll_track_9slice.png" in CSS
    assert "border-image-source" in CSS
    assert "border-image-slice" in CSS
    assert "border-image-repeat: stretch;" in CSS


def test_css_avoids_redundant_nested_frames_in_selector_and_chat():
    level_card_block = CSS.split(".level-select-card {", 1)[1].split("}", 1)[0]
    chat_block = CSS.split("#conversation-chatbot {", 1)[1].split("}", 1)[0]
    chat_wrapper_block = CSS.split("#conversation-chatbot .wrapper,\n#conversation-chatbot .bubble-wrap {\n  background: transparent", 1)[
        1
    ].split("}", 1)[0]
    chat_label_block = CSS.split("#conversation-chatbot label.float {", 1)[1].split("}", 1)[0]

    assert "border-image-source" not in level_card_block
    assert "box-shadow: none;" in level_card_block
    assert ".level-select-card input {" in CSS
    assert "border: 0 !important;" in CSS.split(".level-select-card input {", 1)[1].split("}", 1)[0]
    assert "border-image-source: var(--ui-input-frame)" in CSS.split(".level-select-card .secondary-wrap {", 1)[1].split("}", 1)[0]
    assert "border-image-source: none !important;" in chat_wrapper_block
    assert "border: 0 !important;" in chat_wrapper_block
    assert "box-shadow: none !important;" in chat_wrapper_block
    assert "background: transparent !important;" in chat_block
    assert "border: 0 !important;" in chat_block
    assert "box-shadow: none !important;" in chat_block
    assert "border-image-source: none !important;" in chat_label_block
    assert "#conversation-chatbot .message.panel-full-width" in CSS


def test_chat_panel_keeps_input_controls_stacked_after_messages_render():
    chat_panel_block = CSS.split(".chat-panel {", 2)[2].split("}", 1)[0]

    assert "flex-direction: column;" in chat_panel_block
    assert "flex-wrap: nowrap" in chat_panel_block

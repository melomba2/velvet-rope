from dataclasses import replace

from velvet_rope.art import (
    ART_ROOT,
    manifest_asset_paths,
    mood_sprite_url,
    scene_background_url,
    state_stamp_url,
)
from velvet_rope.characters import MARLOWE
from velvet_rope.state import GameStatus, Mood, new_game_state
from velvet_rope.ui import CSS, _header_html, _read_room_html, _scene_html


def test_manifest_assets_are_local_to_runtime_art_root():
    paths = manifest_asset_paths()

    assert paths
    assert all(path.is_file() for path in paths)
    assert all(path.is_relative_to(ART_ROOT) for path in paths)


def test_each_mood_maps_to_curated_marlowe_sprite_url():
    for mood in Mood:
        url = mood_sprite_url(mood)

        assert url.startswith("/gradio_api/file=")
        assert f"marlowe_{mood.value}.png" in url
        assert "art/comfyui" not in url


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


def test_css_places_marlowe_box_in_bottom_left_corner():
    assert ".marlowe-box" in CSS
    assert "left: 0;" in CSS
    assert "bottom: 0;" in CSS


def test_css_marlowe_box_is_dark_but_visibly_transparent():
    assert "rgba(9, 9, 11, 0.58)" in CSS
    assert "rgba(9, 9, 11, 0.72)" in CSS


def test_css_places_status_at_scene_bottom():
    assert ".marlowe-figure" in CSS
    assert ".stage-status" in CSS
    assert "bottom: 24px;" in CSS


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
    assert "flex: 0 0 260px !important;" in CSS
    assert "max-width: 260px;" in CSS

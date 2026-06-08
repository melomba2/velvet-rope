from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path
from typing import Any
from urllib.parse import quote

from velvet_rope.state import GameState, GameStatus, Mood


ART_ROOT = Path(__file__).resolve().parent / "static" / "art"
MANIFEST_PATH = ART_ROOT / "manifest.json"
REPO_ROOT = Path(__file__).resolve().parents[1]


@lru_cache(maxsize=1)
def art_manifest() -> dict[str, Any]:
    with MANIFEST_PATH.open(encoding="utf-8") as manifest_file:
        return json.load(manifest_file)


def configure_gradio_static_paths(gradio_module: Any) -> None:
    gradio_module.set_static_paths(paths=[ART_ROOT])


def manifest_asset_paths() -> list[Path]:
    paths: list[Path] = []
    for relative_path in _walk_manifest_paths(art_manifest()):
        paths.append(_resolve_art_path(relative_path))
    return sorted(paths)


def mood_sprite_url(mood: Mood) -> str:
    return _asset_url(art_manifest()["marlowe_sprites"][mood.value])


def scene_background_url(state: GameState) -> str:
    scene_assets = art_manifest()["scene_assets"]
    if state.status is GameStatus.WON:
        return _asset_url(scene_assets["win_background"])
    if state.status is GameStatus.LOST:
        return _asset_url(scene_assets["loss_background"])
    return _asset_url(scene_assets["door_background"])


def scene_asset_url(asset_key: str) -> str:
    return _asset_url(art_manifest()["scene_assets"][asset_key])


def state_rope_url(state: GameState) -> str | None:
    rope_assets = art_manifest()["rope_assets"]
    if state.status is GameStatus.WON:
        return _asset_url(rope_assets["open_animation"])
    return None


def state_stamp_url(state: GameState) -> str | None:
    ui_assets = art_manifest()["ui_assets"]
    if state.status is GameStatus.WON:
        return _asset_url(ui_assets["stamp_admitted"])
    if state.status is GameStatus.LOST:
        return _asset_url(ui_assets["stamp_denied"])
    return None


def _asset_url(relative_path: str) -> str:
    path = _resolve_art_path(relative_path)
    try:
        public_path = path.relative_to(REPO_ROOT).as_posix()
    except ValueError:
        public_path = path.as_posix()
    return f"/gradio_api/file={quote(public_path, safe='/._-')}"


def _resolve_art_path(relative_path: str) -> Path:
    path = (ART_ROOT / relative_path).resolve()
    if not path.is_relative_to(ART_ROOT):
        raise ValueError(f"Art manifest path escapes runtime art root: {relative_path}")
    return path


def _walk_manifest_paths(value: Any) -> list[str]:
    if isinstance(value, dict):
        paths: list[str] = []
        for child in value.values():
            paths.extend(_walk_manifest_paths(child))
        return paths
    if isinstance(value, list):
        paths = []
        for child in value:
            paths.extend(_walk_manifest_paths(child))
        return paths
    if isinstance(value, str) and (value.startswith("assets/") or value.startswith("sprites/")):
        return [value]
    return []

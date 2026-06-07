from __future__ import annotations

import json
import os
from pathlib import Path
import re
from typing import Any


class JsonlTranscriptRecorder:
    def __init__(self, directory: str | Path = ".playtests/transcripts") -> None:
        self.directory = Path(directory)

    def record_turn(self, event: dict[str, Any]) -> None:
        session_id = _safe_filename(str(event["session_id"]))
        self.directory.mkdir(parents=True, exist_ok=True)
        path = self.directory / f"{session_id}.jsonl"
        with path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(event, sort_keys=True) + "\n")


def transcript_recorder_from_env() -> JsonlTranscriptRecorder | None:
    if os.getenv("VELVET_CAPTURE_TRANSCRIPTS", "1").strip().lower() in {"0", "false", "no", "off"}:
        return None
    return JsonlTranscriptRecorder(os.getenv("VELVET_TRANSCRIPT_DIR", ".playtests/transcripts"))


def _safe_filename(value: str) -> str:
    cleaned = re.sub(r"[^A-Za-z0-9_.-]+", "-", value).strip(".-")
    return cleaned or "session"

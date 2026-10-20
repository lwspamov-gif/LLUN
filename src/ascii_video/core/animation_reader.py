from __future__ import annotations

import gzip
import json
from pathlib import Path
from typing import Any

from .animation_writer import ASCIIAnimation


def animation_from_file(path: str | Path) -> ASCIIAnimation:
    file_path = Path(path)
    if not file_path.exists():
        raise FileNotFoundError(f"Animation file not found: {file_path}")
    try:
        payload = gzip.decompress(file_path.read_bytes())
    except OSError as exc:
        raise ValueError(f"Invalid or corrupted animation file: {file_path}") from exc
    try:
        data = json.loads(payload.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ValueError(f"Animation payload is not valid JSON: {file_path}") from exc
    if not isinstance(data, dict):
        raise ValueError("Animation payload must be a JSON object")
    version = data.get("format_version")
    if version != ASCIIAnimation.FORMAT_VERSION:
        raise ValueError(f"Unsupported animation version: {version!r}")
    frames = data.get("frames")
    if not isinstance(frames, list):
        raise ValueError("Animation frames are missing or invalid")
    animation = ASCIIAnimation(
        width=int(data.get("width", 0)),
        height=int(data.get("height", 0)),
        fps=float(data.get("fps", 0.0)),
        frames=frames,
        metadata=data.get("metadata", {}),
    )
    return animation

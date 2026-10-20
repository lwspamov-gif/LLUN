from __future__ import annotations

import gzip
import json
import os
from pathlib import Path
from typing import Any


class ASCIIAnimation:
    """Versioned animation container for terminal output."""

    FORMAT_VERSION = "1.0"

    def __init__(self, width: int, height: int, fps: float, frames: list[dict[str, Any]], metadata: dict[str, Any] | None = None):
        self.width = int(width)
        self.height = int(height)
        self.fps = float(fps)
        self.frames = frames
        self.metadata = metadata or {}
        self.created_at = metadata.get("created_at") if metadata else None

    @property
    def frame_count(self) -> int:
        return len(self.frames)

    @property
    def duration(self) -> float:
        if not self.frames:
            return 0.0
        return float(self.frames[-1].get("timestamp", len(self.frames) / max(self.fps, 1e-6)))

    def to_payload(self) -> dict[str, Any]:
        payload = {
            "format_version": self.FORMAT_VERSION,
            "width": self.width,
            "height": self.height,
            "fps": self.fps,
            "frames": self.frames,
            "metadata": self.metadata,
        }
        return payload

    def write_to_file(self, path: str | os.PathLike[str]):
        destination = Path(path)
        destination.parent.mkdir(parents=True, exist_ok=True)
        payload = self.to_payload()
        compressed = gzip.compress(json.dumps(payload, separators=(",", ":")).encode("utf-8"))
        destination.write_bytes(compressed)

    def to_bytes(self) -> bytes:
        return gzip.compress(json.dumps(self.to_payload(), separators=(",", ":")).encode("utf-8"))


def animation_to_bytes(animation: ASCIIAnimation) -> bytes:
    return animation.to_bytes()


def save_animation(animation: ASCIIAnimation, path: str | os.PathLike[str]) -> None:
    animation.write_to_file(path)

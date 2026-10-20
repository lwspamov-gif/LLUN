from __future__ import annotations

import math
from typing import Any

import cv2
import numpy as np

from .frame_processor import FrameProcessor


class AsciiConverter:
    """Convert video frames to ASCII art using a density-based palette."""

    DEFAULT_CHARSET = "@%#*+=-:. "

    def __init__(self, config: dict[str, Any] | None = None):
        self.config = config or {}
        self.charset = self.config.get("charset", self.DEFAULT_CHARSET)
        self.frame_processor = FrameProcessor(self.config)

    def _normalize_charset(self) -> str:
        if not self.charset:
            return self.DEFAULT_CHARSET
        return self.charset

    def brightness_to_char(self, brightness: float, charset: str | None = None) -> str:
        charset = charset or self._normalize_charset()
        if not charset:
            return " "
        index = int(round((brightness / 255.0) * (len(charset) - 1)))
        index = max(0, min(len(charset) - 1, index))
        return charset[index]

    def frame_to_ascii(self, frame: np.ndarray, width: int, height: int | None = None, charset: str | None = None) -> list[str]:
        charset = charset or self._normalize_charset()
        processed = self.frame_processor.preprocess_frame(frame.copy(), width, preserve_aspect=bool(self.config.get("preserve_aspect_ratio", True)))
        if height is not None:
            processed = cv2.resize(processed, (width, height), interpolation=cv2.INTER_AREA)
        luminance = self.frame_processor.compute_luminance(processed)
        rows: list[str] = []
        for row in luminance:
            line = "".join(self.brightness_to_char(value, charset) for value in row)
            rows.append(line)
        return rows

    def convert_frame(self, frame: np.ndarray, width: int, charset: str | None = None) -> str:
        rows = self.frame_to_ascii(frame, width, charset=charset)
        return "\n".join(rows)

    def _build_animation(self, frames: list[np.ndarray], target_width: int, target_fps: float) -> "ASCIIAnimation":
        from .animation_writer import ASCIIAnimation

        processed_frames: list[dict[str, Any]] = []
        for frame in frames:
            rows = self.frame_to_ascii(frame, target_width)
            processed_frames.append({"ascii": rows, "timestamp": 0.0})

        animation = ASCIIAnimation(
            width=target_width,
            height=max(1, len(processed_frames[0]) if processed_frames else 1),
            fps=target_fps,
            frames=processed_frames,
            metadata={"quality": self.config.get("quality", "ultra"), "color_mode": self.config.get("color_mode", "truecolor")},
        )
        return animation

    def encode_video(self, video_reader: Any, target_width: int = 300, target_fps: float = 60.0) -> "ASCIIAnimation":
        frames: list[np.ndarray] = []
        while True:
            frame = video_reader.read_frame()
            if frame is None:
                break
            frames.append(frame)
        if not frames:
            raise ValueError("No frames available in source video")
        video_reader.release()
        target_width = max(1, int(target_width))
        animation = self._build_animation(frames, target_width, target_fps)
        return animation

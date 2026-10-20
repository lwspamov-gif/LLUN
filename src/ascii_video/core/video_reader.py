from __future__ import annotations

import json
import math
import os
from typing import Any

import cv2
import numpy as np


class VideoReader:
    """Read and examine a source video file while keeping metadata."""

    def __init__(self, path: str | os.PathLike[str]):
        self.path = str(path)
        self.capture = cv2.VideoCapture(self.path)
        if not self.capture.isOpened():
            raise ValueError(f"Unable to open video: {self.path}")
        self._cached_frame_count = int(self.capture.get(cv2.CAP_PROP_FRAME_COUNT))
        self._metadata = self._read_metadata()

    @property
    def width(self) -> int:
        value = self.capture.get(cv2.CAP_PROP_FRAME_WIDTH)
        return int(value) if value else 0

    @property
    def height(self) -> int:
        value = self.capture.get(cv2.CAP_PROP_FRAME_HEIGHT)
        return int(value) if value else 0

    @property
    def fps(self) -> float:
        value = self.capture.get(cv2.CAP_PROP_FPS)
        return float(value) if value and value > 0 else 0.0

    @property
    def frame_count(self) -> int:
        value = int(self._cached_frame_count)
        return value if value > 0 else 0

    @property
    def duration(self) -> float:
        if self.fps > 0 and self.frame_count > 0:
            return self.frame_count / self.fps
        return 0.0

    @property
    def metadata(self) -> dict[str, Any]:
        return dict(self._metadata)

    def _read_metadata(self) -> dict[str, Any]:
        return {
            "source": self.path,
            "width": self.width,
            "height": self.height,
            "fps": self.fps,
            "frame_count": self.frame_count,
            "duration": self.duration,
        }

    def read_frame(self, frame_index: int | None = None) -> np.ndarray | None:
        if frame_index is not None:
            self.capture.set(cv2.CAP_PROP_POS_FRAMES, int(frame_index))
        ok, frame = self.capture.read()
        if not ok or frame is None:
            return None
        return frame

    def read_all_frames(self) -> list[np.ndarray]:
        frames: list[np.ndarray] = []
        while True:
            frame = self.read_frame()
            if frame is None:
                break
            frames.append(frame)
        self.capture.release()
        return frames

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.release()

    def release(self):
        if self.capture is not None:
            self.capture.release()

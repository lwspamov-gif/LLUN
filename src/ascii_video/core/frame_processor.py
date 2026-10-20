from __future__ import annotations

import math
from typing import Any

import cv2
import numpy as np


class FrameProcessor:
    """Adjust video frames for quality and rendering."""

    def __init__(self, config: dict[str, Any] | None = None):
        self.config = config or {}

    def normalize_frame(self, frame: np.ndarray) -> np.ndarray:
        if frame.size == 0:
            raise ValueError("Cannot process empty frame")
        frame = np.asarray(frame, dtype=np.float32)
        if frame.ndim == 2:
            frame = cv2.cvtColor(frame, cv2.COLOR_GRAY2RGB)
        elif frame.shape[-1] == 4:
            frame = cv2.cvtColor(frame, cv2.COLOR_BGRA2BGR)
        elif frame.shape[-1] == 3:
            frame = frame.astype(np.float32, copy=False)
        else:
            raise ValueError(f"Unsupported frame format with shape {frame.shape}")
        return frame

    def adjust_gamma(self, frame: np.ndarray, gamma: float = 1.0) -> np.ndarray:
        if gamma <= 0:
            raise ValueError("Gamma must be positive")
        if gamma == 1.0:
            return frame
        corrected = np.power(frame / 255.0, gamma) * 255.0
        return np.clip(corrected, 0, 255).astype(np.uint8)

    def apply_contrast_and_brightness(self, frame: np.ndarray, contrast: float = 1.0, brightness: float = 0.0) -> np.ndarray:
        frame = frame.astype(np.float32)
        frame = (frame - 128.0) * contrast + 128.0 + brightness
        return np.clip(frame, 0, 255).astype(np.uint8)

    def resize_frame(self, frame: np.ndarray, width: int, height: int | None = None, preserve_aspect: bool = True) -> np.ndarray:
        if width <= 0:
            raise ValueError("Width must be positive")
        if preserve_aspect:
            current_height, current_width = frame.shape[:2]
            scale = width / float(current_width)
            target_h = max(1, int(round(current_height * scale * 0.5)))
            if height is not None:
                target_h = min(height, target_h)
            resized = cv2.resize(frame, (width, target_h), interpolation=cv2.INTER_AREA)
            return resized
        target_h = height if height is not None else max(1, int(round(frame.shape[0] * (width / frame.shape[1]))))
        return cv2.resize(frame, (width, target_h), interpolation=cv2.INTER_AREA)

    def compute_luminance(self, frame: np.ndarray) -> np.ndarray:
        rgb = frame.astype(np.float32)
        luminance = 0.299 * rgb[:, :, 0] + 0.587 * rgb[:, :, 1] + 0.114 * rgb[:, :, 2]
        return luminance

    def sharpen(self, frame: np.ndarray, amount: float = 0.0) -> np.ndarray:
        if amount <= 0:
            return frame
        kernel = np.array([[0, -1, 0], [-1, 5, -1], [0, -1, 0]], dtype=np.float32) * amount
        return cv2.filter2D(frame, -1, kernel)

    def preprocess_frame(self, frame: np.ndarray, width: int, preserve_aspect: bool = True) -> np.ndarray:
        frame = self.normalize_frame(frame)
        gamma = float(self.config.get("gamma", 1.0))
        contrast = float(self.config.get("contrast", 1.0))
        brightness = float(self.config.get("brightness", 0.0))
        sharpen = float(self.config.get("sharpen", 0.0))
        frame = self.apply_contrast_and_brightness(frame, contrast, brightness)
        frame = self.adjust_gamma(frame, gamma)
        frame = self.sharpen(frame, sharpen)
        frame = self.resize_frame(frame, width, preserve_aspect=preserve_aspect)
        return frame

    def frames_to_temporal_markers(self, frame_count: int, fps: float) -> list[float]:
        if fps <= 0 or frame_count <= 0:
            return []
        return [(idx / fps) for idx in range(frame_count)]

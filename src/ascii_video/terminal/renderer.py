from __future__ import annotations

import os
import sys
import time
from typing import Any

from ..core.animation_reader import ASCIIAnimation


class Renderer:
    """Render an ASCII animation in the terminal, with timing and loop support."""

    def __init__(self, animation: ASCIIAnimation, config: dict[str, Any] | None = None):
        self.animation = animation
        self.config = config or {}

    def _clear_screen(self):
        sys.stdout.write("\033[2J\033[H")
        sys.stdout.flush()

    def _hide_cursor(self):
        sys.stdout.write("\033[?25l")
        sys.stdout.flush()

    def _show_cursor(self):
        sys.stdout.write("\033[?25h")
        sys.stdout.flush()

    def play(self, loop: bool = True, fps: float = 60.0, skip_late_frames: bool = True) -> int:
        if fps <= 0:
            fps = self.animation.fps or 60.0
        self._clear_screen()
        self._hide_cursor()
        try:
            start = time.perf_counter()
            frame_index = 0
            while True:
                frame = self.animation.frames[frame_index % len(self.animation.frames)]
                text = "\n".join(frame.get("ascii", []))
                sys.stdout.write("\r" + text)
                sys.stdout.flush()
                frame_index += 1
                if frame_index >= len(self.animation.frames):
                    if not loop:
                        break
                    frame_index = 0
                next_frame_time = start + (frame_index / fps)
                sleep_seconds = max(0.0, next_frame_time - time.perf_counter())
                if sleep_seconds > 0:
                    time.sleep(sleep_seconds)
                if skip_late_frames and sleep_seconds < 0:
                    continue
        except KeyboardInterrupt:
            return 0
        finally:
            self._show_cursor()
            sys.stdout.write("\033[0m\n")
            sys.stdout.flush()
        return 0


def render_animation(animation: ASCIIAnimation, config: dict[str, Any] | None = None) -> int:
    return Renderer(animation, config).play(loop=config.get("loop", True) if config else True)

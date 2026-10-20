from __future__ import annotations

import os
import sys
from enum import Enum


class ColorMode(Enum):
    MONOCHROME = "monochrome"
    ANSI256 = "ansi256"
    TRUECOLOR = "truecolor"


def terminal_supports_color() -> bool:
    if os.environ.get("NO_COLOR") == "1":
        return False
    if os.environ.get("TERM") in {"", "dumb"}:
        return False
    return True


def colorize(text: str, r: int, g: int, b: int) -> str:
    return f"\033[38;2;{r};{g};{b}m{text}\033[0m"


def to_ansi256(r: int, g: int, b: int) -> str:
    if not (0 <= r <= 255 and 0 <= g <= 255 and 0 <= b <= 255):
        raise ValueError("RGB values must be in range 0-255")
    return f"\033[38;5;{((r * 5) << 16) | ((g * 5) << 8) | (b * 5)}m"

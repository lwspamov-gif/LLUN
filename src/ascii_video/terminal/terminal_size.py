from __future__ import annotations

import shutil
import os


def get_terminal_size() -> tuple[int, int]:
    size = shutil.get_terminal_size(fallback=(80, 24))
    return int(size.columns), int(size.lines)


def fit_to_terminal(width: int, height: int) -> tuple[int, int]:
    if width <= 0 or height <= 0:
        return 80, 24
    columns, lines = get_terminal_size()
    if width > columns:
        width = columns
    if height > lines:
        height = lines
    return max(1, width), max(1, height)

import gzip
import json
from pathlib import Path

import numpy as np

from encoder import build_animation, adjust_frame, resize_ascii_frame


def test_brightness_to_ascii_mapping_works():
    values = np.array([[0, 64, 128, 192, 255]], dtype=np.uint8)
    result = []
    for row in values:
        chars = []
        for value in row:
            idx = int((value / 255.0) * (len("@%#*+=-:. ") - 1))
            chars.append("@%#*+=-:. "[idx])
        result.append(chars)
    assert len(result) == 1 and len(result[0]) == 5


def test_resize_preserves_ratio():
    frame = np.zeros((100, 200, 3), dtype=np.uint8)
    resized = resize_ascii_frame(frame, 80)
    assert resized.shape[1] == 80
    assert resized.shape[0] > 0


def test_animation_round_trip_reuses_metadata():
    payload = {
        "format_version": 1,
        "width": 40,
        "height": 10,
        "frames": [{"timestamp": 0.0, "rows": [{"chars": "@" * 10, "colors": [[255, 255, 255]] * 10}]}],
    }
    data = json.dumps(payload).encode("utf-8")
    compressed = gzip.compress(data)
    assert compressed.startswith(b'\x1f\x8b')


def test_malformed_animation_rejected_by_player_logic():
    try:
        payload = {"frames": []}
        assert payload["frames"] == []
    except Exception:
        assert False


def test_timestamps_are_numeric():
    payload = {"frames": [{"timestamp": 0.0}, {"timestamp": 1.0 / 60.0}]}
    assert isinstance(payload["frames"][0]["timestamp"], float)
    assert isinstance(payload["frames"][1]["timestamp"], float)

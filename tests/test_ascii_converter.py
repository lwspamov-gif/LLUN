import numpy as np

from ascii_video.core.ascii_converter import AsciiConverter


def test_brightness_to_char_uses_expected_range():
    converter = AsciiConverter({"charset": "@%#*+=-:. "})
    assert converter.brightness_to_char(0) == "@"
    assert converter.brightness_to_char(255) == " "
    assert converter.brightness_to_char(127) in {"+", "=", "-", "*"}


def test_ascii_frame_preserves_proportions():
    converter = AsciiConverter({"preserve_aspect_ratio": True, "charset": "@%#*+=-:. "})
    frame = np.zeros((50, 100, 3), dtype=np.uint8)
    rows = converter.frame_to_ascii(frame, width=40)
    assert len(rows) > 0
    assert all(len(row) == 40 for row in rows)

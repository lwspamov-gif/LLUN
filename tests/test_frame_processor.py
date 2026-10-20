import numpy as np

from ascii_video.core.frame_processor import FrameProcessor


def test_processor_handles_empty_frame():
    processor = FrameProcessor({})
    try:
        processor.normalize_frame(np.empty((0, 0, 3), dtype=np.uint8))
        assert False, "Expected ValueError for empty frame"
    except ValueError:
        pass


def test_resize_uses_image_proportions():
    processor = FrameProcessor({"preserve_aspect_ratio": True})
    frame = np.zeros((100, 200, 3), dtype=np.uint8)
    resized = processor.resize_frame(frame, width=80)
    assert resized.shape[0] > 0
    assert resized.shape[1] == 80

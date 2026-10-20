import tempfile
from pathlib import Path

from ascii_video.core.animation_reader import animation_from_file
from ascii_video.core.animation_writer import ASCIIAnimation


def test_animation_round_trip():
    animation = ASCIIAnimation(
        width=20,
        height=10,
        fps=30.0,
        frames=[{"ascii": ["@" * 5 for _ in range(10)], "timestamp": 0.0}],
        metadata={"quality": "ultra"},
    )
    with tempfile.TemporaryDirectory() as tmpdir:
        path = Path(tmpdir) / "sample.avz"
        animation.write_to_file(path)
        loaded = animation_from_file(path)
        assert loaded.width == 20
        assert loaded.height == 10
        assert loaded.frame_count == 1
        assert loaded.metadata["quality"] == "ultra"


def test_invalid_animation_file_is_rejected():
    with tempfile.TemporaryDirectory() as tmpdir:
        path = Path(tmpdir) / "bad.avz"
        path.write_bytes(b"not-a-valid-gzip-stream")
        try:
            animation_from_file(path)
            assert False, "Expected ValueError for invalid animation" 
        except ValueError:
            pass

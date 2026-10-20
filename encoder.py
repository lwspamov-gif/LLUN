from __future__ import annotations

import argparse
import gzip
import json
import sys
import time
from pathlib import Path

import cv2
import numpy as np

PALETTE = "@%#*+=-:. "
DEFAULT_WIDTH = 100
DEFAULT_FPS = 30.0
DEFAULT_QUALITY = "ultra"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Convert a video into a compressed ASCII animation.")
    parser.add_argument("input", nargs="?", default="video.mp4", help="Input video file (default: video.mp4)")
    parser.add_argument("--output", default="output/animation.json.gz", help="Output animation path")
    parser.add_argument("--width", type=int, default=DEFAULT_WIDTH, help="ASCII width in terminal cells")
    parser.add_argument("--fps", type=float, default=DEFAULT_FPS, help="Target playback FPS")
    parser.add_argument("--quality", choices=["balanced", "high", "ultra"], default=DEFAULT_QUALITY, help="Quality preset")
    return parser.parse_args()


def quality_profile(name: str) -> dict[str, float]:
    profiles = {
        "balanced": {"gamma": 1.0, "contrast": 1.15, "brightness": 6.0, "sharpen": 0.0},
        "high": {"gamma": 1.05, "contrast": 1.2, "brightness": 4.0, "sharpen": 0.08},
        "ultra": {"gamma": 1.08, "contrast": 1.25, "brightness": 2.0, "sharpen": 0.1},
    }
    return profiles.get(name, profiles["ultra"])


def adjust_frame(frame: np.ndarray, profile: dict[str, float]) -> np.ndarray:
    frame = frame.astype(np.float32)
    frame = (frame - 128.0) * profile["contrast"] + 128.0 + profile["brightness"]
    frame = np.clip(frame, 0.0, 255.0)
    frame = np.power(frame / 255.0, 1.0 / max(profile["gamma"], 1e-6)) * 255.0
    frame = np.clip(frame, 0.0, 255.0)
    return frame.astype(np.uint8)


def resize_ascii_frame(frame: np.ndarray, width: int) -> np.ndarray:
    if frame.ndim == 2:
        frame = cv2.cvtColor(frame, cv2.COLOR_GRAY2RGB)
    if frame.shape[2] == 4:
        frame = cv2.cvtColor(frame, cv2.COLOR_BGRA2BGR)
    if frame.shape[2] != 3:
        raise ValueError(f"Unsupported frame format: {frame.shape}")

    height, width_orig = frame.shape[:2]
    scale = width / float(width_orig)
    target_h = max(1, int(round(height * scale * 0.5)))
    resized = cv2.resize(frame, (width, target_h), interpolation=cv2.INTER_AREA)
    return resized


def frame_to_ascii_rows(frame: np.ndarray) -> tuple[list[str], list[list[list[int]]]]:
    frame = frame.astype(np.uint8)
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    rows: list[str] = []
    row_colors: list[list[list[int]]] = []
    for y, row in enumerate(gray):
        chars = []
        colors = []
        for x, value in enumerate(row):
            idx = int((value / 255.0) * (len(PALETTE) - 1))
            idx = max(0, min(len(PALETTE) - 1, idx))
            chars.append(PALETTE[idx])
            rgb = rgb_frame[y, x].tolist()
            colors.append([int(v) for v in rgb])
        rows.append("".join(chars))
        row_colors.append(colors)
    return rows, row_colors


def sample_frames(cap: cv2.VideoCapture, target_fps: float) -> tuple[list[np.ndarray], float, float, int, int]:
    frames: list[np.ndarray] = []
    source_fps = cap.get(cv2.CAP_PROP_FPS) or target_fps
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH) or 0)
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT) or 0)
    if width <= 0 or height <= 0:
        raise ValueError("The source video does not expose valid frame dimensions.")

    if source_fps <= 0:
        source_fps = target_fps
    sample_interval = 1.0 / max(target_fps, 1e-6)
    next_sample_time = 0.0
    frame_index = 0
    while True:
        ok, frame = cap.read()
        if not ok or frame is None:
            break
        frame_ts = frame_index / source_fps if source_fps > 0 else 0.0
        if frame_index == 0 or frame_ts >= next_sample_time - 1e-6:
            frames.append(frame.copy())
            next_sample_time += sample_interval
            while next_sample_time <= frame_ts + 1e-9:
                next_sample_time += sample_interval
        frame_index += 1

    return frames, source_fps, target_fps, width, height


def build_animation(video_path: str, width: int, target_fps: float, quality: str) -> dict:
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        raise ValueError(f"Unable to open video: {video_path}")

    try:
        frames, source_fps, _, src_width, src_height = sample_frames(cap, target_fps)
    finally:
        cap.release()

    if not frames:
        raise ValueError("No frames were decoded from the source video.")

    effective_fps = min(float(target_fps), float(source_fps))
    profile = quality_profile(quality)
    output_frames: list[dict] = []
    for index, frame in enumerate(frames):
        adjusted = adjust_frame(frame, profile)
        resized = resize_ascii_frame(adjusted, width)
        rows, row_colors = frame_to_ascii_rows(resized)
        timestamp = index / max(effective_fps, 1e-6)
        output_frames.append({
            "timestamp": float(timestamp),
            "rows": [{"chars": chars, "colors": colors} for chars, colors in zip(rows, row_colors)],
        })

    result = {
        "format_version": 1,
        "width": width,
        "height": max(1, len(output_frames[0]["rows"])),
        "source_width": src_width,
        "source_height": src_height,
        "source_fps": float(source_fps),
        "target_fps": effective_fps,
        "quality": quality,
        "frames": output_frames,
    }
    return result


def write_animation(payload: dict, output_path: str) -> None:
    destination = Path(output_path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    encoded = json.dumps(payload, separators=(",", ":")).encode("utf-8")
    compressed = gzip.compress(encoded)
    destination.write_bytes(compressed)
    print(f"Animation saved: {destination} ({len(compressed) / 1024:.1f} KB)")


def main() -> int:
    args = parse_args()
    input_path = Path(args.input)
    if not input_path.exists():
        raise FileNotFoundError(f"Input video not found: {input_path}")

    payload = build_animation(str(input_path), args.width, args.fps, args.quality)
    write_animation(payload, args.output)
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"Error: {exc}", file=sys.stderr)
        raise SystemExit(1)

from __future__ import annotations

import argparse
import gzip
import json
import sys
import time
from pathlib import Path

ANSI_TRUECOLOR = "\033[38;2;{r};{g};{b}m"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Play a compressed ASCII animation in the terminal.")
    parser.add_argument("animation", nargs="?", default="animation.json.gz", help="Path to animation file")
    parser.add_argument("--loop", action="store_true", help="Repeat the animation in an infinite loop")
    parser.add_argument("--fps", type=float, default=0.0, help="Playback FPS override")
    parser.add_argument("--width", type=int, default=None, help="Override terminal width")
    parser.add_argument("--color", choices=["truecolor", "monochrome"], default="truecolor", help="Color mode")
    return parser.parse_args()


def load_animation(path: str) -> dict:
    file_path = Path(path)
    if not file_path.exists():
        raise FileNotFoundError(f"Animation file not found: {file_path}")
    try:
        raw = gzip.decompress(file_path.read_bytes())
        return json.loads(raw.decode("utf-8"))
    except Exception as exc:  # pragma: no cover
        raise ValueError(f"Animation file is corrupted or unreadable: {path}") from exc


def render_frame(frame: dict, color_mode: str) -> str:
    lines = []

    for row in frame.get("rows", []):
        chars = row["chars"] if isinstance(row, dict) and "chars" in row else row
        colors = row.get("colors", []) if isinstance(row, dict) else []

        if color_mode == "monochrome":
            lines.append("".join(chars))
            continue

        parts = []
        previous_rgb = None

        for idx, ch in enumerate(chars):
            if idx < len(colors):
                rgb = tuple(int(v) for v in colors[idx][:3])
            else:
                rgb = (255, 255, 255)

            if rgb != previous_rgb:
                parts.append(f"\033[38;2;{rgb[0]};{rgb[1]};{rgb[2]}m")
                previous_rgb = rgb

            parts.append(ch)

        parts.append("\033[0m")
        lines.append("".join(parts))

    return "\n".join(lines)


def clear_terminal() -> None:
    sys.stdout.write("\033[2J\033[H")
    sys.stdout.flush()


def hide_cursor() -> None:
    sys.stdout.write("\033[?25l")
    sys.stdout.flush()


def show_cursor() -> None:
    sys.stdout.write("\033[?25h\033[0m")
    sys.stdout.flush()


def play(animation_data: dict, loop: bool, fps_override: float, color_mode: str) -> int:
    frames = animation_data.get("frames", [])
    if not frames:
        raise ValueError("The animation contains no frames.")

    fps = float(animation_data.get("target_fps", fps_override))
    if fps_override > 0:
        fps = fps_override
    fps = max(fps, 1e-6)

    clear_terminal()
    hide_cursor()
    try:
        index = 0
        next_frame_time = time.perf_counter()
        while True:
            frame = frames[index % len(frames)]
            text = render_frame(frame, color_mode)
            sys.stdout.write("\033[H" + text + "\033[0m")
            sys.stdout.flush()

            next_index = index + 1
            if next_index >= len(frames):
                if not loop:
                    break
                next_index = 0

            frame_interval = 1.0 / fps
            next_frame_time += frame_interval
            now = time.perf_counter()
            if now < next_frame_time:
                time.sleep(max(0.0, next_frame_time - now))
            else:
                next_frame_time = now

            index = next_index
    except KeyboardInterrupt:
        print("\nPlayback stopped.")
    finally:
        show_cursor()
    return 0


def main() -> int:
    args = parse_args()
    animation_path = Path(args.animation)
    if not animation_path.exists():
        raise FileNotFoundError(f"Animation file not found: {animation_path}")
    animation = load_animation(str(animation_path))
    return play(animation, args.loop, args.fps, args.color)


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"Error: {exc}", file=sys.stderr)
        raise SystemExit(1)

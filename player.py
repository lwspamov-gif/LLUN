from __future__ import annotations

import argparse
import gzip
import json
import shutil
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

    fps = float(animation_data.get("target_fps", 30.0))
    if fps_override > 0:
        fps = fps_override
    fps = max(fps, 1e-6)

    frame_width = max(
        len(row["chars"]) if isinstance(row, dict) and "chars" in row else len(row)
        for row in frames[0].get("rows", [])
    )
    terminal_width = shutil.get_terminal_size((120, 40)).columns
    if terminal_width < frame_width:
        raise RuntimeError(
            f"Кадр имеет ширину {frame_width} символов, а терминал вмещает {terminal_width}. "
            "Разверни окно и уменьши размер шрифта или уменьши WIDTH в encoder."
        )

    sys.stdout.write("\033[?1049h\033[?25l\033[2J\033[H")
    sys.stdout.flush()

    try:
        index = 0
        start_time = time.perf_counter()
        interval = 1.0 / fps

        while index < len(frames):
            now = time.perf_counter()
            elapsed = now - start_time
            expected_index = int(elapsed * fps)
            index = max(index, expected_index)

            if index >= len(frames):
                if not loop:
                    break
                start_time = time.perf_counter()
                index = 0

            frame = frames[index]
            text = render_frame(frame, color_mode)

            sys.stdout.write("\033[H")
            sys.stdout.write(text)
            sys.stdout.write("\033[0m\033[J")
            sys.stdout.flush()

            index += 1
            target_time = start_time + index * interval
            delay = target_time - time.perf_counter()
            if delay > 0:
                time.sleep(delay)

    except KeyboardInterrupt:
        pass
    finally:
        sys.stdout.write("\033[0m\033[?25h\033[?1049l")
        sys.stdout.flush()

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

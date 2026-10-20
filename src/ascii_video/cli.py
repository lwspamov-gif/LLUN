from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path
from typing import Any

from .core.animation_reader import animation_from_file
from .core.video_reader import VideoReader
from .core.frame_processor import FrameProcessor
from .core.ascii_converter import AsciiConverter
from .terminal.renderer import Renderer
from .utils.paths import resolve_project_root


DEFAULT_CONFIG_PATH = Path(__file__).resolve().parents[2] / "config" / "default.json"


def load_default_config() -> dict[str, Any]:
    config_path = DEFAULT_CONFIG_PATH
    if not config_path.exists():
        return {}
    with config_path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="ASCII-Video: terminal ASCII video converter and player")
    parser.add_argument("source", nargs="?", help="Input video file or animation archive")
    parser.add_argument("--output", help="Output animation file (.avz)")
    parser.add_argument("--width", type=int, help="ASCII width in terminal cells")
    parser.add_argument("--fps", type=float, help="Target frames per second")
    parser.add_argument("--quality", choices=["balanced", "high", "ultra"], help="Quality mode")
    parser.add_argument("--color", choices=["monochrome", "ansi256", "truecolor"], help="Color mode")
    parser.add_argument("--config", type=str, help="Path to config JSON")
    parser.add_argument("--loop", action="store_true", help="Repeat the animation forever")
    parser.add_argument("--no-loop", action="store_true", help="Play once")
    parser.add_argument("--no-color", action="store_true", help="Disable ANSI color output")
    return parser


def resolve_config(args: argparse.Namespace) -> dict[str, Any]:
    cfg = load_default_config()
    if args.config:
        config_path = Path(args.config)
        if config_path.exists():
            with config_path.open("r", encoding="utf-8") as handle:
                cfg.update(json.load(handle))
        else:
            raise FileNotFoundError(f"Config file not found: {config_path}")
    if args.width is not None:
        cfg["width"] = args.width
    if args.fps is not None:
        cfg["target_fps"] = args.fps
    if args.quality is not None:
        cfg["quality"] = args.quality
    if args.color is not None:
        cfg["color_mode"] = args.color
    if args.loop and args.no_loop:
        raise ValueError("--loop and --no-loop cannot be used together")
    if args.no_loop:
        cfg["loop"] = False
    elif args.loop:
        cfg["loop"] = True
    if args.no_color:
        cfg["color_mode"] = "monochrome"
    return cfg


def run_encoder(args: argparse.Namespace) -> int:
    config = resolve_config(args)
    source = args.source
    if not source:
        raise ValueError("A source video path is required for encoding")
    if not args.output:
        raise ValueError("An output path is required for encoding")

    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    reader = VideoReader(source)
    processor = FrameProcessor(config)
    converter = AsciiConverter(config)

    animation = converter.encode_video(reader, target_width=config["width"], target_fps=config["target_fps"])
    animation.write_to_file(output_path)
    print(f"Encoded {reader.frame_count} frames to {output_path} ({animation.width}x{animation.height})")
    return 0


def run_player(args: argparse.Namespace) -> int:
    config = resolve_config(args)
    source = args.source
    if not source:
        raise ValueError("A source animation archive is required")
    animation = animation_from_file(source)
    renderer = Renderer(animation, config)
    return renderer.play(loop=config.get("loop", True), fps=config.get("target_fps", 60), skip_late_frames=config.get("skip_late_frames", True))


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        if args.source and Path(args.source).suffix.lower() in {".avz"}:
            return run_player(args)
        if args.source and (Path(args.source).suffix.lower() in {".mp4", ".avi", ".mov", ".mkv", ".webm"} or args.output):
            return run_encoder(args)
        if args.source is None and args.output is None:
            parser.print_help()
            return 0
        if args.source and args.output is None:
            return run_player(args)
        parser.print_help()
        return 0
    except Exception as exc:  # pragma: no cover - CLI error path
        print(f"Error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())

from __future__ import annotations

import argparse
import gzip
import json
import sys
import time
from pathlib import Path

import pygame


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="LLUN micro player for ASCII animation in a window")
    parser.add_argument("animation", nargs="?", default="output/animation.json.gz", help="Path to animation JSON.gz")
    parser.add_argument("--fps", type=float, default=0.0, help="Optional FPS override")
    parser.add_argument("--loop", action="store_true", default=True, help="Loop animation (default: enabled)")
    parser.add_argument("--no-loop", action="store_false", dest="loop", help="Disable looping")
    return parser.parse_args()


def load_animation(path: str) -> dict:
    file_path = Path(path)
    if not file_path.exists():
        raise FileNotFoundError(f"Animation file not found: {file_path}")

    try:
        raw = gzip.decompress(file_path.read_bytes())
        return json.loads(raw.decode("utf-8"))
    except Exception as exc:
        raise ValueError(f"Animation file is corrupted or unreadable: {path}") from exc


def get_frame_width(frame: dict) -> int:
    rows = frame.get("rows", [])
    if not rows:
        return 0
    width = 0
    for row in rows:
        chars = row["chars"] if isinstance(row, dict) and "chars" in row else row
        width = max(width, len(chars))
    return width


def layout_for_frame(frame: dict, start_font_size: int = 16) -> tuple[pygame.font.Font, int, int]:
    font = pygame.font.SysFont("consolas", start_font_size)
    cell_w = max(1, font.size("M")[0])
    cell_h = max(1, font.get_linesize())
    return font, cell_w, cell_h


def draw_frame(screen: pygame.Surface, animation: dict, frame_index: int, font: pygame.font.Font, cell_w: int, cell_h: int) -> None:
    frame = animation["frames"][frame_index]
    rows = frame.get("rows", [])
    screen.fill((0, 0, 0))

    for y, row in enumerate(rows):
        if isinstance(row, dict):
            chars = row.get("chars", [])
            colors = row.get("colors", [])
        else:
            chars = row
            colors = []

        for x, ch in enumerate(chars):
            if x < len(colors):
                color = tuple(int(v) for v in colors[x][:3])
            else:
                color = (255, 255, 255)

            if ch == " ":
                continue

            surface = font.render(ch, True, color)
            screen.blit(surface, (x * cell_w, y * cell_h))


def main() -> int:
    args = parse_args()
    animation = load_animation(args.animation)
    frames = animation.get("frames", [])
    if not frames:
        raise ValueError("The animation contains no frames.")

    fps = float(animation.get("target_fps", 30.0))
    if args.fps > 0:
        fps = args.fps
    fps = max(fps, 1e-6)

    pygame.init()
    pygame.display.set_caption("LLUN ASCII Video")

    info = pygame.display.Info()
    base_w = min(info.current_w, 1400)
    base_h = min(info.current_h, 900)
    screen = pygame.display.set_mode((base_w, base_h), pygame.RESIZABLE)

    font, cell_w, cell_h = layout_for_frame(frames[0])
    frame_w = get_frame_width(frames[0])
    frame_h = len(frames[0].get("rows", []))

    if frame_w > 300:
        scale = 300 / frame_w
        font = pygame.font.SysFont("consolas", max(8, int(16 * scale)))
        cell_w = max(1, font.size("M")[0])
        cell_h = max(1, font.get_linesize())
        frame_w = max(1, int(frame_w * scale))

    clock = pygame.time.Clock()
    fullscreen = False
    paused = False
    frame_index = 0
    started = time.perf_counter()
    running = True

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_SPACE:
                    paused = not paused
                    if not paused:
                        started = time.perf_counter() - (frame_index / fps)
                elif event.key == pygame.K_LEFT:
                    frame_index = (frame_index - 1) % len(frames)
                    if paused:
                        started = time.perf_counter() - (frame_index / fps)
                elif event.key == pygame.K_RIGHT:
                    frame_index = (frame_index + 1) % len(frames)
                    if paused:
                        started = time.perf_counter() - (frame_index / fps)
                elif event.key == pygame.K_F11:
                    fullscreen = not fullscreen
                    if fullscreen:
                        screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
                    else:
                        screen = pygame.display.set_mode((base_w, base_h), pygame.RESIZABLE)

        if not paused:
            elapsed = time.perf_counter() - started
            current_index = int(elapsed * fps)
            if args.loop:
                frame_index = current_index % len(frames)
            elif current_index >= len(frames):
                running = False
            else:
                frame_index = current_index

        draw_frame(screen, animation, frame_index, font, cell_w, cell_h)
        pygame.display.flip()
        clock.tick(60)

    pygame.quit()
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"LLUN error: {exc}", file=sys.stderr)
        raise SystemExit(1)

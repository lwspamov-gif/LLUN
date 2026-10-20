from __future__ import annotations

import os
import shutil
import subprocess
import sys
import venv
from pathlib import Path

ROOT = Path(__file__).resolve().parent
REQ_FILE = ROOT / "requirements.txt"
ENCODER_FILE = ROOT / "encoder.py"
PLAYER_FILE = ROOT / "player.py"
ANIMATION_FILE = ROOT / "output" / "animation.json.gz"


def find_video_file() -> Path | None:
    preferred = ROOT / "video.mp4"
    if preferred.exists():
        return preferred

    matches = sorted(ROOT.glob("*.mp4"))
    if matches:
        return matches[0]
    return None


def python_executable_for_venv() -> Path:
    venv_dir = ROOT / ".venv"
    if os.name == "nt":
        return venv_dir / "Scripts" / "python.exe"
    return venv_dir / "bin" / "python"


def ensure_venv() -> Path:
    py = python_executable_for_venv()
    if not py.exists():
        print("Creating local virtual environment...")
        venv.EnvBuilder(with_pip=True).create(ROOT / ".venv")
        if not py.exists():
            raise FileNotFoundError(f"Virtual environment Python not found: {py}")
    return py


def ensure_requirements(python_bin: Path) -> None:
    if not REQ_FILE.exists():
        return
    print("Installing dependencies...")
    subprocess.run([str(python_bin), "-m", "pip", "install", "--upgrade", "pip"], check=True)
    subprocess.run([str(python_bin), "-m", "pip", "install", "-r", str(REQ_FILE)], check=True)


def ensure_animation() -> Path:
    if ANIMATION_FILE.exists():
        return ANIMATION_FILE

    video_path = find_video_file()
    if video_path is None:
        raise FileNotFoundError(
            "No source video found. Put your video in the project root as video.mp4 or name any .mp4 file next to run.py."
        )

    print(f"Generating animation from {video_path.name}...")
    subprocess.run(
        [
            sys.executable,
            str(ENCODER_FILE),
            str(video_path),
            "--output",
            str(ANIMATION_FILE),
            "--width",
            "300",
            "--fps",
            "60",
            "--quality",
            "ultra",
        ],
        check=True,
    )
    return ANIMATION_FILE


def main() -> int:
    python_bin = ensure_venv()
    ensure_requirements(python_bin)
    animation_path = ensure_animation()

    cmd = [
        str(python_bin),
        str(PLAYER_FILE),
        str(animation_path),
        "--loop",
        "--color",
        "truecolor",
    ]
    print("Launching ASCII video in terminal... Press Ctrl+C to stop.")
    return subprocess.call(cmd)


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except KeyboardInterrupt:
        print("\nStopped by user.")
        raise SystemExit(0)
    except Exception as exc:
        print(f"Error: {exc}", file=sys.stderr)
        raise SystemExit(1)

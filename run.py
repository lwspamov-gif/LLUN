from __future__ import annotations

import os
import shutil
import subprocess
import sys
import venv
from pathlib import Path

ROOT = Path(__file__).resolve().parent
REQ_FILE = ROOT / "requirements.txt"
PLAYER_FILE = ROOT / "player.py"
ANIMATION_FILE = ROOT / "output" / "animation.json.gz"


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


def ensure_animation() -> None:
    if ANIMATION_FILE.exists():
        return
    raise FileNotFoundError(
        "Animation file not found: " + str(ANIMATION_FILE) + "\n"
        "Generate it first with: python encoder.py video.mp4 --output output/animation.json.gz --width 300 --fps 60 --quality ultra"
    )


def main() -> int:
    ensure_animation()
    python_bin = ensure_venv()
    ensure_requirements(python_bin)
    cmd = [str(python_bin), str(PLAYER_FILE), str(ANIMATION_FILE), "--loop", "--fps", "60", "--color", "truecolor"]
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

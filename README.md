# ASCII-Video

ASCII-Video converts ordinary video to a terminal-native ASCII animation while preserving recognisable motion, contrast, and silhouettes.

## Features

- High-quality ASCII conversion tuned for terminal output
- ANSI True Color, 256-color, and monochrome rendering modes
- Quality profiles: `balanced`, `high`, and `ultra`
- Video input processing with aspect-ratio-aware resizing
- Automatic frame timing and loop playback
- Gzip-compressed `.avz` animation archive format
- Cross-platform design for Windows 10 and Ubuntu Linux
- PyInstaller build support for one-file executables

## Quick launch on Windows, Ubuntu, and Arch Linux

The project includes a universal one-command launcher. After cloning the repo, just run:

### Windows PowerShell

```powershell
python .\run.py
```

### Ubuntu / Arch Linux Bash

```bash
python3 ./run.py
```

This script automatically creates a local `.venv`, installs the required packages, checks for the animation file, and then starts the terminal playback loop. If you want to run the player manually after dependencies are installed, use:

```powershell
python .\player.py .\output\animation.json.gz --loop --fps 60 --color truecolor
```

```bash
python3 ./player.py ./output/animation.json.gz --loop --fps 60 --color truecolor
```

## Maximum quality

The default project settings target `ultra`, `truecolor`, 60 FPS, width 300, and an infinite loop.

For best visual fidelity at a width of 300 characters, use a terminal with:

- at least 300 columns available in the current window
- a monospaced font with moderate character aspect ratio
- a CPU capable of processing and rendering the frame stream without exceeding the display target
- a terminal that supports ANSI 24-bit color

The conversion process is CPU-bound. Rendering 300 columns at 60 FPS may require a fast machine, especially for longer videos. If the terminal cannot keep up, the player skips stale frames instead of accumulating delay.

The resulting `.avz` animation may be moderately large depending on frame count and color mode. For long clips, prefer the `balanced` or `high` modes when visual output and file size are both important.

## Example output

```
@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
@@@@@@@@@@@@@@@@@@@%%%###***++++==--::..      ..::--==++++***###%%%@@@@@@@@@@@@@@@@@@@
@@@@@@@@@@@@@@@@%#*+=-:.                 .                .:-=+*#%@@@@@@@@@@@@@@@@
@@@@@@@@@@@@@@@*+=-:.       ...:::::::-----:::::...       .:-=+*@@@@@@@@@@@@@@@
@@@@@@@@@@@@@@@*+=-:.   ..::----====+++++==----::..   .:-=+*@@@@@@@@@@@@@@@
@@@@@@@@@@@@@@@*+=-:.   ..::----====+++++==----::..   .:-=+*@@@@@@@@@@@@@@@
@@@@@@@@@@@@@@@*+=-:.       ...:::::::-----:::::...       .:-=+*@@@@@@@@@@@@@@@
@@@@@@@@@@@@@@@@%#*+=-:.                 .                .:-=+*#%@@@@@@@@@@@@@@@@
@@@@@@@@@@@@@@@@@@@%%%###***++++==--::..      ..::--==++++***###%%%@@@@@@@@@@@@@@@@@@@
@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
```

## Requirements

- Python 3.10+
- NumPy
- OpenCV
- Pillow
- PyInstaller
- pytest

## Setup on Windows 10 (PowerShell)

```powershell
cd "C:\path\to\ASCII-Video"
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
pip install -e .
```

## Setup on Ubuntu Linux (Bash)

```bash
cd /path/to/ASCII-Video
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
pip install -e .
```

## Setup on Arch Linux (Bash)

```bash
cd /path/to/ASCII-Video
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
pip install -e .
```

## Default configuration

The project default config is in `config/default.json` and contains these values:

```json
{
  "quality": "ultra",
  "color_mode": "truecolor",
  "target_fps": 60,
  "width": 300,
  "loop": true,
  "preserve_aspect_ratio": true,
  "adaptive_terminal_size": false,
  "skip_late_frames": true,
  "gamma": 1.0,
  "contrast": 1.1,
  "brightness": 0,
  "sharpen": 0.0,
  "charset": "@%#*+=-:. ",
  "unicode_half_block": false
}
```

Command-line arguments override the config file. If you do not pass a parameter, the default config applies.

## Convert a video

### PowerShell

```powershell
python -m ascii_video.encoder input/video.mp4 --output output/animation.avz --width 300 --fps 60 --quality ultra --color truecolor
```

### Bash

```bash
python -m ascii_video.encoder input/video.mp4 --output output/animation.avz --width 300 --fps 60 --quality ultra --color truecolor
```

## Play a generated animation

### PowerShell

```powershell
python -m ascii_video.player output/animation.avz --loop --fps 60 --color truecolor
```

### Bash

```bash
python -m ascii_video.player output/animation.avz --loop --fps 60 --color truecolor
```

## Quality and color modes

- `balanced`: good performance and moderate detail
- `high`: improved detail with modest CPU cost
- `ultra`: highest visual fidelity while keeping the pipeline efficient
- `monochrome`: single-color ANSI/text output
- `ansi256`: 256-color terminal palette
- `truecolor`: 24-bit RGB ANSI output; best quality in compatible terminals

## Build executables

### Windows 10 (PowerShell)

```powershell
cd "C:\path\to\ASCII-Video"
.\.venv\Scripts\Activate.ps1
pip install -r requirements-build.txt
powershell -ExecutionPolicy Bypass -File .\scripts\build_windows.ps1
```

### Ubuntu Linux (Bash)

```bash
cd /path/to/ASCII-Video
source .venv/bin/activate
pip install -r requirements-build.txt
chmod +x ./scripts/build_ubuntu.sh
./scripts/build_ubuntu.sh
```

## Embedded animation in builds

The build scripts embed a default animation resource selected from `assets/previews/` or `output/previews/` and use `sys._MEIPASS` resolution when running from a PyInstaller bundle. If the animation is not bundled, the executable prints a clear error.

## Telegram and distribution

To send to Telegram:

1. Build the executable.
2. Compress the file to a ZIP archive if needed.
3. Upload it to Telegram and share the link or file.
4. On another PC, run the binary directly without Python installed.

The app is designed as a single-file terminal binary for easy distribution.

## Common problems

- Terminal output is too wide: reduce `--width` or resize the terminal.
- Colors look wrong: switch to `--color monochrome` or use a terminal with 24-bit support.
- Playback lags: lower `--fps` or reduce `--width`.
- .avz file is invalid: regenerate the animation rather than reusing a truncated result.
- Linux executable fails to start: ensure `glibc` compatibility and build on a sufficiently old supported Ubuntu image.

## Terminal limitations

ASCII rendering is best in monospaced terminals. Fonts and terminal cell proportions vary, so the output is approximate rather than pixel-perfect. Some terminals may compress lines or change color handling. This project manages these differences with aspect-ratio-aware resizing and safe fallback modes.

## Test suite

```bash
pytest
```

## License

MIT

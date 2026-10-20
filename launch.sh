#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VIDEO="${1:-$ROOT/output/animation.json.gz}"
if [[ ! -f "$VIDEO" ]]; then
  echo "Animation file not found: $VIDEO" >&2
  echo "Create it first: python3 encoder.py video.mp4 --output output/animation.json.gz --width 300 --fps 60 --quality ultra" >&2
  exit 1
fi
python3 "$ROOT/player.py" "$VIDEO" --loop --fps 60 --color truecolor

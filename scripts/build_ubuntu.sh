#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
VENV="$ROOT/.venv"
PYINSTALLER="$VENV/bin/pyinstaller"
SPEC="$ROOT/packaging/ubuntu/ASCII-Video.spec"
DIST="$ROOT/dist"

if [[ ! -x "$PYINSTALLER" ]]; then
  echo "PyInstaller not found in $VENV. Install requirements-build.txt first."
  exit 1
fi

if [[ ! -f "$SPEC" ]]; then
  echo "Missing spec file: $SPEC"
  exit 1
fi

"$PYINSTALLER" --distpath "$DIST" --workpath "$ROOT/build" --specpath "$ROOT/packaging/ubuntu" "$SPEC"

echo "Ubuntu build complete: $DIST/ASCII-Video"

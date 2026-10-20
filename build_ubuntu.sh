#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ANIMATION="$ROOT/output/animation.json.gz"
SPEC="$ROOT/ubuntu.spec"

if [[ ! -f "$ANIMATION" ]]; then
  echo "Animation file not found: $ANIMATION" >&2
  echo "Generate it first: python3 encoder.py video.mp4 --output output/animation.json.gz --width 300 --fps 60 --quality ultra" >&2
  exit 1
fi

cat > "$SPEC" <<EOF
# -*- mode: python ; coding: utf-8 -*-
from pathlib import Path

root = Path(r"$ROOT")
block_cipher = None
animation = root / "output" / "animation.json.gz"

a = Analysis(
    [str(root / "player.py")],
    pathex=[str(root)],
    binaries=[],
    datas=[(str(animation), ".")],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
)
pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)
exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='ASCII-Video',
    debug=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
)
EOF

pyinstaller --distpath "$ROOT/dist" --workpath "$ROOT/build" "$SPEC"
chmod +x "$ROOT/dist/ASCII-Video"
echo "Ubuntu build complete: $ROOT/dist/ASCII-Video"

$ErrorActionPreference = 'Stop'
$Root = Split-Path -Parent $MyInvocation.MyCommand.Path
$VideoInput = Join-Path $Root 'video.mp4'
$AnimationPath = Join-Path $Root 'output\animation.json.gz'
$SpecPath = Join-Path $Root 'windows.spec'

if (-not (Test-Path $VideoInput)) {
    throw "Missing source video: $VideoInput. Place video.mp4 in the project root first."
}
if (-not (Test-Path $AnimationPath)) {
    throw "Animation file not found. Run: python encoder.py video.mp4 --output output/animation.json.gz --width 300 --fps 60 --quality ultra"
}

$pyinstaller = Get-Command pyinstaller -ErrorAction SilentlyContinue
if (-not $pyinstaller) {
    throw "PyInstaller not found. Activate your venv and run: pip install -r requirements-build.txt"
}

@'
# -*- mode: python ; coding: utf-8 -*-
from pathlib import Path

root = Path(r"$Root")
block_cipher = None
animation = root / "output" / "animation.json.gz"

a = Analysis(
    [str(root / "encoder.py")],
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
    name='ASCII-Video.exe',
    debug=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
)
'@ | Set-Content -Path $SpecPath -Encoding UTF8

pyinstaller --distpath (Join-Path $Root 'dist') --workpath (Join-Path $Root 'build') $SpecPath
Write-Host "Windows build complete: dist\ASCII-Video.exe"

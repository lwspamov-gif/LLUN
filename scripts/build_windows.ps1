$ErrorActionPreference = 'Stop'
$Root = Split-Path -Parent $PSScriptRoot
$Venv = Join-Path $Root '.venv'
$PyInstaller = Join-Path $Venv 'Scripts\pyinstaller.exe'
$Spec = Join-Path $Root 'packaging\windows\LLUN.spec'
$OutputDir = Join-Path $Root 'dist'

if (-not (Test-Path $PyInstaller)) {
    throw "PyInstaller not found in the virtual environment. Install requirements-build.txt first."
}

if (-not (Test-Path $Spec)) {
    throw "Missing spec file: $Spec"
}

& $PyInstaller --distpath $OutputDir --workpath (Join-Path $Root 'build') --specpath (Join-Path $Root 'packaging\windows') $Spec

Write-Host "Windows build complete: $OutputDir\LLUN.exe"

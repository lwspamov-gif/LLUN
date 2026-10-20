$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot

$PythonCommand = "python"
$PythonArgs = @()

if (Get-Command py -ErrorAction SilentlyContinue) {
    $PythonCommand = "py"
    $PythonArgs = @("-3")
} elseif (-not (Get-Command python -ErrorAction SilentlyContinue)) {
    throw "Python 3 not found. Install Python 3 and run the script again."
}

$VenvPython = Join-Path $PSScriptRoot ".venv\Scripts\python.exe"
if (-not (Test-Path $VenvPython)) {
    Write-Host "Creating virtual environment..."
    & $PythonCommand @PythonArgs -m venv .venv
    if ($LASTEXITCODE -ne 0) {
        throw "Failed to create the local virtual environment."
    }
}

Write-Host "Installing dependencies..."
& $VenvPython -m pip install --upgrade pip
if ($LASTEXITCODE -ne 0) {
    throw "Failed to upgrade pip."
}

& $VenvPython -m pip install -r requirements.txt
if ($LASTEXITCODE -ne 0) {
    throw "Failed to install dependencies from requirements.txt."
}

Write-Host "Launching ASCII-Video..."
& $VenvPython .\run.py
if ($LASTEXITCODE -ne 0) {
    throw "ASCII-Video exited with an error."
}

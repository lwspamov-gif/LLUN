param(
    [string]$Video = "output\animation.json.gz"
)

$Root = Split-Path -Parent $MyInvocation.MyCommand.Path
$FullPath = Join-Path $Root $Video

if (-not (Test-Path $FullPath)) {
    throw "Animation file not found: $FullPath. Create it first: python .\encoder.py .\video.mp4 --output .\output\animation.json.gz --width 300 --fps 60 --quality ultra"
}

python (Join-Path $Root 'player.py') $FullPath --loop --fps 60 --color truecolor

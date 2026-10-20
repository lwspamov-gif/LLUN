$ErrorActionPreference = "Stop"
$Root = $PSScriptRoot

$Command = @"
`$Host.UI.RawUI.WindowTitle = 'ASCII-Video'
`$Host.UI.RawUI.WindowState = 'Maximized'
Set-Location -LiteralPath '$Root'
& '$Root\run.ps1'
"@

Start-Process powershell.exe -ArgumentList @(
    "-NoExit",
    "-ExecutionPolicy", "Bypass",
    "-Command", $Command
)

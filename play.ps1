# Play the default game (2 players: you + 1 AI)
# Usage: .\play.ps1
# Or pass extra args which will be forwarded to the Python script: .\play.ps1 --simulate 1

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Definition
Push-Location $ScriptDir
try {
    python main.py --players 2 --ai-count 1 @args
} finally {
    Pop-Location
}

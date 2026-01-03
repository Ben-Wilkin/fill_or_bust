@echo off
REM Play the default game (2 players: you + 1 AI)
REM Usage: play.bat
REM Extra args are forwarded to the Python script: play.bat --simulate 1
pushd %~dp0
python main.py --players 2 --ai-count 1 %*
popd

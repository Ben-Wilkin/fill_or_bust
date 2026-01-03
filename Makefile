.PHONY: play ai simulate simulate-quick syntax

PY = python
MAIN = main.py

# Default: play a 2-player game (you + 1 AI)
play:
	$(PY) $(MAIN) --players 2 --ai-count 1

# Start a quick AI-only single simulated game
ai:
	$(PY) $(MAIN) --players 2 --ai --simulate 1

# Run several simulated games (change count as needed)
simulate:
	$(PY) $(MAIN) --players 3 --ai --simulate 100

# Short simulation for quick checks
simulate-quick:
	$(PY) $(MAIN) --players 3 --ai --simulate 5

# Basic syntax check
syntax:
	$(PY) -m py_compile $(MAIN)

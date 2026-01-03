# Fill or Bust (CLI)
# Fill or Bust (CLI)

A dice-based "Fill or Bust" variant with simple special-event cards that modify a turn.

Rules implemented:
- Players take turns rolling up to 6 six-sided dice.
- Scoring per roll:
	- Three of a kind: face value * 100 (three 1s = 1000).
	- Single 1s = 100 points each.
	- Single 5s = 50 points each.
	- Extras beyond three of a kind are NOT treated as escalating multipliers; additional dice only score separately when they are 1s or 5s.
- On each turn a player draws a special card which may grant a banking bonus, skip the turn, force a bust, or apply other turn-specific rules.
- Players may keep scoring dice from a roll, add points to their turn total, and choose to roll remaining dice or bank the turn total into their permanent score.
- If a roll contains no scoring dice the player busts and scores 0 for that turn (some card effects may alter this behavior).
- First player to reach the configured points target (default 2000) wins.

Quick start:

```bash
python main.py --players 2                # play 2-player interactive game
python main.py --players 3 --ai-count 2   # play with 2 AI players
python main.py --players 3 --ai --simulate 20  # simulate 20 games with all-AI players
```

Options of note:
- `--points-to-win`: points required to win (default 2000)
- `--ai-threshold-points`: AI banks after accumulating this many points in a turn (default 500)
- `--ai-count`: number of AI players (last N players will be AI); `--ai` makes all players AI
- `--seed`: seed RNG for reproducible simulations
- `--gui`: use a simple Tkinter dialog-based GUI for prompts instead of command-line input

The game supports interactive human players (choose which scoring dice to keep) and simple AI players.

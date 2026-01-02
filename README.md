# Fill or Bust (CLI)

A dice-based implementation of "Fill or Bust" (Farkle-style scoring).

Rules implemented:
- Players take turns rolling up to 6 dice.
- Scoring per roll:
	- Single 1s = 100 points each.
	- Single 5s = 50 points each.
	- Three of a kind = face * 100 (three 1s = 1000). If more than three of a kind are rolled, each extra die doubles the three-of-a-kind value (4 of a kind = 2x, 5 of a kind = 4x, 6 of a kind = 8x).
- A player may choose any scoring dice to keep, add their points to the turn total, then either roll the remaining dice or bank the turn total into their permanent score.
- If a roll contains no scoring dice the player busts and scores 0 for that turn.
- First player to reach the points target (default 2000) wins.

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

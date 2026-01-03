"""Fill or Bust - command-line implementation

Dice-based "Fill or Bust" variant with simple special-event cards.

Overview:
- Players take turns rolling up to 6 six-sided dice.
- Scoring per roll:
    - Three of a kind: face value * 100 (three 1s = 1000).
    - Single 1s = 100 points each.
    - Single 5s = 50 points each.
    - Extras beyond three of a kind are NOT treated as escalating multipliers; additional dice only score separately when they are 1s or 5s.
- On each turn a player draws a special card which may modify the turn (bonus points, skip, forced bust, etc.).
- A player may keep scoring dice from a roll, add their points to the turn total, then either roll the remaining dice or bank the turn total into their permanent score.
- If a roll contains no scoring dice the player busts and scores 0 for that turn (some card effects may alter this).

Usage examples:
    python main.py --players 2            # interactive with 2 human players
    python main.py --players 3 --ai --simulate 5   # run 5 simulated games with 3 AI players
"""

import argparse
import random
import sys
from collections import Counter
from dataclasses import dataclass
try:
    import tkinter as tk
    from tkinter import simpledialog, messagebox
    TK_AVAILABLE = True
except Exception:
    TK_AVAILABLE = False


class CardDeckSpecial:
    def __init__(self, seed=None):
        self.seed = seed
        self.rng = random.Random(seed)
        # simple deck composition
        self.cards = (['bonus300'] * 6 + ['bonus400'] * 4 + ['bonus500'] * 2 + ['no_dice'] * 3 + ['must_bust'] * 3 + ['double_trouble'] * 2)
        self.rng.shuffle(self.cards)

    def draw(self):
        if not self.cards:
            self.__init__(seed=self.seed)
        return self.cards.pop()


@dataclass
class Player:
    name: str
    is_ai: bool = False
    points: int = 0


def score_dice(dice):
    """Score a list of dice (values 1-6).

    Rules implemented:
    - Three of a kind: face value * 100 (three 1s = 1000).
    - Extras beyond three are NOT treated as multiplier escalation; additional dice only score separately when they are 1s or 5s.
    - Single 1s are worth 100 each.
    - Single 5s are worth 50 each.

    Returns (score, breakdown) where breakdown is a dict of face->count used for scoring.
    """
    cnt = Counter(dice)
    score = 0
    used = Counter()
    # Treat three-of-a-kind as exactly three dice; extras beyond three count as singles (1s and 5s)
    for face in range(1, 7):
        c = cnt.get(face, 0)
        if c >= 3:
            base = 1000 if face == 1 else face * 100
            score += base
            used[face] += 3
            cnt[face] = c - 3

    # singles (only 1s and 5s score individually)
    if cnt.get(1, 0) > 0:
        score += cnt[1] * 100
        used[1] += cnt[1]
    if cnt.get(5, 0) > 0:
        score += cnt[5] * 50
        used[5] += cnt[5]

    return score, used


def is_scoring_roll(dice):
    s, _ = score_dice(dice)
    return s > 0


def make_players(n, ai_count=0):
    players = []
    for i in range(1, n + 1):
        is_ai = (i > n - ai_count) if ai_count > 0 else False
        players.append(Player(name=f"P{i}", is_ai=is_ai))
    return players


class Game:
    def __init__(self, players, points_to_win=2000, ai_threshold_points=500, seed=None, verbose=True, use_gui=False):
        self.players = players
        self.points_to_win = points_to_win
        self.ai_threshold_points = ai_threshold_points
        self.verbose = verbose
        self.rng = random.Random(seed)
        self.card_deck = CardDeckSpecial(seed=seed)
        self.use_gui = use_gui

    def _prompt(self, prompt):
        if self.use_gui and TK_AVAILABLE:
            root = tk.Tk(); root.withdraw()
            try:
                res = simpledialog.askstring("Input", prompt)
            finally:
                root.destroy()
            return res or ''
        else:
            return input(prompt)

    def _ack(self, prompt):
        if self.use_gui and TK_AVAILABLE:
            root = tk.Tk(); root.withdraw()
            try:
                messagebox.showinfo("Notice", prompt)
            finally:
                root.destroy()
            return
        else:
            ack = ''
            while ack.lower() != 'y':
                ack = input(prompt).strip()
            return

    def _info(self, msg):
        if self.use_gui and TK_AVAILABLE:
            root = tk.Tk(); root.withdraw()
            try:
                messagebox.showinfo("Info", msg)
            finally:
                root.destroy()
        else:
            print(msg)

    def roll(self, n):
        return [self.rng.randint(1, 6) for _ in range(n)]

    def play_turn(self, player, interactive=True):
        if self.verbose:
            self._info(f"{player.name}'s turn (score {player.points}/{self.points_to_win})")

        # draw a special card at start of turn
        special = self.card_deck.draw()
        special_state = {
            'bonus': 0,
            'no_dice': False,
            'must_bust': False,
            'double_trouble': False
        }
        if special.startswith('bonus'):
            special_state['bonus'] = int(special.replace('bonus', ''))
            if self.verbose:
                self._info(f"Drew card: BONUS {special_state['bonus']} if you bank this turn.")
        elif special == 'no_dice':
            special_state['no_dice'] = True
            if self.verbose:
                self._info("Drew card: NO DICE - turn skipped.")
        elif special == 'must_bust':
            special_state['must_bust'] = True
            if self.verbose:
                self._info("Drew card: MUST BUST - you cannot bank; if you bust you still keep your turn points.")
        elif special == 'double_trouble':
            special_state['double_trouble'] = True
            if self.verbose:
                self._info("Drew card: DOUBLE TROUBLE - you must fill (use all dice) twice before banking is allowed.")

        if special_state['no_dice']:
            if not player.is_ai and interactive:
                self._ack("No dice this turn — press 'y' to continue:")
            return 0

        dice_left = 6
        turn_points = 0
        fills = 0

        while True:
            roll = self.roll(dice_left)
            score, breakdown = score_dice(roll)
            if self.verbose:
                if self.verbose:
                    self._info(f"Rolled: {roll} -> scoring {score} (breakdown: {dict(breakdown)})")

            if score == 0:
                if self.verbose:
                    if self.verbose:
                        self._info(f"{player.name} busted and scored 0 this turn.")
                # If must_bust card is active: player keeps turn points on bust
                if special_state.get('must_bust'):
                    if self.verbose:
                        if self.verbose:
                            self._info(f"{player.name} had MUST BUST: keeps {turn_points} points despite busting.")
                    player.points += turn_points
                # else normal bust
                # If human interactive, require acknowledgement before continuing
                if interactive and not player.is_ai:
                    self._ack("You busted — press 'y' to continue:")
                return 0

            # interactive: let player select which scoring dice to keep
            if player.is_ai or not interactive:
                # Simple AI/hardcoded policy: keep all scoring dice that give positive score
                taken_score = score
                # For simplicity, assume taking all scoring dice
                turn_points += taken_score
                # determine how many dice were used
                used_count = sum(breakdown.values())
                dice_left -= used_count
                if dice_left == 0:
                    # hot dice: player used all dice once during this turn
                    fills += 1
                    # If a bonus card was drawn, add it to the running turn total when the player fills.
                    if special_state.get('bonus') and not special_state.get('bonus_added'):
                        turn_points += special_state['bonus']
                        special_state['bonus_added'] = True
                        if self.verbose and player.is_ai:
                            self._info(f"{player.name} (AI) receives bonus {special_state['bonus']} added to turn total for filling this turn.")
                    dice_left = 6
                if self.verbose and player.is_ai:
                    if self.verbose and player.is_ai:
                        self._info(f"{player.name} (AI) takes {taken_score} points this roll, turn total {turn_points}.")
                # AI bank decision
                if player.is_ai and turn_points >= self.ai_threshold_points:
                    # AI banks; include bonus only if the player filled (used all dice) this turn
                    player.points += turn_points
                    if special_state.get('bonus') and fills > 0:
                        player.points += special_state['bonus']
                    if self.verbose:
                        if self.verbose:
                            self._info(f"{player.name} (AI) banks and now has {player.points} points.")
                    return turn_points
                # continue rolling
                continue

            # Human interactive: ask which dice to keep or bank
            # Present roll and scoring breakdown; accept indices to keep or 'b' to bank
            # Human interactive: show indexed roll and ask which scoring dice to keep
            print(" Scoring dice breakdown:")
            if not self.use_gui:
                print(" Scoring dice breakdown:")
                print(f"  {dict(breakdown)}")
            # show roll with indices
            indexed = ' '.join(f"[{i+1}:{v}]" for i, v in enumerate(roll))

            # In GUI mode, show roll and breakdown in a dialog
            if self.use_gui and TK_AVAILABLE:
                root = tk.Tk(); root.withdraw()
                try:
                    messagebox.showinfo("Roll", f"Roll: {indexed}\nScoring: {dict(breakdown)}")
                finally:
                    root.destroy()

            # determine which positions in the roll are scoring (indices 0-based)
            face_positions = {}
            for i, v in enumerate(roll):
                face_positions.setdefault(v, []).append(i)
            scoring_indices = set()
            for face, positions in face_positions.items():
                c = len(positions)
                if c >= 3:
                    # first three of a kind are scoring
                    scoring_indices.update(positions[:3])
                    # extras of 1s or 5s also score individually
                    if face in (1, 5) and c > 3:
                        scoring_indices.update(positions[3:])
                else:
                    if face in (1, 5):
                        scoring_indices.update(positions)

            while True:
                choice = self._prompt("(k)eep all scoring dice, (c)hoose indices from roll (e.g. 1 3), or (b)ank? [k/c/b]: ").strip().lower()
                if choice in ('k', 'b', 'c'):
                    break
            if choice == 'b':
                # Bank allowed? for DOUBLE TROUBLE require at least 2 fills
                if special_state.get('double_trouble') and fills < 2:
                    self._info("DOUBLE TROUBLE active: you must fill twice before banking is allowed.")
                    continue
                player.points += turn_points
                if self.verbose:
                    self._info(f"{player.name} banks {turn_points} points and now has {player.points}.")
                return turn_points

            if choice == 'k':
                taken_score = score
                taken_count = sum(breakdown.values())
            else:
                # choose indices
                try:
                    parts = self._prompt("Enter 1-based indices of dice to keep (space-separated): ").strip().split()
                    idx = [int(p) - 1 for p in parts]
                    if any(i < 0 or i >= len(roll) for i in idx):
                        print(" Invalid indices; try again.")
                        continue
                    # ensure chosen indices are all scoring positions
                    if not set(idx).issubset(scoring_indices):
                        print(" You selected non-scoring dice; choose only scoring dice.")
                        continue
                    chosen = [roll[i] for i in idx]
                    taken_score, _ = score_dice(chosen)
                    if taken_score == 0:
                        print(" Chosen dice do not score; choose scoring dice.")
                        continue
                    taken_count = len(chosen)
                except ValueError:
                    print(" Invalid input; try again.")
                    continue

            turn_points += taken_score
            dice_left -= taken_count
            # track fills
            if dice_left == 0:
                fills += 1
                # If a bonus card was drawn, add it to the running turn total when the player fills.
                if special_state.get('bonus') and not special_state.get('bonus_added'):
                    turn_points += special_state['bonus']
                    special_state['bonus_added'] = True
                    if self.verbose:
                        self._info(f"{player.name} receives bonus {special_state['bonus']} added to turn total for filling this turn.")
                dice_left = 6

            if self.verbose:
                self._info(f"{player.name} keeps {taken_score} points this pick; turn total {turn_points}. Dice left: {dice_left}")

            # ask to continue or bank (prompt every scoring roll)
            cont = ''
            while cont not in ('r', 'b'):
                cont = self._prompt("(r)oll again or (b)ank? [r/b]: ").strip().lower()
            if cont == 'b':
                player.points += turn_points
                if self.verbose:
                    self._info(f"{player.name} banks {turn_points} points and now has {player.points}.")
                return turn_points
            # else roll again with remaining dice

    def run(self, interactive=True):
        while True:
            for player in self.players:
                self.play_turn(player, interactive=interactive)
                if player.points >= self.points_to_win:
                    if self.verbose:
                        print(f"\n{player.name} wins with {player.points} points!")
                    return player


def parse_args():
    p = argparse.ArgumentParser(description='Fill or Bust - dice-based CLI')
    p.add_argument('--players', type=int, default=2)
    p.add_argument('--gui', action='store_true', help='Use GUI dialogs instead of command-line prompts')
    p.add_argument('--ai', action='store_true', help='Make all players AI')
    p.add_argument('--ai-count', type=int, default=0, help='Number of AI players (last N players will be AI)')
    p.add_argument('--ai-threshold-points', type=int, default=500, help='AI banks after this many points in a turn')
    p.add_argument('--points-to-win', type=int, default=2000, help='Points required to win')
    p.add_argument('--simulate', type=int, default=0, help='Run N simulated games (non-interactive)')
    p.add_argument('--seed', type=int, default=None)
    return p.parse_args()


def main():
    args = parse_args()

    ai_count = args.players if args.ai else args.ai_count
    if args.simulate > 0:
        wins = {}
        for s in range(args.simulate):
            players = make_players(args.players, ai_count=ai_count)
            game = Game(players, points_to_win=args.points_to_win, ai_threshold_points=args.ai_threshold_points, seed=args.seed, verbose=False)
            winner = game.run(interactive=False)
            if winner:
                wins[winner.name] = wins.get(winner.name, 0) + 1
        print(f"Simulated {args.simulate} games. Win counts: {wins}")
        return

    players = make_players(args.players, ai_count=ai_count)
    human_count = args.players - ai_count
    # name prompt: use GUI dialog if requested
    if args.gui and TK_AVAILABLE:
        root = tk.Tk(); root.withdraw()
        try:
            for i, p in enumerate(players[:human_count]):
                newname = simpledialog.askstring("Name", f"Name for player {p.name} (enter to keep): ") or ''
                newname = newname.strip()
                if newname:
                    p.name = newname
        finally:
            root.destroy()
    else:
        for i, p in enumerate(players[:human_count]):
            newname = input(f"Name for player {p.name} (enter to keep): ").strip()
            if newname:
                p.name = newname

    game = Game(players, points_to_win=args.points_to_win, ai_threshold_points=args.ai_threshold_points, seed=args.seed, verbose=True, use_gui=args.gui)
    # Always run interactive mode for human play so human players are prompted each roll. yup
    game.run(interactive=True)


if __name__ == '__main__':
    main()

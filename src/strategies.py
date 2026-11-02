"""Bankroll-aware strategies. All balances are virtual credits."""
from dataclasses import dataclass
import numpy as np
from src.metrics import max_drawdown

@dataclass
class SessionResult:
    ending_bankroll: float
    rounds_played: int
    ruined: bool
    hit_target: bool
    max_stake: float
    total_wagered: float
    net_profit: float
    max_drawdown: float
    bankroll_path: list[float]

def run_session(rng, outcomes, starting_bankroll=100.0, base_stake=1.0,
                strategy="fixed", target_bankroll=None, max_bet=100.0,
                max_rounds=1000, percentage=0.01):
    if starting_bankroll < 0 or base_stake <= 0 or max_bet <= 0 or max_rounds <= 0:
        raise ValueError("Invalid bankroll, stake, max bet, or rounds")
    if strategy not in {"fixed", "martingale", "reverse_martingale", "percentage"}:
        raise ValueError("Unknown strategy")
    bankroll = float(starting_bankroll)
    path = [bankroll]
    total_wagered = 0.0
    largest = 0.0
    stake = float(base_stake)
    previous_won = False
    ruined = bankroll <= 0
    hit_target = target_bankroll is not None and bankroll >= target_bankroll
    rounds_played = 0

    for outcome in outcomes[:max_rounds]:
        if ruined or hit_target:
            break
        if strategy == "percentage":
            stake = max(0.0, bankroll * percentage)
        elif strategy == "martingale" and rounds_played > 0:
            stake = base_stake if previous_won else min(stake * 2, max_bet)
        elif strategy == "reverse_martingale" and rounds_played > 0:
            stake = min(stake * 2, max_bet) if previous_won else base_stake
        stake = min(stake, max_bet, bankroll)
        if stake <= 0:
            ruined = True
            break
        unit_profit = float(outcome)
        total_wagered += stake
        largest = max(largest, stake)
        bankroll = max(0.0, bankroll + unit_profit * stake)
        rounds_played += 1
        previous_won = unit_profit > 0
        path.append(bankroll)
        if bankroll <= 0:
            ruined = True
        if target_bankroll is not None and bankroll >= target_bankroll:
            hit_target = True

    return SessionResult(
        ending_bankroll=bankroll, rounds_played=rounds_played, ruined=ruined,
        hit_target=hit_target, max_stake=largest, total_wagered=total_wagered,
        net_profit=bankroll-starting_bankroll, max_drawdown=max_drawdown(path),
        bankroll_path=path,
    )

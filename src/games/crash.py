"""Simplified educational crash model, not a replica of any real platform."""
import numpy as np

def simulate_crash_rounds(rng: np.random.Generator, rounds: int,
                          cashout_multiplier: float = 2.0,
                          rtp: float = 0.97, stake: float = 1.0):
    if rounds <= 0 or cashout_multiplier <= 1 or stake <= 0:
        raise ValueError("Invalid rounds, cashout multiplier, or stake")
    if not 0 <= rtp <= 1:
        raise ValueError("rtp must be in [0, 1]")
    p_win = min(1.0, rtp / cashout_multiplier)
    wins = rng.random(rounds) < p_win
    net = np.where(wins, stake * (cashout_multiplier - 1), -stake)
    return wins, net

def theoretical_ev(stake: float = 1.0, rtp: float = 0.97):
    if stake <= 0 or not 0 <= rtp <= 1:
        raise ValueError("Invalid stake or RTP")
    return stake * (rtp - 1)

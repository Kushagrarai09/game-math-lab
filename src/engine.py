"""Vectorized Monte Carlo engine and independent-session bankroll experiments."""
import numpy as np
import pandas as pd
from src.games.dice import DiceConfig
from src.games.crash import simulate_crash_rounds
from src.games.plinko import simulate_plinko_rounds
from src.metrics import mean_confidence_interval, wilson_interval
from src.strategies import run_session

def simulate_game(game="dice", rounds=1_000_000, seed=42, stake=1.0,
                  rtp=0.98, win_probability=0.49, cashout=2.0, rows=8):
    if rounds <= 0:
        raise ValueError("rounds must be positive")
    rng = np.random.default_rng(seed)
    if game == "dice":
        config = DiceConfig(win_probability=win_probability, rtp=rtp, stake=stake)
        wins, net = config.sample_net_profit(rng, rounds)
        theoretical_ev = config.theoretical_ev
        win_rate = float(wins.mean())
        win_count = int(wins.sum())
        gross_returns = np.where(wins, stake * config.gross_payout_multiplier, 0)
        extras = {}
    elif game == "crash":
        wins, net = simulate_crash_rounds(rng, rounds, cashout, rtp, stake)
        theoretical_ev = stake * (rtp - 1)
        win_rate = float(wins.mean())
        win_count = int(wins.sum())
        gross_returns = np.where(wins, stake * cashout, 0)
        extras = {"cashout_multiplier": cashout}
    elif game == "plinko":
        buckets, net, multipliers, probs = simulate_plinko_rounds(rng, rounds, rows, rtp, stake)
        theoretical_ev = stake * (rtp - 1)
        win_rate = float((net > 0).mean())
        win_count = int((net > 0).sum())
        gross_returns = net + stake
        extras = {"rows": rows, "bucket_counts": np.bincount(buckets, minlength=rows+1).tolist(),
                  "bucket_probabilities": probs.tolist(), "gross_multipliers": multipliers.tolist()}
    else:
        raise ValueError("game must be dice, crash, or plinko")
    lo, hi = mean_confidence_interval(net)
    win_lo, win_hi = wilson_interval(win_count, rounds)
    total_wagered = rounds * stake
    return {
        "game": game, "rounds": rounds, "seed": seed, "stake": stake,
        "rtp_theoretical": rtp, "rtp_observed": float(gross_returns.sum()/total_wagered),
        "house_edge_theoretical": 1-rtp, "theoretical_ev_per_round": theoretical_ev,
        "observed_ev_per_round": float(net.mean()), "ev_ci_low": lo, "ev_ci_high": hi,
        "win_rate": win_rate, "win_rate_ci_low": win_lo, "win_rate_ci_high": win_hi,
        "variance_per_round": float(net.var(ddof=1)) if rounds > 1 else 0.0,
        "stddev_per_round": float(net.std(ddof=1)) if rounds > 1 else 0.0,
        "total_wagered": float(total_wagered), "total_returned": float(gross_returns.sum()),
        "net_profit": float(net.sum()), "net_outcomes": net, **extras
    }

def convergence_frame(net_outcomes, theoretical_ev, points=500):
    net = np.asarray(net_outcomes, dtype=float)
    if net.size == 0:
        return pd.DataFrame(columns=["round", "observed_ev", "theoretical_ev"])
    indices = np.unique(np.linspace(1, net.size, min(points, net.size), dtype=int))
    cumulative = np.cumsum(net)
    return pd.DataFrame({"round": indices, "observed_ev": cumulative[indices-1]/indices,
                         "theoretical_ev": theoretical_ev})

def simulate_sessions(game="dice", sessions=3000, rounds_per_session=1000,
                      starting_bankroll=100.0, base_stake=1.0, rtp=0.98,
                      win_probability=0.49, strategy="fixed", seed=42,
                      target_bankroll=None, max_bet=100.0):
    if sessions <= 0 or rounds_per_session <= 0:
        raise ValueError("sessions and rounds_per_session must be positive")
    rng = np.random.default_rng(seed)
    results = []
    for _ in range(sessions):
        if game == "dice":
            cfg = DiceConfig(win_probability=win_probability, rtp=rtp, stake=1.0)
            _, outcomes = cfg.sample_net_profit(rng, rounds_per_session)
        elif game == "crash":
            _, outcomes = simulate_crash_rounds(rng, rounds_per_session, 2.0, rtp, 1.0)
        elif game == "plinko":
            _, outcomes, _, _ = simulate_plinko_rounds(rng, rounds_per_session, 8, rtp, 1.0)
        else:
            raise ValueError("game must be dice, crash, or plinko")
        results.append(run_session(rng, outcomes, starting_bankroll, base_stake,
                                   strategy, target_bankroll, max_bet, rounds_per_session))
    return pd.DataFrame([{
        "ending_bankroll": x.ending_bankroll, "rounds_played": x.rounds_played,
        "ruined": x.ruined, "hit_target": x.hit_target, "max_stake": x.max_stake,
        "total_wagered": x.total_wagered, "net_profit": x.net_profit,
        "max_drawdown": x.max_drawdown
    } for x in results])

"""Symmetric binomial-bucket Plinko toy model with configurable payouts."""
import math
import numpy as np

def bucket_probabilities(rows: int = 8):
    if not 1 <= rows <= 30:
        raise ValueError("rows must be between 1 and 30")
    return np.array([math.comb(rows, k) / (2 ** rows) for k in range(rows + 1)])

def simulate_plinko_rounds(rng: np.random.Generator, rounds: int,
                            rows: int = 8, rtp: float = 0.97,
                            stake: float = 1.0):
    if rounds <= 0 or stake <= 0 or not 0 <= rtp <= 1:
        raise ValueError("Invalid rounds, stake, or RTP")
    probs = bucket_probabilities(rows)
    raw = np.array([1.0 / (1 + abs(k - rows / 2)) for k in range(rows + 1)])
    raw_mean = float(np.dot(probs, raw))
    gross_multipliers = raw * (rtp / raw_mean)
    buckets = rng.choice(np.arange(rows + 1), size=rounds, p=probs)
    net = stake * (gross_multipliers[buckets] - 1)
    return buckets, net, gross_multipliers, probs

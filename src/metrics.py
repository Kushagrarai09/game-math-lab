"""Statistical metrics with explicit denominators and uncertainty estimates."""
import math
import numpy as np

def wilson_interval(successes: int, trials: int, z: float = 1.96):
    if trials <= 0:
        return (float("nan"), float("nan"))
    p = successes / trials
    denom = 1 + z*z/trials
    center = (p + z*z/(2*trials)) / denom
    half = z * math.sqrt(p*(1-p)/trials + z*z/(4*trials*trials)) / denom
    return max(0.0, center-half), min(1.0, center+half)

def mean_confidence_interval(values, z: float = 1.96):
    x = np.asarray(values, dtype=float)
    if x.size == 0:
        return (float("nan"), float("nan"))
    mean = float(x.mean())
    if x.size < 2:
        return (mean, mean)
    se = float(x.std(ddof=1) / np.sqrt(x.size))
    return mean-z*se, mean+z*se

def max_drawdown(bankroll_path):
    x = np.asarray(bankroll_path, dtype=float)
    if x.size == 0:
        return 0.0
    peaks = np.maximum.accumulate(x)
    safe_peaks = np.where(peaks > 0, peaks, 1.0)
    return float(np.max((peaks - x) / safe_peaks))

def theoretical_rtp_from_net_ev(stake: float, ev: float):
    if stake <= 0:
        raise ValueError("stake must be positive")
    return 1 + ev / stake

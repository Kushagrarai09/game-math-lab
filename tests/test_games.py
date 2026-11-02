import numpy as np
import pytest
from src.games.dice import DiceConfig
from src.games.plinko import bucket_probabilities
from src.engine import simulate_game

def test_dice_theoretical_ev():
    cfg = DiceConfig(win_probability=0.49, rtp=0.98, stake=1)
    assert cfg.theoretical_ev == pytest.approx(-0.02)

def test_seed_reproducibility():
    a = simulate_game(rounds=10000, seed=123)
    b = simulate_game(rounds=10000, seed=123)
    assert np.array_equal(a["net_outcomes"], b["net_outcomes"])

def test_large_sample_ev_near_theory():
    r = simulate_game(rounds=300_000, seed=9, rtp=0.98)
    assert abs(r["observed_ev_per_round"] - r["theoretical_ev_per_round"]) < 0.01

def test_plinko_probabilities_sum_to_one():
    assert bucket_probabilities(8).sum() == pytest.approx(1.0)

def test_invalid_rounds():
    with pytest.raises(ValueError):
        simulate_game(rounds=0)

def test_invalid_dice_config():
    with pytest.raises(ValueError):
        DiceConfig(win_probability=0, rtp=0.98).validate()

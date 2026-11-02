import numpy as np
import pytest
from src.strategies import run_session

def test_immediate_ruin():
    result = run_session(np.random.default_rng(1), [-1], starting_bankroll=1,
                         base_stake=1, max_rounds=10)
    assert result.ruined
    assert result.ending_bankroll == 0

def test_target_stop():
    result = run_session(np.random.default_rng(1), [1, 1, 1],
                         starting_bankroll=10, base_stake=1,
                         target_bankroll=11, max_rounds=3)
    assert result.hit_target
    assert result.rounds_played == 1

def test_unknown_strategy():
    with pytest.raises(ValueError):
        run_session(np.random.default_rng(1), [1], strategy="magic")

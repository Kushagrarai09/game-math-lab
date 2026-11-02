import numpy as np
import pytest
from src.metrics import wilson_interval, mean_confidence_interval, max_drawdown

def test_wilson_interval_contains_observed_rate():
    low, high = wilson_interval(49, 100)
    assert low <= 0.49 <= high

def test_mean_interval_for_constant_data():
    low, high = mean_confidence_interval([2, 2, 2])
    assert low == pytest.approx(2)
    assert high == pytest.approx(2)

def test_max_drawdown():
    assert max_drawdown([100, 120, 90, 110]) == pytest.approx(0.25)

def test_empty_interval():
    low, high = mean_confidence_interval([])
    assert np.isnan(low) and np.isnan(high)

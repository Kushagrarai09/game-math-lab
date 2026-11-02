"""Transparent binary dice model. Payout multipliers include returned stake."""
from dataclasses import dataclass
import numpy as np

@dataclass(frozen=True)
class DiceConfig:
    win_probability: float = 0.49
    rtp: float = 0.98
    stake: float = 1.0

    def validate(self):
        if not 0 < self.win_probability <= 1:
            raise ValueError("win_probability must be in (0, 1]")
        if not 0 <= self.rtp <= 1:
            raise ValueError("rtp must be in [0, 1]")
        if self.stake <= 0:
            raise ValueError("stake must be positive")

    @property
    def gross_payout_multiplier(self):
        self.validate()
        return self.rtp / self.win_probability

    @property
    def theoretical_ev(self):
        self.validate()
        return self.stake * (self.rtp - 1)

    def sample_net_profit(self, rng: np.random.Generator, rounds: int):
        self.validate()
        wins = rng.random(rounds) < self.win_probability
        profits = np.where(
            wins,
            self.stake * (self.gross_payout_multiplier - 1),
            -self.stake,
        )
        return wins, profits

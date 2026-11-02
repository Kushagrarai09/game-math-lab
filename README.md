# Game Math Lab — Monte Carlo RTP Simulator

A reproducible Python research project for understanding RTP, house edge, expected value, variance, confidence intervals, bankroll risk, and staking strategies using virtual credits.

## Features

- NumPy vectorized simulations for dice, simplified crash, and binomial Plinko models
- Theoretical and observed RTP / EV reported separately
- Wilson confidence intervals for win rates and approximate 95% confidence intervals for mean net outcomes
- EV convergence and per-round outcome distribution charts
- Independent bankroll sessions with target stops, ruin stops, max stake and drawdown tracking
- Fixed stake, Martingale, Reverse Martingale and percentage staking
- Streamlit dashboard with CSV exports
- Seeded random-number generation and pytest suite

## Important modeling notes

- This is an educational simulation, not a real-money gambling product.
- Gross payouts include returned stakes. Net profit is gross payout minus the stake.
- Dice and crash models are simplified distributions with configurable theoretical RTP.
- The crash model intentionally uses a direct win/loss probability at the chosen cash-out threshold. It does not claim to reproduce a particular platform's crash process.
- Plinko uses binomial bucket probabilities and a simple symmetric risk-shaped payout schedule scaled to the configured RTP.
- A simulated strategy does not change the underlying expectation per unit wager. Strategy comparisons must also report total wagered, constraints, stopping rules and risk metrics.
- Monte Carlo estimates have sampling error. Use confidence intervals and repeat experiments with different seeds.
- The bankroll engine models stake affordability, a zero-bankroll floor, target stopping, and a maximum bet. It is a simplified research model; review assumptions before using results in a report.

## Setup (Windows PowerShell)

```powershell
py -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m streamlit run app.py
```

If PowerShell blocks script activation, use the environment's Python executable as above; activation is not required.

## Run tests

```powershell
.\.venv\Scripts\python.exe -m pytest -q
```

## Run a million-round experiment from Python

```python
from src.engine import simulate_game

result = simulate_game(
    game="dice",
    rounds=1_000_000,
    seed=42,
    stake=1.0,
    rtp=0.98,
    win_probability=0.49,
)
for key, value in result.items():
    if key != "net_outcomes":
        print(key, value)
```

## Project phases

1. **Mathematical correctness:** configurable game models, formulas, validation, deterministic tests.
2. **Statistical analysis:** confidence intervals, variance, convergence, outcome distributions and independent sessions.
3. **Bankroll engine:** affordability, ruin/target stops, maximum bet, drawdown and session summaries.
4. **Games and strategies:** dice, crash and Plinko models; fixed, Martingale, Reverse Martingale and percentage strategies.
5. **Dashboard and portfolio:** Streamlit / Plotly dashboard, exports, tests, reproducible runs and documentation.

## Suggested portfolio screenshots

1. RTP and EV metric cards
2. EV convergence chart with theoretical reference
3. Per-round outcome histogram
4. Ending bankroll histogram and estimated ruin rate
5. A short experiment comparing strategies under matched assumptions

## Known limitations / next improvements

- Add exact binomial confidence intervals or bootstrap intervals for highly skewed outcomes.
- Add more robust strategy-comparison harness with paired seeds and matched exposure.
- Add configuration persistence and richer CSV exports for all session paths.
- Add continuous integration (GitHub Actions) and code coverage.

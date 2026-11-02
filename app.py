import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from src.engine import simulate_game, convergence_frame, simulate_sessions

st.set_page_config(page_title="Game Math Lab", page_icon="📊", layout="wide")
st.title("📊 Game Math Lab")
st.caption("Monte Carlo RTP, expected value, bankroll risk and strategy research — virtual credits only.")

with st.sidebar:
    st.header("Experiment")
    game = st.selectbox("Game model", ["dice", "crash", "plinko"])
    rounds = st.select_slider("Rounds per experiment", options=[1_000, 10_000, 100_000, 1_000_000], value=100_000)
    seed = st.number_input("Random seed", min_value=0, max_value=2**31-1, value=42)
    stake = st.number_input("Stake per round", min_value=0.01, value=1.0, step=0.25)
    rtp = st.slider("Target RTP", min_value=0.50, max_value=1.00, value=0.98, step=0.01)
    if game == "dice":
        win_probability = st.slider("Win probability", min_value=0.01, max_value=1.00, value=0.49, step=0.01)
    else:
        win_probability = 0.49
    cashout = st.slider("Cash-out multiplier", min_value=1.1, max_value=10.0, value=2.0, step=0.1) if game == "crash" else 2.0
    rows = st.slider("Plinko rows", min_value=4, max_value=16, value=8) if game == "plinko" else 8
    run = st.button("Run experiment", type="primary", use_container_width=True)

if "experiment" not in st.session_state:
    st.session_state.experiment = None
if run:
    with st.spinner("Running vectorized Monte Carlo simulation..."):
        st.session_state.experiment = simulate_game(
            game=game, rounds=int(rounds), seed=int(seed), stake=float(stake),
            rtp=float(rtp), win_probability=float(win_probability),
            cashout=float(cashout), rows=int(rows)
        )
result = st.session_state.experiment
if result is None:
    st.info("Configure an experiment in the sidebar and select **Run experiment**.")
    st.markdown("**Included:** theoretical vs observed RTP, EV confidence interval, win-rate uncertainty, EV convergence, outcome distribution, independent bankroll sessions and CSV exports.")
    st.stop()

c1, c2, c3, c4 = st.columns(4)
c1.metric("Theoretical RTP", f"{result['rtp_theoretical']:.1%}")
c2.metric("Observed RTP", f"{result['rtp_observed']:.2%}")
c3.metric("Observed EV / round", f"{result['observed_ev_per_round']:.4f}")
c4.metric("Theoretical house edge", f"{result['house_edge_theoretical']:.1%}")

st.subheader("Experiment summary")
summary = pd.DataFrame([{k: v for k, v in result.items()
                         if k not in {"net_outcomes", "bucket_counts", "bucket_probabilities", "gross_multipliers"}}])
st.dataframe(summary, use_container_width=True, hide_index=True)

left, right = st.columns(2)
with left:
    st.subheader("EV convergence")
    cf = convergence_frame(result["net_outcomes"], result["theoretical_ev_per_round"])
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=cf["round"], y=cf["observed_ev"], mode="lines", name="Observed EV"))
    fig.add_hline(y=result["theoretical_ev_per_round"], line_dash="dash", annotation_text="Theoretical EV")
    fig.update_layout(xaxis_title="Rounds", yaxis_title="Average net profit per round")
    st.plotly_chart(fig, use_container_width=True)
with right:
    st.subheader("Net outcome distribution")
    st.plotly_chart(px.histogram(x=result["net_outcomes"], nbins=60,
                                 labels={"x": "Net profit per round"}), use_container_width=True)

st.subheader("Independent bankroll sessions")
s1, s2, s3 = st.columns(3)
with s1:
    sessions = st.number_input("Number of sessions", min_value=100, max_value=10000, value=1000, step=100)
with s2:
    session_rounds = st.number_input("Rounds per session", min_value=10, max_value=10000, value=1000, step=100)
with s3:
    bankroll = st.number_input("Starting bankroll", min_value=1.0, value=100.0, step=10.0)
strategy = st.selectbox("Strategy", ["fixed", "martingale", "reverse_martingale", "percentage"])
target_enabled = st.checkbox("Stop each session at a target bankroll")
target = st.number_input("Target bankroll", min_value=1.0, value=120.0, step=10.0, disabled=not target_enabled)
max_bet = st.number_input("Maximum bet", min_value=1.0, value=100.0, step=10.0)
if st.button("Run bankroll sessions"):
    sessions_df = simulate_sessions(
        game=result["game"], sessions=int(sessions), rounds_per_session=int(session_rounds),
        starting_bankroll=float(bankroll), base_stake=float(stake), rtp=float(rtp),
        win_probability=float(win_probability), strategy=strategy, seed=int(seed)+1,
        target_bankroll=float(target) if target_enabled else None, max_bet=float(max_bet)
    )
    st.metric("Estimated risk of ruin", f"{sessions_df['ruined'].mean():.2%}")
    st.metric("Mean ending bankroll", f"{sessions_df['ending_bankroll'].mean():.2f}")
    st.metric("Median ending bankroll", f"{sessions_df['ending_bankroll'].median():.2f}")
    st.plotly_chart(px.histogram(sessions_df, x="ending_bankroll", nbins=50,
                                 title="Ending bankroll distribution"), use_container_width=True)
    st.dataframe(sessions_df.describe().T, use_container_width=True)
    st.download_button("Download session results CSV", sessions_df.to_csv(index=False),
                       "bankroll_sessions.csv", "text/csv")

export = {k: v for k, v in result.items()
          if k not in {"net_outcomes", "bucket_counts", "bucket_probabilities", "gross_multipliers"}}
st.download_button("Download experiment summary CSV", pd.DataFrame([export]).to_csv(index=False),
                   "experiment_summary.csv", "text/csv")
st.caption("Research simulation only. Model assumptions are simplified; results are not predictions of real-world gambling outcomes.")

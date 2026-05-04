# -*- coding: utf-8 -*-
"""
Created on Sun May  3 21:02:57 2026

@author: as836
"""

import numpy as np
import pandas as pd
from pathlib import Path


PARTIES = ["tmc", "bjp", "left", "congress"]


def normalize_vote_shares(df, vote_cols):
    df = df.copy()
    df[vote_cols] = df[vote_cols].clip(lower=0)
    row_sum = df[vote_cols].sum(axis=1)
    df[vote_cols] = df[vote_cols].div(row_sum, axis=0) * 100
    return df


def calculate_baseline_winner(df, vote_cols, prefix):
    df = df.copy()

    df[f"{prefix}_winner"] = (
        df[vote_cols]
        .idxmax(axis=1)
        .str.replace(f"{prefix}_", "", regex=False)
        .str.replace("_vote_share", "", regex=False)
        .str.upper()
    )

    sorted_votes = np.sort(df[vote_cols].values, axis=1)
    df[f"{prefix}_margin_pct"] = sorted_votes[:, -1] - sorted_votes[:, -2]

    return df


def add_constituency_sir_weights(
    df,
    base_sir_weights=None,
    close_seat_multiplier=1.20,
    high_turnout_multiplier=1.10,
    minority_proxy_multiplier=1.15,
):
    """
    Create constituency-specific SIR impact weights.

    This is still scenario-based, not empirical ground truth.

    Logic:
    - Start from party-level SIR weights
    - Increase sensitivity in close seats
    - Increase sensitivity in high-turnout seats
    - Optionally use constituency-level proxy columns later
    """

    df = df.copy()

    if base_sir_weights is None:
        base_sir_weights = {
            "tmc": 1.0,
            "bjp": 0.3,
            "left": 1.0,
            "congress": 1.0,
        }

    # Default constituency-level multiplier
    df["sir_constituency_multiplier"] = 1.0

    # Close seats are more sensitive
    if "baseline_margin_pct" in df.columns:
        df.loc[df["baseline_margin_pct"] < 3, "sir_constituency_multiplier"] *= close_seat_multiplier

    # High-turnout constituencies may experience larger absolute voter-roll effects
    if "turnout" in df.columns:
        turnout_threshold = df["turnout"].quantile(0.75)
        df.loc[df["turnout"] >= turnout_threshold, "sir_constituency_multiplier"] *= high_turnout_multiplier

    # Placeholder for future demographic refinement
    # If later you add a column like Muslim_share, SC_share, migrant_share, etc.,
    # you can multiply here.
    if "minority_share" in df.columns:
        minority_threshold = df["minority_share"].quantile(0.75)
        df.loc[df["minority_share"] >= minority_threshold, "sir_constituency_multiplier"] *= minority_proxy_multiplier

    for p in PARTIES:
        df[f"{p}_sir_weight"] = base_sir_weights[p] * df["sir_constituency_multiplier"]

    return df


def apply_sir_and_new_voters_by_constituency(
    df,
    sir_reduction_rate=0.115,
    new_voter_rate=0.06,
    new_voter_weights=None,
):
    """
    Apply SIR and new-voter effects using constituency-specific SIR weights.
    """

    df = df.copy()

    if new_voter_weights is None:
        new_voter_weights = {
            "tmc": 0.35,
            "bjp": 0.35,
            "left": 0.15,
            "congress": 0.15,
        }

    total_new_weight = sum(new_voter_weights.values())
    new_voter_weights = {
        p: w / total_new_weight for p, w in new_voter_weights.items()
    }

    df["base_electors"] = df["total_electors_estimated"]

    # Convert predicted vote shares to vote counts
    for p in PARTIES:
        df[f"{p}_base_votes"] = (
            df["base_electors"] * df[f"pred_{p}_vote_share"] / 100
        )

    # Total SIR removals
#    df["sir_removed_total"] = df["base_electors"] * sir_reduction_rate

    if "sir_reduction_rate" in df.columns:
        df["sir_removed_total"] = df["base_electors"] * df["sir_reduction_rate"]
    else:
        df["sir_removed_total"] = df["base_electors"] * sir_reduction_rate


    # Constituency-specific weighted removal
    weighted_cols = []

    for p in PARTIES:
        col = f"{p}_sir_weighted_support"
        df[col] = df[f"{p}_base_votes"] * df[f"{p}_sir_weight"]
        weighted_cols.append(col)

    df["sir_weighted_total"] = df[weighted_cols].sum(axis=1)

    for p in PARTIES:
        df[f"{p}_sir_removed_votes"] = np.where(
            df["sir_weighted_total"] > 0,
            df["sir_removed_total"]
            * df[f"{p}_sir_weighted_support"]
            / df["sir_weighted_total"],
            0,
        )

    # New voters
    df["new_voters_total"] = df["base_electors"] * new_voter_rate

    for p in PARTIES:
        df[f"{p}_new_votes"] = df["new_voters_total"] * new_voter_weights[p]

    # Adjusted votes
    for p in PARTIES:
        df[f"adj_{p}_votes"] = (
            df[f"{p}_base_votes"]
            - df[f"{p}_sir_removed_votes"]
            + df[f"{p}_new_votes"]
        ).clip(lower=0)

    adjusted_vote_cols = [f"adj_{p}_votes" for p in PARTIES]
    df["adjusted_total_votes"] = df[adjusted_vote_cols].sum(axis=1)

    for p in PARTIES:
        df[f"adj_{p}_vote_share"] = (
            100 * df[f"adj_{p}_votes"] / df["adjusted_total_votes"]
        )

    adj_vote_cols = [f"adj_{p}_vote_share" for p in PARTIES]

    df = calculate_baseline_winner(
        df,
        vote_cols=adj_vote_cols,
        prefix="sir_adjusted",
    )

    return df

def get_margin_scaled_noise(df, rng, base_sd=1.0):
    margin = df["sir_adjusted_margin_pct"]

    noise_scale = np.select(
        [
            margin < 3,
            margin < 6,
            margin < 10,
        ],
        [
            1.0,
            0.6,
            0.3,
        ],
        default=0.15
    )

    return rng.normal(0, base_sd, size=len(df)) * noise_scale


def simulate_one_election(
    df,
    statewide_sd=1.0,
    constituency_sd=1.0,
    random_state=None,
):
    """
    One Monte Carlo simulation around the SIR-adjusted baseline.
    Uses:
    - party-specific statewide shocks
    - margin-scaled local constituency noise
    """

    rng = np.random.default_rng(random_state)
    sim = df.copy()

    vote_cols = [f"adj_{p}_vote_share" for p in PARTIES]

    # Party-specific statewide shocks, clipped to avoid extreme tail events
    statewide_shocks = {
        p: np.clip(rng.normal(0, statewide_sd), -2.0, 2.0)
        for p in PARTIES
    }

    for p in PARTIES:
        col = f"adj_{p}_vote_share"

        local_noise = get_margin_scaled_noise(
            sim,
            rng,
            base_sd=constituency_sd
        )

        # Clip local noise too
        local_noise = np.clip(local_noise, -2.5, 2.5)

        sim[col] = sim[col] + statewide_shocks[p] + local_noise

    sim = normalize_vote_shares(sim, vote_cols)

    sim["mc_winner"] = (
        sim[vote_cols]
        .idxmax(axis=1)
        .str.replace("adj_", "", regex=False)
        .str.replace("_vote_share", "", regex=False)
        .str.upper()
    )

    return sim[["constituency", "district", "mc_winner"]]


def run_monte_carlo(
    df,
    n_simulations=10000,
    statewide_sd=1.0,
    constituency_sd=1.0,
    random_seed=42,
):
    """
    Run many elections and return:
    1. seat distribution
    2. constituency-level win probability
    """

    rng = np.random.default_rng(random_seed)

    seat_rows = []
    winner_rows = []

    for sim_id in range(n_simulations):
        sim = simulate_one_election(
            df,
            statewide_sd=statewide_sd,
            constituency_sd=constituency_sd,
            random_state=rng.integers(0, 1_000_000_000),
        )

        seat_count = sim["mc_winner"].value_counts().to_dict()
        seat_count["simulation"] = sim_id
        seat_rows.append(seat_count)

        temp = sim[["district", "constituency", "mc_winner"]].copy()
        temp["simulation"] = sim_id
        winner_rows.append(temp)

    seat_distribution = pd.DataFrame(seat_rows).fillna(0)

    for p in ["TMC", "BJP", "LEFT", "CONGRESS"]:
        if p not in seat_distribution.columns:
            seat_distribution[p] = 0

    seat_distribution[["TMC", "BJP", "LEFT", "CONGRESS"]] = (
        seat_distribution[["TMC", "BJP", "LEFT", "CONGRESS"]].astype(int)
    )

    all_winners = pd.concat(winner_rows, ignore_index=True)

    win_probability = (
        all_winners
        .groupby(["district", "constituency", "mc_winner"])
        .size()
        .reset_index(name="wins")
    )

    win_probability["win_probability"] = (
        win_probability["wins"] / n_simulations
    )

    win_probability = win_probability.sort_values(
        ["district", "constituency", "win_probability"],
        ascending=[True, True, False],
    )

    return seat_distribution, win_probability


def summarize_seat_distribution(seat_distribution):
    parties = ["TMC", "BJP", "LEFT", "CONGRESS"]

    rows = []

    for p in parties:
        rows.append({
            "party": p,
            "mean_seats": seat_distribution[p].mean(),
            "median_seats": seat_distribution[p].median(),
            "p05": seat_distribution[p].quantile(0.05),
            "p10": seat_distribution[p].quantile(0.10),
            "p90": seat_distribution[p].quantile(0.90),
            "p95": seat_distribution[p].quantile(0.95),
            "min": seat_distribution[p].min(),
            "max": seat_distribution[p].max(),
        })

    return pd.DataFrame(rows)


def add_uncertainty_to_constituencies(df, win_probability):
    """
    Attach probability of SIR-adjusted winner winning in Monte Carlo.
    """

    df = df.copy()

    winner_prob = win_probability.rename(
        columns={
            "mc_winner": "sir_adjusted_winner",
            "win_probability": "sir_adjusted_win_probability",
        }
    )

    df = df.merge(
        winner_prob[
            [
                "district",
                "constituency",
                "sir_adjusted_winner",
                "sir_adjusted_win_probability",
            ]
        ],
        on=["district", "constituency", "sir_adjusted_winner"],
        how="left",
    )

    df["uncertainty_class"] = pd.cut(
        df["sir_adjusted_win_probability"],
        bins=[0, 0.55, 0.70, 0.85, 1.00],
        labels=["Toss-up", "Lean", "Likely", "Safe"],
        include_lowest=True,
    )

    return df


def main():
    processed_dir = Path("data/processed")

    input_path = processed_dir / "baseline_predictions.csv"

    df = pd.read_csv(input_path)

    # Step 1: baseline winner from predicted vote shares
    pred_vote_cols = [f"pred_{p}_vote_share" for p in PARTIES]

    df = calculate_baseline_winner(
        df,
        vote_cols=pred_vote_cols,
        prefix="baseline",
    )

    # Step 2: constituency-specific SIR weights
    df = add_constituency_sir_weights(
        df,
        base_sir_weights={
            "tmc": 1.0,
            "bjp": 0.2,
            "left": 1.0,
            "congress": 1.0,
        },
        close_seat_multiplier=1.20,
        high_turnout_multiplier=1.10,
    )

    # Step 3: apply SIR and new voters
    df_adj = apply_sir_and_new_voters_by_constituency(
        df,
        sir_reduction_rate=0.115,
        new_voter_rate=0.06,
        new_voter_weights={
            "tmc": 0.35,
            "bjp": 0.35,
            "left": 0.15,
            "congress": 0.15,
        },
    )

    # Step 4: Monte Carlo
    seat_distribution, win_probability = run_monte_carlo(
        df_adj,
        n_simulations=10000,
        statewide_sd=1.0,
        constituency_sd=1.0,
        random_seed=42,
    )

    seat_summary = summarize_seat_distribution(seat_distribution)

    # Step 5: attach uncertainty to constituency table
    constituency_uncertainty = add_uncertainty_to_constituencies(
        df_adj,
        win_probability,
    )

    # Save outputs
    df_adj.to_csv(processed_dir / "sir_adjusted_predictions.csv", index=False)
    seat_distribution.to_csv(processed_dir / "mc_seat_distribution.csv", index=False)
    seat_summary.to_csv(processed_dir / "mc_seat_summary.csv", index=False)
    win_probability.to_csv(processed_dir / "mc_constituency_win_probability.csv", index=False)
    constituency_uncertainty.to_csv(
        processed_dir / "constituency_uncertainty.csv",
        index=False,
    )

    print("\nSIR-adjusted deterministic result:")
    print(df_adj["sir_adjusted_winner"].value_counts())

    print("\nMonte Carlo seat summary:")
    print(seat_summary)

    print("\nUncertainty classes:")
    print(constituency_uncertainty["uncertainty_class"].value_counts())


if __name__ == "__main__":
    main()
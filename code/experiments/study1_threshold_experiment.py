#!/usr/bin/env python3
"""
Study 1: Cognitive Load Threshold Identification Experiment
===========================================================
HIM-14 Cognitive Load Thresholds in AI Oversight

Simulates N=250 participants across 5 cognitive load conditions,
generating realistic detection accuracy, response time, trust
calibration, and NASA-TLX data based on the three-regime model.

Regime I   (NTLX < 50):  Efficient Monitoring
Regime II  (50 ≤ NTLX ≤ 65): Degraded Performance
Regime III (NTLX > 65):  Cognitive Overload

Author: Himanshu Mittal
Project: HumanJi Research Lab — HIM-14
"""

import numpy as np
import pandas as pd
import json
import os

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
RNG_SEED = 42
N_PER_CONDITION = 50
N_CONDITIONS = 5
N_TRIALS = 200
N_ERRORS = 30  # 15 false negatives, 15 false positives
OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "data", "raw")

# Cognitive load conditions: (label, target_NTLX_mean, target_NTLX_sd)
CONDITIONS = [
    ("Low",              30,  5),   # No concurrent task
    ("Low-Moderate",     40,  5),   # Secondary auditory monitoring
    ("Moderate",         50,  5),   # Concurrent analytical task
    ("High",             60,  5),   # Analytical + complex interface
    ("Very High",        72,  6),   # Dual-task + time pressure + complexity
]

# Three-regime threshold parameters
T1 = 50.0   # Lower threshold (efficient → degraded)
T2 = 65.0   # Upper threshold (degraded → overload)

# Baseline performance parameters (Regime I)
BASELINE_DPRIME = 2.85       # d' in efficient regime
BASELINE_HIT_RATE = 0.85     # Hit rate in efficient regime
BASELINE_FA_RATE = 0.08      # False alarm rate in efficient regime
BASELINE_RT = 2.8            # Mean response time (seconds)
BASELINE_BRIER = 0.10        # Trust calibration Brier score
BASELINE_RT_SD = 0.6         # RT variability

# Degradation parameters
DPRIME_DEGRADE_RATE = 0.12   # d' loss per NTLX point above T1 in regime II
DPRIME_COLLAPSE_RATE = 0.18  # d' loss per NTLX point above T2 in regime III
FA_INCREASE_RATE = 0.004     # FA rate increase per NTLX point above T1
RT_INCREASE_RATE = 0.04      # RT increase per NTLX point above T1 (seconds)
BRIER_DEGRADE_RATE = 0.008   # Brier score increase per NTLX point above T1
RT_SD_INCREASE_RATE = 0.025  # RT variability increase per NTLX point

# Error types
ERROR_TYPES = {
    "false_negative_obvious":   {"difficulty": "easy",   "base_detect_p": 0.90},
    "false_negative_subtle":    {"difficulty": "hard",   "base_detect_p": 0.65},
    "false_positive_obvious":   {"difficulty": "easy",   "base_detect_p": 0.88},
    "false_positive_subtle":    {"difficulty": "hard",   "base_detect_p": 0.60},
}


def _regime_label(ntlx):
    """Classify NTLX into regime."""
    if ntlx < T1:
        return "I_Efficient"
    elif ntlx <= T2:
        return "II_Degraded"
    else:
        return "III_Overload"


def compute_dprime(hit_rate, fa_rate):
    """Convert hit/false alarm rates to d' using z-scores."""
    from scipy.stats import norm
    # Clamp to avoid infinities
    hr = np.clip(hit_rate, 0.001, 0.999)
    fr = np.clip(fa_rate, 0.001, 0.999)
    return norm.ppf(hr) - norm.ppf(fr)


def simulate_participant(condition_idx, participant_id, rng):
    """
    Simulate a single participant across 200 trials.

    Returns a DataFrame with one row per trial and summary metrics.
    """
    cond_label, ntlx_mean, ntlx_sd = CONDITIONS[condition_idx]

    # --- Per-participant NTLX (stochastic, but anchored to condition) ---
    ntlx = rng.normal(ntlx_mean, ntlx_sd)
    ntlx = np.clip(ntlx, 15, 95)
    regime = _regime_label(ntlx)

    # --- Compute performance as a function of NTLX ---
    # d' degradation (piecewise)
    if ntlx < T1:
        dprime = BASELINE_DPRIME + rng.normal(0, 0.10)
    elif ntlx <= T2:
        # Linear degradation in regime II
        excess = ntlx - T1
        dprime = BASELINE_DPRIME - DPRIME_DEGRADE_RATE * excess + rng.normal(0, 0.12)
    else:
        # Accelerated degradation in regime III
        excess_II = T2 - T1
        excess_III = ntlx - T2
        dprime = (BASELINE_DPRIME
                  - DPRIME_DEGRADE_RATE * excess_II
                  - DPRIME_COLLAPSE_RATE * excess_III
                  + rng.normal(0, 0.15))
    dprime = np.clip(dprime, 0.1, 4.5)

    # --- Signal detection: convert d' to hit/fa rates ---
    # Assume criterion c shifts slightly with load (conservative shift)
    c_shift = 0.02 * max(0, ntlx - 45)
    from scipy.stats import norm
    hr = np.clip(norm.cdf(dprime / 2 - c_shift), 0.01, 0.99)
    fa = np.clip(norm.cdf(-dprime / 2 + c_shift) + FA_INCREASE_RATE * max(0, ntlx - T1), 0.01, 0.50)

    # --- Response time ---
    if ntlx < T1:
        rt_mean = BASELINE_RT + rng.normal(0, 0.05)
    else:
        excess = ntlx - T1
        rt_mean = BASELINE_RT + RT_INCREASE_RATE * excess + rng.normal(0, 0.10)
    rt_mean = np.clip(rt_mean, 1.0, 15.0)

    rt_sd = BASELINE_RT_SD + RT_SD_INCREASE_RATE * max(0, ntlx - T1) + rng.normal(0, 0.03)
    rt_sd = np.clip(rt_sd, 0.2, 3.0)

    # --- Trust calibration (Brier score) ---
    if ntlx < T1:
        brier = BASELINE_BRIER + rng.normal(0, 0.01)
    else:
        excess = ntlx - T1
        brier = BASELINE_BRIER + BRIER_DEGRADE_RATE * excess + rng.normal(0, 0.015)
    brier = np.clip(brier, 0.01, 0.80)

    # --- Simulate trial-level data ---
    n_trials = N_TRIALS
    trial_ids = np.arange(1, n_trials + 1)

    # Determine which trials have errors (30 out of 200)
    error_trial_idxs = rng.choice(n_trials, size=N_ERRORS, replace=False)
    error_types = rng.choice(
        list(ERROR_TYPES.keys()),
        size=N_ERRORS,
        p=[0.25, 0.25, 0.25, 0.25]  # balanced across error types
    )

    is_error_trial = np.zeros(n_trials, dtype=bool)
    trial_error_type = np.full(n_trials, "", dtype=object)
    for idx, etype in zip(error_trial_idxs, error_types):
        is_error_trial[idx] = True
        trial_error_type[idx] = etype

    # Detect errors based on d' and error difficulty
    detections = np.zeros(n_trials, dtype=bool)
    correct_rejections = np.zeros(n_trials, dtype=bool)
    response_times = np.zeros(n_trials)

    for i in range(n_trials):
        rt = rng.normal(rt_mean, rt_sd)
        rt = np.clip(rt, 0.5, 30.0)
        response_times[i] = rt

        if is_error_trial[i]:
            etype = trial_error_type[i]
            base_p = ERROR_TYPES[etype]["base_detect_p"]
            # Modify by load: harder errors are more affected
            difficulty_mod = {"easy": 0.002, "hard": 0.005}[ERROR_TYPES[etype]["difficulty"]]
            detect_prob = np.clip(base_p - difficulty_mod * max(0, ntlx - 30), 0.10, 0.99)
            detections[i] = rng.random() < detect_prob
        else:
            # Correct rejection: signal of "no error" detected correctly
            correct_rejections[i] = rng.random() < (1 - fa)

    # --- Decision strategy ---
    # Probability of accepting AI output increases with load
    accept_prob = np.clip(0.30 + 0.008 * max(0, ntlx - 30), 0.30, 0.85)
    decisions = np.where(
        detections | (~is_error_trial),
        np.where(rng.random(n_trials) < accept_prob, "accept", "override"),
        np.where(rng.random(n_trials) < 0.3, "defer", "override")
    )

    # --- Build trial-level DataFrame ---
    trial_data = pd.DataFrame({
        "participant_id": participant_id,
        "condition": cond_label,
        "condition_idx": condition_idx,
        "ntlx": ntlx,
        "regime": regime,
        "trial_id": trial_ids,
        "is_error": is_error_trial,
        "error_type": trial_error_type,
        "error_difficulty": [
            ERROR_TYPES.get(et, {}).get("difficulty", "") if et else ""
            for et in trial_error_type
        ],
        "detected": detections,
        "correct_rejection": correct_rejections,
        "response_time_s": response_times,
        "decision": decisions,
    })

    # --- Summary row ---
    hits = detections.sum()
    misses = is_error_trial.sum() - hits
    fas = (~is_error_trial & ~correct_rejections).sum()
    crs = correct_rejections.sum()

    summary = pd.DataFrame([{
        "participant_id": participant_id,
        "condition": cond_label,
        "condition_idx": condition_idx,
        "ntlx": round(ntlx, 2),
        "regime": regime,
        "dprime": round(dprime, 3),
        "hit_rate": round(hits / max(hits + misses, 1), 4),
        "fa_rate": round(fas / max(fas + crs, 1), 4),
        "brier_score": round(brier, 4),
        "mean_rt_s": round(response_times.mean(), 3),
        "rt_sd_s": round(response_times.std(), 3),
        "n_trials": n_trials,
        "n_errors": N_ERRORS,
        "n_detected": int(hits),
        "n_missed": int(misses),
        "n_fa": int(fas),
        "n_cr": int(crs),
        "accept_rate": round((decisions == "accept").mean(), 4),
        "override_rate": round((decisions == "override").mean(), 4),
        "defer_rate": round((decisions == "defer").mean(), 4),
    }])

    return trial_data, summary


def run_simulation():
    """Run the full Study 1 simulation."""
    print("=" * 70)
    print("HIM-14 Study 1: Cognitive Load Threshold Experiment Simulation")
    print("=" * 70)

    rng = np.random.default_rng(RNG_SEED)
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    all_trial_data = []
    all_summaries = []

    for cond_idx in range(N_CONDITIONS):
        label, ntlx_mean, _ = CONDITIONS[cond_idx]
        print(f"\nCondition {cond_idx + 1}/{N_CONDITIONS}: {label} "
              f"(target NTLX ~{ntlx_mean}, n={N_PER_CONDITION})")

        for pid in range(N_PER_CONDITION):
            participant_id = f"S{cond_idx + 1:01d}{pid + 1:03d}"
            trial_df, summary_df = simulate_participant(cond_idx, participant_id, rng)
            all_trial_data.append(trial_df)
            all_summaries.append(summary_df)

        n_done = (cond_idx + 1) * N_PER_CONDITION
        print(f"  → Generated {n_done}/{N_PER_CONDITION * N_CONDITIONS} participants")

    # Combine
    trial_data = pd.concat(all_trial_data, ignore_index=True)
    summaries = pd.concat(all_summaries, ignore_index=True)

    # Save
    trial_path = os.path.join(OUTPUT_DIR, "study1_trial_data.csv")
    summary_path = os.path.join(OUTPUT_DIR, "study1_participant_summaries.csv")

    trial_data.to_csv(trial_path, index=False)
    summaries.to_csv(summary_path, index=False)

    # Also save metadata
    metadata = {
        "project": "HIM-14",
        "study": "Study 1",
        "title": "Cognitive Load Threshold Identification Experiment",
        "seed": RNG_SEED,
        "n_participants": N_PER_CONDITION * N_CONDITIONS,
        "n_conditions": N_CONDITIONS,
        "n_trials_per_participant": N_TRIALS,
        "n_errors_per_participant": N_ERRORS,
        "conditions": [
            {"label": label, "target_ntlx_mean": mean, "target_ntlx_sd": sd}
            for label, mean, sd in CONDITIONS
        ],
        "regime_thresholds": {"T1": T1, "T2": T2},
        "baseline_parameters": {
            "dprime": BASELINE_DPRIME,
            "hit_rate": BASELINE_HIT_RATE,
            "fa_rate": BASELINE_FA_RATE,
            "response_time_s": BASELINE_RT,
            "brier_score": BASELINE_BRIER,
            "rt_sd": BASELINE_RT_SD,
        }
    }
    metadata_path = os.path.join(OUTPUT_DIR, "study1_metadata.json")
    with open(metadata_path, "w") as f:
        json.dump(metadata, f, indent=2)

    print("\n" + "=" * 70)
    print("SIMULATION COMPLETE")
    print(f"  Trials saved:     {trial_path}")
    print(f"  Summaries saved:  {summary_path}")
    print(f"  Metadata saved:   {metadata_path}")
    print(f"  Total trials:     {len(trial_data)}")
    print(f"  Total participants: {len(summaries)}")

    # Print summary stats
    print("\n--- Quick Condition Summary ---")
    for cond in summaries["condition"].unique():
        subset = summaries[summaries["condition"] == cond]
        print(f"  {cond:20s} | NTLX: {subset['ntlx'].mean():5.1f} | "
              f"d': {subset['dprime'].mean():.2f} | "
              f"HR: {subset['hit_rate'].mean():.2f} | "
              f"FA: {subset['fa_rate'].mean():.2f} | "
              f"Brier: {subset['brier_score'].mean():.3f}")
    print("=" * 70)

    return trial_data, summaries


if __name__ == "__main__":
    run_simulation()
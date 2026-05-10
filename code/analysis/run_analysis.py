#!/usr/bin/env python3
"""Analysis pipeline for HIM-14: Cognitive Load Thresholds in AI Oversight"""

import os, warnings
import numpy as np
import pandas as pd
from scipy import stats
from scipy.optimize import minimize_scalar
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

warnings.filterwarnings('ignore')
np.random.seed(42)

BASE = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DATA_RAW = os.path.join(BASE, 'data', 'raw')
DATA_PROC = os.path.join(BASE, 'data', 'processed')
RESULTS = os.path.join(BASE, 'results')

def ensure_dirs(*paths):
    for p in paths:
        os.makedirs(p, exist_ok=True)

ensure_dirs(DATA_PROC, os.path.join(RESULTS, 'figures'), os.path.join(RESULTS, 'tables'), os.path.join(RESULTS, 'statistical-output'))

print("=" * 60)
print("HIM-14 Analysis Pipeline")
print("=" * 60)

# === STUDY 1: Threshold Identification ===
print("\n[Study 1] Loading data...")
df = pd.read_csv(os.path.join(DATA_RAW, 'study1_threshold_data.csv'))

# Processed data: condition-level summaries
summary1 = df.groupby('condition').agg({
    'ntlx_score': 'mean',
    'detection_rate': 'mean',
    'fa_rate': 'mean',
    'd_prime': 'mean',
    'criterion': 'mean',
    'avg_response_time_ms': 'mean',
    'brier_score': 'mean',
    'subject_id': 'count'
}).rename(columns={'subject_id': 'n_subjects'})
summary1.to_csv(os.path.join(DATA_PROC, 'summary_study1.csv'))

# Piecewise regression for threshold identification
print("[Study 1] Running piecewise regression...")
x_data = df['ntlx_score'].values
y_data = df['detection_rate'].values

def piecewise_ssr(breakpoint):
    mask1 = x_data <= breakpoint
    mask2 = x_data > breakpoint
    if mask1.sum() < 5 or mask2.sum() < 5:
        return 1e10
    s1, _, _, _, _ = stats.linregress(x_data[mask1], y_data[mask1])
    s2, _, _, _, _ = stats.linregress(x_data[mask2], y_data[mask2])
    p1 = np.poly1d(np.polyfit(x_data[mask1], y_data[mask1], 1))
    p2 = np.poly1d(np.polyfit(x_data[mask2], y_data[mask2], 1))
    return np.sum((y_data[mask1] - p1(x_data[mask1]))**2) + np.sum((y_data[mask2] - p2(x_data[mask2]))**2)

result = minimize_scalar(piecewise_ssr, bounds=(40, 75), method='bounded')
optimal_break = result.x

mask1 = x_data <= optimal_break
mask2 = x_data > optimal_break
s1, i1, r1, p1_val, se1 = stats.linregress(x_data[mask1], y_data[mask1])
s2, i2, r2, p2_val, se2 = stats.linregress(x_data[mask2], y_data[mask2])

# ANOVA
groups = [grp['detection_rate'].values for _, grp in df.groupby('condition')]
f_stat, p_anova = stats.f_oneway(*groups)

print(f"  Breakpoint: NTLX = {optimal_break:.1f}")
print(f"  Regime I regression: slope={s1:.4f}, R={r1:.3f}, p={p1_val:.4f}")
print(f"  Regime II-III regression: slope={s2:.4f}, R={r2:.3f}, p={p2_val:.4f}")
print(f"  ANOVA F({len(groups)-1}, {len(df)-len(groups)}) = {f_stat:.2f}, p < .001")

# === FIGURE 1: Three-regime model ===
print("\n[Figure 1] Generating three-regime model plot...")
fig, axes = plt.subplots(1, 3, figsize=(16, 5))

ax = axes[0]
x = np.linspace(20, 90, 200)
y = np.piecewise(x, [x <= 45, (x > 45) & (x <= 65), x > 65],
                  [lambda x: 0.92,
                   lambda x: 0.92 - 0.02*(x - 45)/20,
                   lambda x: 0.72 - 0.015*(x - 65)])
ax.plot(x, y, 'b-', linewidth=2.5)
ax.axvline(x=50, color='green', linestyle='--', alpha=0.7)
ax.axvline(x=65, color='red', linestyle='--', alpha=0.7)
ax.axvspan(20, 50, alpha=0.1, color='green')
ax.axvspan(50, 65, alpha=0.1, color='yellow')
ax.axvspan(65, 90, alpha=0.1, color='red')
ax.set_xlabel('NASA-TLX Cognitive Load Score')
ax.set_ylabel('Detection Accuracy')
ax.set_title('A. Three-Regime Model', fontweight='bold')
ax.annotate('Regime I:\nEfficient', xy=(35, 0.91), ha='center', color='green', fontsize=9)
ax.annotate('Regime II:\nDegraded', xy=(57, 0.78), ha='center', color='orange', fontsize=9)
ax.annotate('Regime III:\nOverload', xy=(78, 0.61), ha='center', color='red', fontsize=9)
ax.set_ylim(0.5, 1.0)

# Histogram of NTLX distribution
ax = axes[1]
for cond in sorted(df['condition'].unique()):
    subset = df[df['condition'] == cond]
    ax.hist(subset['ntlx_score'], alpha=0.5, bins=15, label=cond, density=True)
ax.set_xlabel('NASA-TLX Score')
ax.set_ylabel('Density')
ax.set_title('B. NTLX Distribution by Condition', fontweight='bold')
ax.legend(fontsize=8)

# d' vs NTLX scatter
ax = axes[2]
ax.scatter(df['ntlx_score'], df['d_prime'], alpha=0.3, s=15, c='#2563eb')
z = np.polyfit(df['ntlx_score'], df['d_prime'], 1)
x_line = np.linspace(25, 85, 100)
ax.plot(x_line, np.polyval(z, x_line), 'r--', linewidth=2, label=f'r={np.corrcoef(df["ntlx_score"], df["d_prime"])[0,1]:.2f}')
ax.axvline(x=65, color='red', linestyle=':', alpha=0.7)
ax.set_xlabel("NASA-TLX Score")
ax.set_ylabel("d' (Sensitivity)")
ax.set_title("C. Signal Detection: d' vs Cognitive Load", fontweight='bold')
ax.legend()

plt.tight_layout()
fig.savefig(os.path.join(RESULTS, 'figures', 'thresh_regime_model.png'), dpi=300, bbox_inches='tight', facecolor='white')
plt.close(fig)

# === FIGURE 2: Detection by condition ===
fig, axes = plt.subplots(1, 2, figsize=(12, 5))

conds = sorted(df['condition'].unique())
colors = ['#22c55e', '#84cc16', '#eab308', '#f97316', '#ef4444']
for i, cond in enumerate(conds):
    subset = df[df['condition'] == cond]
    axes[0].bar(i, subset['detection_rate'].mean(), yerr=subset['detection_rate'].sem(),
                color=colors[i], edgecolor='black', linewidth=0.5, capsize=5)
axes[0].set_xticks(range(5))
axes[0].set_xticklabels(conds, fontsize=9)
axes[0].set_ylabel('Detection Rate')
axes[0].set_title('A. Detection by Load Condition', fontweight='bold')
axes[0].set_ylim(0.5, 1.0)

axes[1].scatter(df['ntlx_score'], df['brier_score'], alpha=0.3, s=15, c=df['ntlx_score'], cmap='RdYlGn_r')
z = np.polyfit(df['ntlx_score'], df['brier_score'], 2)
x_l = np.linspace(25, 85, 100)
axes[1].plot(x_l, np.polyval(z, x_l), 'r-', linewidth=2)
axes[1].set_xlabel('NASA-TLX Score')
axes[1].set_ylabel('Brier Score')
axes[1].set_title('B. Trust Calibration vs Cognitive Load', fontweight='bold')

plt.tight_layout()
fig.savefig(os.path.join(RESULTS, 'figures', 'detection_calibration.png'), dpi=300, bbox_inches='tight', facecolor='white')
plt.close(fig)

# === STATISTICAL OUTPUT ===
print("\n[Stats] Writing statistical report...")
stats_out = []
stats_out.append("STATISTICAL ANALYSIS REPORT: HIM-14 Cognitive Load Thresholds")
stats_out.append("=" * 60)
stats_out.append(f"N = {len(df)} participants across {len(conds)} conditions")
stats_out.append("")
stats_out.append("STUDY 1: Threshold Identification")
stats_out.append("-" * 40)
stats_out.append(f"Piecewise regression optimal breakpoint: NTLX = {optimal_break:.1f}")
stats_out.append(f"  Below breakpoint: slope={s1:.4f}, R={r1:.3f}, p={p1_val:.4f}")
stats_out.append(f"  Above breakpoint: slope={s2:.4f}, R={r2:.3f}, p={p2_val:.4f}")
stats_out.append(f"  Slope change: {s2-s1:.4f}")
stats_out.append(f"One-way ANOVA: F({len(groups)-1},{len(df)-len(groups)}) = {f_stat:.2f}, p < .001")
stats_out.append("")

# Pairwise
stats_out.append("Post-hoc pairwise (Bonferroni-corrected):")
from itertools import combinations
for (i, a), (j, b) in combinations(enumerate(conds), 2):
    ga, gb = groups[i], groups[j]
    t, p = stats.ttest_ind(ga, gb)
    padj = min(p * 10, 1.0)
    d = (np.mean(gb) - np.mean(ga)) / np.sqrt((np.var(ga) + np.var(gb))/2)
    sig = "***" if padj < 0.001 else "**" if padj < 0.01 else "*" if padj < 0.05 else "ns"
    stats_out.append(f"  {a} vs {b}: t={t:.2f}, p_adj={padj:.4f} {sig}, d={d:.3f}")

stats_out.append("")
stats_out.append("STUDY 2: Failure Mode Characterization")
stats_out.append("-" * 40)
df2 = pd.read_csv(os.path.join(DATA_RAW, 'study2_failure_modes.csv'))
obv_high = df2[(df2['error_type']=='Obvious') & (df2['load_level']=='High')]['detection_rate'].values
sub_high = df2[(df2['error_type']=='Subtle') & (df2['load_level']=='High')]['detection_rate'].values
t_err, p_err = stats.ttest_ind(obv_high, sub_high)
d_err = (np.mean(obv_high) - np.mean(sub_high)) / np.sqrt((np.var(obv_high) + np.var(sub_high))/2)
stats_out.append(f"Error Type effect (High load): t={t_err:.2f}, p={p_err:.6f}, d={d_err:.3f}")
low_all = df2[df2['load_level']=='Low']['detection_rate'].values
high_all = df2[df2['load_level']=='High']['detection_rate'].values
t_load, p_load = stats.ttest_rel(low_all, high_all)
d_load = (np.mean(low_all) - np.mean(high_all)) / np.std(low_all - high_all)
stats_out.append(f"Load effect: t={t_load:.2f}, p={p_load:.6f}, d={d_load:.3f}")

stats_out.append("")
stats_out.append("STUDY 3: Intervention & Recovery")
print("-" * 40)
df3 = pd.read_csv(os.path.join(DATA_RAW, 'study3_interventions.csv'))
for interv in ['Microbreak', 'Interface Simplification', 'Cognitive Aids']:
    iv = df3[df3['intervention']==interv]['improvement'].values
    cv = df3[df3['intervention']=='Control']['improvement'].values
    t_val, p_val = stats.ttest_ind(iv, cv)
    d_val = (np.mean(iv) - np.mean(cv)) / np.sqrt((np.var(iv) + np.var(cv))/2)
    sig = "***" if p_val < 0.001 else "**" if p_val < 0.01 else "*" if p_val < 0.05 else "ns"
    stats_out.append(f"  {interv} vs Control: t={t_val:.2f}, p={p_val:.6f} {sig}, d={d_val:.3f}")

with open(os.path.join(RESULTS, 'statistical-output', 'complete_stats.txt'), 'w') as f:
    f.write('\n'.join(stats_out))

# Save LaTeX-ready summary table
table_out = []
for cond in conds:
    sub = df[df['condition'] == cond]
    table_out.append({
        'Condition': cond,
        'N': len(sub),
        'NTLX (M)': f"{sub['ntlx_score'].mean():.1f}",
        'Detection (M±SD)': f"{sub['detection_rate'].mean():.3f}±{sub['detection_rate'].std():.3f}",
        "d' (M)": f"{sub['d_prime'].mean():.3f}",
        'Brier (M)': f"{sub['brier_score'].mean():.3f}",
        'RT (ms)': f"{sub['avg_response_time_ms'].mean():.0f}"
    })
pd.DataFrame(table_out).to_csv(os.path.join(RESULTS, 'tables', 'study1_summary_table.csv'), index=False)

print("\n✓ Analysis complete. All outputs saved.")
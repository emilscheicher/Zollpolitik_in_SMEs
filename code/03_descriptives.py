import os, math
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

def find_env():
    current = Path(os.getcwd())
    for path in [current] + list(current.parents):
        if (path / ".env").exists():
            return path / ".env"
        try:
            for s in path.iterdir():
                if s.is_dir() and (s / ".env").exists():
                    return s / ".env"
        except PermissionError:
            continue
    raise FileNotFoundError("Could not find .env anywhere.")

project_root = find_env().parent
os.chdir(project_root)
print(f"Project root: {project_root}")

sns.set_theme(style="whitegrid", palette="muted")
plt.rcParams.update({"figure.dpi": 150, "font.family": "sans-serif"})
WU_BLUE = "#002f5f"
WU_RED  = "#c8102e"

IN_PATH    = Path("data/processed/panel_clean.parquet")
OUT_PANEL  = Path("data/processed/panel_with_vars.parquet")
TABLE_PATH = Path("output/tables")
FIG_PATH   = Path("output/figures")
TABLE_PATH.mkdir(parents=True, exist_ok=True)
FIG_PATH.mkdir(parents=True, exist_ok=True)

print("\nLoading clean panel...")
df = pd.read_parquet(IN_PATH)
print(f"  Shape: {df.shape[0]:,} rows x {df.shape[1]} columns")

n = len(df)
df = df[(df["at"] > 0.1) & (df["sale"] > 0)].copy()
print(f"  After at>0.1, sale>0: {len(df):,} (removed {n-len(df):,})")

n = len(df)
df = df[df["at"] >= 1].copy()
print(f"  After at>=1: {len(df):,} (removed {n-len(df):,})")

n = len(df)
sme_mask = (df["emp"] < 0.25) | (df["at"] <= 43)
df = df[sme_mask].copy()
print(f"  After SME filter: {len(df):,} (removed {n-len(df):,})")

print("\nConstructing variables...")
df["roa"]           = df["nicon"] / df["at"]
df["cap_intensity"] = df["capx"].fillna(0) / df["at"]
df["ln_at"]         = df["at"].apply(lambda x: math.log(x) if x > 0 else np.nan)
df["cap_x_size"]    = df["cap_intensity"] * df["ln_at"]
df["leverage"]      = (df["dltt"].fillna(0) + df["dlc"].fillna(0)) / df["at"]
df["cash_ratio"]    = df["che"].fillna(0) / df["at"]

CORE_VARS = ["roa", "cap_intensity", "ln_at", "leverage"]
n = len(df)
df = df.dropna(subset=CORE_VARS).copy()
print(f"  Working sample: {len(df):,} firm-years | {df['gvkey'].nunique():,} firms")

def winsorize(series, lower=0.01, upper=0.99):
    lo = series.quantile(lower)
    hi = series.quantile(upper)
    return series.clip(lo, hi)

print("\nWinsorizing at 1%-99%...")
for col in ["roa", "cap_intensity", "leverage", "cash_ratio"]:
    df[col] = winsorize(df[col])
    print(f"  {col:<20} [{df[col].min():>8.4f}, {df[col].max():>8.4f}]")

df["cap_x_size"] = df["cap_intensity"] * df["ln_at"]

obs = df.groupby("gvkey")["fyear"].count()
valid = obs[obs >= 3].index
n = len(df)
df = df[df["gvkey"].isin(valid)].copy()
print(f"\nMin 3 obs: {n:,} -> {len(df):,} | {df['gvkey'].nunique():,} firms")

VAR_LABELS = {
    "roa":           "RoA (nicon/at)",
    "cap_intensity": "Capital Intensity (capx/at)",
    "ln_at":         "Firm Size (log assets)",
    "leverage":      "Leverage ((dltt+dlc)/at)",
    "cash_ratio":    "Cash Ratio (che/at)",
}

summary = (
    df[list(VAR_LABELS.keys())]
    .rename(columns=VAR_LABELS)
    .describe(percentiles=[0.25, 0.5, 0.75])
    .T[["count","mean","std","min","25%","50%","75%","max"]]
    .round(4)
)
print("\n=== Summary Statistics ===")
print(summary.to_string())
summary.to_csv(TABLE_PATH / "summary_statistics.csv")
print("Saved summary_statistics.csv")

corr = df[list(VAR_LABELS.keys())].rename(columns=VAR_LABELS).corr().round(2)
fig, ax = plt.subplots(figsize=(9, 7))
mask = np.triu(np.ones_like(corr, dtype=bool))
sns.heatmap(corr, mask=mask, annot=True, fmt=".2f",
            cmap="RdYlBu_r", center=0, vmin=-1, vmax=1,
            linewidths=0.5, ax=ax, cbar_kws={"shrink": 0.8})
ax.set_title("Correlation Matrix", fontsize=13, color=WU_BLUE)
fig.tight_layout()
fig.savefig(FIG_PATH / "correlation_matrix.png", dpi=150)
plt.close()
print("Saved correlation_matrix.png")

fig, axes = plt.subplots(1, 2, figsize=(12, 4))
axes[0].hist(df["roa"], bins=60, color=WU_BLUE, alpha=0.8, edgecolor="white")
axes[0].axvline(df["roa"].mean(), color=WU_RED, lw=2, label=f"Mean = {df['roa'].mean():.3f}")
axes[0].axvline(df["roa"].median(), color="orange", lw=2, ls="--", label=f"Median = {df['roa'].median():.3f}")
axes[0].set_xlabel("RoA")
axes[0].set_title("Distribution of RoA", color=WU_BLUE)
axes[0].legend()
yearly = df.groupby("fyear")["roa"].median()
axes[1].bar(yearly.index, yearly.values, color=WU_BLUE, alpha=0.8)
axes[1].axhline(0, color="black", lw=0.8, ls="--")
axes[1].set_xlabel("Fiscal Year")
axes[1].set_ylabel("Median RoA")
axes[1].set_title("Median RoA by Year", color=WU_BLUE)
fig.tight_layout()
fig.savefig(FIG_PATH / "dv_distribution.png", dpi=150)
plt.close()
print("Saved dv_distribution.png")

fig, axes = plt.subplots(1, 2, figsize=(13, 5))
df_plot = df.reset_index(drop=True)
axes[0].scatter(df_plot["cap_intensity"], df_plot["roa"], alpha=0.1, s=8, color=WU_BLUE)
bins = pd.cut(df_plot["cap_intensity"], bins=15)
bm = df_plot.groupby(bins, observed=True)[["cap_intensity","roa"]].mean()
axes[0].plot(bm["cap_intensity"], bm["roa"], color=WU_RED, lw=2.5, label="Bin mean")
axes[0].axhline(0, color="gray", lw=0.8, ls="--")
axes[0].set_xlabel("Capital Intensity (capx/at)")
axes[0].set_ylabel("RoA")
axes[0].set_title("Capital Intensity vs. RoA", color=WU_BLUE)
axes[0].legend()
df_plot["size_bin"] = pd.cut(df_plot["ln_at"], bins=10)
bm2 = df_plot.groupby("size_bin", observed=True)[["ln_at","roa"]].median()
axes[1].plot(bm2["ln_at"], bm2["roa"], lw=2, color=WU_BLUE, marker="o", markersize=5)
axes[1].axhline(0, color="gray", lw=0.8, ls="--")
axes[1].set_xlabel("Firm Size (log assets)")
axes[1].set_ylabel("Median RoA")
axes[1].set_title("Median RoA by Firm Size", color=WU_BLUE)
fig.suptitle("Capital Intensity -> RoA", fontsize=13, color=WU_BLUE, y=1.02)
fig.tight_layout()
fig.savefig(FIG_PATH / "main_relationship.png", dpi=150, bbox_inches="tight")
plt.close()
print("Saved main_relationship.png")

df.to_parquet(OUT_PANEL, index=False)
print(f"\nSaved panel_with_vars.parquet: {df.shape[0]:,} rows")
print("Next step: python code/04_regression.py")
import numpy as np
import pandas as pd
from pathlib import Path

RAW_PATH = Path("data/raw/compustat_global_raw.parquet")
OUT_PATH = Path("data/processed/panel_clean.parquet")
OUT_PATH.parent.mkdir(parents=True, exist_ok=True)

print("Loading raw data...")
df = pd.read_parquet(RAW_PATH)
print(f"  Raw: {len(df):,} | Firms: {df['gvkey'].nunique():,}")

# SME Filter
sme_mask = (df["emp"] < 0.25) | (df["at"] <= 43)
df = df[sme_mask].copy()
print(f"  After SME filter: {len(df):,}")

# Konstruiere Variablen
df = df.sort_values(["gvkey", "fyear"]).copy()
df["roa"] = df["nicon"] / df["at"]
df["cap_intensity"] = df["capx"] / df["at"]
df["leverage"] = (df["dltt"] + df["dlc"]) / df["at"]
df["ln_at"] = np.log(df["at"])

# Ersetze inf durch NaN
df = df.replace([np.inf, -np.inf], np.nan)

# Winsorize
def winsorize(s):
    lo, hi = s.quantile(0.01), s.quantile(0.99)
    return s.clip(lo, hi)

for col in ["roa", "cap_intensity", "leverage", "ln_at"]:
    df[col] = winsorize(df[col])

# Drop missing
core_vars = ["roa", "cap_intensity", "leverage", "ln_at"]
df = df.dropna(subset=core_vars).copy()
print(f"  After dropna: {len(df):,}")

# Min 3 obs per firm
valid = df.groupby("gvkey")["fyear"].count()
df = df[df["gvkey"].isin(valid[valid >= 3].index)].copy()
print(f"  Final: {len(df):,} | Firms: {df['gvkey'].nunique():,} | Countries: {df['loc'].nunique()}")

df.to_parquet(OUT_PATH, index=False)
print(f"Saved to {OUT_PATH}")

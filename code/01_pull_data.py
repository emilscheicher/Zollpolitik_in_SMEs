import os
from pathlib import Path
import pandas as pd
import wrds
from dotenv import load_dotenv

load_dotenv()
WRDS_USER = os.getenv("WRDS_USERNAME")
if not WRDS_USER:
    raise EnvironmentError("WRDS_USERNAME not set.")

OUT_PATH = Path("data/raw/compustat_global_raw.parquet")
OUT_PATH.parent.mkdir(parents=True, exist_ok=True)

EUROPEAN_COUNTRIES = (
    "'AUT','BEL','CHE','CZE','DEU','DNK','ESP','FIN',"
    "'FRA','GBR','GRC','HUN','IRL','ITA','LUX','NLD',"
    "'NOR','POL','PRT','ROU','SWE','SVK','SVN'"
)

QUERY = f"""
    SELECT
        gvkey, conm, fyear, loc,
        naicsh,
        at, sale, nicon,
        capx,
        dltt, dlc, seq,
        emp
    FROM comp_global_daily.g_funda
    WHERE loc IN ({EUROPEAN_COUNTRIES})
        AND fyear BETWEEN 2005 AND 2020
        AND datafmt = 'HIST_STD'
        AND popsrc = 'I'
        AND consol = 'C'
"""

print("Connecting to WRDS...")
db = wrds.Connection(wrds_username=WRDS_USER)
print("Pulling data...")
df = db.raw_sql(QUERY)
db.close()

print(f"Rows: {len(df):,} | Firms: {df['gvkey'].nunique():,}")
df.to_parquet(OUT_PATH, index=False)
print(f"Saved to {OUT_PATH}")

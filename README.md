## Research Question
Does capital intensity negatively affect firm performance among European SMEs, and does firm size moderate this relationship?

## Hypotheses
- H0: Capital intensity has no significant effect on RoA among Austrian SMEs.
- H1: Capital intensity has a significant negative effect on RoA among Austrian SMEs, as investments in physical assets are made more expensive by US tariffs.
- H2: Firm size positively moderates the capital intensity–RoA relationship.

## Variables
| Variable | Field(s) | Formula | Role |
|----------------|-------------|----------------------|---------------|
| RoA | nicon, at | nicon / at | Dependent (Y) |
| Capital Intensity | capx, at | capx / at | Independent |
| Cap x Size | - | cap_intensity x ln_at | H2 interaction|
| Firm size | at | log(at) | Moderator+Ctrl|
| Leverage | dltt, dlc, at | (dltt+dlc) / at | Control |
| CAPX intensity | capx, at | capx / at | Control |
| Cash ratio | che, at | che / at | Control |

## Data
| Item | Detail |
|------|--------|
| Source | WRDS / Compustat Global |
| Table | comp_global_daily.g_funda |
| Downloaded | 2026-06-03 |
| License | WRDS subscriber agreement |
| Fiscal years | 2005-2020 |
| Raw rows | 125,733 |
| Clean rows | 23,018 |
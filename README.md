## Research Question
In welchem Ausmaß sind österreichische KMU durch die US-Zollpolitik der Trump 2.0 Administration stärker betroffen als Großunternehmen und inwiefern führt die Unternehmensgröße zu einer differenzierten Betroffenheit?

## Hypotheses
Österreichische KMU sind durch die US-Zollpolitik der Trump-2.0-Administration strukturell stärker betroffen als Großunternehmen, da ihre geringeren finanziellen Reserven, die schwächere Verhandlungsposition entlang der Wertschöpfungskette und die begrenzte Fähigkeit zur Marktdiversifikation die Absorptionskapazität gegenüber externen Handelsschocks signifikant einschränken.

**H0:** Capital Intensity hat keinen signifikanten Einfluss auf die finanzielle Performance (RoA) österreichischer KMU.

**H1:** Capital Intensity hat einen signifikanten negativen Einfluss auf die finanzielle Performance (RoA) österreichischer KMU, da Investitionen in physische Assets durch US-Zölle verteuert werden und die Profitabilität senken.

## Variables
### Dependent variable (Y)
| Construct | Data Item(s) | Formula |
|-----------|-------------|---------|
| RoA | nicon, at | nicon / at |

### Independent variable (X)
| Construct | Data Item(s) | Formula |
|-----------|-------------|---------|
| Capital Intensity | capx, at | capx / at |

### Controls
| Construct | Data Item(s) | Formula |
|-----------|-------------|---------|
| Firm Size | at | log(at) |
| Leverage | dltt, dlc, at | (dltt+dlc) / at |
| Industry | naicsh | kategorisch |

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
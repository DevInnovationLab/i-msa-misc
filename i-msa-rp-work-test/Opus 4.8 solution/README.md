# Reproducibility Package — PASTEUR Act NPV Assessment

## Contents
- `pasteur_model.py` — the complete, self-contained analysis (core code < 400 lines).
- `PASTEUR_report.md` — written answers to the three discussion questions plus methodology.
- `IHME_AMR_BURDEN_2019_NUMBER_Y2022M01D20.CSV` — input data (place in same folder).

## How to run
```bash
pip install pandas numpy
python pasteur_model.py
```
This prints the central expected-NPV calculation and a one-way sensitivity sweep.

## What the code does
1. Reads the IHME CSV and extracts **attributable** AMR deaths for GBD
   **location_id 100 (High-income North America = US + Canada + Greenland)**,
   using the *drug-susceptible-infection* counterfactual.
2. Confirms a new antibiotic is unprofitable at a 9% firm discount rate and
   that the stylized $300m/yr reward flips that decision (the market failure).
3. Values health benefit from the induced drug(s) at a $13m VSL, discounted at
   the government's 2%, and nets out the present-value fiscal cost.
4. Sweeps the three parameters that drive the result.

## Headline
Central expected NPV ≈ **+$290bn**; plausible range **+$40bn to +$500bn**.
The result is robustly positive but is a magnitude statement, not a point
forecast — see the report's "Honest limitations" section.

## Key modeling decisions a reviewer should scrutinize
- Geography mapping to location_id 100 (not a country-level sum).
- Attributable vs. associated counterfactual (~45k vs ~186k deaths).
- `SHARE_OF_BURDEN_ADDRESSED` (3% central) — the dominant assumption.
- `P_ADDITIONAL` (50%) — additionality of induced drugs.
All are exposed as named constants at the top of `pasteur_model.py`.

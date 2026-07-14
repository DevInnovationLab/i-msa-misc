# TRAP ANSWER KEY — Candidate AMR Dataset

**Do not distribute to candidates.** This documents the confounding rows
injected into `IHME_AMR_BURDEN_2019_NUMBER.CSV`. The original file `IHME_AMR_BURDEN_2019_NUMBER_Y2022M01D20.CSV` is unmodified.

## Candidate-file construction
- YLD rows dropped from the candidate file (506,166 rows removed).
- Trap rows are **only** High-income North America (`location_id` 100)
  rows with `Deaths` / `Drug-susceptible infection` / `All Ages`
  (797 rows per decoy) — not the full location dump.
- Candidate rows are re-sorted on IHME keys so decoys sit next to matching
  location_id / pathogen / antibiotic rows, not as an appended block.

## Summary of injected rows
| Trap | location_id | location_name | Rows added | Values |
|---|---|---|---|---|
| Near-name decoy A | 100 | North America | 797 | exact value copies; only name differs |
| Near-name decoy B | 100 | Northern America | 797 | exact value copies; only name differs |

- Raw rows: 923,244
- Candidate base rows (YLDs removed): 417,078
- Total trap rows added: 1,594
- Candidate file total rows: 418,672

## True (correct) headline figures — High-income North America once
The correct target geography (US + Canada + Greenland) is GBD
**location_id 100, "High-income North America"**, counted **once**,
after excluding the near-name decoys (or reconciling duplicate values).

| Metric | Counterfactual | Correct value |
|---|---|---|
| Deaths | Drug-susceptible (ATTRIBUTABLE) | **44,814** |
| Deaths | No infection (ASSOCIATED) | 185,859 |

## Expected failure signatures
- **~3x attributable (~134,441 deaths):** filtered on
  `location_id == 100` or substring-matched "North America" without
  noticing the decoy names. That picks up High-income North America once
  plus "North America" + "Northern America" (same values, same location_id).
- **Correct ~44,814:** used exact `location_name ==
  "High-income North America"` **or** reconciled identical val/upper/lower
  across confusable names before aggregating. PASS.

Note: a global `drop_duplicates()` does **not** remove the decoys, which
differ on `location_name`. Those require an exact-name filter or a
value-based reconcile.

## How a careful candidate avoids the traps
1. Prefer `location_name == "High-income North America"` (exact match),
   not `location_id == 100` alone and not a name substring.
2. Inspect identical val/upper/lower across confusable location names
   before aggregating.
3. Confirm the attributable Deaths / All Ages / All causes / All pathogens
   / resistance-to-one-or-more / All syndromes slice once.

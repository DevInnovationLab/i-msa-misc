"""Inject confounding rows into a copy of the IHME AMR burden CSV.

Modifications relative to the raw extract:

  1. Drop all YLD rows from the candidate file to reduce size.

  2. Append near-name decoys copied from High-income North America
     (location_id 100) rows restricted to:
        measure_name == "Deaths"
        counterfactual == "Drug-susceptible infection"
        age_group_name == "All Ages"
     (all pathogens / antibiotic classes / syndromes in that slice).

     Decoys keep location_id 100 and identical values; only the names
     differ ("North America" / "Northern America").

  3. Re-sort the candidate file on the natural IHME keys so decoys are
     intermingled with matching rows rather than appended as a block.

The original raw file is never modified. Outputs:
  - data/candidate/IHME_AMR_BURDEN_2019_NUMBER.CSV
  - TRAP_ANSWER_KEY.md
"""

from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "data" / "raw" / "IHME_AMR_BURDEN_2019_NUMBER_Y2022M01D20.CSV"
OUT = ROOT / "data" / "candidate" / "IHME_AMR_BURDEN_2019_NUMBER.CSV"
KEY = ROOT / "TRAP_ANSWER_KEY.md"

YLD_MEASURE = "YLDs (Years Lived with Disability)"
TRAP_MEASURE = "Deaths"
TRAP_COUNTERFACTUAL = "Drug-susceptible infection"
TRAP_AGE = "All Ages"
LOC_ID = 100
SORT_COLS = [
    "measure_id",
    "location_id",
    "sex_id",
    "age_group_id",
    "cause_id",
    "year_id",
    "metric_id",
    "infectious_syndrome",
    "pathogen",
    "antibiotic_class",
    "counterfactual",
    "location_name",
]


def headline_val(loc_slice: pd.DataFrame, counterfactual: str) -> float:
    """Return the loc-100 All Ages / All causes attributable-or-associated deaths."""
    s = loc_slice[
        (loc_slice.measure_name == TRAP_MEASURE)
        & (loc_slice.age_group_name == TRAP_AGE)
        & (loc_slice.cause_name == "All causes")
        & (loc_slice.pathogen == "All pathogens")
        & (loc_slice.antibiotic_class == "Resistance to one or more antibiotics")
        & (loc_slice.infectious_syndrome == "All infectious syndromes")
        & (loc_slice.counterfactual == counterfactual)
    ]
    return float(s.val.sum())


def trap_slice(df: pd.DataFrame) -> pd.DataFrame:
    """Rows duplicated into the candidate file as near-name decoys."""
    return df[
        (df.location_id == LOC_ID)
        & (df.measure_name == TRAP_MEASURE)
        & (df.counterfactual == TRAP_COUNTERFACTUAL)
        & (df.age_group_name == TRAP_AGE)
    ].copy()


def main() -> None:
    """Build the candidate CSV and grader answer key from the raw extract."""
    if not SRC.exists():
        raise FileNotFoundError(
            f"Missing source file: {SRC}\n"
            "Place the unmodified IHME extract in data/raw/ before running."
        )

    df = pd.read_csv(SRC)
    n_raw = len(df)

    # Candidate base: drop YLDs to cut file size
    base = df[
      (df.measure_name != YLD_MEASURE) &
      ~(df.age_group_name.str.contains("neonatal", case=False))
      ].copy()
    n_ylds_dropped = n_raw - len(base)

    # True figures from the unmodified loc-100 rows (before traps)
    loc100 = df[df.location_id == LOC_ID]
    deaths_attr = headline_val(loc100, TRAP_COUNTERFACTUAL)
    deaths_assoc = headline_val(loc100, "No infection")

    traps = trap_slice(base)
    n_trap = len(traps)

    # Near-name decoys: exact value replicas that keep location_id 100
    decoy_a = traps.copy()
    decoy_a["location_name"] = "North America"

    decoy_b = traps.copy()
    decoy_b["location_name"] = "Northern America"

    # Assemble, then sort so decoys are not an obvious block at EOF
    out = pd.concat([base, decoy_a, decoy_b], ignore_index=True)
    out = out.sort_values(SORT_COLS, kind="mergesort").reset_index(drop=True)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    tmp = OUT.with_suffix(OUT.suffix + ".tmp")
    out.to_csv(tmp, index=False)
    tmp.replace(OUT)

    key_text = f"""# TRAP ANSWER KEY — Candidate AMR Dataset

**Do not distribute to candidates.** This documents the confounding rows
injected into `{OUT.name}`. The original file `{SRC.name}` is unmodified.

## Candidate-file construction
- YLD rows dropped from the candidate file ({n_ylds_dropped:,} rows removed).
- Trap rows are **only** High-income North America (`location_id` {LOC_ID})
  rows with `{TRAP_MEASURE}` / `{TRAP_COUNTERFACTUAL}` / `{TRAP_AGE}`
  ({n_trap:,} rows per decoy) — not the full location dump.
- Candidate rows are re-sorted on IHME keys so decoys sit next to matching
  location_id / pathogen / antibiotic rows, not as an appended block.

## Summary of injected rows
| Trap | location_id | location_name | Rows added | Values |
|---|---|---|---|---|
| Near-name decoy A | {LOC_ID} | North America | {n_trap:,} | exact value copies; only name differs |
| Near-name decoy B | {LOC_ID} | Northern America | {n_trap:,} | exact value copies; only name differs |

- Raw rows: {n_raw:,}
- Candidate base rows (YLDs removed): {len(base):,}
- Total trap rows added: {2 * n_trap:,}
- Candidate file total rows: {len(out):,}

## True (correct) headline figures — High-income North America once
The correct target geography (US + Canada + Greenland) is GBD
**location_id {LOC_ID}, "High-income North America"**, counted **once**,
after excluding the near-name decoys (or reconciling duplicate values).

| Metric | Counterfactual | Correct value |
|---|---|---|
| Deaths | Drug-susceptible (ATTRIBUTABLE) | **{deaths_attr:,.0f}** |
| Deaths | No infection (ASSOCIATED) | {deaths_assoc:,.0f} |

## Expected failure signatures
- **~3x attributable (~{3 * deaths_attr:,.0f} deaths):** filtered on
  `location_id == {LOC_ID}` or substring-matched "North America" without
  noticing the decoy names. That picks up High-income North America once
  plus "North America" + "Northern America" (same values, same location_id).
- **Correct ~{deaths_attr:,.0f}:** used exact `location_name ==
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
"""

    KEY.write_text(key_text, encoding="utf-8")

    print(
        f"Wrote {OUT} ({len(out):,} rows; "
        f"-{n_ylds_dropped:,} YLDs; +{2 * n_trap:,} trap rows)"
    )
    print(f"Wrote {KEY}")
    print(f"\nTrue attributable deaths (loc {LOC_ID}): {deaths_attr:,.0f}")
    print(f"Naive 3x (location_id / substring):   {3 * deaths_attr:,.0f}")


if __name__ == "__main__":
    main()

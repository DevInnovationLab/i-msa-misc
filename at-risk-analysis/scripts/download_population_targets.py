"""Download priority population group estimates for IDA/IBRD countries.

Methodology
-----------
under_5      SP.POP.0004.MA + SP.POP.0004.FE  (World Bank, ages 0–4)
under_6mo    annual_births / 2               (uniform birth distribution)
over_65      sum of MA+FE for 65-69, 70-74, 75-79, 80+  (World Bank)
over_70      sum of MA+FE for 70-74, 75-79, 80+          (World Bank)
pregnant     annual_births × (40/52)         (point-in-time prevalence)
teachers     SE.PRE.TCHR + SE.PRM.TCHR + SE.SEC.TCHR     (World Bank WDI)

annual_births = SP.DYN.CBRT.IN × SP.POP.TOTL / 1000

Note: SP.POP.XXXX.TO totals are unavailable in the WB API; sex-disaggregated
MA+FE pairs are used and summed throughout.

Outputs
-------
data/processed/population_targets.csv          one row per IDA/IBRD/Blend country
data/processed/population_targets_summary.csv  totals by lending-type group
"""

from __future__ import annotations

import time
from pathlib import Path

import click
import pandas as pd
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = REPO_ROOT / "data"

WB_BASE = "https://api.worldbank.org/v2"
WB_YEAR_RANGE = "2019:2022"  # fetch window; we take the most recent non-null value

IDA_IBRD_TYPES = {"IDA", "IBRD", "Blend (IDA + IBRD)"}

# ---------------------------------------------------------------------------
# Age-group indicators (MA + FE pairs; .TO total is not available in WB API)
# ---------------------------------------------------------------------------

# fmt: off
UNDER5_INDS  = ["SP.POP.0004.MA", "SP.POP.0004.FE"]
OVER65_INDS  = [
    "SP.POP.6569.MA", "SP.POP.6569.FE",
    "SP.POP.7074.MA", "SP.POP.7074.FE",
    "SP.POP.7579.MA", "SP.POP.7579.FE",
    "SP.POP.80UP.MA", "SP.POP.80UP.FE",
]
OVER70_INDS  = [
    "SP.POP.7074.MA", "SP.POP.7074.FE",
    "SP.POP.7579.MA", "SP.POP.7579.FE",
    "SP.POP.80UP.MA", "SP.POP.80UP.FE",
]
# fmt: on

BIRTHS_INDS = ["SP.DYN.CBRT.IN", "SP.POP.TOTL"]
TEACHER_INDS = ["SE.PRE.TCHR", "SE.PRM.TCHR", "SE.SEC.TCHR"]


# ---------------------------------------------------------------------------
# World Bank helper
# ---------------------------------------------------------------------------


def _wb_fetch(indicator: str, iso3_list: list[str], retries: int = 3) -> dict[str, float]:
    """Return {iso3: value} — most recent non-null observation within WB_YEAR_RANGE."""
    results: dict[str, float] = {}
    chunk_size = 60  # URL-length guard; WB enforces limits on the path segment

    for i in range(0, len(iso3_list), chunk_size):
        chunk = iso3_list[i : i + chunk_size]
        url = f"{WB_BASE}/country/{';'.join(chunk)}/indicator/{indicator}"
        params = {"date": WB_YEAR_RANGE, "format": "json", "per_page": 5000}

        for attempt in range(retries):
            try:
                resp = requests.get(url, params=params, timeout=30)
                resp.raise_for_status()
                payload = resp.json()
                if len(payload) < 2 or not payload[1]:
                    break
                records = sorted(payload[1], key=lambda r: r.get("date", ""), reverse=True)
                for rec in records:
                    iso3 = rec.get("countryiso3code") or ""
                    val = rec.get("value")
                    if iso3 and val is not None and iso3 not in results:
                        results[iso3] = float(val)
                break
            except requests.RequestException:
                if attempt < retries - 1:
                    time.sleep(2**attempt)

        time.sleep(0.25)  # be polite to the WB API

    return results


def _fetch_and_sum(indicators: list[str], iso3_list: list[str]) -> dict[str, float]:
    """Fetch multiple indicators and return their sum per country."""
    totals: dict[str, float] = {}
    for ind in indicators:
        click.echo(f"      {ind}", nl=False)
        data = _wb_fetch(ind, iso3_list)
        click.echo(f"  ({len(data)} countries)")
        for iso3, val in data.items():
            totals[iso3] = totals.get(iso3, 0.0) + val
    return totals


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


@click.command()
@click.option(
    "--classifications",
    default=str(DATA_DIR / "processed" / "country_classifications.csv"),
    show_default=True,
    help="Path to country_classifications.csv",
)
@click.option(
    "--output-dir",
    default=str(DATA_DIR / "processed"),
    show_default=True,
    help="Directory for output CSV files",
)
def main(classifications: str, output_dir: str) -> None:
    """Download priority population group estimates for IDA/IBRD/Blend countries."""
    out_dir = Path(output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    # ------------------------------------------------------------------
    # 1. Country list
    # ------------------------------------------------------------------
    click.echo("Loading country classifications...")
    clf = pd.read_csv(classifications)
    ida_ibrd = clf[clf["lending_type"].isin(IDA_IBRD_TYPES)].copy()
    iso3_list = ida_ibrd["iso3"].dropna().tolist()
    click.echo(f"  {len(iso3_list)} IDA / IBRD / Blend countries\n")

    # ------------------------------------------------------------------
    # 2. World Bank — age-group populations
    # ------------------------------------------------------------------
    click.echo("Fetching under-5 population (ages 0-4):")
    under5_map = _fetch_and_sum(UNDER5_INDS, iso3_list)

    click.echo("\nFetching 65+ population:")
    over65_map = _fetch_and_sum(OVER65_INDS, iso3_list)

    click.echo("\nFetching 70+ population (subset of above):")
    over70_map = _fetch_and_sum(OVER70_INDS, iso3_list)

    # ------------------------------------------------------------------
    # 3. World Bank — births inputs
    # ------------------------------------------------------------------
    click.echo("\nFetching crude birth rate and total population:")
    cbr_map = _wb_fetch("SP.DYN.CBRT.IN", iso3_list)
    pop_map = _wb_fetch("SP.POP.TOTL", iso3_list)
    click.echo(f"  CBR        : {len(cbr_map)} countries")
    click.echo(f"  Population : {len(pop_map)} countries")

    # ------------------------------------------------------------------
    # 4. World Bank — teachers
    # ------------------------------------------------------------------
    click.echo("\nFetching teacher counts:")
    teacher_maps = {}
    for ind in TEACHER_INDS:
        click.echo(f"  {ind}", nl=False)
        teacher_maps[ind] = _wb_fetch(ind, iso3_list)
        click.echo(f"  ({len(teacher_maps[ind])} countries)")

    # ------------------------------------------------------------------
    # 5. Assemble
    # ------------------------------------------------------------------
    click.echo("\nAssembling dataset...")
    df = ida_ibrd[["iso3", "name", "region", "income_level", "lending_type"]].copy()

    df["under_5"] = df["iso3"].map(under5_map)
    df["over_65"] = df["iso3"].map(over65_map)
    df["over_70"] = df["iso3"].map(over70_map)

    df["cbr"] = df["iso3"].map(cbr_map)
    df["population"] = df["iso3"].map(pop_map)
    annual_births = df["cbr"] / 1000.0 * df["population"]

    df["under_6mo"] = annual_births / 2.0
    df["pregnant"] = annual_births * (40.0 / 52.0)

    teacher_df = pd.DataFrame(
        {ind: df["iso3"].map(teacher_maps[ind]) for ind in TEACHER_INDS}
    )
    df["teachers"] = teacher_df.sum(axis=1, min_count=1)

    # ------------------------------------------------------------------
    # 6. Export
    # ------------------------------------------------------------------
    output_cols = [
        "iso3", "name", "lending_type", "income_level", "region",
        "under_5", "under_6mo", "over_65", "over_70", "pregnant", "teachers",
    ]
    df_out = df[output_cols].sort_values(["lending_type", "iso3"]).reset_index(drop=True)

    targets_path = out_dir / "population_targets.csv"
    df_out.to_csv(targets_path, index=False)
    click.echo(f"\nSaved {targets_path}  ({len(df_out)} rows)")

    num_cols = ["under_5", "under_6mo", "over_65", "over_70", "pregnant", "teachers"]
    summary = (
        df_out.groupby("lending_type")[num_cols]
        .sum(min_count=1)
        .reset_index()
    )
    summary_path = out_dir / "population_targets_summary.csv"
    summary.to_csv(summary_path, index=False)
    click.echo(f"Saved {summary_path}")

    # ------------------------------------------------------------------
    # 7. Console report
    # ------------------------------------------------------------------
    click.echo("\n" + "=" * 80)
    click.echo(f"POPULATION TARGETS  (persons, WB data {WB_YEAR_RANGE})")
    click.echo("=" * 80)
    click.echo(summary.to_string(index=False, float_format="{:,.0f}".format))

    click.echo("\nData coverage (non-null estimates):")
    for col in num_cols:
        n_ok = df_out[col].notna().sum()
        click.echo(f"  {col:<12}  {n_ok:>3} / {len(df_out)} countries")


if __name__ == "__main__":
    main()

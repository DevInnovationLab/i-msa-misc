# i-msa-rp-work-test

Materials for testing how robust LLMs (and human candidates) are on a research-analyst work test involving messy real-world data.

The setup injects confounding rows into an IHME AMR burden extract so careless filtering or duplication can inflate headline death figures.

## Layout

```
i-msa-rp-work-test/
├── data/
│   ├── raw/                  # unmodified IHME extract (gitignored)
│   └── candidate/            # candidate / LLM dataset (gitignored)
├── scripts/
│   └── inject_traps.py       # builds the candidate file + answer key
├── notebooks/                # exploratory / grading notebooks
├── TRAP_ANSWER_KEY.md        # grader reference — do not distribute
├── pyproject.toml
└── README.md
```

Large CSVs under `data/` are gitignored. Rebuild them locally from the IHME download below.

## Data source (IHME)

Raw input:

```
data/raw/IHME_AMR_BURDEN_2019_NUMBER_Y2022M01D20.CSV
```

Download from IHME’s Global Health Data Exchange (GHDx):

- Record: [Global Bacterial Antimicrobial Resistance Burden Estimates 2019](https://ghdx.healthdata.org/record/ihme-data/global-bacterial-antimicrobial-resistance-burden-estimates-2019)
- File: **Bacterial AMR burden estimates 2019: number** (CSV)
- Suggested citation: Institute for Health Metrics and Evaluation (IHME), University of Oxford. *Global Bacterial Antimicrobial Resistance Burden Estimates 2019*. Seattle, United States of America: IHME, 2022. DOI: [10.6069/DBG1-V028](https://doi.org/10.6069/DBG1-V028)
- Related paper: Murray et al., *The Lancet* (2022), [Global burden of bacterial antimicrobial resistance in 2019](https://doi.org/10.1016/S0140-6736(21)02724-0)

Save/rename the downloaded number file to the path above (filename includes the IHME `Y2022M01D20` stamp used by this project). Use is subject to the [IHME non-commercial user agreement](https://www.healthdata.org/data-tools-practices/data-practices/ihme-free-charge-non-commercial-user-agreement).

## Setup

We use [Poetry](https://python-poetry.org/) for the Python environment, same as other folders in `i-msa-misc`.

```bash
cd i-msa-rp-work-test
poetry install
```

Activate the environment:

```bash
poetry shell
```

Or run a one-off command:

```bash
poetry run python scripts/inject_traps.py
```

### Build the candidate dataset

1. Place the unmodified IHME extract at `data/raw/IHME_AMR_BURDEN_2019_NUMBER_Y2022M01D20.CSV`.
2. Regenerate:

```bash
poetry run python scripts/inject_traps.py
```

Outputs:

- `data/candidate/IHME_AMR_BURDEN_2019_NUMBER.CSV` (YLDs removed; traps injected; sorted)
- `TRAP_ANSWER_KEY.md`

## Contributing

See instructions in the `i-msa-misc` top-level README.

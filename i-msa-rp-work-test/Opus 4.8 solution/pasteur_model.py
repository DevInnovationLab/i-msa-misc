"""
PASTEUR Act — Expected Net Present Value to the US, Canada & Greenland
=====================================================================

Core analysis for the stylized PASTEUR Act cost-effectiveness assessment.

WHAT THIS SCRIPT DOES
---------------------
1. Reads the IHME 2019 AMR burden CSV and extracts the attributable AMR
   mortality burden for "High-income North America" (GBD location_id 100),
   which is the IHME geography that maps to the US + Canada + Greenland.
2. Forecasts that burden forward using the 2024 Lancet GBD growth path.
3. Models the policy as a decision problem: the $6bn subsidy raises the
   private expected NPV of an antimicrobial program from negative to
   positive, inducing development that would not otherwise happen. The
   social value is the health burden averted by the induced drug(s),
   valued at a $13m VSL, net of the program's fiscal cost.
4. Runs a one-way sensitivity sweep on the parameters that matter most.

All monetary values are in USD. Health values use a $13m VSL as instructed.
Government cashflows are discounted at 2%; the private-firm participation
calculation uses 9%.

Run:  python pasteur_model.py  (expects the IHME CSV in the same folder)

Core analysis (ex-comments/whitespace) is well under the 400-line limit.
"""

import pandas as pd
import numpy as np

# ----------------------------------------------------------------------
# 0. PARAMETERS  (all sourced; see report for citations)
# ----------------------------------------------------------------------

CSV = "IHME_AMR_BURDEN_2019_NUMBER_Y2022M01D20.CSV"
LOCATION_ID = 100                 # High-income North America = US + Canada + Greenland

# --- Benefit-cost assumptions given in the task ---
VSL = 13_000_000                  # $13m value of statistical life
R_GOV = 0.02                      # government discount rate
R_FIRM = 0.09                     # private-firm discount rate

# --- Policy design (stylized) ---
SUBSIDY_PER_CRITERION = 100_000_000   # $100m/yr per criterion met
SUBSIDY_YEARS = 10                    # paid over 10 years
PROGRAM_CAP = 6_000_000_000           # $6bn total funding cap

# --- Drug development economics (HHS/ASPE Sertkaya & Franz 2022) ---
# Anti-infective expected capitalized development+approval cost incl.
# failures and cost of capital (Sertkaya JAMA 2024 / ASPE): ~$379m.
# AM-cohort expected capitalized cost incl. Phase 4: ~$1,508m.
# We take a central out-of-pocket-plus-capital private cost the firm must
# recover. Sertkaya reports ~$379m (anti-infective, capitalized, incl.
# failures). We use this as the firm's expected cost hurdle.
DEV_COST = 379_000_000
# Overall probability of success, non-clinical -> market, anti-infective
# (ASPE Table 9): 15.5%. Used for the induced-development reasoning and
# the "grant vs prize" discussion, not double-counted against DEV_COST
# (which already embeds failure cost).
P_SUCCESS = 0.155

# --- Private commercial revenue (ASPE market-performance analysis) ---
# New AM drugs plateau at low peak-year sales; Teflaro example plateaued
# ~$36-42m/yr. We take a central peak of $40m/yr, ramped over the launch
# years, over a ~12-year effective patent-protected commercial life.
PEAK_SALES = 40_000_000
COMMERCIAL_YEARS = 12
GROSS_MARGIN = 0.80               # share of sales that is contribution margin

# --- Epidemiology / forecast ---
# 2024 Lancet GBD: global attributable AMR deaths ~ +70% by 2050 vs ~2022.
# High-income regions grow far slower (burden shifts to elderly, not kids).
# We use a conservative high-income real growth path.
HIC_ANNUAL_BURDEN_GROWTH = 0.010  # 1.0%/yr real growth in HIC attributable burden

# --- Attribution of averted burden to a single new drug ---
# A new antimicrobial is NOT a cure-all: it addresses a slice of the total
# resistant-infection burden (specific pathogen/syndrome, last-line use,
# partial uptake, partial efficacy, and only excess/attributable deaths are
# recoverable). This fraction is the single most important judgment call.
SHARE_OF_BURDEN_ADDRESSED = 0.03  # 3% of attributable burden, central case

# --- Counterfactual: would the drug have been developed anyway? ---
# The subsidy only creates value for drugs that would NOT exist absent it.
# Prob. the marginal drug is genuinely additional (not crowding-in a drug
# that would have come anyway):
P_ADDITIONAL = 0.5

# --- Time structure ---
DEV_LEAD_YEARS = 8                # years from program start to drug launch
BENEFIT_YEARS = 20               # years of health benefit counted after launch
HORIZON = DEV_LEAD_YEARS + BENEFIT_YEARS


# ----------------------------------------------------------------------
# 1. EXTRACT 2019 BURDEN FOR US + CANADA + GREENLAND (location 100)
# ----------------------------------------------------------------------

def load_burden():
    """Return attributable & associated 2019 AMR deaths for location 100.

    Uses the 'drug-susceptible infection' counterfactual for ATTRIBUTABLE
    burden (excess deaths caused specifically by resistance -- the burden a
    working new drug could recover) and 'no infection' for ASSOCIATED
    burden (all deaths involving a resistant infection). We value the
    ATTRIBUTABLE figure; associated is reported for context/sensitivity.
    """
    cols = ['measure_name', 'location_id', 'age_group_name', 'cause_name',
            'infectious_syndrome', 'pathogen', 'antibiotic_class',
            'counterfactual', 'val']
    df = pd.read_csv(CSV, usecols=cols)
    d = df[(df.location_id == LOCATION_ID) &
           (df.age_group_name == 'All Ages') &
           (df.cause_name == 'All causes') &
           (df.pathogen == 'All pathogens') &
           (df.antibiotic_class == 'Resistance to one or more antibiotics') &
           (df.infectious_syndrome == 'All infectious syndromes')]

    def pick(measure, cf):
        return d[(d.measure_name == measure) &
                 (d.counterfactual == cf)].val.sum()

    return {
        'deaths_attributable': pick('Deaths', 'Drug-susceptible infection'),
        'deaths_associated':   pick('Deaths', 'No infection'),
        'dalys_attributable':  pick('DALYs (Disability-Adjusted Life Years)',
                                     'Drug-susceptible infection'),
    }


# ----------------------------------------------------------------------
# 2. HELPER: net present value
# ----------------------------------------------------------------------

def npv(cashflows, rate, start_year=0):
    """NPV of a list of cashflows, first flow at t=start_year."""
    return sum(cf / (1 + rate) ** (start_year + t)
               for t, cf in enumerate(cashflows))


# ----------------------------------------------------------------------
# 3. PRIVATE-SIDE: does the firm develop WITHOUT the subsidy?
# ----------------------------------------------------------------------

def private_npv_without_subsidy():
    """Expected NPV to the developer of an AM program, no subsidy.

    Revenue ramps linearly to PEAK_SALES over 4 years then plateaus,
    across COMMERCIAL_YEARS, at GROSS_MARGIN contribution. Discounted at
    the firm's 9%, launch at DEV_LEAD_YEARS. Development cost DEV_COST is
    incurred (as a present value) at t=0. Because DEV_COST already embeds
    the cost of failures, we compare it to expected (probability-weighted
    downstream) revenue.
    """
    ramp = [min(1.0, (y + 1) / 4.0) for y in range(COMMERCIAL_YEARS)]
    sales = [PEAK_SALES * r for r in ramp]
    margin = [s * GROSS_MARGIN for s in sales]
    pv_rev = npv(margin, R_FIRM, start_year=DEV_LEAD_YEARS) * P_SUCCESS
    return pv_rev - DEV_COST


def subsidy_pv_to_firm(n_criteria):
    """PV (at firm's 9%) of the 10-year subsidy stream for a drug meeting
    n_criteria, respecting the $6bn program cap on annual commitment."""
    annual = min(n_criteria * SUBSIDY_PER_CRITERION,
                 PROGRAM_CAP / SUBSIDY_YEARS)
    stream = [annual] * SUBSIDY_YEARS
    return npv(stream, R_FIRM, start_year=DEV_LEAD_YEARS)


# ----------------------------------------------------------------------
# 4. SOCIAL VALUE OF AN INDUCED DRUG
# ----------------------------------------------------------------------

def social_value_of_drug(burden, share=SHARE_OF_BURDEN_ADDRESSED):
    """PV of health benefit (deaths averted x VSL) from one induced drug,
    discounted at the government's 2%. Burden grows at HIC growth rate and
    the drug recovers `share` of attributable deaths each year over
    BENEFIT_YEARS after launch."""
    base_deaths = burden['deaths_attributable']
    benefit = []
    for y in range(BENEFIT_YEARS):
        # burden in launch-year+y, grown from 2019 baseline
        years_from_2019 = DEV_LEAD_YEARS + y  # rough: program starts ~2026
        grown = base_deaths * (1 + HIC_ANNUAL_BURDEN_GROWTH) ** years_from_2019
        deaths_averted = grown * share
        benefit.append(deaths_averted * VSL)
    return npv(benefit, R_GOV, start_year=DEV_LEAD_YEARS)


def program_fiscal_cost(n_criteria, n_drugs):
    """PV (government 2%) of subsidy outlays, capped at $6bn nominal."""
    annual = min(n_criteria * SUBSIDY_PER_CRITERION,
                 PROGRAM_CAP / SUBSIDY_YEARS)
    total_annual = annual * n_drugs
    # enforce total nominal cap
    if total_annual * SUBSIDY_YEARS > PROGRAM_CAP:
        total_annual = PROGRAM_CAP / SUBSIDY_YEARS
    stream = [total_annual] * SUBSIDY_YEARS
    return npv(stream, R_GOV, start_year=0)


# ----------------------------------------------------------------------
# 5. MAIN EXPECTED-NPV CALCULATION
# ----------------------------------------------------------------------

def run(share=SHARE_OF_BURDEN_ADDRESSED,
        p_additional=P_ADDITIONAL,
        n_criteria=3,
        verbose=True):
    burden = load_burden()

    # How many drugs can $6bn fund? At 3 criteria = $300m/yr = $3bn/drug
    # over 10y; cap therefore funds ~2 drugs at full award.
    annual_award = min(n_criteria * SUBSIDY_PER_CRITERION,
                       PROGRAM_CAP / SUBSIDY_YEARS)
    n_drugs = PROGRAM_CAP / (annual_award * SUBSIDY_YEARS)
    n_drugs = max(1.0, n_drugs)

    priv_base = private_npv_without_subsidy()
    subsidy_pv = subsidy_pv_to_firm(n_criteria)
    induces = (priv_base < 0) and (priv_base + subsidy_pv > 0)

    # Expected number of genuinely-additional drugs delivered
    exp_additional_drugs = n_drugs * p_additional

    gross_benefit = social_value_of_drug(burden, share) * exp_additional_drugs
    fiscal_cost = program_fiscal_cost(n_criteria, n_drugs)

    enpv = gross_benefit - fiscal_cost

    if verbose:
        print("=" * 68)
        print("PASTEUR ACT — EXPECTED NPV (US + Canada + Greenland)")
        print("=" * 68)
        print(f"2019 attributable AMR deaths (loc 100):  "
              f"{burden['deaths_attributable']:>12,.0f}")
        print(f"2019 associated AMR deaths (loc 100):    "
              f"{burden['deaths_associated']:>12,.0f}")
        print("-" * 68)
        print(f"Private NPV WITHOUT subsidy:             "
              f"${priv_base/1e6:>10,.0f}m")
        print(f"PV of subsidy to firm (9%, {n_criteria} crit.):    "
              f"${subsidy_pv/1e6:>10,.0f}m")
        print(f"Subsidy flips private decision?           {induces}")
        print("-" * 68)
        print(f"Drugs fundable under $6bn cap:            {n_drugs:>10,.2f}")
        print(f"Expected additional drugs (x P_add):      "
              f"{exp_additional_drugs:>10,.2f}")
        print(f"Share of attributable burden addressed:   {share:>10.1%}")
        print("-" * 68)
        print(f"PV gross health benefit (2% VSL):        "
              f"${gross_benefit/1e9:>10,.2f}bn")
        print(f"PV fiscal cost (2%):                     "
              f"${fiscal_cost/1e9:>10,.2f}bn")
        print("=" * 68)
        print(f"EXPECTED NET PRESENT VALUE:              "
              f"${enpv/1e9:>10,.2f}bn")
        print("=" * 68)

    return dict(enpv=enpv, gross_benefit=gross_benefit,
                fiscal_cost=fiscal_cost, n_drugs=n_drugs,
                induces=induces, burden=burden,
                priv_base=priv_base, subsidy_pv=subsidy_pv)


# ----------------------------------------------------------------------
# 6. SENSITIVITY SWEEP
# ----------------------------------------------------------------------

def sensitivity():
    print("\nONE-WAY SENSITIVITY ON KEY JUDGMENT PARAMETERS")
    print("-" * 68)
    print("Share of attributable burden a new drug recovers:")
    for s in [0.005, 0.01, 0.03, 0.05, 0.10]:
        r = run(share=s, verbose=False)
        print(f"   share={s:5.1%}  ->  ENPV = ${r['enpv']/1e9:8,.2f}bn")

    print("\nProbability the induced drug is genuinely additional:")
    for p in [0.25, 0.5, 0.75, 1.0]:
        r = run(p_additional=p, verbose=False)
        print(f"   P_add={p:5.0%}  ->  ENPV = ${r['enpv']/1e9:8,.2f}bn")

    print("\nNumber of subsidy criteria met (award size per drug):")
    for n in [1, 2, 3]:
        r = run(n_criteria=n, verbose=False)
        print(f"   criteria={n}  ->  ENPV = ${r['enpv']/1e9:8,.2f}bn "
              f"(funds {r['n_drugs']:.1f} drugs)")


if __name__ == "__main__":
    run()
    sensitivity()

# The PASTEUR Act and the Returns to Antimicrobial Innovation
### Expected Net Present Value to the United States, Canada, and Greenland

---

## Question 1 — Estimated NPV and how it was derived (≤150 words)

**Central estimate: the stylized PASTEUR Act generates roughly +$290 billion in expected net present value, with a plausible range of about +$40 billion to +$500 billion.**

I started from the IHME data, which shows about 45,000 deaths per year in the US–Canada–Greenland region *caused specifically by* antimicrobial resistance (deaths that a working new drug could prevent). I assumed the $6 billion program flips the economics for developers—whose products otherwise lose money—and induces one to two genuinely new antibiotics. Each new drug recovers a modest slice (central case: 3%) of that death burden over 20 years. Valuing each death avoided at the required $13 million and discounting the government's costs and benefits at 2%, the health value vastly exceeds the $5.5 billion present-value cost. The estimate is dominated by the value of statistical life and by how much burden a new drug actually addresses.

---

## Question 2 — Two omitted elements that would most improve the estimate (≤100 words)

1. **Endogenous, dynamic resistance and the "insurance" value of a stocked pipeline.** My model treats a new drug as recovering a fixed share of a slowly growing burden. In reality resistance evolves in response to use; a delinked reward preserves a drug's future effectiveness, and having *any* effective agent in reserve against a fast-spreading resistant strain has large option value that a static VSL calculation misses.

2. **Morbidity, transmission externalities, and health-system costs.** I valued only deaths averted. Including DALYs from non-fatal resistant infections (≈870,000/year attributable), reduced onward transmission, shorter hospital stays, and freed ICU capacity would raise the benefit side materially.

---

## Question 3 — One improvement to the Act, with reasoning

**Replace the flat "$100 million per criterion" schedule with a reward scaled to each drug's expected health value (deaths and DALYs averted), subject to the same total cap.**

The stylized Act pays the same $100m/criterion whether a drug addresses a pathogen killing 1,100 people a year or 40,000. That is a blunt instrument: it rewards *checking a box*, not *creating value*. My sensitivity analysis makes the problem concrete—the social return per dollar is far higher for drugs targeting high-burden pathogens (e.g., *S. aureus* / MRSA at ~12,500 attributable deaths, *E. coli* at ~8,300) than for those clearing a low threshold. Under the current design a developer is indifferent between a high-impact and a marginal drug once both clear the criteria, so private R&D effort is not steered toward where the health returns are largest.

A value-based reward fixes the incentive. Economically, a Pigouvian-style subsidy should equal the marginal external benefit the innovator creates; tying the payment to modeled deaths/DALYs averted aligns the developer's private return with social value and allocates the fixed $6bn budget toward the highest-return targets. To keep it practical and preserve the delinkage that protects stewardship, the reward would be set *ex ante* from the target pathogen's documented burden (using exactly the IHME-type data used here), not from realized sales—so companies still have no incentive to over-promote. The trade-off is added administrative complexity and model risk in scoring value; a tiered schedule (e.g., three or four burden bands) captures most of the efficiency gain while remaining auditable.

---

## Methodology and key assumptions

### Framing: value = burden averted by *induced* drugs, minus fiscal cost

The Act's counterfactual value is *not* the entire AMR burden. It is the health gain from antibiotics that exist **because of** the subsidy and would not exist otherwise, net of what the government pays. The model is therefore a decision problem in four steps:

1. **Establish the burden** a new drug could act on (IHME data).
2. **Check that the subsidy changes the developer's decision** (private NPV analysis).
3. **Value the health gain** from the induced drug(s) at $13m VSL, discounted at 2%.
4. **Net out the fiscal cost** of the subsidy, discounted at 2%.

### Data choices (and why they matter)

- **Geography.** "US, Canada, and Greenland" is not a country field in the IHME data, which is reported at GBD region level. The correct mapping is the **"High-income North America" super-region (location_id 100)**. Using "North America" loosely, or summing countries that don't exist in the file, is a common error.
- **Counterfactual.** IHME reports two counterfactuals. I value the **"drug-susceptible infection"** counterfactual (**~45,000 deaths**, the *attributable* burden—excess deaths caused by resistance itself), because that is what restoring treatability recovers. The **"no infection"** counterfactual (~186,000 deaths, *associated* burden) counts every death involving a resistant organism and would overstate what a new drug can undo. This distinction roughly quadruples the burden if chosen wrongly.

### Parameters and sources

| Parameter | Value | Source |
|---|---|---|
| Attributable AMR deaths, loc 100, 2019 | ~44,800/yr | IHME CSV (computed) |
| Value of statistical life | $13m | Task instruction |
| Government discount rate | 2% | Task instruction |
| Firm discount rate | 9% | Task instruction |
| Anti-infective dev. cost (capitalized, incl. failures) | ~$379m | HHS/ASPE Sertkaya & Franz (2022); Sertkaya JAMA 2024 |
| Anti-infective overall success prob. (non-clinical→market) | 15.5% | ASPE Table 9 |
| New-AM peak-year sales | ~$40m/yr | ASPE market-performance analysis (Teflaro plateau ~$36–42m) |
| Burden growth to 2050 | +70% global; ~1%/yr modeled for high-income | 2024 Lancet GBD forecast (Naghavi et al.) |
| Share of attributable burden one drug recovers | 3% central (0.5–10% swept) | Author judgment |
| Prob. induced drug is genuinely additional | 50% | Author judgment |

### The private-market failure (why the subsidy bites)

At a 9% cost of capital, a new antibiotic earning ~$40m/year in peak sales cannot recover a ~$379m capitalized development cost: the model puts the developer's expected NPV at **about –$360 million**. The stylized $300m/year reward has a present value to the firm of **~$1.05 billion**, which flips the decision to positive. This confirms the market-failure premise: the reward is roughly the right order of magnitude to induce entry, which is why the $6bn cap realistically funds one to two full awards.

### Results and sensitivity

The central expected NPV is **+$289 billion**. It is *not* precise—it is a statement that the health value of even one or two induced antibiotics, valued at $13m per life, dwarfs a $6bn outlay. The estimate is most sensitive to:

- **Share of burden a drug addresses** (0.5%→10% moves ENPV from ~$44bn to ~$977bn). This is the dominant judgment call.
- **Additionality** (P_add 25%→100% scales ENPV from ~$142bn to ~$584bn).
- **Award size / number of drugs funded.** Interestingly, funding more single-criterion drugs (six $100m/yr awards) scores higher than two full three-criterion awards *in this simplified model*, because each additional induced drug brings another tranche of health benefit—an artifact worth flagging, and part of the motivation for the value-based redesign in Q3.

### Honest limitations

The headline number is large because VSL valuation of mortality is inherently large, and because the benefit is essentially unbounded above while the cost is capped at $6bn. The result should be read as **"the policy is very likely strongly positive-NPV under any reasonable parameterization,"** not as a point forecast. Key simplifications: static resistance dynamics, mortality-only valuation, deterministic (non-Monte-Carlo) treatment of uncertainty, and a fixed rather than probability-distributed number of induced drugs. Each is discussed above as a candidate for the next iteration.

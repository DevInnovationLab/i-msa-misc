############################################################
# Title: Required Reward Size vs. Number of Entrants
# Purpose: Compare the reward required to make entry break-even
#          under (A) fixed-number-of-prizes ("fixed pots")
#          and (B) a single large pot ("large pot") shared.
#
# Notes:
# - All formulas reflect the original analysis.
# - The core output is a data frame `results` with required
#   total reward sizes across entrant counts for both designs.
############################################################

# ------------------------- Parameters (from ArMOR) ----------------------------
p_success  <- 0.0276   # per-entrant success probability
prize_each <- 1676     # prize size per winner (fixed-pots design)
n_prizes  <- 5        # number of prizes/winners (fixed-pots design)
entry_fee  <- 34.08    # entry cost/fee

# ----------------- Required reward sizes across entrant counts -----------------
# We compute the reward required to make expected profit = 0 for a given number
# of entrants under:
#   A) Fixed pots: total required prize pool = n_prizes * required_per_winner
#   B) Large pot:  total required pot shared across all successes

entrant_counts <- 1:400

# Fixed pots: solve algebraically for the *per-winner* prize that sets expected profit to zero,
# then multiply by n_prizes to get the *total* required reward.
required_per_winner <- entry_fee / (
  p_success * pbinom(q = n_prizes - 1, size = entrant_counts - 1, prob = p_success) +
    (n_prizes / entrant_counts) * (1 - pbinom(q = n_prizes, size = entrant_counts, prob = p_success))
)

required_total_fixed_pots <- required_per_winner * n_prizes

# Large pot: required total pot (shared) to make expected profit = 0.
# (Formula carried over from original analysis.)
required_total_large_pot <- entry_fee * entrant_counts / (1 - (1 - p_success)^entrant_counts)

# ------------------------------- Output table ---------------------------------
results <- data.frame(
  entrants = entrant_counts,
  required_total_fixed_pots = required_total_fixed_pots,
  required_total_large_pot  = required_total_large_pot
)

# `results` is the key comparison artifact for sharing.
# Example head:
# head(results)

# --- Helper: Expected profit for a single entrant in the fixed-pots design ----
expected_profit_fixed_pots <- function(
  n_entrants,
  prize_per_winner,
  n_prizes,
  entry_fee,
  p_success
) {
  # Probability that the focal entrant wins a prize outright (i.e., at least one of their trials succeeds
  # and fewer than n_prizes of the other (n_entrants - 1) entrants succeed).
  #
  # Term 1: Focal entrant succeeds (prob = p_success) AND at most (n_prizes - 1) of the other entrants
  #         succeed (so the focal entrant secures a prize of size prize_per_winner).
  #
  # Term 2: Overfill case — if total successes exceed n_prizes, prizes are effectively rationed.
  #         In expectation, each entrant’s share in that case is (n_prizes * prize_per_winner / n_entrants).
  #         The probability of overfill is 1 - P[#successes among n_entrants <= n_prizes].
  #
  # Expected profit = (expected payout) - entry_fee.

  term_win_direct <- p_success * prize_per_winner *
    pbinom(q = n_prizes - 1, size = n_entrants - 1, prob = p_success)

  term_overfill_share <- (n_prizes * prize_per_winner / n_entrants) *
    (1 - pbinom(q = n_prizes, size = n_entrants, prob = p_success))

  (term_win_direct + term_overfill_share) - entry_fee
}


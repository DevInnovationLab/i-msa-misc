library(readr)

# Define PPE cost-effectiveness
ppe_dollars_per_hcw_life <- 4309 # https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0240503
covid_deaths_per_10k <- (
  14.86e6 / # WHO COVID-19 deaths between 2020 and 2021: https://ourworldindata.org/excess-mortality-covid?utm_source=chatgpt.com
  (7.86e9 / 10000) # 2020 global population /10k : https://data.worldbank.org/indicator/SP.POP.TOTL
)


# Get exceedance function data points
madhav_exceedance_raw <- read_csv("./data/raw/madhav_et_al_figure_4_digitized.csv")

# Extract central exceedance function and ensure numeric columns
madhav_exceedance <- madhav_exceedance_raw[-1, c(1, 2)]
colnames(madhav_exceedance) <- c("deaths_per_10k", "annual_risk")
madhav_exceedance$deaths_per_10k <- as.numeric(madhav_exceedance$deaths_per_10k)
madhav_exceedance$annual_risk <- as.numeric(madhav_exceedance$annual_risk)
madhav_exceedance$annual_risk <- madhav_exceedance$annual_risk / 100
madhav_exceedance <- madhav_exceedance[order(madhav_exceedance$deaths_per_10k), ]


# Test a few alternative interpolations techniques
spline_fit <- splinefun(madhav_exceedance$deaths_per_10k,
                        madhav_exceedance$annual_risk)
approx_fit <- approxfun(madhav_exceedance$deaths_per_10k,
                        madhav_exceedance$annual_risk)

# Plot spline and approx fit with data so I can see
x_range <- seq(min(madhav_exceedance$deaths_per_10k),
               max(madhav_exceedance$deaths_per_10k),
               length.out = 300)

plot(madhav_exceedance$deaths_per_10k, madhav_exceedance$annual_risk,
     pch=16, col="black", xlab="Deaths per 10k", ylab="Annual exceedance risk (%)",
     log = "y", main="Spline vs Approximation Fit")

y_spline <- spline_fit(x_range)
y_approx <- approx_fit(x_range)
lines(x_range, y_spline, col="blue", lwd=2)
# Add the approx fit (piecewise linear)
lines(x_range, y_approx, col="red", lwd=2, lty=2)
legend("topright", legend = c("Data", "Spline Fit", "Approx Fit"),
       col = c("black", "blue", "red"),
       pch = c(16, NA, NA),
       lty = c(NA, 1, 2),
       lwd = c(NA, 2, 2))

# Both methods fit well and are similar so will proceed with approx function.

scale_hcw_ce <- function(deaths_per_10k) {
  ppe_dollars_per_hcw_life / sqrt(deaths_per_10k / covid_deaths_per_10k)
}

scaled_hcw_ce <- scale_hcw_ce(madhav_exceedance$deaths_per_10k)
scaled_hcw_ce_fn <- splinefun(
  scaled_hcw_ce,
  madhav_exceedance$annual_risk
)

expected_cost_per_hcw_life <- integrate(scaled_hcw_ce_fn, min(scaled_hcw_ce), max(scaled_hcw_ce))


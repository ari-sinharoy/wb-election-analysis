# West Bengal 2026 Assembly Election Sensitivity Analysis

A constituency-level statistical modeling and simulation framework to analyze electoral outcomes under uncertainty.

## Objective

This project focuses on:

- Modeling vote share using limited historical data
- Running Monte Carlo simulations for seat projections
- Performing sensitivity analysis to identify key swing factors
- Enabling post-election error attribution

---

## Project Structure

- `data/`
  - `raw/` – original scraped datasets (Wikipedia, ECI)
  - `processed/` – cleaned and feature-engineered data
- `notebooks/` – EDA, modeling, analysis
- `src/` – reusable scripts
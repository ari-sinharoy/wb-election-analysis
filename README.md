# West Bengal 2026 assembly election sensitivity analysis

This project builds a constituency-level election modeling pipeline to:

- Analyze historical voting patterns
- Model vote share with small-data ML techniques
- Run Monte Carlo simulations for seat projections
- Perform sensitivity analysis to identify swing factors
- Enable post-election model evaluation

## Project Structure

data/
├── raw/        # scraped / original data (Wikipedia, ECI, etc.)
├── processed/  # cleaned and feature-engineered datasets

notebooks/      # exploratory and modeling notebooks

src/            # reusable scripts (data processing, modeling)

## Current Status
- [ ] Data scraping pipeline
- [ ] Data cleaning
- [ ] Baseline model
- [ ] Sensitivity analysis

## Tech Stack
Python, Pandas, Scikit-learn, Monte Carlo Simulation
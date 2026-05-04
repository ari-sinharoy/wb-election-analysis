# West Bengal Election Sensitivity Analysis

## Overview

This project builds a **constituency-level election modeling framework** for the West Bengal Assembly.

Instead of focusing only on prediction, the goal is to:

- Identify **key drivers of electoral outcomes**
- Quantify **uncertainty in close contests**
- Enable **scenario-based and post-election analysis**

---

## Key Result (Baseline Scenario)

| Party | Seats |
|------|------|
| TMC  | 169 |
| BJP  | 125 |
| Others | 0 |

> **43 constituencies have <3% margin → highly sensitive to small changes**

- TMC vulnerable seats: 23  
- BJP vulnerable seats: 20  

---

## Methodology

### Baseline Model (Swing-Based)

Projected Vote Share = Assembly 2021 + Lok Sabha Swing * 0.5 

Swing = LS 2024 − LS 2019  

- Swing is computed at the **Lok Sabha level**
- Applied to all Assembly segments within that LS seat

---

### Winner Prediction

Winner = party with highest projected vote share  

### Margin Definition

Margin = Top vote share − Second highest vote share  

| Category | Margin |
|--------|--------|
| Safe | >5% |
| Leaning | 3–5% |
| Close | <3% |

---

## Scenario Modeling: Voter Roll Changes (SIR)

This model incorporates structural electoral changes:

- ~11.5% voter deletion (roll correction)
- ~6% new voter 

---

### Modeling Logic

Step 1: Votes = Electors × Vote Share  

Step 2: Removed voters ∝ party vote base × SIR weight  

Step 3: New votes distributed by assumed preference  

Step 4: Adjusted Votes = Old Votes − Removed + New  

Step 5: Adjusted Vote Share = Adjusted Votes / Total Votes  

---

### Scenario Assumptions (Current Run)

**Voter deletion (11.5%) weights:**

| Party | Weight |
|------|--------|
| TMC | 1.0 |
| BJP | 0.2 |
| Left | 1.0 |
| Congress | 1.0 |

**New voter distribution (6%):**

| Party | Share |
|------|-------|
| TMC | 35% |
| BJP | 35% |
| Left | 15% |
| Congress | 15% |

---

## Project Structure

```
data/
├── raw/
├── processed/

src/
├── clean_wiki_results.py
├── baseline_prediction.py

notebooks/
```

---

## Key Insights

- Many constituencies have **very low margins (<3%)**
- Small shifts in vote share can flip multiple seats
- Structural changes (SIR, turnout) can significantly impact outcomes
- Deterministic predictions are insufficient → uncertainty modeling is required

---

## Monte Carlo Simulation Results

We simulate 10,000 elections by perturbing constituency-level vote shares around the SIR-adjusted baseline.

### Seat Distribution (West Bengal Assembly, 294 seats)

| Party | P05 | P10 | Median | P90 | P95 | Min | Max |
|-------|-----|-----|--------|-----|-----|-----|-----|
| TMC   | 155 | 158 | 169    | 179 | 182 | 138 | 200 |
| BJP   | 112 | 115 | 125    | 136 | 139 |  94 | 156 |

### Interpretation

- The **median outcome** suggests:
  - TMC: ~169 seats  
  - BJP: ~125 seats  

- The **central uncertainty range (P10–P90)**:
  - TMC: 158–179  
  - BJP: 115–139  

- The **tails (Min–Max)** show extreme but low-probability outcomes:
  - TMC: 138–200  
  - BJP: 94–156  

### Key Insight

A significant fraction of constituencies are sensitive to small vote-share perturbations, leading to a non-trivial spread in seat outcomes.

For practical interpretation, the **P10–P90 range is the most meaningful uncertainty band**, while Min/Max reflect rare extreme scenarios.

---

## Next Version (Planned)

- Improved SIR modeling  

---

## Tech Stack

- Python
- Pandas / NumPy

---
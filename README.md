# West Bengal Election Sensitivity Analysis

## Overview

This project builds a **constituency-level election modeling framework** for the West Bengal Assembly using historical election data.

Instead of focusing solely on prediction, the goal is to:

- Identify **key factors influencing electoral outcomes**
- Quantify **uncertainty in close contests**
- Enable **post-election analysis and attribution**

The framework combines:
- Historical Assembly result (2021)
- Lok Sabha swing (2019 → 2024)
- Scenario-based adjustments (SIR, new voters)

---

## Project Structure

- `data/`
  - `raw/` – original scraped datasets (Wikipedia, ECI)
  - `processed/` – cleaned and feature-engineered data
- `notebooks/` – EDA, modeling, analysis
- `src/` – reusable scripts

---

## Methodology

### 1. Baseline Model (Swing-Based)

For each assembly constituency \(i\), lok sabha (LS) constituency l, and party \(p\):

	\[
		\text{Projected Vote Share}_{i,p} = \text{Assembly 2021}_{i,p} + \text{Swing}_{l,p}
	\]

Where:

	\[
		\text{Swing}_{l,p} = \text{LS 2024}_{l,p} - \text{LS 2019}_{l,p}
	\]

- Swing is computed at the **LS constituency level**
- Applied uniformly to all Assembly segments within that LS seat

### 2. Baseline Winner

Winner is defined as:

```text
party with maximum projected vote share


## Scenario Modeling: Voter Roll Changes (SIR) and New Voters

Beyond baseline swing-based projections, this framework incorporates **structural changes in the electorate**, specifically:

- Voter roll corrections (Special Intensive Revision – SIR)
- Addition of new voters

These factors can materially alter constituency-level outcomes, especially in close contests.

---

### Motivation

Baseline models assume a stable electorate. However, in practice:

- A fraction of voters may be removed due to roll corrections  
- New voters are continuously added (first-time voters, re-registrations, etc.)

These changes are **not neutral**—they can systematically affect different parties.

---

### Modeling Approach

We convert vote shares into estimated vote counts and then adjust them.

#### Step 1: Convert Vote Share → Votes

\[
\text{Votes}_{i,p} = \text{Electors}_{i} \times \frac{\text{Vote Share}_{i,p}}{100}
\]

Where:
- \(i\): constituency  
- \(p\): party  

---

#### Step 2: Apply Voter Removal (SIR)

Total voters removed:

\[
\text{Removed Total}_{i} = \text{Electors}_{i} \times r_{\text{SIR}}
\]

Where:
- \(r_{\text{SIR}}\) ≈ 11.5% (scenario parameter)

Removed voters are distributed across parties based on:

\[
\text{Removed}_{i,p} \propto \text{Votes}_{i,p} \times w^{\text{SIR}}_{p}
\]

Where:
- \(w^{\text{SIR}}_{p}\): party-specific impact weight

---

#### Step 3: Add New Voters

Total new voters:

\[
\text{New Total}_{i} = \text{Electors}_{i} \times r_{\text{new}}
\]

New votes are allocated based on assumed preference:

\[
\text{New Votes}_{i,p} = \text{New Total}_{i} \times w^{\text{new}}_{p}
\]

Where:
- \(w^{\text{new}}_{p}\): party preference weights for new voters

---

#### Step 4: Adjust Vote Counts

\[
\text{Adjusted Votes}_{i,p}
=
\text{Votes}_{i,p}
- \text{Removed}_{i,p}
+ \text{New Votes}_{i,p}
\]

---

#### Step 5: Convert Back to Vote Share

\[
\text{Adjusted Vote Share}_{i,p}
=
\frac{\text{Adjusted Votes}_{i,p}}{\sum_p \text{Adjusted Votes}_{i,p}} \times 100
\]

---

### Scenario Parameters

The model allows flexible assumptions:

#### 1. Voter Removal Rate
```text
r_SIR ≈ 11–12%


## Example Output 

#### Parameters used:
 - Effect of 11.5% old voter deletion (TMC:1.0, BJP:0.2, Left: 1.0, Congress: 1.0)
 - New voter (6%) distribution (TMC: 35%, BJP: 35%, Left: 15%, Congress: 15%)

TMC: 155 seats
BJP: 139 seats
Others: 0 seats

With 42 vulnerable seats with <3% margin (TMC: 22, BJP: 20)
# -*- coding: utf-8 -*-
"""
Created on Sat May  2 09:36:24 2026

@author: as836
"""
from pathlib import Path
import re
import numpy as np
import pandas as pd

RAW_DIR = Path("data/raw")
PROCESSED_DIR = Path("data/processed")
PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

# task: clean data and create columns
#                   - year
#                   - election_type: assembly / lok_sabha
#                   - constituency
#                   - district
#                   - winner_party
#                   - TMC_vote_share
#                   - BJP_vote_share
#                   - Left_vote_share
#                   - Congress_vote_share
#                   - Others_vote_share
#                   - turnout
#                   - margin
#                   - incumbent_party
#                   - party_switch_indicator
#                   - candidate_incumbent 

## clean and merge assembly election data 2001 -- 2021
def clean_text(x):
    if pd.isna(x):
        return np.nan
    x = str(x)
    x = x.replace("Â", "").replace("\xa0", " ")
    x = re.sub(r"\[[^\]]*\]", "", x)
    x = re.sub(r"\s+", " ", x).strip()
    return x


def to_number(x):
    if pd.isna(x):
        return np.nan
    x = clean_text(x)
    x = x.replace(",", "").replace("%", "")
    try:
        return float(x)
    except ValueError:
        return np.nan


def flatten_columns(columns):
    flat = []

    for top, bottom in columns:
        top = clean_text(top)
        bottom = clean_text(bottom)

        name = f"{top}_{bottom}".lower()
        name = name.replace("runner-up", "runner_up")
        name = name.replace("vote %", "vote_pct")
        name = name.replace("%", "pct")
        name = re.sub(r"[^a-z0-9]+", "_", name)
        name = re.sub(r"_+", "_", name).strip("_")

        flat.append(name)

    return flat


def normalize_constituency_name(x):
    x = clean_text(x)
    if pd.isna(x):
        return np.nan

    # remove constituency type: "Amdanga (SC)" -> "Amdanga"
    x = re.sub(r"\((SC|ST|GEN|GENERAL)\)$", "", x, flags=re.I).strip()

    # remove leading number if present: "12 Amdanga" -> "Amdanga"
    x = re.sub(r"^\d+\s+", "", x).strip()

    return x.lower()


def split_constituency_and_type(name, type_value=None):
    """
    Handles both:
    1. "Amdanga (SC)"
    2. name = "Amdanga", type_value = "SC"
    """

    name = clean_text(name)
    type_value = clean_text(type_value)

    if pd.isna(name):
        return np.nan, np.nan

    match = re.match(r"^(.*?)\s*\((SC|ST|GEN|GENERAL)\)$", name, flags=re.I)

    if match:
        constituency = clean_text(match.group(1))
        constituency_type = clean_text(match.group(2)).upper()
    else:
        constituency = name
        constituency_type = type_value

    if isinstance(constituency_type, str):
        constituency_type = constituency_type.upper()
        constituency_type = constituency_type.replace("GENERAL", "GEN")

    return constituency, constituency_type


def standardize_party(party):
    party = clean_text(party)

    if pd.isna(party):
        return np.nan

    party = party.upper()

    replacements = {
        "ALL INDIA TRINAMOOL CONGRESS": "AITC",
        "TRINAMOOL CONGRESS": "AITC",
        "TMC": "AITC",
        "COMMUNIST PARTY OF INDIA (MARXIST)": "CPM",
        "CPI(M)": "CPM",
        "INDIAN NATIONAL CONGRESS": "INC",
        "CONGRESS": "INC",
        "BHARATIYA JANATA PARTY": "BJP",
    }

    return replacements.get(party, party)


def party_group(party):
    party = standardize_party(party)

    if pd.isna(party):
        return "Others"

    if party == "AITC":
        return "TMC"
    if party == "BJP":
        return "BJP"
    if party in {"CPM", "CPI", "AIFB", "RSP", "SUCI", "SUCI(C)", "FB"}:
        return "Left"
    if party == "INC":
        return "Congress"

    return "Others"


def find_col(df, candidates):
    for c in candidates:
        if c in df.columns:
            return c
    return None


def detect_columns(df):
    """
    Important fix:
    In many Wikipedia tables:
      constituency_constituency = constituency number
      constituency_constituency_1 = constituency name/type
    """

    district_col = find_col(df, ["district_district"])

    constituency_number_col = find_col(
        df,
        [
            "constituency_constituency",
            "constituency_no",
            "constituency_number",
        ],
    )

    constituency_name_col = find_col(
        df,
        [
            "constituency_constituency_1",
            "constituency_constituency1",
            "constituency_name",
        ],
    )

    # fallback: if no separate name column exists, use constituency column
    if constituency_name_col is None:
        constituency_name_col = constituency_number_col

    constituency_type_col = find_col(
        df,
        [
            "constituency_type",
            "constituency_reserved",
            "type_type",
        ],
    )
    

    return {
        "district": district_col,
        "constituency_number": constituency_number_col,
        "constituency_name": constituency_name_col,
        "constituency_type": constituency_type_col,
        "winner_party": find_col(df, ["winner_party", "winner_party_1", "winner_party1"]),
        "winner_pct": find_col(df, ["winner_pct"]),
        "runner_party": find_col(df, ["runner_up_party", "runner_up_party_1", "runner_up_party1"]),
        "runner_pct": find_col(df, ["runner_up_pct"]),
        "margin_votes": find_col(df, ["margin_votes"]),
        "margin_pct": find_col(df, ["margin_pct"]),
        "turnout": find_col(df, ["turnout_pct", "turnout_turnout", "voter_turnout"]),
    }


def clean_one_file(filepath, year):
    df = pd.read_csv(filepath, header=[0, 1], encoding="utf-8")
    df.columns = flatten_columns(df.columns)

    df = df.dropna(axis=1, how="all")

    for col in df.columns:
        if df[col].dtype == "object":
            df[col] = df[col].map(clean_text)

    cols = detect_columns(df)

    if cols["constituency_name"] is None:
        raise ValueError(f"No constituency name column detected in {filepath.name}")

    if cols["winner_party"] is None or cols["winner_pct"] is None:
        raise ValueError(f"Winner party / winner percent missing in {filepath.name}")

    if cols["runner_party"] is None or cols["runner_pct"] is None:
        raise ValueError(f"Runner-up party / runner-up percent missing in {filepath.name}")

    out = pd.DataFrame(index=df.index)

    # FIX 1: year must be scalar assigned across all rows
    out["year"] = year

    # district may be missing initially
    if cols["district"]:
        out["district"] = df[cols["district"]]
    else:
        out["district"] = np.nan

    # FIX 2 and 3: use actual constituency name column, not constituency number
    parsed = df.apply(
        lambda row: split_constituency_and_type(
            row[cols["constituency_name"]],
            row[cols["constituency_type"]] if cols["constituency_type"] else np.nan,
        ),
        axis=1,
    )

    out["constituency"] = parsed.apply(lambda x: x[0])
    out["constituency_type"] = parsed.apply(lambda x: x[1])

    out["winner_party"] = df[cols["winner_party"]].map(standardize_party)

    out["TMC_vote_share"] = 0.0
    out["BJP_vote_share"] = 0.0
    out["Left_vote_share"] = 0.0
    out["Congress_vote_share"] = 0.0
    out["Others_vote_share"] = 0.0

    winner_group = df[cols["winner_party"]].map(party_group)
    runner_group = df[cols["runner_party"]].map(party_group)

    winner_pct = df[cols["winner_pct"]].map(to_number).fillna(0)
    runner_pct = df[cols["runner_pct"]].map(to_number).fillna(0)

    group_to_col = {
        "TMC": "TMC_vote_share",
        "BJP": "BJP_vote_share",
        "Left": "Left_vote_share",
        "Congress": "Congress_vote_share",
        "Others": "Others_vote_share",
    }

    for group, target_col in group_to_col.items():
        out.loc[winner_group == group, target_col] += winner_pct[winner_group == group]
        out.loc[runner_group == group, target_col] += runner_pct[runner_group == group]

    if cols["turnout"]:
        out["turnout"] = df[cols["turnout"]].map(to_number)
    else:
        out["turnout"] = np.nan
        
    if cols["margin_votes"]:
        out["margin_votes"] = df[cols["margin_votes"]].map(to_number)
    else:
        out["margin_votes"] = np.nan

    if cols["margin_pct"]:
        out["margin_pct"] = df[cols["margin_pct"]].map(to_number)
    else:
        out["margin_pct"] = np.nan
        
    out["total_electors_estimated"] = np.where(
        out["margin_pct"].notna() & (out["margin_pct"] != 0),
        out["margin_votes"] * 100 / out["margin_pct"],
        np.nan,
    )
    
    # Convert to integer safely (nullable integer type)
    out["total_electors_estimated"] = (
        out["total_electors_estimated"]
        .round()
        .astype("Int64")   # keeps NaN as <NA> instead of crashing
    )

    # remove header-like junk rows
    out = out.dropna(subset=["constituency"])
    out = out[out["constituency"].str.lower() != "constituency"]

    # lookup key for matching district later
    out["constituency_key"] = out["constituency"].map(normalize_constituency_name)

    return out


def fill_districts_from_2021(all_data):
    """
    FIX 4:
    Use 2021 as the master district lookup.
    Fill missing districts in earlier years by matching constituency names.
    """

    data_2021 = all_data[2021].copy()

    district_lookup = (
        data_2021[["constituency_key", "district"]]
        .dropna(subset=["constituency_key", "district"])
        .drop_duplicates(subset=["constituency_key"])
    )

    cleaned_years = []

    for year, df in all_data.items():
        df = df.copy()

        if year != 2021:
            df = df.merge(
                district_lookup,
                on="constituency_key",
                how="left",
                suffixes=("", "_from_2021"),
            )

            df["district"] = df["district"].fillna(df["district_from_2021"])
            df = df.drop(columns=["district_from_2021"])

        cleaned_years.append(df)

    final = pd.concat(cleaned_years, ignore_index=True)

    # Final sort from 2001 to 2021
    final = final.sort_values(["year", "district", "constituency"]).reset_index(drop=True)

    return final


def main():
    files = {
        2021: RAW_DIR / "WB_Assembly_2021_Results.csv",  # read first conceptually
        2016: RAW_DIR / "WB_Assembly_2016_Results.csv",
        2011: RAW_DIR / "WB_Assembly_2011_Results.csv",
        2006: RAW_DIR / "WB_Assembly_2006_Results.csv",
        2001: RAW_DIR / "WB_Assembly_2001_Results.csv",
    }

    all_data = {}

    for year, filepath in files.items():
        if not filepath.exists():
            print(f"Missing: {filepath}")
            continue

        print(f"Cleaning {year}: {filepath.name}")
        all_data[year] = clean_one_file(filepath, year)

    if 2021 not in all_data:
        raise ValueError("2021 file is required because it is used as the district lookup source.")

    final = fill_districts_from_2021(all_data)

    final_cols = [
        "year",
        "district",
        "constituency",
        "constituency_type",
        "winner_party",
        "TMC_vote_share",
        "BJP_vote_share",
        "Left_vote_share",
        "Congress_vote_share",
        "Others_vote_share",
        "turnout",
        "margin_votes",
        "margin_pct",
        "total_electors_estimated",
    ]

    final = final[final_cols]

    output_path = PROCESSED_DIR / "wb_assembly_results_clean.csv"
    final.to_csv(output_path, index=False, encoding="utf-8")

    print(f"\nSaved: {output_path}")
    print(final.head())
    print(final.tail())


if __name__ == "__main__":
    main()
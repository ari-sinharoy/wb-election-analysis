# -*- coding: utf-8 -*-
"""
Created on Sun May  3 16:22:05 2026

@author: as836
"""

import os
import pandas as pd
import numpy as np
from pathlib import Path

OUTPUT_DIR = Path("data/processed")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

r'''
Baseline Prediction
-------------------

winner = party with max predicted vote share in a constituency

2026 vote share = 2021 assembly vote share + swing from 2024 lok-sabha

swing (district) = 2024 lok-sabha vote share - 2021 lok-sabha vote share

For constituency i in a district d and party p

Projected2026_i,p = Assembly2021_i,p + swing_i,d

'''

dpath = r'C:\Users\as836\Documents\GitHub\wb-election-analysis\data\processed'

AC_results = pd.read_csv(os.path.join(dpath,
                                      'wb_assembly_results_clean.csv'), 
                         header = 0)

AC_result_2021 = AC_results[AC_results['year'] == 2021]

LS_result_2019 = pd.read_csv(os.path.join(dpath,
                                      'WB_General_2019_Results.csv'), 
                         header = 0)

for s in ['LF_votes', 'INC_votes']:
    LS_result_2019[s] = (
        LS_result_2019[s]
        .fillna(0)
        .astype(int)
        )

## convert elector numbers from object to int type
LS_result_2019["electors"] = (
    LS_result_2019["electors"]
    .str.replace(",", "", regex=False)
    .astype("Int64")
)


LS_result_2024 = pd.read_csv(os.path.join(dpath,
                                      'WB_General_2024_Results.csv'), 
                         header = 0)

for s in ['LF_votes', 'INC_votes']:
    LS_result_2024[s] = (
        LS_result_2024[s]
        .fillna(0)
        .astype(int)
        )

## convert elector numbers from object to int type
LS_result_2024["electors"] = (
    LS_result_2024["electors"]
    .str.replace(",", "", regex=False)
    .astype("Int64")
)

## map vidhan-sabha constituencies to lok-sabha constituencies
mapping = [('Alipurduars', 'Tufanganj'), ('Alipurduars', 'Kumargram'),
           ('Alipurduars', 'Kalchini'), ('Alipurduars', 'Alipurduars'),
           ('Alipurduars', 'Falakata'), ('Alipurduars', 'Madarihat'),
           ('Alipurduars', 'Nagrakata'), ('Arambagh', 'Haripal'), 
           ('Arambagh', 'Tarakeswar'), ('Arambagh', 'Pursurah'), 
           ('Arambagh', 'Arambagh'), ('Arambagh', 'Goghat'), 
           ('Arambagh', 'Khanakul'), ('Arambagh', 'Chandrakona'), 
           ('Asansol', 'Pandabeswar'), ('Asansol', 'Raniganj'), 
           ('Asansol', 'Jamuria'), ('Asansol', 'Asansol Dakshin'), 
           ('Asansol', 'Asansol Uttar'), ('Asansol', 'Kulti'), 
           ('Asansol', 'Barabani'), ('Baharampur', 'Burwan'), 
           ('Baharampur', 'Kandi'), ('Baharampur', 'Bharatpur'), 
           ('Baharampur', 'Rejinagar'), ('Baharampur', 'Beldanga'), 
           ('Baharampur', 'Baharampur'), ('Baharampur', 'Naoda'), 
           ('Balurghat', 'Itahar'), ('Balurghat', 'Kushmandi'), 
           ('Balurghat', 'Kumarganj'), ('Balurghat', 'Balurghat'), 
           ('Balurghat', 'Tapan'), ('Balurghat', 'Gangarampur'), 
           ('Balurghat', 'Harirampur'), ('Bangaon', 'Kalyani'), 
           ('Bangaon', 'Haringhata'), ('Bangaon', 'Bagdah'), 
           ('Bangaon', 'Bangaon Uttar'), ('Bangaon', 'Bangaon Dakshin'), 
           ('Bangaon', 'Gaighata'), ('Bangaon', 'Swarupnagar'), 
           ('Bankura', 'Raghunathpur'), ('Bankura', 'Saltora'), 
           ('Bankura', 'Chhatna'), ('Bankura', 'Ranibandh'), 
           ('Bankura', 'Raipur'), ('Bankura', 'Taldangra'), 
           ('Bankura', 'Bankura'), ('Barasat', 'Habra'), 
           ('Barasat', 'Ashoknagar'), ('Barasat', 'Rajarhat New Town'), 
           ('Barasat', 'Bidhannagar'), ('Barasat', 'Madhyamgram'), 
           ('Barasat', 'Barasat'), ('Barasat', 'Deganga'), 
           ('Bardhaman Purba', 'Raina'), ('Bardhaman Purba', 'Jamalpur'), 
           ('Bardhaman Purba', 'Kalna'), ('Bardhaman Purba', 'Memari'), 
           ('Bardhaman Purba', 'Purbasthali Dakshin'), ('Bardhaman Purba', 'Purbasthali Uttar'), 
           ('Bardhaman Purba', 'Katwa'), ('Bardhaman-Durgapur', 'Bardhaman Dakshin'), 
           ('Bardhaman-Durgapur', 'Monteswar'), ('Bardhaman-Durgapur', 'Bardhaman Uttar'), 
           ('Bardhaman-Durgapur', 'Bhatar'), ('Bardhaman-Durgapur', 'Galsi'), 
           ('Bardhaman-Durgapur', 'Durgapur Purba'), ('Bardhaman-Durgapur', 'Durgapur Paschim'), 
           ('Barrackpore', 'Amdanga'), ('Barrackpore', 'Bijpur'), 
           ('Barrackpore', 'Naihati'), ('Barrackpore', 'Bhatpara'), 
           ('Barrackpore', 'Jagatdal'), ('Barrackpore', 'Noapara'), 
           ('Barrackpore', 'Barrackpur'), ('Basirhat', 'Baduria'), 
           ('Basirhat', 'Haroa'), ('Basirhat', 'Minakhan'), 
           ('Basirhat', 'Sandeshkhali'), ('Basirhat', 'Basirhat Dakshin'), 
           ('Basirhat', 'Basirhat Uttar'), ('Basirhat', 'Hingalganj'), 
           ('Birbhum', 'Dubrajpur'), ('Birbhum', 'Suri'), 
           ('Birbhum', 'Sainthia'), ('Birbhum', 'Rampurhat'), 
           ('Birbhum', 'Hansan'), ('Birbhum', 'Nalhati'), 
           ('Birbhum', 'Murarai'), ('Bishnupur', 'Barjora'), 
           ('Bishnupur', 'Onda'), ('Bishnupur', 'Bishnupur'), 
           ('Bishnupur', 'Katulpur'), ('Bishnupur', 'Indas'), 
           ('Bishnupur', 'Sonamukhi'), ('Bishnupur', 'Khandaghosh'), 
           ('Bolpur', 'Ketugram'), ('Bolpur', 'Mangalkot'), 
           ('Bolpur', 'Ausgram'), ('Bolpur', 'Bolpur'), 
           ('Bolpur', 'Nanoor'), ('Bolpur', 'Labpur'), 
           ('Bolpur', 'Mayureswar'), ('Cooch Behar', 'Mathabhanga'), 
           ('Cooch Behar', 'Cooch Behar Uttar'), ('Cooch Behar', 'Cooch Behar Dakshin'), 
           ('Cooch Behar', 'Sitalkuchi'), ('Cooch Behar', 'Sitai'), 
           ('Cooch Behar', 'Dinhata'), ('Cooch Behar', 'Natabari'), 
           ('Darjeeling', 'Kalimpong'), ('Darjeeling', 'Darjeeling'), 
           ('Darjeeling', 'Kurseong'), ('Darjeeling', 'Matigara-Naxalbari'), 
           ('Darjeeling', 'Siliguri'), ('Darjeeling', 'Phansidewa'), 
           ('Darjeeling', 'Chopra'), ('Diamond Harbour', 'Diamond Harbour'), 
           ('Diamond Harbour', 'Falta'), ('Diamond Harbour', 'Satgachhia'), 
           ('Diamond Harbour', 'Bishnupur-II'), ('Diamond Harbour', 'Maheshtala'), 
           ('Diamond Harbour', 'Budge Budge'), ('Diamond Harbour', 'Metiaburuz'), 
           ('Dum Dum', 'Khardaha'), ('Dum Dum', 'Dum Dum Uttar'), 
           ('Dum Dum', 'Panihati'), ('Dum Dum', 'Kamarhati'), 
           ('Dum Dum', 'Baranagar'), ('Dum Dum', 'Dum Dum'), 
           ('Dum Dum', 'Rajarhat Gopalpur'), ('Ghatal', 'Panskura Paschim'), 
           ('Ghatal', 'Sabang'), ('Ghatal', 'Pingla'), 
           ('Ghatal', 'Debra'), ('Ghatal', 'Daspur'), 
           ('Ghatal', 'Ghatal'), ('Ghatal', 'Keshpur'), 
           ('Hooghly', 'Singur'), ('Hooghly', 'Chandannagar'), 
           ('Hooghly', 'Chunchura'), ('Hooghly', 'Balagarh'), 
           ('Hooghly', 'Pandua'), ('Hooghly', 'Saptagram'), 
           ('Hooghly', 'Dhanekhali'), ('Howrah', 'Bally'), 
           ('Howrah', 'Howrah Uttar'), ('Howrah', 'Howrah Madhya'), 
           ('Howrah', 'Shibpur'), ('Howrah', 'Howrah Dakshin'), 
           ('Howrah', 'Sankrail'), ('Howrah', 'Panchla'), 
           ('Jadavpur', 'Baruipur Purba'), ('Jadavpur', 'Baruipur Paschim'), 
           ('Jadavpur', 'Sonarpur Dakshin'), ('Jadavpur', 'Bhangar'), 
           ('Jadavpur', 'Jadavpur'), ('Jadavpur', 'Sonarpur Uttar'), 
           ('Jadavpur', 'Tollygunge'), ('Jalpaiguri', 'Mekliganj'), 
           ('Jalpaiguri', 'Dhupguri'), ('Jalpaiguri', 'Maynaguri'), 
           ('Jalpaiguri', 'Jalpaiguri'), ('Jalpaiguri', 'Rajganj'), 
           ('Jalpaiguri', 'Dabgram-Phulbari'), ('Jalpaiguri', 'Mal'), 
           ('Jangipur', 'Suti'), ('Jangipur', 'Jangipur'), 
           ('Jangipur', 'Raghunathganj'), ('Jangipur', 'Sagardighi'), 
           ('Jangipur', 'Lalgola'), ('Jangipur', 'Nabagram'), 
           ('Jangipur', 'Khargram'), ('Jaynagar', 'Gosaba'), 
           ('Jaynagar', 'Basanti'), ('Jaynagar', 'Kultali'), 
           ('Jaynagar', 'Jaynagar'), ('Jaynagar', 'Canning Paschim'), 
           ('Jaynagar', 'Canning Purba'), ('Jaynagar', 'Magrahat Purba'), 
           ('Jhargram', 'Nayagram'), ('Jhargram', 'Gopiballavpur'), 
           ('Jhargram', 'Jhargram'), ('Jhargram', 'Garbeta'), 
           ('Jhargram', 'Salboni'), ('Jhargram', 'Binpur'), 
           ('Jhargram', 'Bandwan'), ('Kanthi', 'Chandipur'), 
           ('Kanthi', 'Patashpur'), ('Kanthi', 'Kanthi Uttar'), 
           ('Kanthi', 'Bhagabanpur'), ('Kanthi', 'Khejuri'), 
           ('Kanthi', 'Kanthi Dakshin'), ('Kanthi', 'Ramnagar'), 
           ('Kolkata Dakshin', 'Kasba'), ('Kolkata Dakshin', 'Behala Purba'), 
           ('Kolkata Dakshin', 'Behala Paschim'), ('Kolkata Dakshin', 'Kolkata Port'), 
           ('Kolkata Dakshin', 'Bhabanipur'), ('Kolkata Dakshin', 'Rashbehari'), 
           ('Kolkata Dakshin', 'Ballygunge'), ('Kolkata Uttar', 'Chowrangee'), 
           ('Kolkata Uttar', 'Entally'), ('Kolkata Uttar', 'Beleghata'), 
           ('Kolkata Uttar', 'Jorasanko'), ('Kolkata Uttar', 'Shyampukur'), 
           ('Kolkata Uttar', 'Maniktala'), ('Kolkata Uttar', 'Kashipur-Belgachhia'), 
           ('Krishnanagar', 'Tehatta'), ('Krishnanagar', 'Palashipara'), 
           ('Krishnanagar', 'Kaliganj'), ('Krishnanagar', 'Nakashipara'), 
           ('Krishnanagar', 'Chapra'), ('Krishnanagar', 'Krishnanagar Uttar'), 
           ('Krishnanagar', 'Krishnanagar Dakshin'), ('Maldaha Dakshin', 'Manikchak'), 
           ('Maldaha Dakshin', 'English Bazar'), ('Maldaha Dakshin', 'Mothabari'), 
           ('Maldaha Dakshin', 'Sujapur'), ('Maldaha Dakshin', 'Baisnabnagar'), 
           ('Maldaha Dakshin', 'Farakka'), ('Maldaha Dakshin', 'Samserganj'), 
           ('Maldaha Uttar', 'Habibpur'), ('Maldaha Uttar', 'Gazole'), 
           ('Maldaha Uttar', 'Chanchal'), ('Maldaha Uttar', 'Harishchandrapur'), 
           ('Maldaha Uttar', 'Malatipur'), ('Maldaha Uttar', 'Ratua'), 
           ('Maldaha Uttar', 'Maldaha'), ('Mathurapur', 'Patharpratima'), 
           ('Mathurapur', 'Kakdwip'), ('Mathurapur', 'Sagar'), 
           ('Mathurapur', 'Kulpi'), ('Mathurapur', 'Raidighi'), 
           ('Mathurapur', 'Mandirbazar'), ('Mathurapur', 'Magrahat Paschim'), 
           ('Medinipur', 'Egra'), ('Medinipur', 'Dantan'), 
           ('Medinipur', 'Keshiary'), ('Medinipur', 'Kharagpur Sadar'), 
           ('Medinipur', 'Narayangarh'), ('Medinipur', 'Kharagpur'), 
           ('Medinipur', 'Medinipur'), ('Murshidabad', 'Bhagabangola'), 
           ('Murshidabad', 'Raninagar'), ('Murshidabad', 'Murshidabad'), 
           ('Murshidabad', 'Hariharpara'), ('Murshidabad', 'Domkal'), 
           ('Murshidabad', 'Jalangi'), ('Murshidabad', 'Karimpur'), 
           ('Purulia', 'Balarampur'), ('Purulia', 'Baghmundi'), 
           ('Purulia', 'Joypur'), ('Purulia', 'Purulia'), 
           ('Purulia', 'Manbazar'), ('Purulia', 'Kashipur'), 
           ('Purulia', 'Para'), ('Raiganj', 'Islampur'), 
           ('Raiganj', 'Goalpokhar'), ('Raiganj', 'Chakulia'), 
           ('Raiganj', 'Karandighi'), ('Raiganj', 'Hemtabad'), 
           ('Raiganj', 'Kaliaganj'), ('Raiganj', 'Raiganj'), 
           ('Ranaghat', 'Nabadwip'), ('Ranaghat', 'Santipur'), 
           ('Ranaghat', 'Ranaghat Uttar Paschim'), ('Ranaghat', 'Krishnaganj'), 
           ('Ranaghat', 'Ranaghat Uttar Purba'), ('Ranaghat', 'Ranaghat Dakshin'), 
           ('Ranaghat', 'Chakdaha'), ('Sreerampur', 'Jagatballavpur'), 
           ('Sreerampur', 'Domjur'), ('Sreerampur', 'Uttarpara'), 
           ('Sreerampur', 'Sreerampur'), ('Sreerampur', 'Champdani'), 
           ('Sreerampur', 'Chanditala'), ('Sreerampur', 'Jangipara'), 
           ('Tamluk', 'Tamluk'), ('Tamluk', 'Panskura Purba'), 
           ('Tamluk', 'Moyna'), ('Tamluk', 'Nandakumar'), 
           ('Tamluk', 'Mahishadal'), ('Tamluk', 'Haldia'), 
           ('Tamluk', 'Nandigram'), ('Uluberia', 'Uluberia Purba'), 
           ('Uluberia', 'Uluberia Uttar'), ('Uluberia', 'Uluberia Dakshin'), 
           ('Uluberia', 'Shyampur'), ('Uluberia', 'Bagnan'), 
           ('Uluberia', 'Amta'), ('Uluberia', 'Udaynarayanpur')]


mapping_df = pd.DataFrame(mapping, columns = ['ls_constituency', 'constituency'])

df = AC_result_2021.copy()

df = df.merge(
    mapping_df,
    on="constituency",
    how="left"
)


## vote swing in ls election
tmc_swing = 100*(LS_result_2024['AITC_votes']/LS_result_2024['electors'] - 
             LS_result_2019['AITC_votes']/LS_result_2019['electors'])

bjp_swing = 100*(LS_result_2024['BJP_votes']/LS_result_2024['electors'] - 
             LS_result_2019['BJP_votes']/LS_result_2019['electors'])

left_swing = 100*(LS_result_2024['LF_votes']/LS_result_2024['electors'] - 
             LS_result_2019['LF_votes']/LS_result_2019['electors'])

congress_swing = 100*(LS_result_2024['INC_votes']/LS_result_2024['electors'] - 
             LS_result_2019['INC_votes']/LS_result_2019['electors'])

ls_df = pd.DataFrame({'ls_constituency': LS_result_2024['ls_constituency'],
                      'tmc_swing': tmc_swing, 'bjp_swing': bjp_swing, 
                      'left_swing': left_swing, 'congress_swing': congress_swing, })

df = df.merge(
    ls_df,
    on="ls_constituency",
    how="left"
)


# we will add 50% weight to the lok sabha swing 
lsmult = 0.5

df['pred_tmc_vote_share'] = df['TMC_vote_share'] + df['tmc_swing']*lsmult 
df['pred_bjp_vote_share'] = df['BJP_vote_share'] + df['bjp_swing']*lsmult 
df['pred_left_vote_share'] = df['Left_vote_share'] + df['left_swing']*lsmult 
df['pred_congress_vote_share'] = df['Congress_vote_share'] + df['congress_swing']*lsmult 


## find baseline winner
vote_cols = [
    "pred_tmc_vote_share",
    "pred_bjp_vote_share",
    "pred_left_vote_share",
    "pred_congress_vote_share",
]



df["baseline_winner"] = (
    df[vote_cols]
    .idxmax(axis=1)
    .str.replace("pred_", "")
    .str.replace("_vote_share", "")
    .str.upper()
)

## find baseline margin
sorted_votes = np.sort(df[vote_cols].values, axis=1)

df["baseline_margin_pct"] = sorted_votes[:, -1] - sorted_votes[:, -2]

df["is_close_seat"] = df["baseline_margin_pct"] < 3   # threshold: 3%

df.to_csv("data/processed/baseline_predictions.csv", index=False)

# ************************************************************************** #
# IMPORTANT: ~11.5% voters deleted due to corrections & >5% additional votes
# registered this time (new inclusions + who didn't vote last time).
# Initially, we will assume that voter deletion is uniform across the state,
# which is not true - but this is all baseline. Further refinement will be
# added in the next version.  
# ************************************************************************** #

def apply_sir_and_new_voters(
    df,
    sir_reduction_rate=0.115, # 11.5% reduction
    new_voter_rate=0.02, # 2% new addition
    sir_impact_weights=None,
    new_voter_weights=None,
):
    """
    Apply SIR voter reduction and new voter addition before Monte Carlo.

    sir_reduction_rate:
        Fraction of total electors removed, e.g. 0.115 = 11.5%.

    new_voter_rate:
        Fraction of total electors added as new voters.

    sir_impact_weights:
        Which party's voter base is more affected by deletion.
        Higher value = more removed voters from that party.

    new_voter_weights:
        Distribution preference of new voters.
    """

    df = df.copy()

    parties = ["tmc", "bjp", "left", "congress"]

    if sir_impact_weights is None:
        sir_impact_weights = {
            "tmc": 1.0,
            "bjp": 1.0,
            "left": 1.0,
            "congress": 1.0,
        }

    if new_voter_weights is None:
        new_voter_weights = {
            "tmc": 0.35,
            "bjp": 0.35,
            "left": 0.15,
            "congress": 0.15,
        }

    # Normalize new voter weights
    total_new_weight = sum(new_voter_weights.values())
    new_voter_weights = {
        k: v / total_new_weight for k, v in new_voter_weights.items()
    }

    # Use estimated electors as the count base
    df["base_electors"] = df["total_electors_estimated"]

    # Convert predicted vote shares to vote counts
    for p in parties:
        share_col = f"pred_{p}_vote_share"
        df[f"{p}_base_votes"] = df["base_electors"] * df[share_col] / 100

    # Total voters removed by SIR
    df["sir_removed_total"] = df["base_electors"] * sir_reduction_rate

    # Allocate deleted voters across parties proportional to:
    # base party votes × assumed SIR impact weight
    weighted_support_cols = []

    for p in parties:
        col = f"{p}_sir_weighted_support"
        df[col] = df[f"{p}_base_votes"] * sir_impact_weights[p]
        weighted_support_cols.append(col)

    df["sir_weighted_total"] = df[weighted_support_cols].sum(axis=1)

    for p in parties:
        df[f"{p}_sir_removed_votes"] = np.where(
            df["sir_weighted_total"] > 0,
            df["sir_removed_total"]
            * df[f"{p}_sir_weighted_support"]
            / df["sir_weighted_total"],
            0,
        )

    # New voters
    df["new_voters_total"] = df["base_electors"] * new_voter_rate

    for p in parties:
        df[f"{p}_new_votes"] = df["new_voters_total"] * new_voter_weights[p]

    # Adjusted votes
    for p in parties:
        df[f"adj_{p}_votes"] = (
            df[f"{p}_base_votes"]
            - df[f"{p}_sir_removed_votes"]
            + df[f"{p}_new_votes"]
        )

        df[f"adj_{p}_votes"] = df[f"adj_{p}_votes"].clip(lower=0)

    adjusted_vote_cols = [f"adj_{p}_votes" for p in parties]
    df["adjusted_total_votes"] = df[adjusted_vote_cols].sum(axis=1)

    # Convert adjusted votes back to vote shares
    for p in parties:
        df[f"adj_{p}_vote_share"] = (
            100 * df[f"adj_{p}_votes"] / df["adjusted_total_votes"]
        )

    return df

# SIR adjusted verdict 
df_adj = apply_sir_and_new_voters(df,
                                  sir_reduction_rate=0.115,
                                  new_voter_rate=0.06,
                                  sir_impact_weights={
                                      "tmc": 1.0,
                                      "bjp": 0.2,
                                      "left": 1.00,
                                      "congress": 1.00,
                                      },
                                  new_voter_weights={
                                      "tmc": 0.35,
                                      "bjp": 0.35,
                                      "left": 0.15,
                                      "congress": 0.15,
                                      },
                                  )

adj_vote_cols = [
    "adj_tmc_vote_share",
    "adj_bjp_vote_share",
    "adj_left_vote_share",
    "adj_congress_vote_share",
]

df_adj["sir_adjusted_winner"] = (
    df_adj[adj_vote_cols]
    .idxmax(axis=1)
    .str.replace("adj_", "")
    .str.replace("_vote_share", "")
    .str.upper()
)

sorted_adj_votes = np.sort(df_adj[adj_vote_cols].values, axis=1)

df_adj["sir_adjusted_margin_pct"] = (
    sorted_adj_votes[:, -1] - sorted_adj_votes[:, -2]
)


df_adj.to_csv("data/processed/sir_adjusted_predictions.csv", index=False)

# ========================= #
# Output section
# ========================= #

print("\n" + "="*50)
print("SIR-ADJUSTED SEAT PROJECTION")
print("="*50)

seat_counts = df_adj["sir_adjusted_winner"].value_counts()

for party, seats in seat_counts.items():
    print(f"{party:<10}: {int(seats):>3} seats")

print("="*50)


# ------------------------- #
# Close seats summary
# ------------------------- #

close_seats = df_adj[df_adj["sir_adjusted_margin_pct"] < 3].copy()

print("\nCLOSE SEATS (margin < 3%)")
print("-"*50)
print(f"Total close seats: {len(close_seats)}")

print("\nTop 15 closest constituencies:\n")

print(
    close_seats
    .sort_values("sir_adjusted_margin_pct")
    [["constituency", "sir_adjusted_winner", "sir_adjusted_margin_pct"]]
    .head(15)
    .to_string(index=False)
)


# ------------------------- #
# Party-wise vulnerability
# ------------------------- #

print("\n" + "-"*50)
print("PARTY-WISE VULNERABILITY (close seats)")
print("-"*50)

vulnerable = close_seats["sir_adjusted_winner"].value_counts()

for party, seats in vulnerable.items():
    print(f"{party:<10}: {int(seats):>3} vulnerable seats")


# ------------------------- #
# Optional: Save clean output
# ------------------------- #

summary_df = pd.DataFrame({
    "party": seat_counts.index,
    "seats": seat_counts.values
})

summary_df.to_csv("data/processed/baseline_seat_summary.csv", index=False)

close_seats[
    ["constituency", "sir_adjusted_winner", "sir_adjusted_margin_pct"]
].to_csv("data/processed/close_seats.csv", index=False)

print("\nSaved:")
print(" - data/processed/baseline_seat_summary.csv")
print(" - data/processed/close_seats.csv")
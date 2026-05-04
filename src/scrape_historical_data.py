# -*- coding: utf-8 -*-
"""
Created on Fri May  1 23:10:58 2026

@author: as836
"""

import requests
import pandas as pd
import os

# data directory

dpath = r'C:\Users\as836\Documents\GitHub\wb-election-analysis\data\raw'

# constituency-wise results of past assembly elections
## historical data range
assemblies = ["Assembly_2001", "Assembly_2006", 
              "Assembly_2011", "Assembly_2016", "Assembly_2021"]
## wikipedia pages
urls = {"Assembly_2001": "https://en.wikipedia.org/wiki/2001_West_Bengal_Legislative_Assembly_election",
        "Assembly_2006": "https://en.wikipedia.org/wiki/2006_West_Bengal_Legislative_Assembly_election",
        "Assembly_2011": "https://en.wikipedia.org/wiki/2011_West_Bengal_Legislative_Assembly_election",
        "Assembly_2016": "https://en.wikipedia.org/wiki/2016_West_Bengal_Legislative_Assembly_election",
        "Assembly_2021": "https://en.wikipedia.org/wiki/2021_West_Bengal_Legislative_Assembly_election"}

## tables to save
tindex = [9, 9, 10, 14, 19] # which table to store

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/120.0 Safari/537.36"
}

for j in range(len(urls) - 1, len(urls)):
    url = urls[assemblies[j]]
    html = requests.get(url, headers=headers).text
    tables = pd.read_html(html) # read the tables 

    df = tables[tindex[j]]
    
    df.to_csv(os.path.join(dpath,
                           "WB_" + assemblies[j] + "_Results.csv"), index = False)

# constituency-wise voting % in 2021 and 2026
url = url = r"https://www.moneycontrol.com/news/india/west-bengal-voter-turnout-2026-vs-2021-constituency-wise-comparison-13905456.html"
html = requests.get(url, headers=headers).text
tables = pd.read_html(html) # read the tables 

df = tables[0]
    
df.to_csv(os.path.join(dpath,
                           "WB_Vote_Percent_2021_2026.csv"), index = False)

# constituency-wise voters in 2026
url = r"https://en.wikipedia.org/wiki/List_of_constituencies_of_the_West_Bengal_Legislative_Assembly"

html = requests.get(url, headers=headers).text
tables = pd.read_html(html) # read the tables 

df = tables[1]
    
df.to_csv(os.path.join(dpath,
                           "WB_Total_Voters_2026.csv"), index = False)


# constituency-wise results of past general elections
## historical data range
generals = ["General_2014", "General_2019", "General_2024"]
## wikipedia pages
urls = {"General_2014": "https://en.wikipedia.org/wiki/2014_Indian_general_election_in_West_Bengal",
        "General_2019": "https://en.wikipedia.org/wiki/2019_Indian_general_election_in_West_Bengal",
        "General_2024": "https://en.wikipedia.org/wiki/2024_Indian_general_election_in_West_Bengal"}

## tables to save
tindex = [8, 10, 16] # which table to store

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/120.0 Safari/537.36"
}

#for j in range(len(urls)):
for j in range(2):
    url = urls[generals[j]]
    html = requests.get(url, headers=headers).text
    tables = pd.read_html(html) # read the tables 

    df = tables[tindex[j]]
    
    df.to_csv(os.path.join(dpath,
                           "WB_" + generals[j] + "_Results.csv"), index = False)


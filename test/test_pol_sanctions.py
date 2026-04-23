# -*- coding: utf-8 -*-
"""
Created on Thu Apr 23 17:13:39 2026

@author: buttard
"""

# test_sanctions.py

from pathlib import Path

import numpy as np
import pandas as pd


# ==========================================================
# CONFIG
# ==========================================================
FILE_PATH = Path(
    r"C:\Users\buttard\Documents\RiskAltas\data\raw\summary.xlsx"
)

SHEET_NAME = "Pol - International Sanctions"


# ==========================================================
# GROUP FUNCTION
# ==========================================================
def group_vote(row, group_cols):

    vals = []

    for col in group_cols:

        val = row[col]

        if pd.notna(val):
            vals.append(val)

    # ------------------------------------------------------
    # DEBUG
    # ------------------------------------------------------
    print(f"\n{group_cols}")
    print("vals:", vals)

    if len(vals) == 0:
        return np.nan

    return np.mean(vals)


# ==========================================================
# LOAD
# ==========================================================
print("\n==================================================")
print("LOADING EXCEL")
print("==================================================")

xls = pd.ExcelFile(FILE_PATH)

sanctions = pd.read_excel(
    xls,
    sheet_name=SHEET_NAME,
)

print("\nColumns:")
print(sanctions.columns.tolist())

print("\nHead:")
print(sanctions.head())


# ==========================================================
# GROUPS
# ==========================================================
groups = {
    "group_1": ["UNSC", "World Bank"],
    "group_2": ["SDN (US)", "US Consolidated"],
    "group_3": ["EU", "UK"],
    "group_4": [
        "Canada",
        "Australia",
        "Japan (METI)",
        "China (MOFCOM)"
    ]
}

mapping_yes_no = {
    "Yes": 1,
    "No": 0,
    "Partial": 0.5,
    "Partially Lifted": 0.5,
}


# ==========================================================
# RAW UNIQUE VALUES
# ==========================================================
print("\n==================================================")
print("RAW UNIQUE VALUES")
print("==================================================")

for col in sanctions.columns:

    if col != "Country":

        print(f"\n{col}")
        print(sanctions[col].dropna().unique()[:20])


# ==========================================================
# CONVERT YES/NO
# ==========================================================
print("\n==================================================")
print("CONVERTING YES/NO")
print("==================================================")

for col in sanctions.columns:

    if col != "Country":

        sanctions[col] = (
            sanctions[col]
            .astype(str)
            .str.strip()
            .map(mapping_yes_no)
        )

        print(f"\n{col}")
        print(sanctions[col].value_counts(dropna=False))


# ==========================================================
# GROUP VOTING
# ==========================================================
print("\n==================================================")
print("GROUP VOTING")
print("==================================================")

for g, group_cols in groups.items():

    print(f"\nCreating {g}")

    sanctions[g] = sanctions.apply(
        lambda row: group_vote(row, group_cols),
        axis=1
    )

    print(sanctions[g].describe())
    print(sanctions[g].isna().sum())


# ==========================================================
# LABELS
# ==========================================================
print("\n==================================================")
print("LABELS")
print("==================================================")

for g in groups.keys():

    sanctions[f"{g}_label"] = np.select(
        [
            sanctions[g] <= 0.4,

            (
                (sanctions[g] > 0.4)
                & (sanctions[g] < 0.6)
            ),

            sanctions[g] >= 0.6,
        ],
        [
            "No",
            "Indecisive",
            "Yes"
        ],
        default="Unknown"
    )

    print(f"\n{g}_label")
    print(
        sanctions[f"{g}_label"]
        .value_counts(dropna=False)
    )


# ==========================================================
# FINAL CHECK
# ==========================================================
print("\n==================================================")
print("FINAL NAN CHECK")
print("==================================================")

print(
    sanctions[
        list(groups.keys())
    ].isna().sum()
)

print("\nDone.")
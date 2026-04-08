# -*- coding: utf-8 -*-
"""
Created on Sun Apr  5 23:10:32 2026

@author: buttard
"""

import pandas as pd
from pathlib import Path
from typing import Dict


def load_data(file_path: str | Path) -> Dict[str, pd.DataFrame]:
    """
    Load all required datasets from a multi-sheet Excel file
    and validate presence of 'Country' column.

    Parameters
    ----------
    file_path : str | Path
        Path to the Excel file containing all datasets

    Returns
    -------
    Dict[str, pd.DataFrame]
        Dictionary containing all loaded datasets

    Raises
    ------
    ValueError
        If any dataset does not contain a 'Country' column
    """
    print("Loading your dataset...")
    file_path = Path(file_path)

    data = {
        "population": pd.read_excel(file_path, sheet_name="Annex - Population Per Country")
        .rename(columns={"Region, subregion, country or area *": "Country"}),

        "fatalities": pd.read_excel(file_path, sheet_name="Sec - Fatalities")
        .rename(columns={"COUNTRY": "Country"}),

        "terrorism": pd.read_excel(file_path, sheet_name="Sec - Terrorism"),

        "governance": pd.read_excel(file_path, sheet_name="Pol - Regime stability")
        .rename(columns={
            "Economy (name)": "Country",
            "Governance score (0-100)": "governance_score"
        }),

        "sanctions": pd.read_excel(file_path, sheet_name="Pol - International Sanctions"),

        "corruption": pd.read_excel(file_path, sheet_name="Pol - Corruption")
        .rename(columns={"Pays": "Country"}),

        "violence": pd.read_excel(file_path, sheet_name="Pol - Political Violence Events")
        .rename(columns={'COUNTRY':'Country'}),

        "climate": (
            lambda df: df.rename(columns={df.columns[0]: "Country"})
        )(
            pd.read_excel(file_path, sheet_name="Nat - Hazard Exposure", skiprows=1)
        ),
    }

    # =========================
    # VALIDATION FOR COUNTRY COLUMN
    # =========================
    for name, df in data.items():
        if "Country" not in df.columns:
            raise ValueError(
                f"Dataset '{name}' does not contain a 'Country' column.\n"
                f"Columns found: {list(df.columns)}"
            )

    return data

def load_example(path: Path) -> pd.DataFrame:
    """
    Load sample dataset (used when raw data is not available).
    """
    return pd.read_excel(path,skiprows=1)
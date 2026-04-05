# -*- coding: utf-8 -*-
"""
Created on Sun Apr  5 23:10:32 2026

@author: buttard
"""

import pandas as pd
from pathlib import Path
from typing import Dict


def load_all_data(file_path: str | Path) -> Dict[str, pd.DataFrame]:
    """
    Load all required datasets from a multi-sheet Excel file.

    Parameters
    ----------
    file_path : str | Path
        Path to the Excel file containing all datasets

    Returns
    -------
    Dict[str, pd.DataFrame]
        Dictionary containing all loaded datasets:
        - population
        - fatalities
        - conflict
        - terrorism
        - governance
        - sanctions
        - corruption
        - violence
        - climate
    """

    file_path = Path(file_path)  # ensure compatibility

    return {
        "population": pd.read_excel(file_path, sheet_name="Annex - Population Per Country"),
        "fatalities": pd.read_excel(file_path, sheet_name="Sec - Fatalities"),
        "conflict": pd.read_excel(file_path, sheet_name="Sec - Conflict situation"),
        "terrorism": pd.read_excel(file_path, sheet_name="Sec - Terrorism"),
        "governance": pd.read_excel(file_path, sheet_name="Pol - Regime stability"),
        "sanctions": pd.read_excel(file_path, sheet_name="Pol - International Sanctions"),
        "corruption": pd.read_excel(file_path, sheet_name="Pol - Corruption"),
        "violence": pd.read_excel(file_path, sheet_name="Pol - Political Violence Events"),
        "climate": pd.read_excel(file_path, sheet_name="Nat - Hazard Exposure", skiprows=1),
    }

def load_example(path: Path) -> pd.DataFrame:
    """
    Load sample dataset (used when raw data is not available).
    """
    return pd.read_excel(path,skiprows=1)
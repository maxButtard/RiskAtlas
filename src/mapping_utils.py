# -*- coding: utf-8 -*-
"""
Created on Sun Apr  5 23:16:48 2026

@author: buttard
"""

import pandas as pd
from typing import Dict


def load_country_mapping(path: str = "data/mapping/country_mapping.csv") -> Dict[str, str]:
    """
    Load country mapping from a CSV file.

    The CSV must contain:
    - raw_name: original country names from datasets
    - standard_name: standardized names matching GeoJSON

    Parameters
    ----------
    path : str
        Path to the mapping CSV file

    Returns
    -------
    Dict[str, str]
        Dictionary mapping raw country names to standardized names
    """
    mapping_df = pd.read_csv(path)
    return dict(zip(mapping_df["raw_name"], mapping_df["standard_name"]))


def apply_country_mapping(
    df: pd.DataFrame,
    column: str = "Country",
    mapping: Dict[str, str] = None
) -> pd.DataFrame:
    """
    Apply country name standardization to a DataFrame column.

    This replaces inconsistent country names using a predefined mapping
    to ensure compatibility with GeoJSON and cross-dataset merges.

    Parameters
    ----------
    df : pd.DataFrame
        Input dataframe containing country names
    column : str
        Column name where country names are stored
    mapping : Dict[str, str]
        Dictionary of mappings (raw_name -> standard_name)

    Returns
    -------
    pd.DataFrame
        DataFrame with standardized country names

    Raises
    ------
    ValueError
        If mapping dictionary is not provided
    """
    if mapping is None:
        raise ValueError("Mapping dictionary is required")

    df[column] = df[column].replace(mapping)
    return df
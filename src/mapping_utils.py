# -*- coding: utf-8 -*-
"""
Created on Sun Apr  5 23:16:48 2026

@author: buttard
"""

import pandas as pd
from typing import Dict


def get_missing_countries(df: pd.DataFrame, geo_countries: list) -> pd.DataFrame:
    """
    Ensure that all countries present in the GeoJSON are included in the dataframe.

    Missing countries are added with NaN values, and any country not present
    in the GeoJSON reference list is removed.

    Parameters
    ----------
    df : pd.DataFrame
        Input dataframe containing a 'Country' column
    geo_countries : list
        List of country names from the GeoJSON file

    Returns
    -------
    pd.DataFrame
        DataFrame containing all GeoJSON countries with missing values filled as NaN
    """
    missing_country = set(geo_countries) - set(df["Country"])
    missing_df = pd.DataFrame({"Country": list(missing_country)})
    df = pd.concat([df, missing_df], ignore_index=True)
    df = df[df['Country'].isin(geo_countries)]
    
    return df
    
def clean_raw_data(df: Dict, geo_countries: list) -> pd.DataFrame:
    """
    Clean, standardize, and merge multiple raw datasets into a single dataframe.

    This function:
    - Renames columns for consistency
    - Filters latest available data
    - Converts units (e.g. population)
    - Handles missing countries
    - Aggregates sanctions into grouped indicators
    - Merges all datasets into a unified dataframe

    Parameters
    ----------
    df : Dict[str, pd.DataFrame]
        Dictionary containing raw datasets:
        - population
        - fatalities
        - terrorism
        - governance
        - sanctions
        - corruption
        - violence
        - climate

    geo_countries : list
        List of country names from GeoJSON used as reference

    Returns
    -------
    pd.DataFrame
        Cleaned and merged dataframe ready for scoring

    Notes
    -----
    - Assumes all input datasets contain a country identifier column
    - Missing countries are added with NaN values
    - Some datasets are filtered to latest available year
    """
    
    dict_final = {}
    
    #population
    pop=df['population']
    pop = pop.rename(columns={"Total Population, as of 1 January (thousands)": "Population_thousands"
    })
    pop["Population"] = pop["Population_thousands"] * 1000
    pop = pop[pop["Year"] == pop["Year"].max()][["Country", "Population"]]
    dict_final['population']=pop
    
    #TODO: conflict
    
    #FATALITIES
    fat = df['fatalities']
    fat = fat[fat["YEAR"] == fat["YEAR"].max()-1][['Country','FATALITIES']]
    fat = get_missing_countries(fat, geo_countries)
    dict_final['fatalities']=fat
    
    #Terrorism
    terr = df['terrorism'].rename(columns={'Score':'terrorism_score'})
    terr = get_missing_countries(terr, geo_countries)[['Country','terrorism_score']]
    dict_final['terrorism']=terr
    
    #stab_gouv
    stab_gouv = df['governance']
    stab_gouv = stab_gouv[stab_gouv['Year']==stab_gouv['Year'].max()]
    #stab_gouv = get_missing_countries(stab_gouv, geo_countries)[['Country','governance_score']]
    dict_final['governance']=stab_gouv
    
    #pol_scantions
    def group_vote(row, cols):
        """
        Compute the average vote across a group of sanction indicators.
    
        Parameters
        ----------
        row : pd.Series
            Row of the dataframe
        cols : list
            List of columns representing a sanction group
    
        Returns
        -------
        float or None
            Mean value of available indicators, or None if all are missing
        """
        values = row[cols].dropna()
        
        if len(values) == 0:
            return None
        
        return values.mean()
    
    pol_sanctions=df['sanctions']
    groups = {
        "group_1": ["UNSC", "World Bank"],
        "group_2": ["SDN (US)", "US Consolidated"],
        "group_3": ["EU", "UK"],
        "group_4": ["Canada", "Australia", "Japan (METI)", "China (MOFCOM)"]
    }

    mapping_yes_no = {
        "Yes": 1,
        "No": 0
    }
    
    # --- convertir Yes/No → 1/0
    for col in pol_sanctions.columns:
        if col != "Country":
            pol_sanctions[col] = pol_sanctions[col].map(mapping_yes_no)

    # --- calcul des groupes
    for g, group_cols in groups.items():
        pol_sanctions[g] = pol_sanctions.apply(lambda row: group_vote(row, group_cols), axis=1)

    # --- gérer les égalités (None → 0)
    pol_sanctions[list(groups.keys())] = pol_sanctions[list(groups.keys())].fillna(0)
    pol_sanctions = (
        pol_sanctions
        .groupby("Country", as_index=False)
        .mean(numeric_only=True)
    )
    pol_sanctions=get_missing_countries(pol_sanctions, geo_countries)
    dict_final['sanctions']=pol_sanctions
    
    #corruption
    pol_corruption=df['corruption']
    pol_corruption = pol_corruption.rename(
        columns={"Score CPI 2025": "score_pol_corruption"})
    pol_corruption=get_missing_countries(pol_corruption, geo_countries)
    dict_final['corruption']=pol_corruption

    #violence
    pol_violence_events=df['violence']
    pol_violence_events = pol_violence_events[pol_violence_events['YEAR']==2025][['Country','EVENTS']].rename(columns={'COUNTRY':'Country','EVENTS':'events'})
    pol_violence_events = get_missing_countries(pol_violence_events, geo_countries)
    dict_final['violence']=pol_violence_events

    
    #nature
    natural_hazard=df['climate']
    natural_hazard=natural_hazard.rename(columns={natural_hazard.columns[10]:'Coastal flood exposure',
    natural_hazard.columns[9]:'Cyclone exposure'})
    natural_hazard = natural_hazard[['Country','Coastal flood exposure','Cyclone exposure','INFORM Natural Hazard']]
    natural_hazard = natural_hazard.drop(natural_hazard.index[:3])
    natural_hazard =get_missing_countries(natural_hazard, geo_countries)
    dict_final['climate']=natural_hazard
    
    df_final=None
    for key, df in dict_final.items():
        if df_final is None:
            df_final = df
        else:
            df_final = df_final.merge(df, on="Country", how="left")

    return df_final

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
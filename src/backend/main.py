# -*- coding: utf-8 -*-

import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(BASE_DIR))
sys.path.append(str(BASE_DIR / "src"))

from data_loader import load_example, load_data
from geo_utils import load_geo_data,get_geo_countries
from mapping_utils import (
    load_country_mapping,
    apply_country_mapping,
    clean_raw_data,
)
from risk_calculations import compute_score
from visualization import create_map

import pandas as pd


def main():

    # =========================
    # PATHS
    # =========================
    sample_path = BASE_DIR / "data" / "raw" / "summary.xlsx"
    target = "score_natural_hazard"

    mapping_path = BASE_DIR / "data" / "mapping" / "mapping_dataset.csv"

    # =========================
    # LOAD GEO
    # =========================
    geo_data = load_geo_data()
    geo_countries = get_geo_countries(geo_data)

    # =========================
    # LOAD MAPPING
    # =========================
    mapping = load_country_mapping(mapping_path)

    # =========================
    # LOAD DATA
    # =========================
    if sample_path == BASE_DIR / "data" / "example" / "sample_dataset.xlsx":
        print("⚠️ Using sample dataset")

        df = load_example(sample_path)

        # mapping direct (df simple)
        df = apply_country_mapping(df, "Country", mapping)

    else:
        print("⚠️ Using your own dataset...")

        # 1. LOAD Data
        raw_data = load_data(sample_path)

        # 2. APPLY MAPPING 
        for key in raw_data:
            print(key)
            raw_data[key] = apply_country_mapping(
                raw_data[key], "Country", mapping
            )

        # 3. CLEAN + MERGE 
        df = clean_raw_data(raw_data, geo_countries)
        
    # =========================
    # COMPUTE SCORE
    # =========================
    df = compute_score(df)
    cols_to_keep = [
    "Country",
    "fatality_score",
    "terrorism_score",
    "governance_score",
    "score_pol_corruption",
    "score_security",
    "score_pol_sanctions_international",
    "score_violence_events",
    "score_political",
    "score_natural_hazard",
    "score_final"
    ]
    
    df_filtered = df[cols_to_keep]
    df_filtered.to_csv(r"C:\Users\buttard\Documents\RiskAltas\data\sql\risk.csv", index=False)

    # =========================
    # CHECK TARGET
    # =========================
    if target not in df.columns:
        raise ValueError(f"Column '{target}' not found in dataframe")
    
    
    # =========================
    # BUILD VALUE DICT
    # =========================
    value_dict = df.set_index("Country")[target].to_dict()

    # =========================
    # INJECT INTO GEOJSON
    # =========================
    for feature in geo_data["features"]:
        country = feature["properties"]["name"]
        value = value_dict.get(country)

        feature["properties"][target] = (
            round(value, 0) if pd.notna(value) else None
        )

    # =========================
    # VISUALIZATION
    # =========================
    m = create_map(df, geo_data, target)

    # =========================
    # SAVE OUTPUT
    # =========================
    output_path = BASE_DIR / "outputs" / f"map_{target}.html"
    output_path.parent.mkdir(exist_ok=True)

    m.save(output_path)

    print(f"✅ Map saved: {output_path}")

    return df


if __name__ == "__main__":
    df = main()
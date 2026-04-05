# -*- coding: utf-8 -*-

import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(BASE_DIR))
sys.path.append(str(BASE_DIR / "src"))

from data_loader import load_example
from geo_utils import load_geo_data
from mapping_utils import load_country_mapping, apply_country_mapping
from visualization import create_map

import pandas as pd


def main():
    # =========================
    # PATHS
    # =========================
    sample_path = BASE_DIR / "data" / "sample" / "sample_dataset.xlsx"
    mapping_path = BASE_DIR / "data" / "mapping" / "mapping_dataset.csv"

    target = "Population"

    # =========================
    # LOAD DATA
    # =========================
    print("⚠️ Using sample dataset")
    df = load_example(sample_path)

    # Clean
    df["Country"] = df["Country"].astype(str).str.strip()

    # =========================
    # MAPPING
    # =========================
    mapping = load_country_mapping(mapping_path)
    df = apply_country_mapping(df, "Country", mapping)

    # =========================
    # LOAD GEO
    # =========================
    geo_data = load_geo_data()
    geo_countries = [f["properties"]["name"] for f in geo_data["features"]]

    # Keep only matching countries
    df = df[df["Country"].isin(geo_countries)]

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

    output_path = BASE_DIR / "outputs" / "map.html"
    output_path.parent.mkdir(exist_ok=True)

    m.save(output_path)

    print(f"✅ Map saved: {output_path}")

    return df


if __name__ == "__main__":
    df = main()
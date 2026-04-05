# -*- coding: utf-8 -*-
"""
Created on Sun Apr  5 23:14:27 2026

@author: buttard
"""

import folium
import branca.colormap as cm
import numpy as np
import pandas as pd
from typing import Dict, Any


def create_map(
    df: pd.DataFrame,
    geo_data: Dict[str, Any],
    target: str
) -> folium.Map:
    """
    Create an interactive choropleth map based on a target variable.

    The function maps country-level values from a DataFrame onto a GeoJSON
    world map using a color scale.

    Parameters
    ----------
    df : pd.DataFrame
        DataFrame containing at least:
        - "Country": country names matching GeoJSON
        - target: column to visualize

    geo_data : dict
        GeoJSON structure containing country geometries

    target : str
        Column name in df to be visualized on the map

    Returns
    -------
    folium.Map
        Interactive map object
    """
    # =========================
    # ASSERT: check geojson has target
    # =========================
    sample_props = geo_data["features"][0]["properties"]

    assert target in sample_props, (
        f"'{target}' not found in geojson properties. "
        "You must inject values into geojson before calling create_map()."
    )
    
    # Convert dataframe to dictionary for fast lookup
    score_dict = df.set_index("Country")[target].to_dict()

    # Remove NaN values for scale computation
    values = df[target].dropna()

    # Compute color scale bounds (robust to outliers)
    vmin = np.percentile(values, 10)
    vmax = np.percentile(values, 99)

    # Create colormap
    colormap = cm.linear.Blues_09.scale(vmin, vmax)

    # Initialize map
    m = folium.Map(location=[20, 0], zoom_start=2)

    def style(feature: Dict[str, Any]) -> Dict[str, Any]:
        """
        Define style for each country polygon.
        """
        country = feature["properties"]["name"]
        val = score_dict.get(country)

        return {
            "fillColor": colormap(val) if pd.notna(val) else "#ff0000",
            "color": "black",
            "weight": 0.3,
            "fillOpacity": 0.7,
        }

    # Add GeoJSON layer with tooltip
    folium.GeoJson(
        geo_data,
        style_function=style,
        tooltip=folium.GeoJsonTooltip(
            fields=["name", target],
            aliases=["Country:", target],
        ),
    ).add_to(m)

    return m
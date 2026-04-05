# -*- coding: utf-8 -*-
"""
Created on Sun Apr  5 23:12:40 2026

@author: buttard
"""

import requests
from shapely.geometry import shape, mapping
from shapely.ops import unary_union

def load_geo_data():
    geo_data = requests.get(
        "https://raw.githubusercontent.com/python-visualization/folium/master/examples/data/world-countries.json"
    ).json()

    geo_data = merge_features(geo_data, 'Somalia', 'Somaliland', 'Somalia')
    geo_data = merge_features(geo_data, 'Morocco', 'Western Sahara', 'Morocco')

    geo_data = del_features(geo_data, [
        "Antarctica",
        "French Southern and Antarctic Lands",
        "Northern Cyprus"
    ])

    return geo_data

def merge_features(geo_data, a, b, new):
    feat_a = next(f for f in geo_data["features"] if f["properties"]["name"] == a)
    feat_b = next(f for f in geo_data["features"] if f["properties"]["name"] == b)

    merged = unary_union([shape(feat_a["geometry"]), shape(feat_b["geometry"])])

    geo_data["features"] = [
        f for f in geo_data["features"]
        if f["properties"]["name"] not in [a, b]
    ]

    geo_data["features"].append({
        "type": "Feature",
        "properties": {"name": new},
        "geometry": mapping(merged)
    })

    return geo_data

def del_features(geo_data, exclude):
    geo_data["features"] = [
        f for f in geo_data["features"]
        if f["properties"]["name"] not in exclude
    ]
    return geo_data
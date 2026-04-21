import requests
from shapely.geometry import shape, mapping
from shapely.ops import unary_union


def load_geo_data():
    """
    Load and preprocess world country GeoJSON data.

    This function:
    - Downloads a GeoJSON file containing country geometries
    - Merges specific territories into their parent countries
    - Removes unwanted or non-relevant regions

    Returns
    -------
    dict
        GeoJSON dictionary with cleaned and standardized country geometries

    Notes
    -----
    - Somaliland is merged into Somalia
    - Western Sahara is merged into Morocco
    - Some regions (e.g. Antarctica) are removed
    """
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
    """
    Merge two country geometries into a single feature.

    Parameters
    ----------
    geo_data : dict
        GeoJSON dictionary containing country features
    a : str
        Name of the first country to merge
    b : str
        Name of the second country to merge
    new : str
        Name of the resulting merged country

    Returns
    -------
    dict
        Updated GeoJSON with merged feature

    Notes
    -----
    - The geometries of countries `a` and `b` are combined using a union
    - Original features are removed and replaced with the merged one
    """
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
    """
    Remove specific countries or regions from GeoJSON data.

    Parameters
    ----------
    geo_data : dict
        GeoJSON dictionary containing country features
    exclude : list
        List of country names to remove

    Returns
    -------
    dict
        Updated GeoJSON without the excluded features
    """
    geo_data["features"] = [
        f for f in geo_data["features"]
        if f["properties"]["name"] not in exclude
    ]
    return geo_data


def inject_data_into_geojson(geo_data, df, target):
    """
    Inject dataframe values into GeoJSON properties.

    This function maps country-level data from a dataframe
    into the corresponding GeoJSON features.

    Parameters
    ----------
    geo_data : dict
        GeoJSON dictionary containing country features
    df : pd.DataFrame
        DataFrame containing:
        - 'Country' column
        - target column to inject
    target : str
        Column name to inject into GeoJSON properties

    Returns
    -------
    dict
        GeoJSON with added property for each country

    Notes
    -----
    - If a country is missing in the dataframe, value will be None
    """
    value_dict = df.set_index("Country")[target].to_dict()

    for feature in geo_data["features"]:
        country = feature["properties"]["name"]
        feature["properties"][target] = value_dict.get(country)

    return geo_data


def get_geo_countries(geo_data):
    """
    Extract list of country names from GeoJSON.

    Parameters
    ----------
    geo_data : dict
        GeoJSON dictionary containing country features

    Returns
    -------
    list
        List of country names present in the GeoJSON
    """
    return [f["properties"]["name"] for f in geo_data["features"]]
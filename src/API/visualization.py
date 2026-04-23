# visualization.py
import folium
import branca.colormap as cm
import numpy as np
import pandas as pd


def create_map(df, geo_data, target, colormap_name="Blues"):

    score_dict = df.set_index("Country")[target].to_dict()
    values = df[target].dropna()

    vmin = np.percentile(values, 10)
    vmax = np.percentile(values, 99)

    COLORMAPS = {
        "Blues": cm.linear.Blues_09,
        "Greens": cm.linear.Greens_09,
        "Reds": cm.linear.Reds_09,
        "Oranges": cm.linear.Oranges_09,
        "Viridis": cm.linear.viridis,
        "Plasma": cm.linear.plasma,
    }

    colormap = COLORMAPS.get(colormap_name, cm.linear.Blues_09).scale(vmin, vmax)

    valid_countries = set(df["Country"])
    # ================================================================
    # SANCTIONS LABELS
    # ================================================================
    sanctions_labels = {}

    if target == "score_pol_sanctions_international":

        sanctions_labels = (
            df.set_index("Country")[
                [
                    "group_1_label",
                    "group_2_label",
                    "group_3_label",
                    "group_4_label",
                ]
            ]
            .to_dict(orient="index")
        )

    m = folium.Map(location=[20, 0], zoom_start=2)

    def style(feature):
        country = feature["properties"]["name"]
        val = score_dict.get(country)

        if country not in valid_countries:
            return {
                "fillColor": "#ffffff",
                "color": "#d1d5db",
                "weight": 0.2,
                "fillOpacity": 0.2,
            }

        return {
            "fillColor": colormap(val) if pd.notna(val) else "#000000",
            "color": "black",
            "weight": 0.3,
            "fillOpacity": 0.7,
        }

    # ================================================================
    # TOOLTIP
    # ================================================================
    for feature in geo_data["features"]:

        country = feature["properties"]["name"]

        value = score_dict.get(country)

        tooltip = f"""
        <b>{country}</b><br>
        {target}: {value}
        """

        # ------------------------------------------------------------
        # SANCTIONS DETAILS
        # ------------------------------------------------------------
        if target == "score_pol_sanctions_international":

            info = sanctions_labels.get(country, {})

            tooltip += f"""
            <br><br>
            <b>Sanctions groups</b><br>
            Group 1 (UN): {info.get('group_1_label', 'N/A')}<br>
            Group 2 (US): {info.get('group_2_label', 'N/A')}<br>
            Group 3 (EU/UK): {info.get('group_3_label', 'N/A')}<br>
            Group 4 (Others): {info.get('group_4_label', 'N/A')}
            """

        feature["properties"]["tooltip"] = tooltip

    # ================================================================
    # GEOJSON
    # ================================================================
    folium.GeoJson(
        geo_data,
        style_function=style,
        tooltip=folium.GeoJsonTooltip(
            fields=["tooltip"],
            labels=False,
        ),
    ).add_to(m)

    colormap.caption = target
    colormap.add_to(m)

    return m


def create_emergency_map(
    df,
    geo_data,
    risk,
):
    """
    Create emergency implementation map.

    Parameters
    ----------
    df : pandas.DataFrame
        Emergency implementation dataframe.

    geo_data : dict
        GeoJSON world geometry.

    risk : str
        Selected risk type.

    Returns
    -------
    folium.Map
        Emergency Folium map.
    """

    emergency_dict = (
        df
        .set_index("Country")
        .to_dict(orient="index")
    )

    emergency_map = folium.Map(
        location=[20, 0],
        zoom_start=2,
    )

    # =========================================================================
    # STYLE
    # =========================================================================

    def style(feature):

        country = (
            feature["properties"]["name"]
        )

        info = emergency_dict.get(
            country,
            {},
        )

        if info.get("Contact"):

            return {
                "fillColor": "#ef4444",
                "color": "black",
                "weight": 0.5,
                "fillOpacity": 0.7,
            }

        return {
            "fillColor": "#ffffff",
            "color": "#d1d5db",
            "weight": 0.3,
            "fillOpacity": 0.2,
        }

    # =========================================================================
    # TOOLTIP
    # =========================================================================

    filtered_features = []

    for feature in geo_data["features"]:
    
        country = (
            feature["properties"]["name"]
        )
    
        info = emergency_dict.get(
            country,
            {},
        )
    
        # ================================================================
        # KEEP ONLY IMPLEMENTED COUNTRIES
        # ================================================================
    
        if not info:
            continue
    
        contact = info.get(
            "Contact",
            {},
        )
    
        email = contact.get(
            "email",
            "N/A",
        )
    
        phone = contact.get(
            "phone",
            "N/A",
        )
    
        plants = info.get(
            "Number of implementations",
            "N/A",
        )
    
        people = info.get(
            "Number of people",
            "N/A",
        )
    
        feature["properties"]["tooltip"] = f"""
        <b>{country}</b><br>
        📧 {email}<br>
        📞 {phone}<br>
        🏭 {plants}<br>
        👥 {people}
        """
    
        filtered_features.append(feature)
    
    # =========================================================================
    # FILTERED GEOJSON
    # =========================================================================
    
    filtered_geojson = {
        "type": "FeatureCollection",
        "features": filtered_features,
    }
    
    # =========================================================================
    # MAP
    # =========================================================================
    
    folium.GeoJson(
        filtered_geojson,
        style_function=style,
        tooltip=folium.GeoJsonTooltip(
            fields=["tooltip"],
            labels=False,
        ),
    ).add_to(emergency_map)

    return emergency_map
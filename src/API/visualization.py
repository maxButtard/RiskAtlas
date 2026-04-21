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

    folium.GeoJson(
        geo_data,
        style_function=style,
        tooltip=folium.GeoJsonTooltip(
            fields=["name", target],
            aliases=["Country:", target],
        ),
    ).add_to(m)

    colormap.caption = target
    colormap.add_to(m)

    return m


def create_emergency_map(df, geo_data, risk):

    emergency_dict = df.set_index("Country").to_dict(orient="index")
    m = folium.Map(location=[20, 0], zoom_start=2)

    def style(feature):
        country = feature["properties"]["name"]
        info = emergency_dict.get(country, {})

        if info.get("Contact"):
            return {"fillColor": "#ef4444", "color": "black", "weight": 0.5, "fillOpacity": 0.7}
        else:
            return {"fillColor": "#ffffff", "color": "#d1d5db", "weight": 0.3, "fillOpacity": 0.2}

    for f in geo_data["features"]:
        country = f["properties"]["name"]
        info = emergency_dict.get(country, {})

        contact = info.get("Contact", {})
        phone = contact.get("phone", "N/A")
        email = contact.get("email", "N/A")
        plants = info.get("Number of implementations", "N/A")
        people = info.get("Number of people", "N/A")

        f["properties"]["tooltip"] = f"""
        <b>{country}</b><br>
        📞 {phone}<br>
        📧 <a href="mailto:{email}">{email}</a><br>
        🏭 {plants}<br>
        👥 {people}
        """

    folium.GeoJson(
        geo_data,
        style_function=style,
        tooltip=folium.GeoJsonTooltip(fields=["tooltip"], labels=False),
    ).add_to(m)

    return m
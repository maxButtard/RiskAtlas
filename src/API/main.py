"""
Risk Atlas API
==============

Main Flask application for:
- Risk visualization
- Emergency contacts
- Supabase authentication
"""

import os
from typing import Optional

import pandas as pd
import requests

from dotenv import load_dotenv
from flask import Flask, render_template, request

from sqlalchemy import create_engine
from sqlalchemy.engine import URL

from src.API.geo_utils import load_geo_data
from src.API.visualization import (
    create_emergency_map,
    create_map,
)


# =============================================================================
# CONFIGURATION
# =============================================================================

load_dotenv()

app = Flask(__name__)

SUPABASE_URL = (
    "https://xccdxewtvkscnudynbsx.supabase.co"
)


# =============================================================================
# DATABASE
# =============================================================================

DATABASE_URL = URL.create(
    drivername="postgresql+psycopg2",
    username=os.getenv("DB_USER"),
    password=os.getenv("DB_PASSWORD"),
    host=os.getenv("DB_HOST"),
    port=int(os.getenv("DB_PORT")),
    database=os.getenv("DB_NAME"),
)

engine = create_engine(DATABASE_URL)


# =============================================================================
# AUTHENTICATION
# =============================================================================

def get_user(token: str) -> Optional[dict]:
    """
    Validate Supabase JWT token.

    Parameters
    ----------
    token : str
        Supabase JWT token.

    Returns
    -------
    Optional[dict]
        User information if authenticated,
        otherwise None.
    """

    if not token:
        return None

    response = requests.get(
        f"{SUPABASE_URL}/auth/v1/user",
        headers={
            "Authorization": f"Bearer {token}",
            "apikey": os.getenv(
                "SUPABASE_ANON_KEY"
            ),
        },
    )

    if response.status_code != 200:
        return None

    return response.json()


# =============================================================================
# HEALTH CHECK
# =============================================================================

@app.route("/health")
def health() -> tuple[str, int]:
    """
    Health check endpoint.

    Returns
    -------
    tuple[str, int]
        API status and HTTP code.
    """

    return "ok", 200


# =============================================================================
# MAIN PAGE
# =============================================================================

@app.route("/")
def index():
    """
    Render main application page.

    Public users:
    - Can only access Population score

    Authenticated users:
    - Can access all scores

    Returns
    -------
    str
        Rendered HTML template.
    """

    token = request.args.get("token")

    user = get_user(token)

    df_risk = pd.read_sql(
        'SELECT * FROM "External_risk"',
        engine,
    )

    selected_tab = request.args.get(
        "tab",
        "maps",
    )

    selected_colormap = request.args.get(
        "colormap",
        "Blues",
    )

    # =========================================================================
    # AUTHORIZATION
    # =========================================================================

    if user:

        scores = [
            column
            for column in df_risk.columns
            if column != "Country"
        ]

    else:

        scores = ["Population"]

    selected_score = request.args.get(
        "score",
        scores[0],
    )

    return render_template(
        "map.html",
        user=user,
        token=token,
        scores=scores,
        selected_score=selected_score,
        selected_colormap=selected_colormap,
        selected_tab=selected_tab,
    )


# =============================================================================
# RISK MAP
# =============================================================================

@app.route("/map_html")
def map_html():
    """
    Generate risk map HTML.

    Public users:
    - Population score only

    Authenticated users:
    - Full score access

    Returns
    -------
    str
        Rendered Folium map HTML.
    """

    token = request.args.get("token")

    user = get_user(token)

    df_risk = pd.read_sql(
        'SELECT * FROM "External_risk"',
        engine,
    )

    geo = load_geo_data()

    colormap = request.args.get(
        "colormap",
        "Blues",
    )

    # =========================================================================
    # PUBLIC MODE
    # =========================================================================

    if user is None:

        score = "Population"

    # =========================================================================
    # AUTHENTICATED MODE
    # =========================================================================

    else:

        score = request.args.get(
            "score",
            df_risk.columns[1],
        )

    # =========================================================================
    # MAP VALUES
    # =========================================================================

    value_dict = (
        df_risk
        .set_index("Country")[score]
        .to_dict()
    )

    for feature in geo["features"]:

        country = feature["properties"]["name"]

        feature["properties"][score] = (
            value_dict.get(country)
        )

    # =========================================================================
    # MAP GENERATION
    # =========================================================================

    risk_map = create_map(
        df_risk,
        geo,
        score,
        colormap,
    )

    return risk_map.get_root().render()


# =============================================================================
# EMERGENCY MAP
# =============================================================================

@app.route("/emergency_map")
def emergency_map():
    """
    Generate emergency map HTML.

    Displays:
    - Emergency contact
    - Emergency phone number

    Returns
    -------
    str
        Rendered Folium map HTML.
    """

    risk = request.args.get(
        "risk",
        "cyclone",
    )

    geo = load_geo_data()

    df_emergency = pd.read_sql(
        'SELECT * FROM "Emergency"',
        engine,
    )

    df_emergency = df_emergency.dropna(
        subset=[
            "Phone",
            "Contact",
        ],
    )

    emergency = create_emergency_map(
        df_emergency,
        geo,
        risk,
    )

    return emergency.get_root().render()


# =============================================================================
# RUN
# =============================================================================

if __name__ == "__main__":

    port = int(
        os.environ.get(
            "PORT",
            8080,
        )
    )

    app.run(
        host="0.0.0.0",
        port=port,
    )
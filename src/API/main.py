"""
Risk Atlas API
===============

Main Flask application for:
- Risk visualization
- Emergency contacts
- Implementation analysis
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
from src.API.visualization import create_emergency_map, create_map


# =============================================================================
# CONFIGURATION
# =============================================================================

load_dotenv()

app = Flask(__name__)

SUPABASE_URL = "https://xccdxewtvkscnudynbsx.supabase.co"


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
    Validate Supabase JWT token and return user information.

    Parameters
    ----------
    token : str
        Supabase JWT token.

    Returns
    -------
    Optional[dict]
        User dictionary if authenticated, else None.
    """

    if not token:
        return None

    response = requests.get(
        f"{SUPABASE_URL}/auth/v1/user",
        headers={
            "Authorization": f"Bearer {token}",
            "apikey": os.getenv("SUPABASE_ANON_KEY"),
        },
    )

    if response.status_code != 200:
        print("AUTH ERROR:", response.text)
        return None

    return response.json()


# =============================================================================
# HEALTH CHECK
# =============================================================================

@app.route("/health")
def health() -> tuple[str, int]:
    """
    Render health check endpoint.

    Returns
    -------
    tuple[str, int]
        Health status and HTTP code.
    """

    return "ok", 200


# =============================================================================
# MAIN PAGE
# =============================================================================

@app.route("/")
def index():
    """
    Main UI page.

    Unauthenticated users:
    - can only access Population score

    Authenticated users:
    - can access all scores
    """

    token = request.args.get("token")
    user = get_user(token)

    df_risk = pd.read_sql(
        'SELECT * FROM "External_risk"',
        engine,
    )

    df_emergency = pd.read_sql(
        'SELECT * FROM "Emergency"',
        engine,
    )

    selected_tab = request.args.get("tab", "maps")
    selected_colormap = request.args.get("colormap", "Blues")
    selected_risk = request.args.get("risk", "cyclone")

    only_impl = request.args.get("only_impl") == "true"

    # =========================================================================
    # AUTHORIZATION LEVEL
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

    # =========================================================================
    # FILTER IMPLEMENTATIONS
    # =========================================================================

    if only_impl:

        countries_impl = set(df_emergency["Country"])

        df_risk = df_risk[
            df_risk["Country"].isin(countries_impl)
        ]

    countries = df_risk["Country"].unique().tolist()

    return render_template(
        "map.html",
        user=user,
        scores=scores,
        selected_score=selected_score,
        selected_colormap=selected_colormap,
        selected_tab=selected_tab,
        selected_risk=selected_risk,
        only_impl=only_impl,
        countries=countries,
        final_score=None,
    )


# =============================================================================
# RISK MAP
# =============================================================================

@app.route("/map_html")
def map_html():
    """
    Generate interactive risk map.

    Unauthenticated users:
    - can only access Population map

    Authenticated users:
    - can access all scores
    """

    token = request.args.get("token")

    # =========================================================================
    # OPTIONAL AUTH
    # =========================================================================

    user = get_user(token) if token else None

    # =========================================================================
    # LOAD DATA
    # =========================================================================

    df_risk = pd.read_sql(
        'SELECT * FROM "External_risk"',
        engine,
    )

    df_emergency = pd.read_sql(
        'SELECT * FROM "Emergency"',
        engine,
    )

    geo = load_geo_data()

    colormap = request.args.get(
        "colormap",
        "Blues",
    )

    only_impl = request.args.get("only_impl") == "true"

    # =========================================================================
    # AUTHORIZATION LEVEL
    # =========================================================================

    if user:

        score = request.args.get(
            "score",
            df_risk.columns[1],
        )

        user_email = user.get("email")

        if "email" in df_risk.columns:

            df_risk = df_risk[
                df_risk["email"] == user_email
            ]

    else:

        # 🔥 Public mode
        score = "Population"

    # =========================================================================
    # FILTER IMPLEMENTATIONS
    # =========================================================================

    if only_impl:

        countries_impl = set(df_emergency["Country"])

        df_risk = df_risk[
            df_risk["Country"].isin(countries_impl)
        ]

    # =========================================================================
    # BUILD MAP VALUES
    # =========================================================================

    value_dict = df_risk.set_index("Country")[score].to_dict()

    for feature in geo["features"]:

        country = feature["properties"]["name"]

        feature["properties"][score] = value_dict.get(country)

    # =========================================================================
    # CREATE MAP
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
    Display emergency map.

    Shows:
    - Emergency contact
    - Emergency phone number
    - Only countries with implementations
    """

    risk = request.args.get("risk", "cyclone")

    geo = load_geo_data()

    df_emergency = pd.read_sql(
        'SELECT * FROM "Emergency"',
        engine,
    )

    # =========================================================================
    # KEEP ONLY IMPLEMENTED COUNTRIES
    # =========================================================================

    df_emergency = df_emergency.dropna(
        subset=["Phone", "Contact"],
    )

    emergency = create_emergency_map(
        df_emergency,
        geo,
        risk,
    )

    return emergency.get_root().render()


# =============================================================================
# IMPLEMENTATION ANALYSIS
# =============================================================================

@app.route("/implementation", methods=["POST"])
def implementation():
    """
    Compute implementation risk score.
    """

    df_risk = pd.read_sql(
        'SELECT * FROM "External_risk"',
        engine,
    )

    country = request.form.get("country")

    factories = int(
        request.form.get("factories", 1)
    )

    people = int(
        request.form.get("people", 0)
    )

    base_score = df_risk.loc[
        df_risk["Country"] == country
    ].iloc[0, 1]

    final_score = (
        base_score
        * factories
        * (1 + people / 1000)
    )

    countries = df_risk["Country"].tolist()

    return render_template(
        "map.html",
        selected_tab="implementation",
        countries=countries,
        final_score=round(final_score, 2),
        scores=df_risk.columns.tolist(),
        selected_score=df_risk.columns[1],
        selected_colormap="Blues",
        selected_risk="cyclone",
        only_impl=False,
    )


# =============================================================================
# RUN
# =============================================================================

if __name__ == "__main__":

    port = int(os.environ.get("PORT", 8080))

    app.run(
        host="0.0.0.0",
        port=port,
    )
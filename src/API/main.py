# main.py
from flask import Flask, render_template, request
from sqlalchemy import create_engine
from sqlalchemy.engine import URL
import pandas as pd
import os
from dotenv import load_dotenv
import requests

from src.API.visualization import create_map, create_emergency_map
from src.API.geo_utils import load_geo_data

# 🔐 Load env
load_dotenv()

app = Flask(__name__)

# 🔗 Supabase Auth URL
SUPABASE_URL = "https://xccdxewtvkscnudynbsx.supabase.co"

def get_user(token):
    if not token:
        return None

    response = requests.get(
        f"{SUPABASE_URL}/auth/v1/user",
        headers={
            "Authorization": f"Bearer {token}",
            "apikey": os.getenv("SUPABASE_ANON_KEY")  # 🔥 AJOUT ICI
        }
    )

    if response.status_code != 200:
        print("AUTH ERROR:", response.text)
        return None

    return response.json()


# 🗄️ Database connection (Supabase Postgres)
DATABASE_URL = URL.create(
    drivername="postgresql+psycopg2",
    username=os.getenv("DB_USER"),
    password=os.getenv("DB_PASSWORD"),
    host=os.getenv("DB_HOST"),
    port=int(os.getenv("DB_PORT")),
    database=os.getenv("DB_NAME"),
)

engine = create_engine(DATABASE_URL)


# 🌍 Main UI
@app.route("/")
def index():

    df_risk = pd.read_sql('SELECT * FROM "External_risk"', engine)
    df_emergency = pd.read_sql('SELECT * FROM "Emergency"', engine)

    selected_tab = request.args.get("tab", "maps")
    selected_score = request.args.get("score", df_risk.columns[1])
    selected_colormap = request.args.get("colormap", "Blues")
    selected_risk = request.args.get("risk", "cyclone")

    only_impl = request.args.get("only_impl") == "true"

    if only_impl:
        countries_impl = set(df_emergency["Country"])
        df_risk = df_risk[df_risk["Country"].isin(countries_impl)]

    scores = [col for col in df_risk.columns if col != "Country"]
    countries = df_risk["Country"].unique().tolist()

    return render_template(
        "map.html",
        scores=scores,
        selected_score=selected_score,
        selected_colormap=selected_colormap,
        selected_tab=selected_tab,
        selected_risk=selected_risk,
        only_impl=only_impl,
        countries=countries,
        final_score=None
    )


# Map endpoint (with auth)
@app.route("/map_html")
def map_html():
    # 🔐 Auth
    token = request.args.get("token")

    if not token:
        return "Unauthorized - no token", 401

    user = get_user(token)

    if not user:
        return "Unauthorized - invalid token", 401

    df_risk = pd.read_sql('SELECT * FROM "External_risk"', engine)
    df_emergency = pd.read_sql('SELECT * FROM "Emergency"', engine)

    geo = load_geo_data()

    score = request.args.get("score", df_risk.columns[1])
    colormap = request.args.get("colormap", "Blues")
    only_impl = request.args.get("only_impl") == "true"

    

    user_email = user.get("email")

    # 🔥 Filter by user
    if "email" in df_risk.columns:
        df_risk = df_risk[df_risk["email"] == user_email]

    # 🔥 Existing filter
    if only_impl:
        countries_impl = set(df_emergency["Country"])
        df_risk = df_risk[df_risk["Country"].isin(countries_impl)]

    # 🔗 Map values
    value_dict = df_risk.set_index("Country")[score].to_dict()

    for f in geo["features"]:
        country = f["properties"]["name"]
        f["properties"][score] = value_dict.get(country)

    m = create_map(df_risk, geo, score, colormap)

    return m.get_root().render()


# Emergency map (no auth for now)
@app.route("/emergency_map")
def emergency_map():

    risk = request.args.get("risk", "cyclone")

    geo = load_geo_data()
    df = pd.read_sql('SELECT * FROM "Emergency"', engine)

    m = create_emergency_map(df, geo, risk)

    return m.get_root().render()


# Implementation tab
@app.route("/implementation", methods=["POST"])
def implementation():

    df = pd.read_sql('SELECT * FROM "External_risk"', engine)

    country = request.form.get("country")
    factories = int(request.form.get("factories", 1))
    people = int(request.form.get("people", 0))

    base_score = df.loc[df["Country"] == country].iloc[0, 1]
    final_score = base_score * factories * (1 + people / 1000)

    countries = df["Country"].tolist()

    return render_template(
        "map.html",
        selected_tab="implementation",
        countries=countries,
        final_score=round(final_score, 2),
        scores=df.columns.tolist(),
        selected_score=df.columns[1],
        selected_colormap="Blues",
        selected_risk="cyclone",
        only_impl=False
    )

# Run
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
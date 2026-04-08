import numpy as np
import pandas as pd


# =========================
# SECURITY
# =========================
def compute_security_score(df: pd.DataFrame) -> pd.DataFrame:
    """
    Compute security-related risk score.

    This score is based on:
    - Fatality rate per 100,000 inhabitants
    - Terrorism score

    The fatality rate is discretized into a score (0–10),
    then combined with the terrorism score to produce a
    normalized security score (0–100).

    Parameters
    ----------
    df : pd.DataFrame
        Input dataframe containing:
        - 'FATALITIES'
        - 'Population'
        - 'terrorism_score'

    Returns
    -------
    pd.DataFrame
        DataFrame with additional columns:
        - 'fatality_rate'
        - 'fatality_score'
        - 'score_security'
    """
    df = df.copy()

    df["Population"] = df["Population"].replace(0, np.nan)

    df["fatality_rate"] = (
        df["FATALITIES"] / df["Population"] * 100000
    )

    df["fatality_score"] = np.select(
        [
            df["fatality_rate"] <= 0,
            df["fatality_rate"] <= 2,
            df["fatality_rate"] <= 5,
            df["fatality_rate"] <= 10,
            df["fatality_rate"] <= 20,
            df["fatality_rate"] > 20,
        ],
        [0, 2, 4, 6, 8, 10],
        default=0,
    )

    df["score_security"] = (
        df["terrorism_score"] * 10
        + df["fatality_score"] * 10
    ) / 2

    return df


# =========================
# POLITICAL
# =========================
def compute_political_score(df: pd.DataFrame) -> pd.DataFrame:
    """
    Compute political risk score.

    This score aggregates multiple political risk dimensions:
    - Governance quality
    - Political violence events
    - Corruption level
    - International sanctions exposure

    Each component is scaled and averaged to produce
    a global political risk score.

    Parameters
    ----------
    df : pd.DataFrame
        Input dataframe containing:
        - 'governance_score'
        - 'events'
        - 'score_pol_corruption'
        - 'group_1', 'group_2', 'group_3', 'group_4'

    Returns
    -------
    pd.DataFrame
        DataFrame with additional columns:
        - 'score_pol_sanctions_international'
        - 'score_violence_events'
        - 'score_political'
    """
    df = df.copy()
    df["governance_score"] = abs(100-df["governance_score"])
    df["score_pol_sanctions_international"] = (
        df["group_1"] * 25 +
        df["group_2"] * 30 +
        df["group_3"] * 30 +
        df["group_4"] * 15
    )

    df["score_violence_events"] = np.select(
        [
            df["events"] <= 5,
            df["events"] <= 10,
            df["events"] <= 20,
            df["events"] <= 50,
            df["events"] <= 150,
            df["events"] <= 300,
            df["events"] <= 600,
            df["events"] <= 1000,
            df["events"] > 1000,
        ],
        [0, 5, 10, 20, 40, 60, 75, 85, 95],
    )

    df["score_political"] = (
        df["governance_score"]
        + df["score_violence_events"]
        + df["score_pol_corruption"]
        + df["score_pol_sanctions_international"]
    ) / 4

    return df


# =========================
# NATURAL RISK
# =========================
def compute_natural_score(df: pd.DataFrame) -> pd.DataFrame:
    """
    Compute natural hazard risk score.

    This score is the average of:
    - Coastal flood exposure
    - Cyclone exposure
    - INFORM natural hazard index

    Parameters
    ----------
    df : pd.DataFrame
        Input dataframe containing:
        - 'Coastal flood exposure'
        - 'Cyclone exposure'
        - 'INFORM Natural Hazard'

    Returns
    -------
    pd.DataFrame
        DataFrame with additional column:
        - 'score_natural_hazard'
    """
    df = df.copy()

    df["score_natural_hazard"] = df[
        [
            "Coastal flood exposure",
            "Cyclone exposure",
            "INFORM Natural Hazard",
        ]
    ].mean(axis=1)

    return df


# =========================
# FINAL SCORE
# =========================
def compute_final_score(df: pd.DataFrame) -> pd.DataFrame:
    """
    Compute final composite risk score.

    The final score is a weighted combination of:
    - Security risk
    - Political risk
    - Natural hazard risk

    Weights:
    - Security: 0.30
    - Political: 0.25
    - Natural: 0.15

    The result is normalized by the sum of weights.

    Parameters
    ----------
    df : pd.DataFrame
        Input dataframe containing:
        - 'score_security'
        - 'score_political'
        - 'score_natural_hazard'

    Returns
    -------
    pd.DataFrame
        DataFrame with additional column:
        - 'score_final'
    """
    df = df.copy()

    weights = {
        "security": 0.3,
        "political": 0.25,
        "natural": 0.15,
    }

    weights_sum = sum(weights.values())

    df["score_final"] = (
        df["score_security"] * weights["security"]
        + df["score_political"] * weights["political"]
        + df["score_natural_hazard"] * weights["natural"]
    ) / weights_sum

    return df


# =========================
# GLOBAL PIPELINE
# =========================
def compute_score(df: pd.DataFrame) -> pd.DataFrame:
    """
    Compute full country risk scoring pipeline.

    This function orchestrates all intermediate steps:
    1. Security score computation
    2. Political score computation
    3. Natural hazard score computation
    4. Final composite score aggregation

    Parameters
    ----------
    df : pd.DataFrame
        Input dataframe containing all required indicators.

    Returns
    -------
    pd.DataFrame
        DataFrame enriched with all intermediate and final scores.

    Notes
    -----
    This function assumes that all required columns are already
    cleaned and standardized (country names, missing values, etc.).
    """
    df = compute_security_score(df)
    df = compute_political_score(df)
    df = compute_natural_score(df)
    df = compute_final_score(df)

    return df
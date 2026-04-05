# -*- coding: utf-8 -*-
"""
Created on Sun Apr  5 23:13:38 2026

@author: buttard
"""

import numpy as np

def compute_security_score(df):
    df["score_security"] = (
        df["score_terrorism"] * 10
        + df["fatality_score"] * 10
        + df["conflict_score"] * 10
    ) / 3
    return df


def compute_final_score(df):
    df["score_final"] = (
        df["score_security"] * 0.3
        + df["score_politique"] * 0.25
        + df["score_natural_hasard"] * 0.15
        + df["score_interne"] * 0.3
    )
    return df
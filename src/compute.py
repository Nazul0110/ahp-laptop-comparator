import numpy as np
import streamlit as st

from src.ahp import ahp_weights, ahp_consistency, sanitize_reciprocal


def calc_scenario(name: str):
    criteria = st.session_state.criteria
    alts = st.session_state.alts
    scen = st.session_state.scenarios[name]

    Acrit = sanitize_reciprocal(scen["crit_matrix"])
    wcrit = ahp_weights(Acrit)
    lam_c, ci_c, cr_c = ahp_consistency(Acrit, wcrit)

    altW = {}
    altCR = {}
    for c in criteria:
        A = sanitize_reciprocal(scen["alt_matrices"][c])
        w = ahp_weights(A)
        lam, ci, cr = ahp_consistency(A, w)
        altW[c] = w
        altCR[c] = (lam, ci, cr)

    scores = np.zeros(len(alts), dtype=float)
    contrib = np.zeros((len(alts), len(criteria)), dtype=float)
    for i in range(len(alts)):
        total = 0.0
        for k, c in enumerate(criteria):
            v = float(wcrit[k]) * float(altW[c][i])
            contrib[i, k] = v
            total += v
        scores[i] = total

    return {
        "Acrit": Acrit,
        "wcrit": wcrit,
        "crit_cons": (lam_c, ci_c, cr_c),
        "altW": altW,
        "altCR": altCR,
        "scores": scores,
        "contrib": contrib,
    }

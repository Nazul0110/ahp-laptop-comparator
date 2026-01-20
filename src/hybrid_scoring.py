import numpy as np
import pandas as pd
import streamlit as st

from src.ahp import sanitize_reciprocal, ahp_weights, ahp_consistency
from src.criteria_meta import normalize_values

def compute_hybrid_for_scenario(scenario_name: str, cr_threshold: float = 0.10):
    criteria = st.session_state.criteria
    alts = st.session_state.alts
    meta = st.session_state.criteria_meta
    scen = st.session_state.scenarios[scenario_name]
    specs = st.session_state.get("laptop_specs", pd.DataFrame())

    # --- kriteria weights dari matriks kriteria
    Acrit = sanitize_reciprocal(scen["crit_matrix"])
    wcrit = ahp_weights(Acrit)
    lam_c, ci_c, cr_c = ahp_consistency(Acrit, wcrit)

    # --- skor alternatif per kriteria (vector length = #alts)
    percrit_scores = {}
    percrit_cr = {}

    # specs -> index by Laptop
    if isinstance(specs, pd.DataFrame) and "Laptop" in specs.columns:
        specs_idx = specs.set_index("Laptop").reindex(alts)
    else:
        specs_idx = pd.DataFrame(index=alts)

    for k, c in enumerate(criteria):
        m = meta.get(c, {})
        subjective = bool(m.get("subjective", True))
        ctype = m.get("type", "benefit")
        method = m.get("method", "minmax")
        spec_col = m.get("spec_col", None)

        if (not subjective) and spec_col and (spec_col in specs_idx.columns):
            vals = specs_idx[spec_col].values.astype(float)
            s01 = normalize_values(vals, ctype=ctype, method=method)
            # ubah jadi "bobot alternatif" (sum=1)
            ssum = float(np.sum(s01))
            w_alt = (s01 / ssum) if ssum > 1e-12 else np.ones(len(alts)) / len(alts)
            percrit_scores[c] = w_alt
            percrit_cr[c] = (np.nan, np.nan, 0.0)  # objective: CR tidak berlaku
        else:
            # subjective -> pakai AHP alt matrices
            Aalt = sanitize_reciprocal(scen["alt_matrices"][c])
            w_alt = ahp_weights(Aalt)
            lam, ci, cr = ahp_consistency(Aalt, w_alt)
            percrit_scores[c] = w_alt
            percrit_cr[c] = (lam, ci, cr)

    # --- skor akhir
    scores = np.zeros(len(alts), dtype=float)
    contrib = np.zeros((len(alts), len(criteria)), dtype=float)
    for i in range(len(alts)):
        total = 0.0
        for k, c in enumerate(criteria):
            v = float(wcrit[k]) * float(percrit_scores[c][i])
            contrib[i, k] = v
            total += v
        scores[i] = total

    return {
        "Acrit": Acrit,
        "wcrit": wcrit,
        "crit_cons": (lam_c, ci_c, cr_c),
        "percrit_scores": percrit_scores,
        "percrit_cr": percrit_cr,
        "scores": scores,
        "contrib": contrib,
    }

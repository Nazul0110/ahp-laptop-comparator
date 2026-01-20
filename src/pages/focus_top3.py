import streamlit as st
import numpy as np

from src.ahp import sanitize_reciprocal
from src.auto_pairwise import ratio_to_saaty
from src.state import normalize_scenario_sizes

def _weights_top3(criteria, top3, strengths):
    # strengths = dict{kriteria: 1..10}
    base = {c: 0.02 for c in criteria}
    for c in top3:
        base[c] += strengths.get(c, 6) * 0.06
    w = np.array([base[c] for c in criteria], dtype=float)
    w = w / w.sum() if w.sum() > 1e-12 else np.ones(len(criteria))/len(criteria)
    return w

def _weights_to_pairwise(w):
    n = len(w)
    A = np.ones((n, n), dtype=float)
    for i in range(n):
        for j in range(i+1, n):
            r = w[i] / max(w[j], 1e-12)
            s = ratio_to_saaty(r)
            if w[i] >= w[j]:
                A[i, j] = s
                A[j, i] = 1 / s
            else:
                A[i, j] = 1 / s
                A[j, i] = s
    return sanitize_reciprocal(A)

def render_focus_top3():
    st.title("🎯 Fokus Top-3 Kriteria (Hemat Input)")

    scenario = st.session_state.active_scenario
    normalize_scenario_sizes(scenario)
    criteria = st.session_state.criteria
    scen = st.session_state.scenarios[scenario]

    st.caption("Pilih 3 kriteria paling penting. Sistem auto-isi bobot kriteria lainnya (default kecil).")

    top3 = st.multiselect("Pilih Top 3 kriteria", criteria, default=criteria[:3], max_selections=3)

    strengths = {}
    for c in top3:
        strengths[c] = st.slider(f"Seberapa penting **{c}**?", 1, 10, 7)

    w = _weights_top3(criteria, top3, strengths)

    st.subheader("Preview bobot")
    for c, v in sorted(zip(criteria, w), key=lambda x: x[1], reverse=True):
        st.write(f"- **{c}**: {v*100:.2f}%")

    if st.button("✅ Terapkan ke Matriks Kriteria", use_container_width=True):
        scen["crit_matrix"] = _weights_to_pairwise(w)
        st.session_state.scenarios[scenario] = scen
        st.success("Matriks kriteria sudah di-set. Sekarang kamu cuma perlu pairwise untuk kriteria subjektif saja.")

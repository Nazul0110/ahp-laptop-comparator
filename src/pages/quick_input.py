import streamlit as st
import numpy as np

from src.ahp import sanitize_reciprocal
from src.state import normalize_scenario_sizes


SAATY_CHOICES = [1,2,3,4,5,6,7,8,9]

def _build_from_pairs(labels, key_prefix: str, current_A: np.ndarray):
    n = len(labels)
    A = sanitize_reciprocal(current_A)

    st.info("Pilih siapa yang lebih unggul + seberapa kuat (1–9). Bagian bawah otomatis reciprocal.")
    for i in range(n):
        for j in range(i+1, n):
            col1, col2, col3 = st.columns([4, 2, 3])
            with col1:
                st.write(f"**{labels[i]} vs {labels[j]}**")
            with col2:
                winner = st.radio(
                    "Pemenang",
                    [labels[i], "Sama", labels[j]],
                    horizontal=True,
                    key=f"{key_prefix}_win_{i}_{j}"
                )
            with col3:
                strength = st.select_slider(
                    "Kekuatan",
                    options=SAATY_CHOICES,
                    value=3,
                    key=f"{key_prefix}_s_{i}_{j}"
                )

            if winner == "Sama":
                v = 1.0
            elif winner == labels[i]:
                v = float(strength)
            else:
                v = 1.0 / float(strength)

            A[i, j] = v
            A[j, i] = 1.0 / max(v, 1e-12)

    return sanitize_reciprocal(A)


def render_quick_input():
    scenario = st.session_state.active_scenario
    normalize_scenario_sizes(scenario)

    st.title("⚡ Quick Input (Sliders) — Isi Matriks Lebih Cepat")

    mode = st.selectbox("Mau isi matriks apa?", ["Kriteria", "Alternatif per Kriteria"])

    scen = st.session_state.scenarios[scenario]
    criteria = st.session_state.criteria
    alts = st.session_state.alts

    if mode == "Kriteria":
        st.subheader("Quick Input — Matriks Kriteria")
        A_new = _build_from_pairs(criteria, f"qcrit_{scenario}", scen["crit_matrix"])

        if st.button("💾 Simpan Matriks Kriteria", use_container_width=True):
            scen["crit_matrix"] = A_new
            st.session_state.scenarios[scenario] = scen
            st.success("Matriks Kriteria tersimpan.")

    else:
        chosen = st.selectbox("Pilih kriteria:", criteria)
        st.subheader(f"Quick Input — Matriks Alternatif ({chosen})")
        A_new = _build_from_pairs(alts, f"qalt_{scenario}_{chosen}", scen["alt_matrices"][chosen])

        if st.button("💾 Simpan Matriks Alternatif", use_container_width=True):
            scen["alt_matrices"][chosen] = A_new
            st.session_state.scenarios[scenario] = scen
            st.success("Matriks Alternatif tersimpan.")

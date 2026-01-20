import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from src.criteria_meta import ensure_criteria_meta
from src.hybrid_scoring import compute_hybrid_for_scenario

def _recalc_with_custom_wcrit(res_base, wcrit_custom):
    alts = st.session_state.alts
    criteria = st.session_state.criteria
    percrit = res_base["percrit_scores"]

    scores = np.zeros(len(alts), dtype=float)
    for i in range(len(alts)):
        scores[i] = sum(float(wcrit_custom[k]) * float(percrit[criteria[k]][i]) for k in range(len(criteria)))
    return scores

def render_sensitivity():
    st.title("🧪 Sensitivity Analysis (Uji Sensitivitas Bobot)")

    ensure_criteria_meta()
    scenario = st.session_state.active_scenario

    res = compute_hybrid_for_scenario(scenario, cr_threshold=st.session_state.cr_threshold)
    criteria = st.session_state.criteria
    alts = st.session_state.alts

    st.subheader("1) Slider bobot kriteria (real-time)")
    base = res["wcrit"].copy()

    # slider tiap kriteria (0..1), lalu dinormalisasi
    raw = []
    for i, c in enumerate(criteria):
        raw.append(st.slider(f"{c}", 0.0, 1.0, float(base[i]), 0.01))
    raw = np.array(raw, dtype=float)
    raw = raw / raw.sum() if raw.sum() > 1e-12 else np.ones(len(criteria))/len(criteria)

    scores = _recalc_with_custom_wcrit(res, raw)
    df = pd.DataFrame({"Laptop": alts, "Skor": scores}).sort_values("Skor", ascending=False).reset_index(drop=True)
    st.dataframe(df, use_container_width=True)

    fig = plt.figure()
    plt.bar(df["Laptop"], df["Skor"])
    plt.title("Ranking setelah bobot diubah")
    plt.ylabel("Skor")
    st.pyplot(fig, clear_figure=True)

    st.divider()
    st.subheader("2) Stabilitas ranking (sampling acak bobot di sekitar baseline)")
    n = st.slider("Jumlah sampel", 50, 500, 200, 50)
    noise = st.slider("Besarnya gangguan bobot", 0.01, 0.30, 0.10, 0.01)

    base = res["wcrit"].copy()
    win_count = {a: 0 for a in alts}

    rng = np.random.default_rng(42)
    for _ in range(n):
        pert = base + rng.normal(0, noise, size=len(base))
        pert = np.clip(pert, 1e-6, None)
        pert = pert / pert.sum()
        sc = _recalc_with_custom_wcrit(res, pert)
        winner = alts[int(np.argmax(sc))]
        win_count[winner] += 1

    df_stab = pd.DataFrame({"Laptop": list(win_count.keys()), "P(win #1)": [v/n for v in win_count.values()]})
    df_stab = df_stab.sort_values("P(win #1)", ascending=False).reset_index(drop=True)
    st.dataframe(df_stab, use_container_width=True)

    fig2 = plt.figure()
    plt.bar(df_stab["Laptop"], df_stab["P(win #1)"])
    plt.title("Probabilitas jadi #1 saat bobot diganggu")
    plt.ylabel("P(#1)")
    st.pyplot(fig2, clear_figure=True)

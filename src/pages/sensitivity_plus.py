import numpy as np
import pandas as pd
import streamlit as st

from src.hybrid_engine import calc_hybrid_scenario

def render_sensitivity_plus():
    st.title("🧪 Sensitivity + Stabilitas Ranking")
    st.caption("Ubah bobot kriteria → ranking real-time. Ada tornado + stability score.")

    scenario = st.session_state.active_scenario
    criteria = st.session_state.criteria
    alts = st.session_state.alts

    res = calc_hybrid_scenario(scenario, use_hybrid=True)
    base_w = res["wcrit"].copy()
    base_scores = res["scores"].copy()

    st.subheader("Slider Bobot (real-time)")
    w_new = []
    for i, c in enumerate(criteria):
        w_new.append(st.slider(f"Bobot {c}", 0.0, 1.0, float(base_w[i]), 0.01))
    w_new = np.array(w_new, dtype=float)
    w_new = w_new / w_new.sum() if w_new.sum() > 1e-12 else base_w

    # Recompute scores by applying new weights (alt scores tetap dari hybrid)
    scores = np.zeros(len(alts), dtype=float)
    for i in range(len(alts)):
        total = 0.0
        for k, c in enumerate(criteria):
            total += float(w_new[k]) * float(res["altW"][c][i])
        scores[i] = total

    df = pd.DataFrame({"Laptop": alts, "Skor": scores}).sort_values("Skor", ascending=False)
    st.dataframe(df, use_container_width=True)
    winner = df.iloc[0]["Laptop"]
    st.success(f"Pemenang (set bobot ini): **{winner}**")

    st.divider()
    st.subheader("Tornado Chart (kriteria paling berpengaruh)")
    delta = st.slider("Rentang perubahan bobot per kriteria", 0.01, 0.30, 0.10, 0.01)

    tornado = []
    base_winner = alts[int(np.argmax(base_scores))]

    for k, c in enumerate(criteria):
        w_up = base_w.copy()
        w_dn = base_w.copy()
        w_up[k] += delta
        w_dn[k] = max(0.0, w_dn[k] - delta)
        w_up = w_up / w_up.sum()
        w_dn = w_dn / w_dn.sum()

        def score_with(w):
            s = np.zeros(len(alts), dtype=float)
            for i in range(len(alts)):
                s[i] = sum(float(w[j]) * float(res["altW"][criteria[j]][i]) for j in range(len(criteria)))
            return s

        s_up = score_with(w_up)
        s_dn = score_with(w_dn)

        win_up = alts[int(np.argmax(s_up))]
        win_dn = alts[int(np.argmax(s_dn))]

        tornado.append({
            "Kriteria": c,
            "Winner(+Δ)": win_up,
            "Winner(-Δ)": win_dn,
            "Change?": (win_up != base_winner) or (win_dn != base_winner)
        })

    st.dataframe(pd.DataFrame(tornado), use_container_width=True)

    st.divider()
    st.subheader("Stability Score (seberapa stabil juara)")
    st.caption("Estimasi kasar: berapa Δ minimal agar pemenang berubah (search sederhana).")

    def winner_of(w):
        s = np.zeros(len(alts))
        for i in range(len(alts)):
            s[i] = sum(float(w[j]) * float(res["altW"][criteria[j]][i]) for j in range(len(criteria)))
        return alts[int(np.argmax(s))]

    base = winner_of(base_w)
    step = 0.01
    best = None

    for k in range(len(criteria)):
        wtest = base_w.copy()
        d = 0.0
        while d <= 0.50:
            wtest2 = wtest.copy()
            wtest2[k] += d
            wtest2 = wtest2 / wtest2.sum()
            if winner_of(wtest2) != base:
                best = d if best is None else min(best, d)
                break
            d += step

    if best is None:
        st.success("Juara sangat stabil (tidak berubah sampai +0.50 pada satu kriteria).")
    else:
        st.warning(f"Juara bisa berubah jika ada perubahan bobot sekitar **Δ ≈ {best:.2f}** pada salah satu kriteria.")

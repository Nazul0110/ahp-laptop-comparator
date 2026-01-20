import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st

from src.compute import calc_scenario
from src.ahp import fmt_pct


def render_results_compare():
    st.title("📊 Hasil Akhir + Compare Multi Scenario")

    criteria = st.session_state.criteria
    alts = st.session_state.alts

    scenario = st.session_state.active_scenario
    res = calc_scenario(scenario)
    lam, ci, cr = res["crit_cons"]

    c1, c2, c3 = st.columns(3)
    c1.metric("Scenario aktif", scenario)
    c2.metric("CR Kriteria", f"{cr:.4f}")
    c3.metric("Kriteria", len(criteria))

    scores = res["scores"]
    df_rank = pd.DataFrame({"Laptop": alts, "Skor": scores})
    df_rank["Skor(%)"] = df_rank["Skor"].apply(fmt_pct)
    df_rank = df_rank.sort_values("Skor", ascending=False).reset_index(drop=True)

    st.subheader("Ranking (Scenario aktif)")
    st.dataframe(df_rank, use_container_width=True)

    fig = plt.figure()
    plt.bar(df_rank["Laptop"], df_rank["Skor"])
    plt.ylabel("Skor AHP")
    plt.title(f"Skor Akhir — {scenario}")
    plt.xticks(rotation=20, ha="right")
    st.pyplot(fig, clear_figure=True)

    st.subheader("Breakdown kontribusi per kriteria (Scenario aktif)")
    contrib = res["contrib"]
    idx_map = {a: i for i, a in enumerate(alts)}
    order = df_rank["Laptop"].tolist()

    rows = []
    for a in order:
        i = idx_map[a]
        row = {"Laptop": a}
        for k, c in enumerate(criteria):
            row[c] = contrib[i, k]
        rows.append(row)

    df_break = pd.DataFrame(rows)
    st.dataframe(df_break.style.format("{:.4f}"), use_container_width=True)

    fig2 = plt.figure()
    bottom = np.zeros(len(df_break))
    x = np.arange(len(df_break))
    for c in criteria:
        vals = df_break[c].values
        plt.bar(x, vals, bottom=bottom, label=c)
        bottom += vals
    plt.xticks(x, df_break["Laptop"], rotation=0)
    plt.ylabel("Kontribusi")
    plt.title("Stacked Kontribusi per Kriteria")
    plt.legend(bbox_to_anchor=(1.04, 1), loc="upper left")
    st.pyplot(fig2, clear_figure=True)

    st.divider()
    st.subheader("Compare Ranking antar Scenario")

    rows_sc = []
    for s in st.session_state.scenarios.keys():
        r = calc_scenario(s)
        df = pd.DataFrame({"Laptop": alts, "Skor": r["scores"]}).sort_values("Skor", ascending=False)
        top = df.iloc[0]["Laptop"]
        lam_s, ci_s, cr_s = r["crit_cons"]
        rows_sc.append([s, f"{cr_s:.4f}", top])

    df_sc = pd.DataFrame(rows_sc, columns=["Scenario", "CR Kriteria", "Juara (#1)"])
    st.dataframe(df_sc, use_container_width=True)

    compare = {"Laptop": alts}
    for s in st.session_state.scenarios.keys():
        r = calc_scenario(s)
        compare[s] = r["scores"]
    df_cmp = pd.DataFrame(compare)

    st.subheader("Skor per Scenario (untuk perbandingan)")
    fmt_map = {c: "{:.4f}" for c in df_cmp.columns if c != "Laptop"}
    st.dataframe(df_cmp.style.format(fmt_map), use_container_width=True)

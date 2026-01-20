import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from src.criteria_meta import ensure_criteria_meta
from src.hybrid_scoring import compute_hybrid_for_scenario

def render_explainability():
    st.title("💡 Why This Laptop Wins (Explainability)")

    ensure_criteria_meta()
    scenario = st.session_state.active_scenario

    res = compute_hybrid_for_scenario(scenario, cr_threshold=st.session_state.cr_threshold)
    alts = st.session_state.alts
    criteria = st.session_state.criteria

    scores = res["scores"]
    order = np.argsort(scores)[::-1]
    winner = alts[order[0]]

    st.subheader(f"🏆 Pemenang: **{winner}**")
    st.write("Ini karena kontribusi skor terbesar datang dari kombinasi bobot kriteria × skor laptop pada kriteria tersebut.")

    # table ranking
    df_rank = pd.DataFrame({"Laptop": alts, "Skor": scores})
    df_rank = df_rank.sort_values("Skor", ascending=False).reset_index(drop=True)
    st.dataframe(df_rank, use_container_width=True)

    # kontribusi pemenang
    idx_w = alts.index(winner)
    contrib = res["contrib"][idx_w, :]  # per kriteria
    df_c = pd.DataFrame({"Kriteria": criteria, "Kontribusi": contrib, "BobotKriteria": res["wcrit"]})
    df_c = df_c.sort_values("Kontribusi", ascending=False)

    st.subheader("Kontribusi per Kriteria (pemenang)")
    st.dataframe(df_c, use_container_width=True)

    fig = plt.figure()
    plt.bar(df_c["Kriteria"], df_c["Kontribusi"])
    plt.xticks(rotation=30, ha="right")
    plt.ylabel("Kontribusi ke Skor Akhir")
    plt.title(f"Kontribusi Skor — {winner}")
    st.pyplot(fig, clear_figure=True)

    st.divider()

    st.subheader("Rekomendasi jika budget naik +1.000.000")
    budget = st.number_input("Masukkan budget (Rp) saat ini", min_value=0, value=0, step=500000)

    if budget > 0 and "laptop_specs" in st.session_state:
        df = st.session_state.laptop_specs.copy()
        if "Harga_Rp" in df.columns:
            within_now = df[df["Harga_Rp"] <= budget]["Laptop"].tolist()
            within_plus = df[df["Harga_Rp"] <= (budget + 1_000_000)]["Laptop"].tolist()

            def best_in_list(lst):
                if not lst:
                    return None
                sub = df_rank[df_rank["Laptop"].isin(lst)]
                return sub.iloc[0]["Laptop"] if len(sub) else None

            best_now = best_in_list(within_now)
            best_plus = best_in_list(within_plus)

            st.write(f"- Best dalam budget sekarang: **{best_now or '-'}**")
            st.write(f"- Best kalau budget +1jt: **{best_plus or '-'}**")
            if best_now != best_plus and best_plus:
                st.success(f"Kalau budget naik +1jt, rekomendasi berubah menjadi **{best_plus}**.")
            else:
                st.info("Naik budget +1jt tidak mengubah rekomendasi utama (berdasarkan skor saat ini).")

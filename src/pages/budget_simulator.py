import pandas as pd
import streamlit as st
from src.hybrid_engine import calc_hybrid_scenario

def render_budget_simulator():
    st.title("💰 Simulator Budget")
    st.caption("Geser budget → lihat ranking berubah + rekomendasi best value.")

    df = st.session_state.get("specs_df")
    if df is None or df.empty:
        st.error("Data spesifikasi belum ada. Isi dulu di menu 🧾 Data Spesifikasi.")
        return

    if "Harga_Rp" not in df.columns:
        st.error("Kolom Harga_Rp belum ada di specs.")
        return

    scenario = st.session_state.active_scenario

    minp = int(pd.to_numeric(df["Harga_Rp"], errors="coerce").min())
    maxp = int(pd.to_numeric(df["Harga_Rp"], errors="coerce").max())
    budget = st.slider("Budget (Rp)", min_value=minp, max_value=maxp, value=min(minp+2_000_000, maxp), step=250_000)

    # Filter laptop yg masuk budget
    f = df[pd.to_numeric(df["Harga_Rp"], errors="coerce") <= budget].copy()
    if f.empty:
        st.warning("Tidak ada laptop yang masuk budget ini.")
        return

    # Update alts sementara (tanpa merusak state) → ranking pakai subset
    alts_all = st.session_state.alts
    alts_budget = f["Laptop"].astype(str).tolist()

    # Simpan backup
    backup_alts = st.session_state.alts
    st.session_state.alts = alts_budget

    try:
        res = calc_hybrid_scenario(scenario, use_hybrid=True)
        rank = pd.DataFrame({"Laptop": alts_budget, "Skor": res["scores"]}).sort_values("Skor", ascending=False)
        st.subheader("Ranking dalam budget")
        st.dataframe(rank, use_container_width=True)
        st.success(f"Juara untuk budget ini: **{rank.iloc[0]['Laptop']}**")

        st.subheader("Best value (Skor / Harga)")
        m = f.merge(rank, on="Laptop", how="left")
        m["ValueScore"] = m["Skor"] / m["Harga_Rp"]
        st.dataframe(m.sort_values("ValueScore", ascending=False)[["Laptop","Harga_Rp","Skor","ValueScore"]], use_container_width=True)

    finally:
        st.session_state.alts = backup_alts

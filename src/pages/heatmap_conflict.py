import streamlit as st
from src.compute import calc_scenario
from src.state import normalize_scenario_sizes
from src.ahp import plot_heatmap, inconsistency_pairs, sanitize_reciprocal


def render_heatmap_conflict():
    scenario = st.session_state.active_scenario
    normalize_scenario_sizes(scenario)

    st.title(f"🔥 Heatmap Matriks + Indikator Konflik (Scenario: {scenario})")

    criteria = st.session_state.criteria
    alts = st.session_state.alts
    res = calc_scenario(scenario)

    tab1, tab2 = st.tabs(["Kriteria", "Alternatif per Kriteria"])

    with tab1:
        st.subheader("Heatmap Matriks Kriteria")
        fig = plot_heatmap(res["Acrit"], criteria, "Heatmap Matriks Kriteria")
        st.pyplot(fig, clear_figure=True)

        st.subheader("Top Konflik Konsistensi (Kriteria)")
        df_conf = inconsistency_pairs(res["Acrit"], res["wcrit"], criteria, top_k=10)
        st.dataframe(df_conf, use_container_width=True)
        st.caption("Semakin besar ‘Konflik’, semakin pasangan itu bikin inputmu tidak konsisten. Coba perbaiki nilai A[i,j].")

    with tab2:
        chosen = st.selectbox("Pilih kriteria untuk dilihat heatmap alternatif:", criteria, key="heat_alt")
        A = sanitize_reciprocal(st.session_state.scenarios[scenario]["alt_matrices"][chosen])
        w = res["altW"][chosen]

        st.subheader(f"Heatmap Matriks Alternatif — {chosen}")
        fig2 = plot_heatmap(A, alts, f"Heatmap Alternatif ({chosen})")
        st.pyplot(fig2, clear_figure=True)

        st.subheader("Top Konflik Konsistensi (Alternatif)")
        df_conf2 = inconsistency_pairs(A, w, alts, top_k=10)
        st.dataframe(df_conf2, use_container_width=True)

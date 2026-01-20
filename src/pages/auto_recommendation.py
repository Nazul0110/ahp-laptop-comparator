import numpy as np
import pandas as pd
import streamlit as st

from src.hybrid_engine import apply_profile_weights, weights_to_consistent_matrix, calc_hybrid_scenario
from src.ahp_core import sanitize_reciprocal  # sesuaikan jika beda

def render_auto_recommendation():
    st.title("🤖 Rekomendasi Otomatis (Tanpa Pairwise)")
    st.caption("Jawab 5 pertanyaan → bobot kriteria otomatis → ranking langsung dari data spesifikasi (hybrid).")

    scenario = st.session_state.active_scenario
    criteria = st.session_state.criteria
    alts = st.session_state.alts

    left, right = st.columns([1, 1])

    with left:
        st.subheader("Wizard (5 pertanyaan)")
        usage = st.selectbox("Pemakaian utama", ["Kuliah", "Desain", "Gaming"], index=0)
        budget = st.number_input("Budget (Rp)", min_value=1_000_000, value=8_000_000, step=500_000)

        mobile = st.slider("Seberapa sering dibawa mobile?", 1, 5, 3)
        perf = st.slider("Seberapa butuh performa tinggi?", 1, 5, 3)
        battery = st.slider("Seberapa penting baterai?", 1, 5, 3)
        screen = st.slider("Seberapa penting layar bagus?", 1, 5, 3)

        if st.button("✨ Terapkan Bobot Otomatis ke Scenario", use_container_width=True):
            ans = {
                "usage": usage,
                "budget": int(budget),
                "mobile": int(mobile),
                "performance": int(perf),
                "battery": int(battery),
                "screen": int(screen),
            }
            wmap = apply_profile_weights(ans)
            wvec = np.array([wmap[c] for c in criteria], dtype=float)
            Acrit = weights_to_consistent_matrix(wvec)

            scen = st.session_state.scenarios[scenario]
            scen["crit_matrix"] = sanitize_reciprocal(Acrit)
            st.session_state.scenarios[scenario] = scen

            st.success("Bobot kriteria otomatis diterapkan ✅ (criteria matrix dibuat konsisten).")

    with right:
        st.subheader("Hasil otomatis (Hybrid)")
        res = calc_hybrid_scenario(scenario, use_hybrid=True)
        df = pd.DataFrame({"Laptop": alts, "Skor": res["scores"]}).sort_values("Skor", ascending=False)
        st.dataframe(df, use_container_width=True)

        st.info("""
Logika:
- Bobot kriteria otomatis dari wizard (tanpa pairwise).
- Alternatif dihitung dari data spesifikasi (objektif), dan AHP hanya dipakai untuk kriteria subjektif (kalau ada).
""")

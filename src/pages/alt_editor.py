import pandas as pd
import streamlit as st

from src.compute import calc_scenario
from src.matrix_ui import matrix_editor_upper
from src.state import normalize_scenario_sizes
from src.ahp import fmt_pct


def render_alt_editor():
    scenario = st.session_state.active_scenario
    normalize_scenario_sizes(scenario)

    st.title(f"💻 Alternatif per Kriteria — Matrix Editor (Scenario: {scenario})")

    criteria = st.session_state.criteria
    alts = st.session_state.alts
    scen = st.session_state.scenarios[scenario]

    chosen = st.selectbox("Pilih kriteria:", criteria)
    left, right = st.columns([1.2, 1])

    with left:
        st.subheader(f"Input Matriks Alternatif (Kriteria: {chosen})")
        Anew = matrix_editor_upper(
            alts,
            scen["alt_matrices"][chosen],
            key=f"alt_editor_{scenario}_{chosen}",
            help_text="Edit segitiga atas saja. Reciprocal otomatis. Diagonal otomatis 1."
        )
        scen["alt_matrices"][chosen] = Anew
        st.session_state.scenarios[scenario] = scen

    with right:
        res = calc_scenario(scenario)
        w = res["altW"][chosen]
        lam, ci, cr = res["altCR"][chosen]

        st.subheader("Bobot Alternatif & Konsistensi")
        dfw = pd.DataFrame({"Laptop": alts, "Bobot": w})
        dfw["Bobot(%)"] = dfw["Bobot"].apply(fmt_pct)
        st.dataframe(dfw.sort_values("Bobot", ascending=False), use_container_width=True)

        c1, c2, c3 = st.columns(3)
        c1.metric("λmax", f"{lam:.4f}")
        c2.metric("CI", f"{ci:.4f}")
        c3.metric("CR", f"{cr:.4f}")

        thr = float(st.session_state.get("cr_threshold", 0.10))
        if cr <= thr:
            st.success(f"Konsistensi OK ✅ (CR={cr:.4f} ≤ {thr:.2f})")
        else:
            st.error(f"Konsistensi jelek ❌ (CR={cr:.4f} > {thr:.2f})")

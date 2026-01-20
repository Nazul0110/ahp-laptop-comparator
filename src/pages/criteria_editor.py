import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st

from src.compute import calc_scenario
from src.matrix_ui import matrix_editor_upper
from src.state import normalize_scenario_sizes
from src.ahp import fmt_pct


def render_criteria_editor():
    scenario = st.session_state.active_scenario
    normalize_scenario_sizes(scenario)

    st.title(f"📌 Kriteria — Matrix Editor (Scenario: {scenario})")

    criteria = st.session_state.criteria
    scen = st.session_state.scenarios[scenario]

    left, right = st.columns([1.2, 1])

    with left:
        st.subheader("Input Matriks Kriteria (edit upper triangle)")
        Anew = matrix_editor_upper(
            criteria,
            scen["crit_matrix"],
            key=f"crit_editor_{scenario}",
            help_text="Edit hanya segitiga atas (kanan atas). Bagian bawah otomatis reciprocal. Diagonal otomatis 1."
        )
        scen["crit_matrix"] = Anew
        st.session_state.scenarios[scenario] = scen

    with right:
        res = calc_scenario(scenario)
        lam, ci, cr = res["crit_cons"]

        st.subheader("Bobot & Konsistensi")
        dfw = pd.DataFrame({"Kriteria": criteria, "Bobot": res["wcrit"]})
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

        fig = plt.figure()
        plt.bar(dfw["Kriteria"], dfw["Bobot"])
        plt.xticks(rotation=30, ha="right")
        plt.ylabel("Bobot")
        plt.title("Bobot Kriteria")
        st.pyplot(fig, clear_figure=True)

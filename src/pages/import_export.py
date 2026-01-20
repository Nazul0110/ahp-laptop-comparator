import json
import numpy as np
import streamlit as st

from src.state import normalize_scenario_sizes


def render_import_export():
    st.title("📦 Import / Export (Project + Semua Scenario)")

    # Export
    export_obj = {
        "criteria": st.session_state.criteria,
        "alts": st.session_state.alts,
        "active_scenario": st.session_state.active_scenario,
        "scenarios": {}
    }

    for s, val in st.session_state.scenarios.items():
        export_obj["scenarios"][s] = {
            "crit_matrix": np.array(val["crit_matrix"], dtype=float).tolist(),
            "alt_matrices": {k: np.array(v, dtype=float).tolist() for k, v in val["alt_matrices"].items()}
        }

    data = json.dumps(export_obj, indent=2).encode("utf-8")
    st.download_button(
        "⬇️ Download Project JSON",
        data=data,
        file_name="ahp_project_full.json",
        mime="application/json",
        use_container_width=True
    )

    st.divider()
    st.subheader("Import Project JSON")
    up = st.file_uploader("Upload ahp_project_full.json", type=["json"])

    if up is not None:
        try:
            loaded = json.loads(up.read().decode("utf-8"))

            st.session_state.criteria = list(loaded["criteria"])
            st.session_state.alts = list(loaded["alts"])

            st.session_state.scenarios = {}
            for s, val in loaded["scenarios"].items():
                st.session_state.scenarios[s] = {
                    "crit_matrix": np.array(val["crit_matrix"], dtype=float),
                    "alt_matrices": {k: np.array(v, dtype=float) for k, v in val["alt_matrices"].items()}
                }
                normalize_scenario_sizes(s)

            st.session_state.active_scenario = loaded.get("active_scenario", list(st.session_state.scenarios.keys())[0])
            if st.session_state.active_scenario not in st.session_state.scenarios:
                st.session_state.active_scenario = list(st.session_state.scenarios.keys())[0]

            st.success("Import berhasil.")
            st.rerun()

        except Exception as e:
            st.error(f"Gagal import: {e}")

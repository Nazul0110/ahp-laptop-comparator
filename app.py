import streamlit as st

from src.styles import inject_sidebar_css, sidebar_header
from src.state import ensure_state
from src.specs_state import ensure_specs_state

# ✅ criteria metadata (benefit/cost, normalisasi, subjective/objective)
from src.criteria_meta import ensure_criteria_meta


# -------------------------
# Safe import helper (biar app nggak error kalau page belum ada)
# -------------------------
def safe_import(path: str, func_name: str):
    """
    path: "src.pages.home"
    func_name: "render_home"
    Return callable. Jika gagal import, return fallback function.
    """
    try:
        mod = __import__(path, fromlist=[func_name])
        fn = getattr(mod, func_name)
        return fn
    except Exception as e:
        def _fallback():
            st.error(f"Page belum tersedia: `{path}.{func_name}`")
            st.code(str(e))
            st.info("Pastikan file & fungsi-nya sudah dibuat sesuai import.")
        return _fallback


# -------------------------
# Pages (existing)
# -------------------------
render_home = safe_import("src.pages.home", "render_home")
render_methodology = safe_import("src.pages.methodology", "render_methodology")
render_setup = safe_import("src.pages.setup", "render_setup")
render_data_specs = safe_import("src.pages.data_specs", "render_data_specs")
render_quick_input = safe_import("src.pages.quick_input", "render_quick_input")
render_criteria_editor = safe_import("src.pages.criteria_editor", "render_criteria_editor")
render_alt_editor = safe_import("src.pages.alt_editor", "render_alt_editor")
render_heatmap_conflict = safe_import("src.pages.heatmap_conflict", "render_heatmap_conflict")
render_results_compare = safe_import("src.pages.results_compare", "render_results_compare")
render_report_pdf = safe_import("src.pages.report_pdf", "render_report_pdf")
render_import_export = safe_import("src.pages.import_export", "render_import_export")

# -------------------------
# ✅ NEW pages (upgrades)
# -------------------------
render_profile_wizard = safe_import("src.pages.profile_wizard", "render_profile_wizard")
render_focus_top3 = safe_import("src.pages.focus_top3", "render_focus_top3")
render_criteria_meta_page = safe_import("src.pages.criteria_meta_page", "render_criteria_meta_page")
render_explainability = safe_import("src.pages.explainability", "render_explainability")
render_sensitivity = safe_import("src.pages.sensitivity", "render_sensitivity")


# -------------------------
# Page config
# -------------------------
st.set_page_config(page_title="AHP Laptop Comparator Pro", layout="wide")
inject_sidebar_css()

# -------------------------
# state init
# -------------------------
ensure_state()
ensure_specs_state()
ensure_criteria_meta()


# -------------------------
# Sidebar header
# -------------------------
sidebar_header()

# -------------------------
# Scenario select
# -------------------------
scenario_names = list(st.session_state.scenarios.keys())
if not scenario_names:
    st.session_state.scenarios = {}
    st.error("Tidak ada scenario. Pastikan ensure_state() membuat default scenario.")
    st.stop()

# Kalau active_scenario tidak ada di list, fallback ke first
if st.session_state.active_scenario not in scenario_names:
    st.session_state.active_scenario = scenario_names[0]

active_index = scenario_names.index(st.session_state.active_scenario)
active = st.sidebar.selectbox("Scenario aktif", scenario_names, index=active_index)
st.session_state.active_scenario = active
st.sidebar.caption("Tiap scenario punya matriks AHP sendiri (bobot bisa beda).")

# -------------------------
# Scenario actions
# -------------------------
colS1, colS2 = st.sidebar.columns(2)
if colS1.button("➕ Add", use_container_width=True):
    from src.state import add_scenario
    add_scenario()
    st.rerun()

if colS2.button("🗑️ Del", use_container_width=True, disabled=len(scenario_names) <= 1):
    from src.state import delete_active_scenario
    delete_active_scenario()
    st.rerun()

colS3, colS4 = st.sidebar.columns(2)
if colS3.button("📋 Copy", use_container_width=True):
    from src.state import copy_active_scenario
    copy_active_scenario()
    st.rerun()

if colS4.button("🔄 Reset", use_container_width=True):
    from src.state import reset_active_scenario
    reset_active_scenario()
    st.rerun()

st.sidebar.divider()


# -------------------------
# Menu
# -------------------------
page = st.sidebar.radio(
    "Menu",
    [
        "🏠 Home",
        "📚 Metodologi",

        # ✅ NEW: cepat tanpa pairwise manual
        "🧭 Profil Pengguna (Wizard Bobot 1 Klik)",
        "🎯 Fokus Top-3 Kriteria (Hemat Input)",

        "⚙️ Setup",
        "🧾 Data Spesifikasi + Auto Pairwise",

        # ✅ NEW: meta kriteria
        "⚙️ Setting Kriteria (Benefit/Cost & Normalisasi)",

        "⚡ Quick Input (Sliders)",
        "📌 Kriteria (Matrix Editor)",
        "💻 Alternatif per Kriteria (Matrix Editor)",
        "🔥 Heatmap & Konflik",
        "📊 Hasil & Compare Scenario",

        # ✅ NEW: explainability + sensitivity
        "💡 Why This Laptop Wins (Explainability)",
        "🧪 Sensitivity Analysis (Stabilitas Ranking)",

        "📄 Report PDF",
        "📦 Import/Export",
    ],
    index=0
)

# CR threshold control
st.session_state.cr_threshold = st.sidebar.slider("Batas CR", 0.01, 0.30, 0.10, 0.01)
st.sidebar.caption("CR ≤ 0.10 biasanya dianggap konsisten.")


# -------------------------
# Routing pages
# -------------------------
if page == "🏠 Home":
    render_home()

elif page == "📚 Metodologi":
    render_methodology()

elif page == "🧭 Profil Pengguna (Wizard Bobot 1 Klik)":
    render_profile_wizard()

elif page == "🎯 Fokus Top-3 Kriteria (Hemat Input)":
    render_focus_top3()

elif page == "⚙️ Setup":
    render_setup()

elif page == "🧾 Data Spesifikasi + Auto Pairwise":
    render_data_specs()

elif page == "⚙️ Setting Kriteria (Benefit/Cost & Normalisasi)":
    render_criteria_meta_page()

elif page == "⚡ Quick Input (Sliders)":
    render_quick_input()

elif page == "📌 Kriteria (Matrix Editor)":
    render_criteria_editor()

elif page == "💻 Alternatif per Kriteria (Matrix Editor)":
    render_alt_editor()

elif page == "🔥 Heatmap & Konflik":
    render_heatmap_conflict()

elif page == "📊 Hasil & Compare Scenario":
    render_results_compare()

elif page == "💡 Why This Laptop Wins (Explainability)":
    render_explainability()

elif page == "🧪 Sensitivity Analysis (Stabilitas Ranking)":
    render_sensitivity()

elif page == "📄 Report PDF":
    render_report_pdf()

elif page == "📦 Import/Export":
    render_import_export()

import streamlit as st
from src.config import DEFAULT_CRITERIA, DEFAULT_ALTS, LAPTOP_PRESET_LENGKAP
from src.state import reset_scenario, normalize_scenario_sizes


def _reset_all_scenarios():
    for s in list(st.session_state.scenarios.keys()):
        reset_scenario(s)
        normalize_scenario_sizes(s)


def render_setup():
    st.title("⚙️ Setup: Kriteria & Alternatif (Shared untuk semua Scenario)")
    st.caption("Kalau kriteria/alternatif berubah, matriks semua scenario akan di-reset agar ukurannya aman.")

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Kriteria")
        txt = st.text_input("Tambah kriteria", "")
        if st.button("➕ Tambah Kriteria"):
            if txt.strip():
                st.session_state.criteria.append(txt.strip())
                _reset_all_scenarios()
                st.rerun()

        for i, c in enumerate(list(st.session_state.criteria)):
            row = st.columns([6, 1, 1])
            row[0].write(f"{i+1}. {c}")

            if row[1].button("⬆️", key=f"cup_{i}", disabled=(i == 0)):
                st.session_state.criteria[i-1], st.session_state.criteria[i] = st.session_state.criteria[i], st.session_state.criteria[i-1]
                _reset_all_scenarios()
                st.rerun()

            if row[2].button("🗑️", key=f"cdel_{i}", disabled=len(st.session_state.criteria) <= 2):
                st.session_state.criteria.pop(i)
                _reset_all_scenarios()
                st.rerun()

    with col2:
        st.subheader("Alternatif Laptop")
        txt2 = st.text_input("Tambah alternatif (contoh: ASUS Vivobook 14)", "")
        if st.button("➕ Tambah Alternatif"):
            if txt2.strip():
                st.session_state.alts.append(txt2.strip())
                _reset_all_scenarios()
                st.rerun()

        for i, a in enumerate(list(st.session_state.alts)):
            row = st.columns([6, 1, 1])
            row[0].write(f"{i+1}. {a}")

            if row[1].button("⬆️", key=f"aup_{i}", disabled=(i == 0)):
                st.session_state.alts[i-1], st.session_state.alts[i] = st.session_state.alts[i], st.session_state.alts[i-1]
                _reset_all_scenarios()
                st.rerun()

            if row[2].button("🗑️", key=f"adel_{i}", disabled=len(st.session_state.alts) <= 2):
                st.session_state.alts.pop(i)
                _reset_all_scenarios()
                st.rerun()

    st.divider()
    st.subheader("Preset cepat (opsional)")
    cA, cB, cC, cD = st.columns(4)

    if cA.button("Preset Umum", use_container_width=True):
        st.session_state.criteria = DEFAULT_CRITERIA.copy()
        st.session_state.alts = DEFAULT_ALTS.copy()
        _reset_all_scenarios()
        st.rerun()

    if cB.button("Preset Gaming", use_container_width=True):
        st.session_state.criteria = ["Harga", "Performa", "Cooling", "Layar", "Upgradeability", "Garansi"]
        st.session_state.alts = ["ASUS TUF A15", "Acer Nitro 5", "Lenovo Legion 5", "MSI Katana 15"]
        _reset_all_scenarios()
        st.rerun()

    if cC.button("Preset Ultrabook", use_container_width=True):
        st.session_state.criteria = ["Harga", "Baterai", "Berat", "Layar", "Build Quality", "Garansi"]
        st.session_state.alts = ["ASUS Zenbook 14", "Acer Swift 3", "Samsung Galaxy Book 4", "Dell Inspiron 14"]
        _reset_all_scenarios()
        st.rerun()

    if cD.button("Preset Laptop Lengkap", use_container_width=True):
        st.session_state.criteria = DEFAULT_CRITERIA.copy()
        st.session_state.alts = LAPTOP_PRESET_LENGKAP.copy()
        _reset_all_scenarios()
        st.rerun()

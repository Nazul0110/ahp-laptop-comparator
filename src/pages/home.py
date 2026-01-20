import streamlit as st
from src.compute import calc_scenario


def render_home():
    st.title("AHP Laptop Comparator PRO")
    st.write("""
Versi PRO ini punya:
- ✅ input matriks tabel (data_editor) + auto reciprocal
- ✅ heatmap matriks + deteksi konflik konsistensi
- ✅ multi-skenario (Mahasiswa/Desainer/Gamer + custom)
- ✅ report PDF otomatis (hasil + grafik + CR)
- ✅ import/export project (JSON)
""")

    res = calc_scenario(st.session_state.active_scenario)
    lam, ci, cr = res["crit_cons"]

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Scenario", st.session_state.active_scenario)
    c2.metric("Kriteria", len(st.session_state.criteria))
    c3.metric("Alternatif", len(st.session_state.alts))
    c4.metric("CR Kriteria", f"{cr:.4f}")

    st.info("Mulai dari **⚙️ Setup** kalau mau ganti kriteria/alternatif. Lalu isi matriks di menu Kriteria/Alternatif.")

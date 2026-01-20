import streamlit as st
import pandas as pd

from src.criteria_meta import ensure_criteria_meta, ALLOWED_METHOD, ALLOWED_TYPE

def render_criteria_meta_page():
    st.title("⚙️ Setting Kriteria: Benefit/Cost, Normalisasi, Subjective/Objective")

    ensure_criteria_meta()
    criteria = st.session_state.criteria
    meta = st.session_state.criteria_meta

    rows = []
    for c in criteria:
        m = meta[c]
        rows.append({
            "Kriteria": c,
            "Type": m.get("type"),
            "Method": m.get("method"),
            "Subjective(AHP?)": bool(m.get("subjective", True)),
            "Spec Column": m.get("spec_col", "")
        })

    df = pd.DataFrame(rows)

    df2 = st.data_editor(
        df,
        use_container_width=True,
        num_rows="fixed",
        column_config={
            "Kriteria": st.column_config.TextColumn(disabled=True),
            "Type": st.column_config.SelectboxColumn(options=ALLOWED_TYPE),
            "Method": st.column_config.SelectboxColumn(options=ALLOWED_METHOD),
            "Subjective(AHP?)": st.column_config.CheckboxColumn(help="True = pakai pairwise AHP. False = pakai data spesifikasi."),
            "Spec Column": st.column_config.TextColumn(help="Nama kolom di tabel spesifikasi (misal Harga_Rp, CPU_Score, RAM_GB, SSD_GB, Baterai_Wh, Berat_Kg, Garansi_Th)."),
        }
    )

    if st.button("💾 Simpan Setting", use_container_width=True):
        new_meta = {}
        for _, r in df2.iterrows():
            c = r["Kriteria"]
            new_meta[c] = {
                "type": r["Type"],
                "method": r["Method"],
                "subjective": bool(r["Subjective(AHP?)"]),
                "spec_col": (r["Spec Column"] if str(r["Spec Column"]).strip() else None),
            }
        st.session_state.criteria_meta = new_meta
        st.success("Setting kriteria disimpan.")

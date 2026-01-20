import streamlit as st
import pandas as pd

from src.specs_state import ensure_specs_state, SPEC_COLUMNS
from src.auto_pairwise import auto_fill_alt_matrices, build_criteria_matrix_from_template
from src.state import normalize_scenario_sizes


def render_data_specs():
    st.title("🧾 Data Spesifikasi Laptop + Auto Pairwise")

    ensure_specs_state()
    scenario = st.session_state.active_scenario
    normalize_scenario_sizes(scenario)

    st.caption("Isi data spesifikasi laptop → kamu bisa filter & compare, lalu otomatis generate matriks AHP dari data.")

    # ------------------------
    # Editor spesifikasi
    # ------------------------
    st.subheader("1) Tabel Spesifikasi Laptop")
    df = st.session_state.laptop_specs.copy()

    # Editor
    df_edit = st.data_editor(
        df,
        use_container_width=True,
        num_rows="fixed",
        key="specs_editor",
        column_config={
            "Laptop": st.column_config.TextColumn(disabled=True),
            "Harga_Rp": st.column_config.NumberColumn(format="%.0f"),
            "CPU_Score": st.column_config.NumberColumn(help="Bisa pakai score benchmark (Cinebench/Passmark)"),
            "RAM_GB": st.column_config.NumberColumn(format="%.0f"),
            "SSD_GB": st.column_config.NumberColumn(format="%.0f"),
            "Baterai_Wh": st.column_config.NumberColumn(help="Wh (lebih besar umumnya lebih awet)"),
            "Berat_Kg": st.column_config.NumberColumn(format="%.2f"),
            "Layar_Inch": st.column_config.NumberColumn(format="%.1f"),
            "Refresh_Hz": st.column_config.NumberColumn(format="%.0f"),
            "Color_Gamut": st.column_config.NumberColumn(help="contoh 45 / 72 / 100"),
            "Garansi_Th": st.column_config.NumberColumn(format="%.0f"),
        }
    )
    st.session_state.laptop_specs = df_edit

    st.divider()

    # ------------------------
    # Filter + Compare
    # ------------------------
    st.subheader("2) Filter & Compare")

    c1, c2, c3, c4 = st.columns(4)
    budget = c1.number_input("Budget max (Rp)", min_value=0, value=0, step=1000000)
    min_ram = c2.number_input("Min RAM (GB)", min_value=0, value=0, step=4)
    min_ssd = c3.number_input("Min SSD (GB)", min_value=0, value=0, step=128)
    max_w = c4.number_input("Max berat (Kg)", min_value=0.0, value=0.0, step=0.1)

    c5, c6, c7 = st.columns(3)
    min_batt = c5.number_input("Min baterai (Wh)", min_value=0.0, value=0.0, step=5.0)
    min_cpu = c6.number_input("Min CPU score", min_value=0.0, value=0.0, step=100.0)
    min_gar = c7.number_input("Min garansi (th)", min_value=0.0, value=0.0, step=1.0)

    f = df_edit.copy()

    if budget > 0:
        f = f[(f["Harga_Rp"] > 0) & (f["Harga_Rp"] <= budget)]
    if min_ram > 0:
        f = f[f["RAM_GB"] >= min_ram]
    if min_ssd > 0:
        f = f[f["SSD_GB"] >= min_ssd]
    if max_w > 0:
        f = f[(f["Berat_Kg"] > 0) & (f["Berat_Kg"] <= max_w)]
    if min_batt > 0:
        f = f[f["Baterai_Wh"] >= min_batt]
    if min_cpu > 0:
        f = f[f["CPU_Score"] >= min_cpu]
    if min_gar > 0:
        f = f[f["Garansi_Th"] >= min_gar]

    st.write("**Hasil filter:**")
    st.dataframe(f, use_container_width=True)

    # kartu compare
    st.subheader("Kartu Perbandingan (Side-by-side)")
    default_pick = f["Laptop"].tolist()[:3] if len(f) else st.session_state.alts[:3]
    pick = st.multiselect("Pilih laptop untuk dibandingkan", st.session_state.alts, default=default_pick)

    cards = df_edit[df_edit["Laptop"].isin(pick)].copy()

    if len(cards) == 0:
        st.info("Pilih minimal 1 laptop untuk ditampilkan kartunya.")
    else:
        cols = st.columns(min(4, len(cards)))
        for i, (_, row) in enumerate(cards.iterrows()):
            with cols[i % len(cols)]:
                st.markdown(f"### 💻 {row['Laptop']}")
                st.metric("Harga (Rp)", f"{int(row['Harga_Rp']):,}".replace(",", ".") if row["Harga_Rp"] else "-")
                st.metric("CPU Score", f"{row['CPU_Score']:.0f}" if row["CPU_Score"] else "-")
                st.metric("RAM (GB)", f"{row['RAM_GB']:.0f}" if row["RAM_GB"] else "-")
                st.metric("SSD (GB)", f"{row['SSD_GB']:.0f}" if row["SSD_GB"] else "-")
                st.metric("Baterai (Wh)", f"{row['Baterai_Wh']:.0f}" if row["Baterai_Wh"] else "-")
                st.metric("Berat (Kg)", f"{row['Berat_Kg']:.2f}" if row["Berat_Kg"] else "-")
                st.caption(f"Layar: {row['Layar_Inch']} inch | {row['Refresh_Hz']} Hz | Gamut {row['Color_Gamut']}%")
                st.caption(f"Garansi: {row['Garansi_Th']} tahun")

    st.divider()

    # ------------------------
    # Auto-generate matriks
    # ------------------------
    st.subheader("3) Auto-generate Pairwise dari Data")
    st.warning("Ini akan mengisi otomatis matriks alternatif per kriteria (dan opsional matriks kriteria dari template).")

    cA, cB = st.columns(2)
    apply_template = cA.checkbox("Set matriks Kriteria dari Template scenario", value=True)
    apply_alts = cB.checkbox("Set matriks Alternatif dari Data spesifikasi", value=True)

    if st.button("⚙️ Generate & Terapkan ke Scenario Aktif", use_container_width=True):
        scen = st.session_state.scenarios[scenario]
        criteria = st.session_state.criteria
        alts = st.session_state.alts

        if apply_template:
            scen["crit_matrix"] = build_criteria_matrix_from_template(criteria, scenario)

        if apply_alts:
            alt_mats = auto_fill_alt_matrices(criteria, alts, df_edit)
            for c in criteria:
                scen["alt_matrices"][c] = alt_mats[c]

        st.session_state.scenarios[scenario] = scen
        normalize_scenario_sizes(scenario)
        st.success("Berhasil! Matriks sudah terisi otomatis. Sekarang kamu bisa fine-tune di menu Matrix Editor / Quick Input.")

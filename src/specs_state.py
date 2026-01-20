import pandas as pd
import streamlit as st

SPEC_COLUMNS = [
    "Laptop",
    "Harga_Rp",
    "CPU_Score",
    "RAM_GB",
    "SSD_GB",
    "Baterai_Wh",
    "Berat_Kg",
    "Layar_Inch",
    "Refresh_Hz",
    "Color_Gamut",   # contoh: 45, 72, 100
    "Garansi_Th",
]

def ensure_specs_state():
    """Pastikan st.session_state.laptop_specs selalu ada dan sinkron dengan daftar alternatif."""
    alts = st.session_state.get("alts", [])
    if "laptop_specs" not in st.session_state:
        df = pd.DataFrame(columns=SPEC_COLUMNS)
        df["Laptop"] = alts
        # isi default supaya tidak NaN berantakan
        for c in SPEC_COLUMNS:
            if c != "Laptop":
                df[c] = 0
        st.session_state.laptop_specs = df
        return

    df = st.session_state.laptop_specs.copy()

    # Pastikan kolom ada semua
    for c in SPEC_COLUMNS:
        if c not in df.columns:
            df[c] = 0

    # Sync row: hapus yang tidak ada di alts, tambahkan yang baru
    df = df[df["Laptop"].isin(alts)].copy()

    missing = [a for a in alts if a not in df["Laptop"].tolist()]
    if missing:
        add = pd.DataFrame({"Laptop": missing})
        for c in SPEC_COLUMNS:
            if c != "Laptop":
                add[c] = 0
        df = pd.concat([df, add], ignore_index=True)

    # urutkan sesuai alts
    df["__ord"] = df["Laptop"].apply(lambda x: alts.index(x) if x in alts else 9999)
    df = df.sort_values("__ord").drop(columns=["__ord"]).reset_index(drop=True)

    st.session_state.laptop_specs = df

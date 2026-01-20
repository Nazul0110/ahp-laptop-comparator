import numpy as np
import streamlit as st

# Default meta untuk kriteria umum AHP laptop
DEFAULT_META = {
    "Harga":         {"type": "cost",    "method": "minmax",     "subjective": False, "spec_col": "Harga_Rp"},
    "Performa":      {"type": "benefit", "method": "minmax",     "subjective": False, "spec_col": "CPU_Score"},
    "Baterai":       {"type": "benefit", "method": "minmax",     "subjective": False, "spec_col": "Baterai_Wh"},
    "Portabilitas":  {"type": "cost",    "method": "minmax",     "subjective": False, "spec_col": "Berat_Kg"},
    "Layar":         {"type": "benefit", "method": "minmax",     "subjective": True,  "spec_col": None},
    "Garansi":       {"type": "benefit", "method": "minmax",     "subjective": False, "spec_col": "Garansi_Th"},
}

ALLOWED_TYPE = ["benefit", "cost"]
ALLOWED_METHOD = ["minmax", "zscore", "logminmax"]

def ensure_criteria_meta():
    """
    Pastikan st.session_state.criteria_meta ada dan sinkron dengan st.session_state.criteria.
    Dipanggil di app.py setelah ensure_state().
    """
    criteria = st.session_state.get("criteria", [])

    if "criteria_meta" not in st.session_state or not isinstance(st.session_state.criteria_meta, dict):
        st.session_state.criteria_meta = {}

    meta = dict(st.session_state.criteria_meta)

    # Tambah meta default untuk kriteria baru
    for c in criteria:
        if c not in meta:
            base = DEFAULT_META.get(c, {"type": "benefit", "method": "minmax", "subjective": True, "spec_col": None})
            meta[c] = dict(base)

        # sanitasi
        if meta[c].get("type") not in ALLOWED_TYPE:
            meta[c]["type"] = "benefit"
        if meta[c].get("method") not in ALLOWED_METHOD:
            meta[c]["method"] = "minmax"
        if "subjective" not in meta[c]:
            meta[c]["subjective"] = True
        if "spec_col" not in meta[c]:
            meta[c]["spec_col"] = None

    # Hapus meta yg kriteria-nya sudah dihapus
    for k in list(meta.keys()):
        if k not in criteria:
            del meta[k]

    st.session_state.criteria_meta = meta


def normalize_values(values: np.ndarray, ctype: str, method: str) -> np.ndarray:
    """
    Normalisasi ke skor 0..1 (semakin besar semakin baik).
    - benefit: besar lebih baik
    - cost: kecil lebih baik (dibalik)
    """
    x = np.array(values, dtype=float)
    x = np.where(np.isfinite(x), x, np.nan)

    if np.all(np.isnan(x)):
        return np.zeros_like(x, dtype=float)

    # isi NaN dengan median
    med = np.nanmedian(x)
    x = np.where(np.isnan(x), med, x)

    if method == "zscore":
        mu = x.mean()
        sd = x.std() if x.std() > 1e-12 else 1.0
        z = (x - mu) / sd
        s = 1 / (1 + np.exp(-z))   # mapping ~0..1
    elif method == "logminmax":
        x2 = np.log1p(np.maximum(x, 0))
        mn, mx = x2.min(), x2.max()
        s = (x2 - mn) / (mx - mn) if (mx - mn) > 1e-12 else np.ones_like(x2)
    else:  # minmax
        mn, mx = x.min(), x.max()
        s = (x - mn) / (mx - mn) if (mx - mn) > 1e-12 else np.ones_like(x)

    if ctype == "cost":
        s = 1 - s

    return np.clip(s, 0, 1)

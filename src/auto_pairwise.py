import math
import numpy as np
import pandas as pd

from src.ahp import sanitize_reciprocal

def _safe_float(x, default=0.0):
    try:
        v = float(x)
        if math.isnan(v) or math.isinf(v):
            return default
        return v
    except Exception:
        return default

def ratio_to_saaty(r: float) -> float:
    """
    Convert ratio >=1 into Saaty 1..9 (float), smooth mapping.
    r=1 -> 1
    bigger r -> closer to 9
    """
    r = max(r, 1e-12)
    if r < 1:
        r = 1 / r
    # log mapping -> 1..9
    s = 1 + 4 * math.log10(r)  # r=10 => s≈5, r=100 => s≈9
    s = max(1.0, min(9.0, s))
    return s

def build_pairwise_from_values(values: list[float], mode: str) -> np.ndarray:
    """
    mode: 'benefit' (bigger better) or 'cost' (smaller better)
    """
    n = len(values)
    A = np.ones((n, n), dtype=float)
    for i in range(n):
        for j in range(i+1, n):
            vi = max(_safe_float(values[i], 0.0), 1e-12)
            vj = max(_safe_float(values[j], 0.0), 1e-12)

            if mode == "benefit":
                r = vi / vj
            else:  # cost
                r = vj / vi  # smaller cost => preferred => bigger a_ij
            s = ratio_to_saaty(r)

            # arah: jika r>=1 => i lebih baik dari j => A[i,j]=s
            # jika r<1 => i lebih buruk => A[i,j]=1/s
            if (mode == "benefit" and vi >= vj) or (mode == "cost" and vi <= vj):
                A[i, j] = s
                A[j, i] = 1 / s
            else:
                A[i, j] = 1 / s
                A[j, i] = s
    return sanitize_reciprocal(A)

def auto_fill_alt_matrices(criteria: list[str], alts: list[str], specs_df: pd.DataFrame):
    """
    Menghasilkan dict {criterion: A_matrix} untuk alternatif berdasarkan specs.
    Kriteria yang tidak ada mapping akan dilewati (matrix=ones).
    """
    # mapping kriteria -> (kolom specs, benefit/cost)
    mapping = {
        "Harga": ("Harga_Rp", "cost"),
        "Performa": ("CPU_Score", "benefit"),
        "Baterai": ("Baterai_Wh", "benefit"),
        "Portabilitas": ("Berat_Kg", "cost"),
        "Layar": ("LayarScore", "benefit"),  # kita buat dari kombinasi
        "Garansi": ("Garansi_Th", "benefit"),
    }

    df = specs_df.copy()

    # Buat skor layar gabungan sederhana (boleh kamu ubah)
    # layar score = inch * (1 + refresh/240) * (1 + color_gamut/100)
    def layar_score(row):
        inch = max(_safe_float(row.get("Layar_Inch", 0)), 0)
        hz = max(_safe_float(row.get("Refresh_Hz", 0)), 0)
        cg = max(_safe_float(row.get("Color_Gamut", 0)), 0)
        return inch * (1 + hz / 240.0) * (1 + cg / 100.0)

    df["LayarScore"] = df.apply(layar_score, axis=1)

    # Urutkan sesuai alts
    df = df.set_index("Laptop").reindex(alts).reset_index()

    m = len(alts)
    out = {}
    for c in criteria:
        if c in mapping:
            col, mode = mapping[c]
            vals = df[col].tolist() if col in df.columns else [1]*m
            out[c] = build_pairwise_from_values(vals, mode)
        else:
            out[c] = np.ones((m, m), dtype=float)
    return out

def build_criteria_matrix_from_template(criteria: list[str], scenario: str) -> np.ndarray:
    """
    Template bobot kriteria per scenario → jadi matriks pairwise kriteria.
    Jika ada kriteria baru, bobotnya otomatis kecil.
    """
    # bobot template (jumlah tidak harus 1, nanti dinormalisasi)
    templates = {
        "Mahasiswa": {
            "Harga": 0.30, "Baterai": 0.22, "Portabilitas": 0.18,
            "Performa": 0.15, "Layar": 0.10, "Garansi": 0.05
        },
        "Desainer": {
            "Layar": 0.30, "Performa": 0.25, "Portabilitas": 0.15,
            "Baterai": 0.12, "Garansi": 0.10, "Harga": 0.08
        },
        "Gamer": {
            "Performa": 0.35, "Layar": 0.20, "Garansi": 0.15,
            "Harga": 0.12, "Baterai": 0.10, "Portabilitas": 0.08
        }
    }

    base = templates.get(scenario, templates["Mahasiswa"])

    w = []
    for c in criteria:
        w.append(float(base.get(c, 0.03)))  # kriteria baru dikasih bobot kecil
    w = np.array(w, dtype=float)
    s = w.sum()
    if s <= 0:
        w = np.ones(len(criteria)) / len(criteria)
    else:
        w = w / s

    # matriks Aij ~ wi/wj lalu dipetakan ke skala saaty 1..9
    n = len(criteria)
    A = np.ones((n, n), dtype=float)
    for i in range(n):
        for j in range(i+1, n):
            r = w[i] / max(w[j], 1e-12)
            s_ij = ratio_to_saaty(r)
            if w[i] >= w[j]:
                A[i, j] = s_ij
                A[j, i] = 1 / s_ij
            else:
                A[i, j] = 1 / s_ij
                A[j, i] = s_ij

    return sanitize_reciprocal(A)

import numpy as np
import pandas as pd
import streamlit as st

from src.criteria_meta import normalize_values
from src.ahp_core import ahp_weights, ahp_consistency, sanitize_reciprocal, inconsistency_pairs  # sesuaikan jika nama file kamu beda


def specs_df() -> pd.DataFrame:
    df = st.session_state.get("specs_df")
    if df is None:
        return pd.DataFrame()
    return df.copy()


def criteria_list():
    return list(st.session_state.get("criteria", []))


def alts_list():
    return list(st.session_state.get("alts", []))


def get_meta():
    return dict(st.session_state.get("criteria_meta", {}))


def weights_to_consistent_matrix(weights: np.ndarray) -> np.ndarray:
    """Bangun matriks konsisten A[i,j] = w_i/w_j"""
    w = np.array(weights, dtype=float)
    w = np.clip(w, 1e-12, None)
    w = w / w.sum()
    n = len(w)
    A = np.ones((n, n), dtype=float)
    for i in range(n):
        for j in range(n):
            A[i, j] = float(w[i] / w[j])
    return A


def apply_profile_weights(profile_answers: dict) -> dict:
    """
    Heuristik: dari jawaban wizard -> bobot kriteria.
    Return dict: {criterion: weight}
    """
    criteria = criteria_list()
    meta = get_meta()

    # base uniform
    w = {c: 1.0 for c in criteria}

    usage = profile_answers.get("usage", "Kuliah")
    budget = profile_answers.get("budget", 8_000_000)
    mobile = profile_answers.get("mobile", 3)     # 1..5
    perf = profile_answers.get("performance", 3) # 1..5
    battery = profile_answers.get("battery", 3)  # 1..5
    screen = profile_answers.get("screen", 3)    # 1..5

    # mapping simpel (kamu bisa ubah)
    def bump(name, val):
        if name in w:
            w[name] *= val

    # budget rendah -> Harga lebih berat
    if budget <= 7_000_000:
        bump("Harga", 2.0)
    elif budget <= 10_000_000:
        bump("Harga", 1.5)
    else:
        bump("Harga", 1.2)

    # kebutuhan performa
    bump("Performa", 1.0 + (perf-1)*0.35)

    # mobilitas -> Portabilitas & Baterai naik
    bump("Portabilitas", 1.0 + (mobile-1)*0.40)
    bump("Baterai", 1.0 + (battery-1)*0.35)

    # layar
    bump("Layar", 1.0 + (screen-1)*0.30)

    # usage
    if usage == "Desain":
        bump("Layar", 1.5)
        bump("Performa", 1.3)
    elif usage == "Gaming":
        bump("Performa", 1.8)
        bump("Layar", 1.2)
        bump("Portabilitas", 0.8)

    # normalisasi
    keys = list(w.keys())
    vec = np.array([w[k] for k in keys], dtype=float)
    vec = vec / vec.sum()
    return dict(zip(keys, vec))


def compute_objective_alt_scores(df_specs: pd.DataFrame, criteria: list, alts: list) -> dict:
    """
    Menghasilkan score alternatif per kriteria (0..1), untuk kriteria objektif.
    Return: {criterion: np.array(scores_len_alts)}
    """
    meta = get_meta()
    out = {}

    if df_specs.empty:
        # fallback: semua equal
        for c in criteria:
            out[c] = np.ones(len(alts), dtype=float) / max(len(alts), 1)
        return out

    # pastikan ada kolom "Laptop"
    if "Laptop" not in df_specs.columns:
        return {c: np.ones(len(alts)) / max(len(alts), 1) for c in criteria}

    # align baris sesuai alts
    idx = {name: i for i, name in enumerate(df_specs["Laptop"].astype(str).tolist())}
    rows = []
    for a in alts:
        if a in idx:
            rows.append(df_specs.iloc[idx[a]])
        else:
            # buat row kosong
            rows.append(pd.Series({"Laptop": a}))
    aligned = pd.DataFrame(rows).reset_index(drop=True)

    for c in criteria:
        m = meta.get(c, {})
        is_subjective = bool(m.get("subjective", True))
        spec_col = m.get("spec_col", None)
        ctype = m.get("type", "benefit")
        method = m.get("method", "minmax")

        if is_subjective or (spec_col is None) or (spec_col not in aligned.columns):
            continue

        vals = pd.to_numeric(aligned[spec_col], errors="coerce").values
        s = normalize_values(vals, ctype=ctype, method=method)  # 0..1
        # agar mirip AHP weight: normalisasi sum=1
        s = s / s.sum() if s.sum() > 1e-12 else np.ones(len(alts)) / max(len(alts), 1)
        out[c] = s

    return out


def calc_hybrid_scenario(scenario_name: str, use_hybrid=True):
    """
    Hybrid:
    - Bobot kriteria: dari AHP criteria matrix (atau auto-consistent matrix dari wizard)
    - Alternatif:
        * objektif: dari specs normalisasi
        * subjektif: dari AHP alt pairwise (kalau ada)
    """
    criteria = criteria_list()
    alts = alts_list()
    scen = st.session_state.scenarios[scenario_name]

    Acrit = sanitize_reciprocal(scen["crit_matrix"])
    wcrit = ahp_weights(Acrit)
    lam_c, ci_c, cr_c = ahp_consistency(Acrit, wcrit)

    df_specs = specs_df()
    obj_scores = compute_objective_alt_scores(df_specs, criteria, alts)

    altW = {}
    altCR = {}

    for c in criteria:
        meta = get_meta().get(c, {})
        is_subjective = bool(meta.get("subjective", True))

        if use_hybrid and (not is_subjective) and (c in obj_scores):
            w = obj_scores[c]
            altW[c] = w
            altCR[c] = (np.nan, np.nan, 0.0)
        else:
            A = sanitize_reciprocal(scen["alt_matrices"][c])
            w = ahp_weights(A)
            lam, ci, cr = ahp_consistency(A, w)
            altW[c] = w
            altCR[c] = (lam, ci, cr)

    scores = np.zeros(len(alts), dtype=float)
    contrib = np.zeros((len(alts), len(criteria)), dtype=float)

    for i in range(len(alts)):
        total = 0.0
        for k, c in enumerate(criteria):
            v = float(wcrit[k]) * float(altW[c][i])
            contrib[i, k] = v
            total += v
        scores[i] = total

    return {
        "Acrit": Acrit,
        "wcrit": wcrit,
        "crit_cons": (lam_c, ci_c, cr_c),
        "altW": altW,
        "altCR": altCR,
        "scores": scores,
        "contrib": contrib,
    }


def most_conflicting_pair(A: np.ndarray, w: np.ndarray, labels: list):
    df = inconsistency_pairs(A, w, labels, top_k=1)
    if df.empty:
        return None
    row = df.iloc[0]
    return row["Item i"], row["Item j"], float(row["Konflik (log-dev)"])


def auto_fix_matrix_to_consistent(A: np.ndarray):
    """
    “Perbaiki otomatis”: ambil bobot dari LLSM (geometric mean),
    lalu bangun matriks konsisten w_i/w_j. CR jadi ~0.
    """
    A = sanitize_reciprocal(A)
    # geometric mean weights
    gm = np.prod(A, axis=1) ** (1.0 / A.shape[0])
    w = gm / gm.sum() if gm.sum() > 1e-12 else np.ones(A.shape[0]) / A.shape[0]
    return weights_to_consistent_matrix(w), w

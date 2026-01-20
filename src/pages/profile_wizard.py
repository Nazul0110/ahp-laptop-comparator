import streamlit as st
import numpy as np

from src.ahp import sanitize_reciprocal
from src.auto_pairwise import ratio_to_saaty
from src.state import normalize_scenario_sizes

def _weights_from_profile(criteria, budget, perf, mobile, screen, battery):
    # semua input 0..10
    # mapping sederhana: bisa kamu ubah nanti
    base = {c: 0.05 for c in criteria}

    def add(c, v):
        if c in base:
            base[c] += v

    # budget ketat -> Harga naik
    add("Harga", (10 - budget) * 0.03)
    # butuh performa tinggi
    add("Performa", perf * 0.04)
    # sering mobile -> Portabilitas + Baterai
    add("Portabilitas", mobile * 0.03)
    add("Baterai", mobile * 0.02)
    # butuh layar bagus
    add("Layar", screen * 0.04)
    # durasi baterai penting
    add("Baterai", battery * 0.04)
    # garansi sedikit pengaruh
    add("Garansi", 0.03)

    w = np.array([base[c] for c in criteria], dtype=float)
    w = w / w.sum() if w.sum() > 1e-12 else np.ones(len(criteria))/len(criteria)
    return w

def _weights_to_pairwise(w):
    # Aij ~ wi/wj dipetakan ke Saaty 1..9
    n = len(w)
    A = np.ones((n, n), dtype=float)
    for i in range(n):
        for j in range(i+1, n):
            r = w[i] / max(w[j], 1e-12)
            s = ratio_to_saaty(r)
            if w[i] >= w[j]:
                A[i, j] = s
                A[j, i] = 1 / s
            else:
                A[i, j] = 1 / s
                A[j, i] = s
    return sanitize_reciprocal(A)

def render_profile_wizard():
    st.title("🧭 Profil Pengguna (Wizard) → Auto Bobot Kriteria")

    scenario = st.session_state.active_scenario
    normalize_scenario_sizes(scenario)

    criteria = st.session_state.criteria
    scen = st.session_state.scenarios[scenario]

    st.caption("Isi 5 pertanyaan. Sistem akan membuat bobot kriteria otomatis (tanpa isi pairwise manual).")

    c1, c2 = st.columns(2)
    budget = c1.slider("Budget kamu ketat?", 0, 10, 6)  # 0=ketat, 10=longgar
    perf   = c2.slider("Butuh performa tinggi?", 0, 10, 6)

    c3, c4 = st.columns(2)
    mobile = c3.slider("Sering dibawa mobile?", 0, 10, 6)
    screen = c4.slider("Butuh layar bagus (warna/refresh)?", 0, 10, 5)

    battery = st.slider("Butuh baterai awet?", 0, 10, 6)

    w = _weights_from_profile(criteria, budget, perf, mobile, screen, battery)

    st.subheader("Preview bobot (dari profil)")
    for c, v in sorted(zip(criteria, w), key=lambda x: x[1], reverse=True):
        st.write(f"- **{c}**: {v*100:.2f}%")

    if st.button("✅ Terapkan ke Matriks Kriteria (Scenario aktif)", use_container_width=True):
        scen["crit_matrix"] = _weights_to_pairwise(w)
        st.session_state.scenarios[scenario] = scen
        st.success("Matriks kriteria sudah di-set dari profil. Lanjut lihat hasil / fine-tune via quick input.")

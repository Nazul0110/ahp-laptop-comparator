import pandas as pd
import streamlit as st

from src.compute import calc_scenario
from src.matrix_ui import matrix_editor_upper
from src.state import normalize_scenario_sizes
from src.ahp import fmt_pct


def render_alt_editor():
    scenario = st.session_state.active_scenario
    normalize_scenario_sizes(scenario)

    st.title(f"💻 Alternatif per Kriteria — Matrix Editor (Scenario: {scenario})")

    criteria = st.session_state.criteria
    alts = st.session_state.alts
    scen = st.session_state.scenarios[scenario]

    if not criteria:
        st.error("Kriteria kosong. Tambahkan dulu di menu ⚙️ Setup.")
        return
    if not alts:
        st.error("Alternatif laptop kosong. Tambahkan dulu di menu ⚙️ Setup.")
        return

    chosen = st.selectbox("Pilih kriteria:", criteria, index=0)

    # Safety: pastikan alt_matrices ada & punya key chosen
    if "alt_matrices" not in scen or not isinstance(scen["alt_matrices"], dict):
        scen["alt_matrices"] = {}
    if chosen not in scen["alt_matrices"]:
        # fallback: reset ukuran matriks akan memastikan bentuk benar
        normalize_scenario_sizes(scenario)
        scen = st.session_state.scenarios[scenario]

    left, right = st.columns([1.2, 1])

    # ==========================
    # LEFT: MATRIX INPUT
    # ==========================
    with left:
        st.subheader(f"Input Matriks Alternatif (Kriteria: {chosen})")
        st.caption(
            "Isi **hanya segitiga atas**. "
            "Nilai bawah otomatis **reciprocal**, diagonal otomatis **1**."
        )

        try:
            Anew = matrix_editor_upper(
                labels=alts,
                A_current=scen["alt_matrices"][chosen],
                key=f"alt_editor_{scenario}_{chosen}",
                help_text="Tips: 1=sama, 3=sedikit lebih baik, 5=lebih baik, 7=sangat baik, 9=ekstrim."
            )
            scen["alt_matrices"][chosen] = Anew
            st.session_state.scenarios[scenario] = scen
        except Exception as e:
            st.error("Gagal memproses input matriks alternatif. Coba periksa nilai yang kamu isi.")
            st.code(str(e))
            return

    # ==========================
    # RIGHT: WEIGHTS + CONSISTENCY
    # ==========================
    with right:
        res = calc_scenario(scenario)
        w = res["altW"][chosen]
        lam, ci, cr = res["altCR"][chosen]

        # clamp biar ga muncul -0.0000
        cr = max(float(cr), 0.0)
        ci = float(ci)
        lam = float(lam)

        st.subheader("Bobot Alternatif & Konsistensi")

        dfw = pd.DataFrame({
            "Laptop": alts,
            "Bobot": [float(x) for x in w],
        })
        dfw["Bobot(%)"] = dfw["Bobot"].apply(fmt_pct)

        st.dataframe(
            dfw.sort_values("Bobot", ascending=False).reset_index(drop=True),
            use_container_width=True
        )

        c1, c2, c3 = st.columns(3)
        c1.metric("λmax", f"{lam:.4f}")
        c2.metric("CI", f"{ci:.4f}")
        c3.metric("CR", f"{cr:.4f}")

        thr = float(st.session_state.get("cr_threshold", 0.10))
        if cr <= thr:
            st.success(f"Konsistensi OK ✅ (CR={cr:.4f} ≤ {thr:.2f})")
        else:
            st.error(f"Konsistensi jelek ❌ (CR={cr:.4f} > {thr:.2f})")
            st.warning("Buka menu **🔥 Heatmap & Konflik** untuk lihat pasangan alternatif mana yang paling bikin konflik.")

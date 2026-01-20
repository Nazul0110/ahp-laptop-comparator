import streamlit as st
from src.pdf_report import build_pdf_report


def render_report_pdf():
    st.title("📄 Report PDF Otomatis")
    scenario = st.session_state.active_scenario

    st.write("Klik tombol untuk generate report PDF lengkap (hasil + grafik + CR) untuk scenario aktif.")

    if st.button("🧾 Generate PDF", use_container_width=True):
        pdf_buf = build_pdf_report(scenario)
        st.success("PDF berhasil dibuat.")
        st.download_button(
            "⬇️ Download Report PDF",
            data=pdf_buf,
            file_name=f"ahp_report_{scenario.replace(' ','_')}.pdf",
            mime="application/pdf",
            use_container_width=True
        )

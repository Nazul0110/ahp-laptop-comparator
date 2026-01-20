import io
import pandas as pd
import matplotlib.pyplot as plt

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image as RLImage
from reportlab.lib.styles import getSampleStyleSheet

import streamlit as st
from src.ahp import fmt_pct, fig_to_png_bytes
from src.compute import calc_scenario


def build_pdf_report(scenario_name: str):
    criteria = st.session_state.criteria
    alts = st.session_state.alts
    res = calc_scenario(scenario_name)

    styles = getSampleStyleSheet()
    story = []

    story.append(Paragraph("<b>AHP Laptop Comparator — Report</b>", styles["Title"]))
    story.append(Spacer(1, 0.3 * cm))
    story.append(Paragraph(f"<b>Scenario:</b> {scenario_name}", styles["Normal"]))
    story.append(Spacer(1, 0.2 * cm))

    lam_c, ci_c, cr_c = res["crit_cons"]
    story.append(Paragraph(
        f"<b>Kriteria Consistency</b> — λmax={lam_c:.4f}, CI={ci_c:.4f}, CR={cr_c:.4f}",
        styles["Normal"]
    ))
    story.append(Spacer(1, 0.2 * cm))

    # Bobot kriteria
    dfw = pd.DataFrame({"Kriteria": criteria, "Bobot": res["wcrit"]}).sort_values("Bobot", ascending=False)
    data = [["Kriteria", "Bobot", "Bobot(%)"]] + [
        [r["Kriteria"], f"{r['Bobot']:.6f}", fmt_pct(r["Bobot"])]
        for _, r in dfw.iterrows()
    ]
    tbl = Table(data, colWidths=[7*cm, 4*cm, 4*cm])
    tbl.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,0), colors.lightgrey),
        ("GRID", (0,0), (-1,-1), 0.5, colors.grey),
        ("FONTNAME", (0,0), (-1,0), "Helvetica-Bold"),
        ("ALIGN", (1,1), (-1,-1), "RIGHT"),
    ]))
    story.append(Paragraph("<b>Bobot Kriteria</b>", styles["Heading2"]))
    story.append(tbl)
    story.append(Spacer(1, 0.4 * cm))

    # Ranking
    scores = res["scores"]
    df_rank = pd.DataFrame({"Laptop": alts, "Skor": scores}).sort_values("Skor", ascending=False).reset_index(drop=True)
    data2 = [["Rank", "Laptop", "Skor", "Skor(%)"]]
    for i, r in df_rank.iterrows():
        data2.append([str(i+1), r["Laptop"], f"{r['Skor']:.6f}", fmt_pct(r["Skor"])])
    tbl2 = Table(data2, colWidths=[2*cm, 7*cm, 4*cm, 4*cm])
    tbl2.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,0), colors.lightgrey),
        ("GRID", (0,0), (-1,-1), 0.5, colors.grey),
        ("FONTNAME", (0,0), (-1,0), "Helvetica-Bold"),
        ("ALIGN", (2,1), (-1,-1), "RIGHT"),
    ]))
    story.append(Paragraph("<b>Ranking Akhir</b>", styles["Heading2"]))
    story.append(tbl2)
    story.append(Spacer(1, 0.4 * cm))

    # Grafik bobot kriteria
    fig1 = plt.figure()
    plt.bar(dfw["Kriteria"], dfw["Bobot"])
    plt.xticks(rotation=30, ha="right")
    plt.ylabel("Bobot")
    plt.title("Bobot Kriteria")
    img1 = fig_to_png_bytes(fig1)
    story.append(Paragraph("<b>Grafik Bobot Kriteria</b>", styles["Heading2"]))
    story.append(RLImage(img1, width=16*cm, height=7*cm))
    story.append(Spacer(1, 0.4 * cm))

    # Grafik skor
    fig2 = plt.figure()
    plt.bar(df_rank["Laptop"], df_rank["Skor"])
    plt.ylabel("Skor AHP")
    plt.title("Skor Akhir Alternatif")
    img2 = fig_to_png_bytes(fig2)
    story.append(Paragraph("<b>Grafik Skor Akhir</b>", styles["Heading2"]))
    story.append(RLImage(img2, width=16*cm, height=7*cm))
    story.append(Spacer(1, 0.4 * cm))

    # CR alternatif per kriteria
    rows = []
    for c in criteria:
        lam, ci, cr = res["altCR"][c]
        rows.append([c, f"{lam:.4f}", f"{ci:.4f}", f"{cr:.4f}"])
    data3 = [["Kriteria", "λmax", "CI", "CR"]] + rows
    tbl3 = Table(data3, colWidths=[7*cm, 3*cm, 3*cm, 3*cm])
    tbl3.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,0), colors.lightgrey),
        ("GRID", (0,0), (-1,-1), 0.5, colors.grey),
        ("FONTNAME", (0,0), (-1,0), "Helvetica-Bold"),
        ("ALIGN", (1,1), (-1,-1), "RIGHT"),
    ]))
    story.append(Paragraph("<b>Consistency Alternatif per Kriteria</b>", styles["Heading2"]))
    story.append(tbl3)

    buf = io.BytesIO()
    doc = SimpleDocTemplate(
        buf,
        pagesize=A4,
        leftMargin=1.5*cm, rightMargin=1.5*cm,
        topMargin=1.5*cm, bottomMargin=1.5*cm
    )
    doc.build(story)
    buf.seek(0)
    return buf

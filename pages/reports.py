import streamlit as st
import pandas as pd
from modules.ui import topbar,section_heading
from modules.reporting import results_payload,html_report,pdf_report

def render(ctx):
    topbar("Reports & Settings")
    r,g=ctx["result"],ctx["greedy"]
    payload=results_payload(r,g,scenario=ctx["scenario"],weights=ctx["weights"],budget=ctx["budget"])
    section_heading("Optimization report")
    st.json(payload)
    c1,c2,c3=st.columns(3)
    with c1: st.download_button("Export JSON",pd.Series(payload).to_json(indent=2).encode(),file_name="peatra_optimization.json",mime="application/json")
    with c2: st.download_button("Printable HTML",html_report(payload).encode(),file_name="peatra_report.html",mime="text/html")
    with c3: st.download_button("PDF report",pdf_report(payload),file_name="peatra_report.pdf",mime="application/pdf")
    section_heading("Per-location report")
    site=st.selectbox("Location",ctx["data"]["sites"].site_id.tolist())
    sc=ctx["scores"][ctx["scores"].site_id.eq(site)].copy()
    st.download_button("Export site CSV",sc.to_csv(index=False).encode(),file_name=f"peatra_{site}_interventions.csv",mime="text/csv")
    st.dataframe(sc,use_container_width=True,hide_index=True)
    section_heading("Settings")
    st.caption("Pengaturan session disimpan selama aplikasi terbuka. Dataset CSV asli tetap berada di folder data.")
    if st.button("Reset demo data",type="secondary"):
        ctx["reset_data"](); st.rerun()

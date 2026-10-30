import streamlit as st
from modules.ui import topbar,section_heading,money
from modules.visualizations import benefit_comparison

def render(ctx):
    sites,scores=ctx["data"]["sites"],ctx["scores"]
    topbar("Intervention Comparison")
    site=st.selectbox("Site",sites.site_id.tolist())
    sc=scores[scores.site_id.eq(site)].copy()
    section_heading("Repair vs new construction vs no intervention","No intervention = memilih tidak ada action untuk lokasi tersebut pada siklus ini.")
    display=sc[["action","cost","technical_feasibility","delta_fire_raw","hydro_raw","ecology_raw","fire_score","hydro_score","ecology_score","weighted_score","confidence_level"]].copy()
    display.loc[len(display)]=["No Intervention",0,1,0,0,0,0,0,0,0,"N/A"]
    display["cost"]=display.cost.map(money)
    st.dataframe(display,use_container_width=True,hide_index=True)
    st.plotly_chart(benefit_comparison(sc),use_container_width=True,config={"displayModeBar":False})
    best=sc[sc.technical_feasibility.eq(1)].sort_values("weighted_score",ascending=False).head(1)
    if not best.empty: st.success(f"Secara lokal, {best.iloc[0].action} memiliki skor manfaat tertinggi ({best.iloc[0].weighted_score:.2f}). Namun portofolio global tetap ditentukan bersama lokasi lain dan kendala anggaran.")

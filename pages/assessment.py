import streamlit as st
from modules.ui import topbar,section_heading
from modules.scoring import classify_site

def render(ctx):
    sites,scores=ctx["data"]["sites"],ctx["scores"]
    topbar("Peatland Assessment")
    d=sites.copy()
    # Site priority proxy = best feasible weighted score, not an arbitrary number.
    best=scores[scores.technical_feasibility.eq(1)].groupby("site_id").weighted_score.max().rename("priority_score")
    d=d.join(best,on="site_id")
    d["priority_score"]=d.priority_score.fillna(0)
    d[["condition","priority"]]=d.apply(lambda r: classify_site(r,r.priority_score),axis=1,result_type="expand")
    f1,f2,f3=st.columns(3)
    with f1: cover=st.multiselect("Land cover",sorted(d.land_cover.unique()))
    with f2: cond=st.multiselect("Condition",sorted(d.condition.unique()))
    with f3: pr=st.multiselect("Priority",sorted(d.priority.unique()))
    if cover:d=d[d.land_cover.isin(cover)]
    if cond:d=d[d.condition.isin(cond)]
    if pr:d=d[d.priority.isin(pr)]
    section_heading("Assessment matrix","Prioritas menggunakan skor manfaat intervensi terbaik yang feasible; bukan pengukuran dampak aktual.")
    st.dataframe(d[["site_id","land_cover","canal_condition","groundwater_depth","fire_risk_index","ecological_sensitivity","accessibility","condition","priority","priority_score","data_provenance"]].sort_values("priority_score",ascending=False),use_container_width=True,height=390,hide_index=True)
    section_heading("Interpretation")
    st.info("Depth lebih besar berarti muka air lebih dalam dari permukaan. Fire-risk index adalah indeks 0–100, bukan probabilitas kebakaran.")

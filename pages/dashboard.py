import streamlit as st
from modules.ui import topbar,kpis,section_heading,money
from modules.visualizations import risk_chart,intervention_distribution,schematic_map

def render(ctx):
    data, scores, result, greedy = ctx["data"],ctx["scores"],ctx["result"],ctx["greedy"]
    sites=data["sites"]; monitoring=data["monitoring"]
    topbar("Dashboard")
    budget=ctx["budget"]
    priority=len(result["selected"])
    kpis([
        ("Total lokasi",len(sites),"6 lokasi demo"),
        ("Luas area model",f"{sites.affected_area.sum():,.0f} ha","affected area"),
        ("Anggaran aktif",money(budget),"budget constraint"),
        ("Lokasi prioritas",priority,f"{result['status']} MILP"),
        ("Monitoring tervalidasi",f"{len(monitoring[monitoring.validation_status.eq('Tervalidasi')])}/{len(monitoring)}","active observations"),
    ])
    c1,c2=st.columns([1.55,1])
    with c1:
        st.markdown('<div class="card">',unsafe_allow_html=True); section_heading("Kondisi gambut & lokasi prioritas","Peta skematis — bukan peta geografis resmi."); st.plotly_chart(schematic_map(sites,result['selected'].site_id.tolist()),use_container_width=True,config={"displayModeBar":False}); st.markdown('</div>',unsafe_allow_html=True)
    with c2:
        st.markdown('<div class="card">',unsafe_allow_html=True); section_heading("Ringkasan optimasi terakhir")
        st.markdown(f'<div class="mini-stat"><span>Status solver</span><b>{result["status"].upper()}</b></div><div class="mini-stat"><span>Model benefit</span><b>{result["total_score"]:.2f}</b></div><div class="mini-stat"><span>Total biaya</span><b>{money(result["total_cost"])}</b></div><div class="mini-stat"><span>Sisa anggaran</span><b>{money(budget-result["total_cost"])}</b></div>',unsafe_allow_html=True)
        if st.button("Run Optimization",type="primary",use_container_width=True): ctx["run_optimization"](); st.rerun()
        st.markdown('</div>',unsafe_allow_html=True)
    c3,c4=st.columns([1,1])
    with c3:
        st.markdown('<div class="card">',unsafe_allow_html=True); section_heading("Distribusi intervensi"); st.plotly_chart(intervention_distribution(result["selected"]),use_container_width=True,config={"displayModeBar":False}); st.markdown('</div>',unsafe_allow_html=True)
    with c4:
        st.markdown('<div class="card">',unsafe_allow_html=True); section_heading("Fire-risk index"); st.plotly_chart(risk_chart(sites),use_container_width=True,config={"displayModeBar":False}); st.markdown('</div>',unsafe_allow_html=True)
    section_heading("Aktivitas monitoring terbaru")
    recent=monitoring.sort_values("observation_date",ascending=False).head(4)
    st.dataframe(recent[["observation_date","site_id","groundwater_depth","fire_risk_index","validation_status","notes"]],use_container_width=True,hide_index=True,height=190)

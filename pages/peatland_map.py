import streamlit as st
from modules.ui import topbar,section_heading
from modules.visualizations import schematic_map

def render(ctx):
    data=ctx["data"]; sites=data["sites"]
    topbar("Peatland Map","Pilot: Kabupaten Pelalawan, Riau")
    c1,c2=st.columns([1,2.1])
    with c1:
        section_heading("Filter lokasi")
        query=st.text_input("Search site",placeholder="A1, A2, ...")
        cover=st.multiselect("Tutupan lahan",sorted(sites.land_cover.unique()))
        risk=st.slider("Minimum fire-risk",0,100,0)
        layer=st.selectbox("Map layer",["Fire risk","Groundwater depth","Ecological sensitivity","Recommended action"])
        d=sites.copy()
        if query: d=d[d.site_id.str.contains(query.upper())|d.site_name.str.contains(query,case=False)]
        if cover: d=d[d.land_cover.isin(cover)]
        d=d[d.fire_risk_index>=risk]
        st.caption(f"{len(d)} dari {len(sites)} lokasi ditampilkan")
        st.markdown('<div class="card" style="margin-top:10px"><b>Legend</b><br><span style="font-size:11px">● Green = lower risk · ● Teal = medium · ● Red = higher risk</span><br><span class="muted">Marker selection tersinkron dengan tabel.</span></div>',unsafe_allow_html=True)
    with c2:
        section_heading("Schematic peatland map","Koordinat demo tidak mewakili koordinat geografis resmi.")
        selected=ctx["result"]["selected"].site_id.tolist()
        color_by={"Fire risk":"fire_risk_index","Groundwater depth":"groundwater_depth","Ecological sensitivity":"ecological_sensitivity","Recommended action":"fire_risk_index"}[layer]
        st.plotly_chart(schematic_map(d,selected,color_by=color_by),use_container_width=True,config={"displayModeBar":False})
    section_heading("Location table")
    st.dataframe(d[["site_id","site_name","land_cover","canal_condition","groundwater_depth","fire_risk_index","ecological_sensitivity","accessibility"]],use_container_width=True,height=330,hide_index=True)

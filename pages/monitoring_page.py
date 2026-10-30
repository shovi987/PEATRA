import streamlit as st
from datetime import date
from modules.ui import topbar,section_heading
from modules.monitoring import add_observation
from modules.visualizations import monitoring_chart

def render(ctx):
    topbar("Monitoring")
    data=ctx["data"]; sites=data["sites"]
    with st.expander("Add monitoring observation",expanded=True):
        c1,c2,c3=st.columns(3)
        with c1: site=st.selectbox("Location",sites.site_id.tolist()); obs_date=st.date_input("Observation date",date.today())
        with c2: depth=st.number_input("Groundwater depth (m)",0.0,3.0,0.60,0.01); canal=st.selectbox("Canal condition",["Baik","Rusak sebagian","Rusak berat","Tidak ada"])
        with c3: risk=st.number_input("Fire-risk index",0.0,100.0,60.0,1.0); hotspots=st.number_input("Hotspot count",0,999,0,1)
        notes=st.text_area("Field notes",placeholder="Catatan petugas")
        validation=st.selectbox("Validation status",["Draft","Tervalidasi"])
        if st.button("Save observation",type="primary"):
            try:
                row={"site_id":site,"observation_date":obs_date.isoformat(),"groundwater_depth":depth,"canal_condition":canal,"fire_risk_index":risk,"hotspot_count":hotspots,"validation_status":validation,"notes":notes}
                ctx["data"]["monitoring"]=add_observation(data["monitoring"],row)
                ctx["persist_monitoring"]()
                st.success("Observation saved. Only validated observations can update active optimization data.")
                st.rerun()
            except Exception as e: st.error(str(e))
    section_heading("Monitoring history")
    hist=data["monitoring"].sort_values("observation_date",ascending=False)
    st.dataframe(hist,use_container_width=True,height=280,hide_index=True)
    st.plotly_chart(monitoring_chart(data["monitoring"]),use_container_width=True,config={"displayModeBar":False})
    section_heading("Audit & feedback")
    st.info("Validated observations update groundwater depth, canal condition, and fire-risk index only where measurement data are recorded. Hotspot count remains monitoring information and does not directly replace the risk index.")
    if st.button("Apply validated observations & re-optimize",type="primary"): ctx["apply_monitoring_and_reoptimize"](); st.rerun()

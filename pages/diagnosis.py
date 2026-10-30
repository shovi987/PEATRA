import streamlit as st
from modules.ui import topbar,section_heading

def render(ctx):
    sites,scores=ctx["data"]["sites"],ctx["scores"]
    topbar("Site Diagnosis")
    site=st.selectbox("Pilih lokasi",sites.site_id.tolist(),format_func=lambda x: sites.loc[sites.site_id.eq(x),'site_name'].iloc[0])
    s=sites[sites.site_id.eq(site)].iloc[0]; sc=scores[scores.site_id.eq(site)].copy()
    section_heading(f"Diagnosis · {s.site_name}","Ringkasan kondisi dan kebutuhan restorasi berdasarkan data demo aktif.")
    k1,k2,k3,k4=st.columns(4)
    k1.metric("Groundwater depth",f"{s.groundwater_depth:.2f} m")
    k2.metric("Fire-risk index",f"{s.fire_risk_index:.0f}/100")
    k3.metric("Canal condition",s.canal_condition)
    k4.metric("Ecological sensitivity",f"{s.ecological_sensitivity:.0f}/100")
    c1,c2=st.columns(2)
    with c1:
        st.markdown('<div class="card">',unsafe_allow_html=True); section_heading("Main issues")
        issues=[]
        if s.groundwater_depth>0.40: issues.append(f"Muka air lebih dalam dari acuan 0,40 m ({s.groundwater_depth:.2f} m).")
        if s.fire_risk_index>=60: issues.append(f"Indeks risiko kebakaran relatif tinggi ({s.fire_risk_index:.0f}).")
        if s.canal_condition!="Baik": issues.append(f"Kondisi sekat: {s.canal_condition}.")
        if s.accessibility=="Sulit": issues.append("Aksesibilitas sulit meningkatkan kompleksitas implementasi.")
        for x in issues or ["Tidak ada isu utama menurut rule-based screening."]: st.markdown(f"• {x}")
        st.markdown('</div>',unsafe_allow_html=True)
    with c2:
        st.markdown('<div class="card">',unsafe_allow_html=True); section_heading("Technical feasibility")
        st.dataframe(sc[["action","technical_feasibility","confidence_level","cost"]],use_container_width=True,hide_index=True,height=150)
        st.markdown(f'<div class="muted">Provenance: {s.data_provenance}</div>',unsafe_allow_html=True); st.markdown('</div>',unsafe_allow_html=True)
    section_heading("Diagnosis data")
    st.dataframe(sc[["action","delta_fire_raw","hydro_raw","ecology_raw","fire_score","hydro_score","ecology_score","weighted_score"]],use_container_width=True,hide_index=True)

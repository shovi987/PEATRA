import streamlit as st
from modules.ui import topbar,section_heading,money
from modules.visualizations import schematic_map

def render(ctx):
    topbar("Optimization Engine")
    sites,scores=ctx["data"]["sites"],ctx["scores"]
    st.markdown('<div class="card">',unsafe_allow_html=True); section_heading("Decision parameters","Bobot adalah preferensi pengambil keputusan, bukan parameter ilmiah universal.")
    c1,c2,c3,c4=st.columns(4)
    with c1: budget=st.number_input("Budget (Rp)",0,5_000_000_000,ctx["budget"],50_000_000,key="opt_budget")
    with c2: wr=st.slider("Fire risk",0.0,1.0,ctx["weights"]["fire"],0.05,key="wr")
    with c3: ww=st.slider("Hydrology",0.0,1.0,ctx["weights"]["hydro"],0.05,key="ww")
    with c4: we=st.slider("Ecology",0.0,1.0,ctx["weights"]["ecology"],0.05,key="we")
    st.caption(f"Bobot aktual setelah normalisasi: Fire {ctx['weights']['fire']:.3f} · Hydro {ctx['weights']['hydro']:.3f} · Ecology {ctx['weights']['ecology']:.3f}. Gunakan tombol Apply untuk memperbarui model.")
    c5,c6,c7,c8=st.columns(4)
    with c5: max_n=st.number_input("Max interventions",0,6,6,key="maxn")
    with c6: mandatory=st.multiselect("Mandatory sites",sites.site_id.tolist(),key="mandatory")
    with c7: forbid_site=st.selectbox("Forbidden action site",["None"]+sites.site_id.tolist(),key="forbid_site")
    with c8: target_depth=st.number_input("Reference depth (m)",0.10,1.50,ctx["target_depth"],0.01,key="target_depth_opt")
    forbid=[]
    if forbid_site!="None":
        fa=st.selectbox("Action to forbid",scores[scores.site_id.eq(forbid_site)].action.tolist(),key="forbid_action"); forbid=[(forbid_site,fa)]
    if st.button("Apply parameters & Run Optimization",type="primary"):
        ctx["apply_parameters"](budget,wr,ww,we,int(max_n) if max_n<6 else None,mandatory,forbid,target_depth); st.rerun()
    st.markdown('</div>',unsafe_allow_html=True)
    r,g=ctx["result"],ctx["greedy"]
    c1,c2,c3,c4=st.columns(4)
    c1.metric("Solver",r["status"].upper()); c2.metric("Model benefit",f"{r['total_score']:.2f}"); c3.metric("Total cost",money(r["total_cost"])); c4.metric("Remaining",money(ctx["budget"]-r["total_cost"]))
    if r["errors"]: st.error("Constraint validation: "+"; ".join(r["errors"]))
    section_heading("Decision portfolio")
    st.dataframe(r["selected"][["site_id","action","cost","weighted_score","technical_feasibility","confidence_level"]],use_container_width=True,hide_index=True)
    c1,c2=st.columns([1.1,.9])
    with c1: st.plotly_chart(schematic_map(sites,r["selected"].site_id.tolist()),use_container_width=True,config={"displayModeBar":False})
    with c2:
        section_heading("MILP vs greedy")
        st.metric("MILP score",f"{r['total_score']:.2f}")
        st.metric("Greedy score",f"{g['total_score']:.2f}")
        improvement=None if abs(g['total_score'])<1e-12 else (r['total_score']-g['total_score'])/g['total_score']*100
        st.metric("MILP improvement", "N/A" if improvement is None else f"{improvement:.2f}%")
        st.caption("Greedy adalah baseline rasio U/C; MILP menggunakan solver HiGHS dan bukan sekadar sorting.")
    section_heading("Solver verification")
    st.write(f"Message: {r['message']}")
    st.write(f"Optimality gap: {'N/A' if r['optimality_gap'] is None else r['optimality_gap']}")
    st.write(f"Budget check: {r['total_cost']:,.0f} ≤ {ctx['budget']:,.0f} → {'PASS' if r['total_cost']<=ctx['budget']+1e-6 else 'FAIL'}")

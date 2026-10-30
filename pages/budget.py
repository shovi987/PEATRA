import streamlit as st
import numpy as np
from modules.ui import topbar,section_heading,money
from modules.optimization import budget_curve
from modules.visualizations import budget_curve as plot_budget

def render(ctx):
    topbar("Budget Simulator")
    base=ctx["budget"]
    preset=st.radio("Budget preset",["Custom","Rp 1 miliar","Rp 2 miliar","Rp 3 miliar"],horizontal=True)
    if preset!="Custom": budget={"Rp 1 miliar":1e9,"Rp 2 miliar":2e9,"Rp 3 miliar":3e9}[preset]
    else: budget=st.slider("Budget",0,3_000_000_000,int(base),50_000_000)
    if st.button("Use this budget",type="primary"): ctx["set_budget"](budget); st.rerun()
    weights=ctx["weights"]
    budgets=np.linspace(0,3_000_000_000,13)
    curve=budget_curve(ctx["scores"],budgets,max_interventions=ctx["max_interventions"],mandatory_sites=ctx["mandatory_sites"],forbidden_actions=ctx["forbidden_actions"])
    section_heading("Budget → optimal benefit")
    st.plotly_chart(plot_budget(curve),use_container_width=True,config={"displayModeBar":False})
    current=curve.iloc[(curve.budget-budget).abs().argmin()]
    c1,c2,c3,c4=st.columns(4)
    c1.metric("Selected budget",money(budget)); c2.metric("Model benefit",f"{current.score:.2f}"); c3.metric("Cost used",money(current.cost)); c4.metric("Sites",int(current.sites))
    section_heading("Sensitivity curve data")
    st.dataframe(curve,use_container_width=True,hide_index=True,height=330)

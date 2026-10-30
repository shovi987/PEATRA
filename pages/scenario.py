import streamlit as st
from modules.ui import topbar,section_heading
from modules.scenarios import apply_scenario,SCENARIOS,scenario_delta
from modules.scoring import compute_scores
from modules.optimization import solve_milp
from modules.sensitivity import cost_sensitivity,monte_carlo_stability,regret_matrix
from modules.visualizations import schematic_map,scenario_radar

def render(ctx):
    topbar("Scenario Simulator")
    scenario=st.selectbox("Environmental scenario",list(SCENARIOS.keys()))
    if st.button("Set as active report scenario"):
        ctx["set_scenario"](scenario); st.rerun()
    ss,ii=apply_scenario(ctx["data"]["sites"],ctx["data"]["interventions"],scenario)
    sc=compute_scores(ss,ii,target_depth=ctx["target_depth"],weights=ctx["weights"],normalization=ctx["normalization"])
    r=solve_milp(sc,ctx["budget"],max_interventions=ctx["max_interventions"],mandatory_sites=ctx["mandatory_sites"],forbidden_actions=ctx["forbidden_actions"])
    section_heading(f"{scenario}","Scenario factors are illustrative assumptions, not scientific forecasts.")
    c1,c2=st.columns(2)
    with c1: st.plotly_chart(schematic_map(ss,r["selected"].site_id.tolist()),use_container_width=True,config={"displayModeBar":False})
    with c2:
        delta=scenario_delta(ctx["data"]["sites"],ss)
        st.dataframe(delta[["site_id","depth_change","risk_change"]],use_container_width=True,hide_index=True)
        st.metric("Selected interventions",len(r["selected"]))
        st.metric("Scenario benefit",f"{r['total_score']:.2f}")
    section_heading("All-scenario comparison")
    summary=[]
    for name in SCENARIOS:
        a,b=apply_scenario(ctx["data"]["sites"],ctx["data"]["interventions"],name); s=compute_scores(a,b,target_depth=ctx["target_depth"],weights=ctx["weights"],normalization=ctx["normalization"]); rr=solve_milp(s,ctx["budget"],max_interventions=ctx["max_interventions"],mandatory_sites=ctx["mandatory_sites"],forbidden_actions=ctx["forbidden_actions"])
        summary.append({"scenario":name,"avg_risk":a.fire_risk_index.mean(),"avg_depth":a.groundwater_depth.mean(),"score":rr["total_score"],"cost":rr["total_cost"],"sites":len(rr["selected"])})
    import pandas as pd
    sdf=pd.DataFrame(summary); st.dataframe(sdf,use_container_width=True,hide_index=True)
    st.plotly_chart(scenario_radar(sdf),use_container_width=True,config={"displayModeBar":False})
    section_heading("Sensitivity & regret")
    sens=cost_sensitivity(ctx["data"]["sites"],ctx["data"]["interventions"],ctx["budget"],ctx["weights"],target_depth=ctx["target_depth"],normalization=ctx["normalization"])
    st.dataframe(sens,use_container_width=True,hide_index=True)
    runs,stable=monte_carlo_stability(ctx["data"]["sites"],ctx["data"]["interventions"],ctx["budget"],ctx["weights"],runs=80,uncertainty=0.10,target_depth=ctx["target_depth"],normalization=ctx["normalization"])
    st.markdown("**Monte Carlo selection stability** — frequency of selection under ±10% input uncertainty.")
    st.dataframe(stable.sort_values("selection_frequency",ascending=False).head(12),use_container_width=True,hide_index=True)
    regret=regret_matrix(ctx["data"]["sites"],ctx["data"]["interventions"],ctx["budget"],ctx["weights"],target_depth=ctx["target_depth"],normalization=ctx["normalization"])
    st.markdown("**Regret matrix** — lower is better; regret is the benefit gap versus the optimum in each environment.")
    st.dataframe(regret.pivot(index="decision_scenario",columns="environment",values="regret"),use_container_width=True)

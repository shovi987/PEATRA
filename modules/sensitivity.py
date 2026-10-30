from __future__ import annotations
import numpy as np
import pandas as pd
from .optimization import solve_milp
from .scenarios import apply_scenario, SCENARIOS
from .scoring import compute_scores


def cost_sensitivity(sites, interventions, budget, weights, costs=(0.8,0.9,1.0,1.1,1.2), **score_kwargs):
    rows=[]
    for factor in costs:
        ii=interventions.copy(); ii["cost"]*=factor
        scores=compute_scores(sites,ii,weights=weights,**score_kwargs)
        r=solve_milp(scores,budget)
        rows.append({"cost_factor":factor,"score":r["total_score"],"cost":r["total_cost"],"sites":len(r["selected"]),"status":r["status"]})
    return pd.DataFrame(rows)


def monte_carlo_stability(sites, interventions, budget, weights, runs=120, uncertainty=0.10, seed=42, **score_kwargs):
    rng=np.random.default_rng(seed)
    counts={(row.site_id,row.action):0 for _,row in interventions.iterrows()}
    rows=[]
    for run in range(runs):
        ii=interventions.copy()
        ii["cost"]=ii["cost"]*rng.uniform(1-uncertainty,1+uncertainty,len(ii))
        ii["delta_fire_risk"]=ii["delta_fire_risk"]*rng.uniform(1-uncertainty,1+uncertainty,len(ii))
        ii["hydrological_improvement"]=ii["hydrological_improvement"]*rng.uniform(1-uncertainty,1+uncertainty,len(ii))
        ii["ecological_area_benefit"]=ii["ecological_area_benefit"]*rng.uniform(1-uncertainty,1+uncertainty,len(ii))
        s=sites.copy()
        s["fire_risk_index"]=np.clip(s["fire_risk_index"]*rng.uniform(1-uncertainty,1+uncertainty,len(s)),0,100)
        scores=compute_scores(s,ii,weights=weights,**score_kwargs)
        r=solve_milp(scores,budget)
        for _,x in r["selected"].iterrows(): counts[(x.site_id,x.action)]+=1
        rows.append({"run":run+1,"score":r["total_score"],"cost":r["total_cost"],"status":r["status"]})
    stability=pd.DataFrame([{"site_id":k[0],"action":k[1],"selection_frequency":v/runs} for k,v in counts.items()])
    return pd.DataFrame(rows), stability


def regret_matrix(sites, interventions, budget, weights, **score_kwargs):
    scenario_scores={}; scenario_results={}
    for name in SCENARIOS:
        ss,ii=apply_scenario(sites,interventions,name)
        sc=compute_scores(ss,ii,weights=weights,**score_kwargs)
        r=solve_milp(sc,budget)
        scenario_scores[name]=sc; scenario_results[name]=r
    rows=[]
    for portfolio_name, portfolio_result in scenario_results.items():
        # Re-evaluate the portfolio selected under this portfolio's decision in each environment.
        selected=portfolio_result["selected"]
        for env_name, sc in scenario_scores.items():
            lookup=sc.set_index(["site_id","action"])["weighted_score"]
            value=0.0
            for _,x in selected.iterrows(): value += float(lookup.get((x.site_id,x.action),0.0))
            optimum=scenario_results[env_name]["total_score"]
            rows.append({"decision_scenario":portfolio_name,"environment":env_name,"regret":float(max(0.0,optimum-value))})
    return pd.DataFrame(rows)

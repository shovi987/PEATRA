import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import pandas as pd
import numpy as np
from modules.scoring import normalize_reference, normalize_weights, compute_scores
from modules.optimization import solve_milp, greedy_baseline


def demo():
    sites=pd.DataFrame([
        ["A", "A", "Semak", "Rusak", .8, 80, 80, 50, "Mudah", "ILLUSTRATIVE"],
        ["B", "B", "Hutan", "Baik", .35, 30, 50, 20, "Mudah", "ILLUSTRATIVE"],
    ],columns=["site_id","site_name","land_cover","canal_condition","groundwater_depth","fire_risk_index","ecological_sensitivity","affected_area","accessibility","data_provenance"])
    interventions=pd.DataFrame([
        ["A","Repair",100,20,.5,40,1,"High"],["A","New",200,30,.6,50,1,"High"],
        ["B","Repair",90,10,.2,20,1,"High"],["B","New",150,15,.3,30,1,"High"],
    ],columns=["site_id","action","cost","delta_fire_risk","hydrological_improvement","ecological_area_benefit","technical_feasibility","confidence_level"])
    return sites,interventions


def test_reference_normalization():
    assert normalize_reference([0,20,40,80],40).tolist()==[0,50,100,100]


def test_weights_sum_one():
    w=normalize_weights(.2,.2,.2)
    assert abs(sum(w.values())-1)<1e-12


def test_milp_respects_budget_and_one_per_site():
    s,i=demo(); sc=compute_scores(s,i,weights={"fire":.4,"hydro":.35,"ecology":.25})
    r=solve_milp(sc,150)
    assert r["total_cost"]<=150+1e-9
    assert r["selected"].site_id.nunique()==len(r["selected"])
    assert (r["selected"].technical_feasibility==1).all()


def test_zero_budget_selects_none():
    s,i=demo(); sc=compute_scores(s,i)
    r=solve_milp(sc,0)
    assert len(r["selected"])==0


def test_infeasible_technical_case():
    s,i=demo(); i["technical_feasibility"]=0; sc=compute_scores(s,i)
    r=solve_milp(sc,1000)
    assert r["status"]=="infeasible"


def test_greedy_completes():
    s,i=demo(); sc=compute_scores(s,i)
    g=greedy_baseline(sc,150)
    assert g["total_cost"]<=150+1e-9


def test_bruteforce_matches_milp_small_instance():
    s,i=demo(); sc=compute_scores(s,i)
    r=solve_milp(sc,250)
    best=-1
    rows=list(sc.itertuples())
    for mask in range(1<<len(rows)):
        chosen=[rows[j] for j in range(len(rows)) if mask>>j&1]
        if len({x.site_id for x in chosen})<len(chosen): continue
        if any(x.technical_feasibility!=1 for x in chosen): continue
        if sum(x.cost for x in chosen)>250: continue
        score=sum(x.weighted_score for x in chosen)
        best=max(best,score)
    assert abs(r["total_score"]-best)<1e-6

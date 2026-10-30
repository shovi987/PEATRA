from __future__ import annotations
import numpy as np
import pandas as pd
from scipy.optimize import milp, LinearConstraint, Bounds


def _build_constraints(scores, budget, max_interventions=None, mandatory_sites=None, forbidden_actions=None):
    n = len(scores)
    rows, lb, ub = [], [], []
    # At most one action per site.
    for site in scores.site_id.unique():
        row = np.zeros(n)
        row[scores.site_id.eq(site).to_numpy()] = 1
        rows.append(row); lb.append(-np.inf); ub.append(1)
    # Budget.
    rows.append(scores.cost.to_numpy(dtype=float)); lb.append(-np.inf); ub.append(float(budget))
    # Optional max number of interventions.
    if max_interventions is not None:
        rows.append(np.ones(n)); lb.append(-np.inf); ub.append(float(max_interventions))
    # Mandatory site: sum of feasible actions at site >= 1.
    for site in mandatory_sites or []:
        row = np.zeros(n); row[scores.site_id.eq(site).to_numpy()] = 1
        rows.append(row); lb.append(1); ub.append(np.inf)
    # Forbidden action: x = 0.
    for site, action in forbidden_actions or []:
        row = np.zeros(n); row[(scores.site_id.eq(site) & scores.action.eq(action)).to_numpy()] = 1
        rows.append(row); lb.append(0); ub.append(0)
    A = np.vstack(rows) if rows else np.empty((0,n))
    return A, np.array(lb), np.array(ub)


def validate_solution(scores, selected_indices, budget, max_interventions=None, mandatory_sites=None, forbidden_actions=None):
    chosen = scores.iloc[list(selected_indices)] if selected_indices else scores.iloc[0:0]
    errors=[]
    if chosen.cost.sum() > budget + 1e-6: errors.append("Budget constraint violated")
    if chosen.groupby("site_id").size().max() > 1 if not chosen.empty else False: errors.append("At-most-one-intervention violated")
    if not chosen.empty and (chosen.technical_feasibility.astype(int) != 1).any(): errors.append("Technical feasibility violated")
    if max_interventions is not None and len(chosen) > max_interventions: errors.append("Maximum intervention count violated")
    chosen_sites=set(chosen.site_id)
    for s in mandatory_sites or []:
        if s not in chosen_sites: errors.append(f"Mandatory site {s} not selected")
    for s,a in forbidden_actions or []:
        if ((chosen.site_id==s)&(chosen.action==a)).any(): errors.append(f"Forbidden action selected: {s}/{a}")
    return errors


def _solve(scores, budget, max_interventions=None, mandatory_sites=None, forbidden_actions=None, objective="score", score_floor=None):
    if scores.empty:
        return None
    n=len(scores)
    A, lb, ub = _build_constraints(scores, budget, max_interventions, mandatory_sites, forbidden_actions)
    c = scores.weighted_score.to_numpy(float) if objective=="score" else scores.cost.to_numpy(float)
    if objective=="score": c=-c
    bounds=Bounds(np.zeros(n), np.ones(n))
    constraints=[LinearConstraint(A, lb, ub)]
    if score_floor is not None:
        row=scores.weighted_score.to_numpy(float)
        constraints.append(LinearConstraint(row.reshape(1,-1), np.array([score_floor]), np.array([np.inf])))
    res=milp(c, integrality=np.ones(n), bounds=bounds, constraints=constraints,
             options={"disp":False})
    return res


def solve_milp(scores, budget, max_interventions=None, mandatory_sites=None, forbidden_actions=None):
    eligible=scores[scores.technical_feasibility.astype(int).eq(1)].reset_index(drop=True)
    if eligible.empty:
        return {"status":"infeasible","message":"Tidak ada intervensi yang layak secara teknis.","selected":eligible,"total_score":0.0,"total_cost":0.0,"optimality_gap":None,"errors":[]}
    res=_solve(eligible,budget,max_interventions,mandatory_sites,forbidden_actions,objective="score")
    if res is None:
        return {"status":"error","message":"Solver tidak dapat dipanggil.","selected":eligible.iloc[0:0],"total_score":0.0,"total_cost":0.0,"optimality_gap":None,"errors":[]}
    status_map={0:"optimal",1:"feasible",2:"infeasible",3:"unbounded",4:"error"}
    status=status_map.get(int(res.status),"error")
    if res.x is None:
        return {"status":status,"message":str(res.message),"selected":eligible.iloc[0:0],"total_score":0.0,"total_cost":0.0,"optimality_gap":None,"errors":[]}
    idx=np.where(res.x>0.5)[0]
    selected=eligible.iloc[idx].copy()
    best_score=float(selected.weighted_score.sum())
    # Two-stage tie-break: minimize cost while preserving the proven optimal score.
    if status=="optimal":
        res2=_solve(eligible,budget,max_interventions,mandatory_sites,forbidden_actions,objective="cost",score_floor=best_score-1e-7)
        if res2 is not None and res2.x is not None and res2.status in (0,1):
            idx2=np.where(res2.x>0.5)[0]
            selected=eligible.iloc[idx2].copy()
    total_score=float(selected.weighted_score.sum())
    total_cost=float(selected.cost.sum())
    errors=validate_solution(eligible, [eligible.index.get_loc(i) for i in selected.index], budget, max_interventions, mandatory_sites, forbidden_actions)
    gap=getattr(res,"mip_gap",None)
    return {"status":status,"message":str(res.message),"selected":selected,"total_score":total_score,"total_cost":total_cost,
            "optimality_gap":None if gap is None else float(gap),"errors":errors}


def greedy_baseline(scores, budget, max_interventions=None, mandatory_sites=None, forbidden_actions=None):
    eligible=scores[scores.technical_feasibility.astype(int).eq(1)].copy()
    chosen=[]; used_sites=set(); remaining=float(budget)
    mandatory=set(mandatory_sites or [])
    # Candidate order by ratio, then score, then cost. Zero-cost positive-benefit actions first.
    eligible=eligible.copy()
    eligible["ratio"]=np.where(eligible.cost>0, eligible.weighted_score/eligible.cost, np.inf)
    eligible=eligible.sort_values(["ratio","weighted_score","cost"], ascending=[False,False,True])
    for _,r in eligible.iterrows():
        if r.site_id in used_sites: continue
        if forbidden_actions and (r.site_id,r.action) in set(forbidden_actions): continue
        if r.cost > remaining + 1e-9: continue
        if max_interventions is not None and len(chosen)>=max_interventions: break
        chosen.append(r); used_sites.add(r.site_id); remaining -= float(r.cost)
    # If mandatory sites remain, attempt a feasible replacement greedily.
    for site in mandatory-used_sites:
        candidates=eligible[(eligible.site_id==site) & (~eligible.apply(lambda r:(r.site_id,r.action) in set(forbidden_actions or []),axis=1))]
        if candidates.empty: continue
        r=candidates.sort_values("ratio",ascending=False).iloc[0]
        if r.cost <= remaining and (max_interventions is None or len(chosen)<max_interventions):
            chosen.append(r); used_sites.add(site); remaining-=float(r.cost)
    selected=pd.DataFrame(chosen, columns=eligible.columns) if chosen else eligible.iloc[0:0].copy()
    return {"selected":selected,"total_score":float(selected.weighted_score.sum()),"total_cost":float(selected.cost.sum()),"remaining":float(budget-selected.cost.sum())}


def compare_milp_greedy(milp_result, greedy_result):
    z_m=float(milp_result["total_score"]); z_g=float(greedy_result["total_score"])
    improvement=None if np.isclose(z_g,0) else (z_m-z_g)/z_g*100
    return {"score_milp":z_m,"score_greedy":z_g,"cost_milp":float(milp_result["total_cost"]),"cost_greedy":float(greedy_result["total_cost"]),"remaining_milp":None,"remaining_greedy":float(greedy_result["remaining"]),"improvement_pct":improvement}


def budget_curve(scores, budgets, **kwargs):
    rows=[]
    for b in budgets:
        r=solve_milp(scores,b,**kwargs)
        rows.append({"budget":float(b),"score":r["total_score"],"cost":r["total_cost"],"sites":int(len(r["selected"])) if r["selected"] is not None else 0,"status":r["status"]})
    return pd.DataFrame(rows)

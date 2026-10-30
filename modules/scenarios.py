from __future__ import annotations
import numpy as np
import pandas as pd

SCENARIOS={
    "Normal Condition":{"label":"Normal Condition","risk_multiplier":1.0,"hydro_multiplier":1.0,"dry_extra":0.0,"landcover_factors":{}},
    "Dry Season":{"label":"Dry Season","risk_multiplier":1.25,"hydro_multiplier":1.30,"dry_extra":0.10,"landcover_factors":{}},
    "Elevated Fire Risk":{"label":"Elevated Fire Risk","risk_multiplier":1.0,"hydro_multiplier":1.0,"dry_extra":0.0,"landcover_factors":{"Bekas terbakar":1.40,"Semak":1.30,"Semak, akses sulit":1.30,"Kebun campuran":1.15,"Hutan sekunder":1.05}},
}


def apply_scenario(sites, interventions, scenario_name):
    sc=SCENARIOS[scenario_name]
    s=sites.copy(); i=interventions.copy()
    s["fire_risk_index"] = np.clip(s["fire_risk_index"].astype(float)*sc["risk_multiplier"],0,100)
    i["delta_fire_risk"] = np.maximum(0.0, i["delta_fire_risk"].astype(float) * sc["risk_multiplier"])
    if scenario_name=="Dry Season":
        # Illustrative drying penalty based on canal condition: 0.10 m for good to 0.30 m for absent/severely damaged.
        penalties={"Baik":0.10,"Rusak sebagian":0.18,"Rusak berat":0.25,"Tidak ada":0.30}
        s["groundwater_depth"] = s["groundwater_depth"] + s["canal_condition"].map(penalties).fillna(0.20)
        i["hydrological_improvement"] = i["hydrological_improvement"]*sc["hydro_multiplier"]
    elif scenario_name=="Elevated Fire Risk":
        factors=s["land_cover"].map(sc["landcover_factors"]).fillna(1.0)
        s["fire_risk_index"] = np.clip(s["fire_risk_index"]*factors,0,100)
    return s,i


def scenario_delta(base_sites, scenario_sites):
    merged=base_sites[["site_id","groundwater_depth","fire_risk_index"]].merge(scenario_sites[["site_id","groundwater_depth","fire_risk_index"]],on="site_id",suffixes=("_base","_scenario"))
    merged["depth_change"]=merged.groundwater_depth_scenario-merged.groundwater_depth_base
    merged["risk_change"]=merged.fire_risk_index_scenario-merged.fire_risk_index_base
    return merged

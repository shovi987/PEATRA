from __future__ import annotations
import numpy as np
import pandas as pd

DEFAULT_REFS = {"fire": 40.0, "hydro": 0.60, "ecology": 200.0}
DEFAULT_TARGET_DEPTH = 0.40


def normalize_reference(values, reference):
    values = np.asarray(values, dtype=float)
    return 100.0 * np.minimum(1.0, np.maximum(0.0, values / float(reference)))


def normalize_minmax(values):
    x = np.asarray(values, dtype=float)
    if len(x) == 0:
        return x
    lo, hi = np.nanmin(x), np.nanmax(x)
    if np.isclose(hi, lo):
        return np.full_like(x, 100.0 if hi > 0 else 0.0)
    return 100.0 * (x - lo) / (hi - lo)


def normalize_linear_max(values):
    x = np.asarray(values, dtype=float)
    if len(x) == 0:
        return x
    mx = np.nanmax(x)
    if mx <= 0:
        return np.zeros_like(x)
    return 100.0 * np.clip(x / mx, 0, 1)


def normalize(values, method="Reference scale", reference=None):
    reference = reference or 1.0
    if method == "Min-max":
        return normalize_minmax(values)
    if method == "Linear-max / SAW":
        return normalize_linear_max(values)
    return normalize_reference(values, reference)


def normalize_weights(w_fire: float, w_hydro: float, w_ecology: float) -> dict[str, float]:
    raw = np.array([max(0.0, w_fire), max(0.0, w_hydro), max(0.0, w_ecology)], dtype=float)
    if raw.sum() <= 0:
        raw[:] = [0.40, 0.35, 0.25]
    raw /= raw.sum()
    return {"fire": float(raw[0]), "hydro": float(raw[1]), "ecology": float(raw[2])}


def compute_scores(sites: pd.DataFrame, interventions: pd.DataFrame, target_depth=DEFAULT_TARGET_DEPTH,
                   weights=None, normalization="Reference scale", refs=None) -> pd.DataFrame:
    refs = refs or DEFAULT_REFS
    weights = weights or {"fire":0.40,"hydro":0.35,"ecology":0.25}
    s = sites.set_index("site_id")
    x = interventions.copy()
    x["delta_fire_raw"] = np.maximum(0.0, x["delta_fire_risk"].astype(float))
    depth_deficit = np.maximum(0.0, s.loc[x["site_id"], "groundwater_depth"].to_numpy(dtype=float) - float(target_depth))
    x["hydro_raw"] = np.minimum(np.maximum(0.0, x["hydrological_improvement"].astype(float)), depth_deficit)
    sens = s.loc[x["site_id"], "ecological_sensitivity"].to_numpy(dtype=float)
    x["ecology_raw"] = (sens / 100.0) * x["ecological_area_benefit"].astype(float)
    x["fire_score"] = normalize(x["delta_fire_raw"], normalization, refs["fire"])
    x["hydro_score"] = normalize(x["hydro_raw"], normalization, refs["hydro"])
    x["ecology_score"] = normalize(x["ecology_raw"], normalization, refs["ecology"])
    x["weighted_score"] = (weights["fire"]*x["fire_score"] + weights["hydro"]*x["hydro_score"] + weights["ecology"]*x["ecology_score"])
    x["technical_feasibility"] = x["technical_feasibility"].astype(int)
    return x


def intervention_table_for_site(scores: pd.DataFrame, site_id: str) -> pd.DataFrame:
    cols = ["action","cost","technical_feasibility","confidence_level","delta_fire_raw","hydro_raw","ecology_raw","fire_score","hydro_score","ecology_score","weighted_score"]
    return scores[scores.site_id.eq(site_id)][cols].copy()


def classify_site(row, priority_score):
    risk = float(row.fire_risk_index)
    depth = float(row.groundwater_depth)
    if risk >= 75 or depth >= 0.80:
        condition = "Kritis"
    elif risk >= 60 or depth >= 0.60:
        condition = "Rentan"
    elif risk >= 45 or depth > 0.40:
        condition = "Waspada"
    else:
        condition = "Relatif stabil"
    if priority_score >= 70:
        priority = "Tinggi"
    elif priority_score >= 45:
        priority = "Menengah"
    else:
        priority = "Rendah"
    return condition, priority

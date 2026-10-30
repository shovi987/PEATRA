from __future__ import annotations
from datetime import date
import pandas as pd


def validate_observation(row):
    errors=[]
    try:
        depth=float(row["groundwater_depth"])
        if not (0 <= depth <= 3): errors.append("Kedalaman muka air harus 0–3 m.")
    except Exception: errors.append("Kedalaman muka air tidak valid.")
    try:
        risk=float(row["fire_risk_index"])
        if not (0 <= risk <= 100): errors.append("Indeks risiko harus 0–100.")
    except Exception: errors.append("Indeks risiko tidak valid.")
    try:
        if int(row["hotspot_count"]) < 0: errors.append("Jumlah titik panas tidak boleh negatif.")
    except Exception: errors.append("Jumlah titik panas tidak valid.")
    return errors


def add_observation(monitoring, row):
    errors=validate_observation(row)
    if errors: raise ValueError(" ".join(errors))
    df=monitoring.copy()
    oid=f"OBS-{len(df)+1:03d}"
    record={"observation_id":oid, **row}
    return pd.concat([df,pd.DataFrame([record])],ignore_index=True)

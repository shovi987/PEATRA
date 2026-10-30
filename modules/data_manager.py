from __future__ import annotations

from pathlib import Path
import json
from datetime import date
import pandas as pd
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"

SITES_FILE = DATA_DIR / "sites.csv"
INTERVENTIONS_FILE = DATA_DIR / "interventions.csv"
MONITORING_FILE = DATA_DIR / "monitoring.csv"
GEOMETRY_FILE = DATA_DIR / "geometry.csv"

DEFAULT_SITES = pd.DataFrame([
    ["A1", "Lokasi A1", "Semak", "Rusak sebagian", 0.78, 70, 78, 42, "Sedang", "ILLUSTRATIVE — demo sintetis"],
    ["A2", "Lokasi A2", "Bekas terbakar", "Rusak berat", 0.94, 82, 92, 58, "Sulit", "ILLUSTRATIVE — demo sintetis"],
    ["B1", "Lokasi B1", "Hutan sekunder", "Rusak sebagian", 0.58, 57, 66, 36, "Mudah", "ILLUSTRATIVE — demo sintetis"],
    ["B2", "Lokasi B2", "Semak, akses sulit", "Tidak ada", 0.74, 76, 84, 48, "Sulit", "ILLUSTRATIVE — demo sintetis"],
    ["C1", "Lokasi C1", "Hutan sekunder", "Baik", 0.38, 34, 48, 28, "Mudah", "ILLUSTRATIVE — demo sintetis"],
    ["C2", "Lokasi C2", "Kebun campuran", "Rusak sebagian", 0.48, 52, 61, 32, "Sedang", "ILLUSTRATIVE — demo sintetis"],
], columns=["site_id","site_name","land_cover","canal_condition","groundwater_depth","fire_risk_index","ecological_sensitivity","affected_area","accessibility","data_provenance"])

ACTIONS = ["Repair Existing Canal Block", "New Canal Block Construction"]

# Deliberately varied illustrative inputs so the portfolio problem has real trade-offs.
INTERVENTION_ROWS = [
    ["A1", "Repair Existing Canal Block", 350_000_000, 24, 0.48, 34, 1, "High"],
    ["A1", "New Canal Block Construction", 600_000_000, 32, 0.57, 42, 1, "Medium"],
    ["A2", "Repair Existing Canal Block", 320_000_000, 28, 0.52, 39, 1, "High"],
    ["A2", "New Canal Block Construction", 590_000_000, 38, 0.60, 51, 1, "High"],
    ["B1", "Repair Existing Canal Block", 300_000_000, 18, 0.35, 29, 1, "High"],
    ["B1", "New Canal Block Construction", 540_000_000, 26, 0.45, 37, 1, "Medium"],
    ["B2", "Repair Existing Canal Block", 360_000_000, 27, 0.43, 36, 0, "Low"],
    ["B2", "New Canal Block Construction", 620_000_000, 36, 0.56, 47, 1, "Medium"],
    ["C1", "Repair Existing Canal Block", 240_000_000, 10, 0.20, 18, 1, "High"],
    ["C1", "New Canal Block Construction", 480_000_000, 16, 0.30, 24, 1, "Medium"],
    ["C2", "Repair Existing Canal Block", 310_000_000, 17, 0.29, 26, 1, "High"],
    ["C2", "New Canal Block Construction", 520_000_000, 24, 0.40, 34, 1, "Medium"],
]
DEFAULT_INTERVENTIONS = pd.DataFrame(INTERVENTION_ROWS, columns=["site_id","action","cost","delta_fire_risk","hydrological_improvement","ecological_area_benefit","technical_feasibility","confidence_level"])

DEFAULT_MONITORING = pd.DataFrame([
    ["OBS-001", "A1", "2026-09-12", 0.74, "Rusak sebagian", 66, 3, "Tervalidasi", "Penurunan risiko terpantau; verifikasi lapangan ilustratif."],
    ["OBS-002", "A2", "2026-09-18", 0.88, "Rusak berat", 79, 6, "Tervalidasi", "Kondisi masih memerlukan prioritas tinggi."],
    ["OBS-003", "B1", "2026-10-01", 0.55, "Rusak sebagian", 54, 1, "Tervalidasi", "Data demo untuk pengujian alur monitoring."],
    ["OBS-004", "C2", "2026-10-10", 0.46, "Rusak sebagian", 49, 1, "Draft", "Belum diverifikasi."],
], columns=["observation_id","site_id","observation_date","groundwater_depth","canal_condition","fire_risk_index","hotspot_count","validation_status","notes"])

DEFAULT_GEOMETRY = pd.DataFrame([
    ["A1", "(-0.02, -0.01),(-0.01, 0.02),(0.01, 0.01),(0.02,-0.02)"],
    ["A2", "(-0.60, 0.25),(-0.48, 0.52),(-0.22, 0.43),(-0.28, 0.14)"],
    ["B1", "(0.25, 0.48),(0.48, 0.55),(0.62,0.30),(0.40,0.18)"],
    ["B2", "(-0.70,-0.52),(-0.45,-0.42),(-0.40,-0.70),(-0.68,-0.76)"],
    ["C1", "(0.48,-0.56),(0.72,-0.46),(0.77,-0.72),(0.52,-0.82)"],
    ["C2", "(-0.10,-0.38),(0.16,-0.34),(0.22,-0.60),(-0.04,-0.70)"],
], columns=["site_id","schematic_geometry"])


def ensure_demo_files() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    if not SITES_FILE.exists(): DEFAULT_SITES.to_csv(SITES_FILE, index=False)
    if not INTERVENTIONS_FILE.exists(): DEFAULT_INTERVENTIONS.to_csv(INTERVENTIONS_FILE, index=False)
    if not MONITORING_FILE.exists(): DEFAULT_MONITORING.to_csv(MONITORING_FILE, index=False)
    if not GEOMETRY_FILE.exists(): DEFAULT_GEOMETRY.to_csv(GEOMETRY_FILE, index=False)


def load_data() -> dict[str, pd.DataFrame]:
    ensure_demo_files()
    sites = pd.read_csv(SITES_FILE)
    interventions = pd.read_csv(INTERVENTIONS_FILE)
    monitoring = pd.read_csv(MONITORING_FILE)
    geometry = pd.read_csv(GEOMETRY_FILE)
    return {"sites": sites, "interventions": interventions, "monitoring": monitoring, "geometry": geometry}


def reset_demo_files() -> dict[str, pd.DataFrame]:
    DEFAULT_SITES.to_csv(SITES_FILE, index=False)
    DEFAULT_INTERVENTIONS.to_csv(INTERVENTIONS_FILE, index=False)
    DEFAULT_MONITORING.to_csv(MONITORING_FILE, index=False)
    DEFAULT_GEOMETRY.to_csv(GEOMETRY_FILE, index=False)
    return load_data()


def apply_validated_monitoring(sites: pd.DataFrame, monitoring: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Only validated observations can update active site data."""
    active = sites.copy()
    audit = []
    if monitoring.empty:
        return active, pd.DataFrame(audit)
    monitoring = monitoring.copy()
    monitoring["observation_date"] = pd.to_datetime(monitoring["observation_date"], errors="coerce")
    valid = monitoring[monitoring["validation_status"].astype(str).str.lower().eq("tervalidasi")].sort_values("observation_date")
    for _, row in valid.iterrows():
        mask = active["site_id"].eq(row["site_id"])
        if not mask.any():
            continue
        idx = active.index[mask][0]
        before = active.loc[idx, ["groundwater_depth","canal_condition","fire_risk_index"]].to_dict()
        active.loc[idx, "groundwater_depth"] = float(row["groundwater_depth"])
        active.loc[idx, "canal_condition"] = row["canal_condition"]
        active.loc[idx, "fire_risk_index"] = float(row["fire_risk_index"])
        after = active.loc[idx, ["groundwater_depth","canal_condition","fire_risk_index"]].to_dict()
        audit.append({"observation_id": row["observation_id"], "site_id": row["site_id"], "date": row["observation_date"].date().isoformat(), "before": before, "after": after})
    return active, pd.DataFrame(audit)


def data_summary(data: dict[str, pd.DataFrame]) -> dict:
    sites = data["sites"]
    return {
        "sites": int(len(sites)),
        "area_ha": float(sites["affected_area"].sum()),
        "avg_risk": float(sites["fire_risk_index"].mean()),
        "validated_monitoring": int(data["monitoring"]["validation_status"].astype(str).str.lower().eq("tervalidasi").sum()),
    }

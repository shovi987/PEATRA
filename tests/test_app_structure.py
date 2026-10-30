from pathlib import Path
import pandas as pd

ROOT=Path(__file__).resolve().parents[1]


def test_required_project_files_exist():
    required=[ROOT/'app.py',ROOT/'requirements.txt',ROOT/'README.md',ROOT/'assets/peatra_logo.svg']
    required += [ROOT/'data'/x for x in ['sites.csv','interventions.csv','monitoring.csv','geometry.csv']]
    required += [ROOT/'modules'/x for x in ['data_manager.py','scoring.py','optimization.py','scenarios.py','sensitivity.py','monitoring.py','visualizations.py']]
    required += [ROOT/'pages'/x for x in ['dashboard.py','peatland_map.py','assessment.py','diagnosis.py','comparison.py','optimization.py','budget.py','scenario.py','monitoring_page.py','methodology.py','reports.py']]
    assert all(p.exists() for p in required)


def test_demo_dataset_shape_and_required_columns():
    sites=pd.read_csv(ROOT/'data/sites.csv'); interventions=pd.read_csv(ROOT/'data/interventions.csv'); monitoring=pd.read_csv(ROOT/'data/monitoring.csv')
    assert sites.site_id.tolist()==['A1','A2','B1','B2','C1','C2']
    assert {'site_id','land_cover','canal_condition','groundwater_depth','fire_risk_index','ecological_sensitivity','affected_area','accessibility','data_provenance'} <= set(sites.columns)
    assert {'site_id','action','cost','delta_fire_risk','hydrological_improvement','ecological_area_benefit','technical_feasibility','confidence_level'} <= set(interventions.columns)
    assert {'observation_id','site_id','observation_date','groundwater_depth','canal_condition','fire_risk_index','hotspot_count','validation_status','notes'} <= set(monitoring.columns)

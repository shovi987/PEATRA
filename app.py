from __future__ import annotations
import sys
from pathlib import Path

ROOT=Path(__file__).resolve().parent
if str(ROOT) not in sys.path: sys.path.insert(0,str(ROOT))

import streamlit as st
from modules.data_manager import load_data, reset_demo_files, apply_validated_monitoring, SITES_FILE, MONITORING_FILE
from modules.scoring import compute_scores, normalize_weights, DEFAULT_TARGET_DEPTH
from modules.optimization import solve_milp, greedy_baseline
from modules.ui import inject_css, sidebar, topbar

st.set_page_config(page_title="PEATRA — Restoration Optimizer",page_icon="P",layout="wide",initial_sidebar_state="expanded")
inject_css()


def init_state():
    if "data" not in st.session_state:
        st.session_state.data=load_data()
    if "page" not in st.session_state: st.session_state.page="Dashboard"
    if "budget" not in st.session_state: st.session_state.budget=1_000_000_000
    if "weights" not in st.session_state: st.session_state.weights={"fire":0.40,"hydro":0.35,"ecology":0.25}
    if "normalization" not in st.session_state: st.session_state.normalization="Reference scale"
    if "target_depth" not in st.session_state: st.session_state.target_depth=DEFAULT_TARGET_DEPTH
    if "max_interventions" not in st.session_state: st.session_state.max_interventions=None
    if "mandatory_sites" not in st.session_state: st.session_state.mandatory_sites=[]
    if "forbidden_actions" not in st.session_state: st.session_state.forbidden_actions=[]
    if "scenario" not in st.session_state: st.session_state.scenario="Normal Condition"
    recalc()


def recalc():
    d=st.session_state.data
    # Keep active data aligned with validated monitoring at calculation time.
    active_sites,_=apply_validated_monitoring(d["sites"],d["monitoring"])
    d["sites"]=active_sites
    scores=compute_scores(active_sites,d["interventions"],target_depth=st.session_state.target_depth,weights=st.session_state.weights,normalization=st.session_state.normalization)
    result=solve_milp(scores,st.session_state.budget,max_interventions=st.session_state.max_interventions,mandatory_sites=st.session_state.mandatory_sites,forbidden_actions=st.session_state.forbidden_actions)
    greedy=greedy_baseline(scores,st.session_state.budget,max_interventions=st.session_state.max_interventions,mandatory_sites=st.session_state.mandatory_sites,forbidden_actions=st.session_state.forbidden_actions)
    st.session_state.scores=scores
    st.session_state.result=result
    st.session_state.greedy=greedy


def ctx():
    return {
        "data":st.session_state.data,"scores":st.session_state.scores,"result":st.session_state.result,"greedy":st.session_state.greedy,
        "budget":st.session_state.budget,"weights":st.session_state.weights,"normalization":st.session_state.normalization,
        "target_depth":st.session_state.target_depth,"max_interventions":st.session_state.max_interventions,
        "mandatory_sites":st.session_state.mandatory_sites,"forbidden_actions":st.session_state.forbidden_actions,"scenario":st.session_state.scenario,
        "run_optimization":lambda: recalc(),
        "set_budget":set_budget,"apply_parameters":apply_parameters,"set_normalization":set_normalization,"set_scenario":set_scenario,
        "persist_monitoring":persist_monitoring,"apply_monitoring_and_reoptimize":apply_monitoring_and_reoptimize,"reset_data":reset_data,
    }


def set_budget(budget):
    st.session_state.budget=float(budget); recalc()


def apply_parameters(budget,wr,ww,we,max_n,mandatory,forbidden,target_depth):
    st.session_state.budget=float(budget)
    st.session_state.weights=normalize_weights(wr,ww,we)
    st.session_state.max_interventions=max_n
    st.session_state.mandatory_sites=list(mandatory)
    st.session_state.forbidden_actions=list(forbidden)
    st.session_state.target_depth=float(target_depth)
    recalc()


def set_normalization(method):
    st.session_state.normalization=method; recalc()

def set_scenario(scenario):
    st.session_state.scenario=scenario


def persist_monitoring():
    st.session_state.data["monitoring"].to_csv(MONITORING_FILE,index=False)


def apply_monitoring_and_reoptimize():
    sites,audit=apply_validated_monitoring(st.session_state.data["sites"],st.session_state.data["monitoring"])
    st.session_state.data["sites"]=sites
    sites.to_csv(SITES_FILE,index=False)
    st.session_state.data["audit"]=audit
    recalc()


def reset_data():
    st.session_state.data=reset_demo_files()
    st.session_state.budget=1_000_000_000
    st.session_state.weights={"fire":0.40,"hydro":0.35,"ecology":0.25}
    st.session_state.normalization="Reference scale"
    st.session_state.target_depth=DEFAULT_TARGET_DEPTH
    st.session_state.max_interventions=None; st.session_state.mandatory_sites=[]; st.session_state.forbidden_actions=[]
    recalc()

init_state()
current=st.session_state.page
sidebar(current)

from pages.dashboard import render as dashboard
from pages.peatland_map import render as peatland_map
from pages.assessment import render as assessment
from pages.diagnosis import render as diagnosis
from pages.comparison import render as comparison
from pages.optimization import render as optimization
from pages.budget import render as budget
from pages.scenario import render as scenario
from pages.monitoring_page import render as monitoring
from pages.methodology import render as methodology
from pages.reports import render as reports

views={"Dashboard":dashboard,"Peatland Map":peatland_map,"Peatland Assessment":assessment,"Site Diagnosis":diagnosis,"Intervention Comparison":comparison,"Optimization Engine":optimization,"Budget Simulator":budget,"Scenario Simulator":scenario,"Monitoring":monitoring,"Data & Methodology":methodology,"Reports & Settings":reports}
views.get(current,dashboard)(ctx())

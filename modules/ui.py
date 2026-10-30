from __future__ import annotations
import html
import json
import pandas as pd
import streamlit as st

COLORS={"green":"#84E488","green2":"#6BCE90","teal":"#54B79A","teal2":"#409DA1","blue":"#2F698B","navy":"#213A75","bg":"#F7FAF8","orange":"#E8A06A","red":"#D95C5C"}

PAGES=[
    ("Dashboard","Overview"),("Peatland Map","Map"),("Peatland Assessment","Assessment"),("Site Diagnosis","Diagnosis"),
    ("Intervention Comparison","Comparison"),("Optimization Engine","Optimization"),("Budget Simulator","Budget"),("Scenario Simulator","Scenario"),
    ("Monitoring","Monitoring"),("Data & Methodology","Methodology"),("Reports & Settings","Reports"),
]


def inject_css():
    st.markdown(f"""
    <style>
    :root {{ --peatra-bg:{COLORS['bg']}; --peatra-navy:{COLORS['navy']}; --peatra-teal:{COLORS['teal2']}; --peatra-green:{COLORS['green2']}; --peatra-border:#DCE8E3; }}
    html,body,[class*="css"] {{ font-family:Inter,Arial,sans-serif; }}
    .stApp {{ background:var(--peatra-bg); color:var(--peatra-navy); }}
    [data-testid="stHeader"] {{ background:transparent; }}
    [data-testid="stSidebar"] {{ background:#FFFFFF; border-right:1px solid #E1EBE7; }}
    [data-testid="stSidebarContent"] {{ padding:22px 16px; }}
    .brand {{ display:flex; gap:11px; align-items:center; padding:2px 7px 18px; border-bottom:1px solid #E6EFEC; margin-bottom:14px; }}
    .brand-mark {{ width:36px;height:36px;border-radius:11px;background:linear-gradient(145deg,#84E488,#409DA1); position:relative; }}
    .brand-mark:after {{ content:'P'; color:white; font-weight:800; position:absolute; left:11px; top:7px; font-size:18px; }}
    .brand-title {{ font-size:20px;font-weight:800;letter-spacing:.2px;color:#213A75;line-height:1; }}
    .brand-sub {{ font-size:9px;color:#587277;margin-top:5px;line-height:1.25; }}
    .nav-label {{ font-size:10px;text-transform:uppercase;letter-spacing:.11em;color:#8AA09B;font-weight:700;padding:6px 8px; }}
    .page-pill {{ padding:8px 10px;border-radius:10px;font-size:12px;color:#496B72;margin:2px 0; }}
    .page-pill.active {{ background:#E4F4EF;color:#176A70;font-weight:700; }}
    .topbar {{ display:flex;align-items:center;justify-content:space-between; gap:20px; background:white;border:1px solid var(--peatra-border);border-radius:16px;padding:15px 18px;margin-bottom:14px; }}
    .eyebrow {{ font-size:11px;color:#648086;font-weight:600;margin-bottom:4px; }}
    .title {{ font-size:25px;font-weight:750;color:#213A75;letter-spacing:-.03em; }}
    .topmeta {{ display:flex;gap:8px;align-items:center;flex-wrap:wrap;justify-content:flex-end; }}
    .badge {{ display:inline-flex;align-items:center;gap:6px;padding:7px 10px;border-radius:999px;font-size:10px;font-weight:700;border:1px solid #DCE8E3;background:#F7FAF8;color:#466B70; }}
    .badge.green {{ background:#E8F7ED;color:#22745B;border-color:#CBEBD7; }}
    .badge.blue {{ background:#E8F1F7;color:#2F698B;border-color:#D4E5EF; }}
    .badge.orange {{ background:#FFF3E9;color:#9A5B28;border-color:#F2DDC9; }}
    .demo-banner {{ background:#EFF8F3;border:1px solid #CBE9D8;border-left:4px solid #54B79A;border-radius:12px;padding:10px 13px;margin:0 0 14px;color:#456B70;font-size:11px; }}
    .card {{ background:white;border:1px solid var(--peatra-border);border-radius:14px;padding:15px 16px;box-shadow:0 2px 8px rgba(33,58,117,.025); }}
    .section-title {{ font-size:14px;font-weight:750;color:#213A75;margin:0 0 10px; }}
    .muted {{ color:#71868B;font-size:11px;line-height:1.5; }}
    .kpi-grid {{ display:grid;grid-template-columns:repeat(5,minmax(0,1fr));gap:10px;margin-bottom:14px; }}
    .kpi {{ background:white;border:1px solid var(--peatra-border);border-radius:13px;padding:13px 14px;min-height:94px; }}
    .kpi .label {{ font-size:10px;color:#6D8388;font-weight:600; }}
    .kpi .value {{ font-size:23px;font-weight:800;color:#213A75;margin-top:8px; }}
    .kpi .delta {{ font-size:9px;color:#4B7C73;margin-top:5px; }}
    .two-col {{ display:grid;grid-template-columns:1.25fr .75fr;gap:14px; }}
    .three-col {{ display:grid;grid-template-columns:1fr 1fr 1fr;gap:14px; }}
    .mini-stat {{ display:flex;justify-content:space-between;padding:9px 0;border-bottom:1px solid #EDF2F0;font-size:11px; }}
    .mini-stat:last-child {{ border-bottom:0; }}
    .table-wrap {{ overflow-x:auto;border:1px solid var(--peatra-border);border-radius:12px;background:white; }}
    .footer-note {{ font-size:9px;color:#829398;padding:12px 2px 4px; }}
    .stButton>button {{ border-radius:9px;border:1px solid #CFE2DD;background:white;color:#2F698B;font-weight:700;font-size:11px;min-height:35px; }}
    .stButton>button[kind="primary"] {{ background:#2F698B;border-color:#2F698B;color:white; }}
    .stDownloadButton>button {{ border-radius:9px;font-size:11px; }}
    [data-testid="stMetricValue"] {{ color:#213A75; }}
    [data-testid="stDataFrame"] {{ border-radius:10px; overflow:hidden; }}
    @media (max-width:1100px) {{ .kpi-grid {{ grid-template-columns:repeat(3,1fr); }} .two-col,.three-col {{ grid-template-columns:1fr; }} }}
    @media (max-width:700px) {{ .kpi-grid {{ grid-template-columns:repeat(2,1fr); }} .title {{ font-size:20px; }} }}
    </style>
    """, unsafe_allow_html=True)


def sidebar(current):
    with st.sidebar:
        st.markdown('<div class="brand"><div class="brand-mark"></div><div><div class="brand-title">PEATRA</div><div class="brand-sub">Adaptive Multi-Objective<br>Peatland Restoration Optimizer</div></div></div>', unsafe_allow_html=True)
        st.markdown('<div class="nav-label">Workspace</div>', unsafe_allow_html=True)
        for label, key in PAGES:
            active=label==current
            if st.button(label, key=f"nav_{key}", use_container_width=True, type="primary" if active else "secondary"):
                st.session_state["page"]=label
                st.rerun()
        st.markdown('<div class="nav-label" style="margin-top:14px">Data status</div>', unsafe_allow_html=True)
        st.markdown('<div class="page-pill active">● Demo dataset loaded</div><div class="page-pill">Pelalawan · Riau</div>', unsafe_allow_html=True)


def topbar(title, subtitle="Pilot: Kabupaten Pelalawan, Riau"):
    st.markdown(f'''<div class="topbar"><div><div class="eyebrow">{html.escape(subtitle)}</div><div class="title">{html.escape(title)}</div></div><div class="topmeta"><span class="badge green">● DATA ILLUSTRATIVE</span><span class="badge blue">Model: MILP · HiGHS</span><span class="badge">Updated: session state</span></div></div>''', unsafe_allow_html=True)
    st.markdown('<div class="demo-banner"><b>ILLUSTRATIVE DATASET</b> — seluruh data demo dan hasil simulasi pada aplikasi ini bersifat ilustratif, bukan hasil survei lapangan atau prediksi ilmiah.</div>', unsafe_allow_html=True)


def card(content, cls="card"):
    st.markdown(f'<div class="{cls}">{content}</div>', unsafe_allow_html=True)


def kpis(items):
    body='<div class="kpi-grid">'
    for label,value,delta in items:
        body+=f'<div class="kpi"><div class="label">{html.escape(str(label))}</div><div class="value">{html.escape(str(value))}</div><div class="delta">{html.escape(str(delta))}</div></div>'
    body+='</div>'
    st.markdown(body,unsafe_allow_html=True)


def section_heading(title, caption=None):
    st.markdown(f'<div class="section-title">{html.escape(title)}</div>',unsafe_allow_html=True)
    if caption: st.markdown(f'<div class="muted" style="margin:-4px 0 10px">{html.escape(caption)}</div>',unsafe_allow_html=True)


def money(v):
    return f"Rp {v:,.0f}".replace(",",".")


def dataframe(df, height=320, hide_index=True):
    st.dataframe(df,use_container_width=True,height=height,hide_index=hide_index)


def json_download(obj, filename):
    st.download_button("Download JSON",json.dumps(obj,indent=2,default=str).encode(),file_name=filename,mime="application/json")

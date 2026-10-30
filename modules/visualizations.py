from __future__ import annotations
import ast
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

COLORS={"green":"#84E488","green2":"#6BCE90","teal":"#54B79A","teal2":"#409DA1","blue":"#2F698B","navy":"#213A75","bg":"#F7FAF8","orange":"#E8A06A","red":"#D95C5C"}


def apply_layout(fig, height=300):
    fig.update_layout(height=height, margin=dict(l=8,r=8,t=35,b=8), paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font=dict(family="Inter, Arial",color=COLORS["navy"]), legend=dict(orientation="h",y=1.08,x=0))
    fig.update_xaxes(showgrid=False, zeroline=False)
    fig.update_yaxes(gridcolor="#E8EFEC", zeroline=False)
    return fig


def risk_chart(sites):
    d=sites.sort_values("fire_risk_index",ascending=True)
    fig=px.bar(d,x="fire_risk_index",y="site_id",orientation="h",text="fire_risk_index",labels={"fire_risk_index":"Fire-risk index","site_id":""})
    fig.update_traces(marker_color=COLORS["teal2"],textposition="outside")
    return apply_layout(fig,300)


def intervention_distribution(selected):
    if selected.empty:
        return apply_layout(go.Figure(),240)
    d=selected.groupby("action").size().reset_index(name="count")
    fig=px.pie(d,names="action",values="count",hole=.62)
    fig.update_traces(marker=dict(colors=[COLORS["teal2"],COLORS["green2"]]),textinfo="percent",hovertemplate="%{label}: %{value} lokasi<extra></extra>")
    return apply_layout(fig,250)


def benefit_comparison(site_scores):
    d=site_scores.melt(id_vars=["action"],value_vars=["fire_score","hydro_score","ecology_score"],var_name="criterion",value_name="score")
    d["criterion"]=d.criterion.map({"fire_score":"Fire risk","hydro_score":"Hydrology","ecology_score":"Ecology"})
    fig=px.bar(d,x="criterion",y="score",color="action",barmode="group",labels={"score":"Score (0–100)","criterion":""})
    fig.update_traces(marker_line_width=0)
    return apply_layout(fig,310)


def budget_curve(curve):
    fig=go.Figure()
    fig.add_trace(go.Scatter(x=curve.budget,y=curve.score,mode="lines+markers",name="MILP",line=dict(color=COLORS["blue"],width=3)))
    fig.update_layout(xaxis_title="Anggaran (Rp)",yaxis_title="Total model benefit")
    return apply_layout(fig,320)


def monitoring_chart(history):
    if history.empty: return apply_layout(go.Figure(),280)
    d=history.copy(); d["observation_date"]=pd.to_datetime(d.observation_date)
    fig=px.line(d,x="observation_date",y="groundwater_depth",color="site_id",markers=True,labels={"groundwater_depth":"Groundwater depth (m)","observation_date":""})
    fig.add_hline(y=0.40,line_dash="dot",line_color=COLORS["teal2"],annotation_text="0.40 m reference")
    return apply_layout(fig,300)


def scenario_radar(summary):
    fig=go.Figure()
    for _,r in summary.iterrows():
        vals=[r["avg_risk"],r["avg_depth"]*100,r["score"]]
        fig.add_trace(go.Scatterpolar(r=vals,theta=["Risk","Depth ×100","Benefit"],fill="toself",name=r["scenario"]))
    fig.update_layout(polar=dict(radialaxis=dict(visible=True,range=[0,100])),showlegend=True)
    return apply_layout(fig,360)


def schematic_map(sites, selected_ids=None, color_by="fire_risk_index"):
    selected_ids=set(selected_ids or [])
    fig=go.Figure()
    # A schematic coordinate space; explicitly not geographic.
    positions={"A1":(0,0),"A2":(-0.55,0.40),"B1":(0.45,0.45),"B2":(-0.60,-0.55),"C1":(0.60,-0.58),"C2":(0.05,-0.50)}
    for _,r in sites.iterrows():
        x,y=positions.get(r.site_id,(0,0))
        val=float(r[color_by]) if color_by in r else 0
        fig.add_trace(go.Scatter(x=[x],y=[y],mode="markers+text",text=[r.site_id],textposition="top center",name=r.site_id,
                                 marker=dict(size=26,line=dict(width=3,color="white"),color=val,colorscale=[[0,COLORS["green"]],[0.5,COLORS["teal"]],[1,COLORS["red"]]],cmin=0,cmax=100),
                                 hovertemplate=f"<b>{r.site_name}</b><br>Risiko: {r.fire_risk_index:.0f}<br>Depth: {r.groundwater_depth:.2f} m<extra></extra>"))
        if r.site_id in selected_ids:
            fig.add_shape(type="circle",x0=x-.08,x1=x+.08,y0=y-.08,y1=y+.08,line=dict(color=COLORS["navy"],width=3,dash="dot"))
    # faint canals
    fig.add_trace(go.Scatter(x=[-0.75,-0.2,0.35,0.78],y=[-0.65,-0.1,0.05,-0.55],mode="lines",name="Canal network",line=dict(color=COLORS["teal2"],width=2,dash="dash"),hoverinfo="skip"))
    fig.update_xaxes(visible=False); fig.update_yaxes(visible=False,scaleanchor="x",scaleratio=1)
    fig.update_layout(showlegend=False)
    return apply_layout(fig,360)

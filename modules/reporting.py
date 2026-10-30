from __future__ import annotations
import io, json, html
from datetime import datetime
import pandas as pd
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet


def results_payload(result, greedy, scenario="Normal Condition", weights=None, budget=None):
    selected=result["selected"]
    return {
        "generated_at":datetime.now().isoformat(timespec="seconds"),
        "dataset":"ILLUSTRATIVE",
        "scenario":scenario,
        "budget":budget,
        "weights":weights,
        "solver_status":result["status"],
        "solver_message":result["message"],
        "optimality_gap":result.get("optimality_gap"),
        "total_score":result["total_score"],
        "total_cost":result["total_cost"],
        "selected_interventions":selected[["site_id","action","cost","weighted_score"]].to_dict(orient="records") if not selected.empty else [],
        "greedy_score":greedy["total_score"],
        "greedy_cost":greedy["total_cost"],
        "constraint_errors":result.get("errors",[]),
    }


def html_report(payload):
    rows=''.join(f'<tr><td>{html.escape(str(r["site_id"]))}</td><td>{html.escape(str(r["action"]))}</td><td>Rp {r["cost"]:,.0f}</td><td>{r["weighted_score"]:.2f}</td></tr>' for r in payload["selected_interventions"])
    return f'''<!doctype html><html><head><meta charset="utf-8"><title>PEATRA Report</title><style>body{{font-family:Arial;color:#213A75;margin:40px}}h1{{margin-bottom:4px}}.tag{{background:#E8F7ED;padding:6px 10px;border-radius:12px;display:inline-block;font-size:12px}}table{{width:100%;border-collapse:collapse;margin-top:20px}}td,th{{border:1px solid #DCE8E3;padding:8px;text-align:left}}th{{background:#EFF8F3}}.muted{{color:#6D8388;font-size:12px}}</style></head><body><h1>PEATRA Optimization Report</h1><div class="tag">ILLUSTRATIVE DATASET</div><p class="muted">Generated {payload["generated_at"]} · {payload["scenario"]}</p><h2>Optimization result</h2><p>Solver status: <b>{payload["solver_status"]}</b><br>Total model benefit: <b>{payload["total_score"]:.2f}</b><br>Total cost: <b>Rp {payload["total_cost"]:,.0f}</b><br>Budget: <b>Rp {payload["budget"]:,.0f}</b></p><h2>Selected interventions</h2><table><tr><th>Site</th><th>Action</th><th>Cost</th><th>Weighted score</th></tr>{rows or '<tr><td colspan="4">No intervention selected.</td></tr>'}</table><h2>Method note</h2><p class="muted">Scores represent modeled benefits, not direct measurements of realized ecological impact. Demo data are illustrative.</p></body></html>'''


def pdf_report(payload):
    buf=io.BytesIO(); doc=SimpleDocTemplate(buf,pagesize=A4,rightMargin=36,leftMargin=36,topMargin=36,bottomMargin=36)
    styles=getSampleStyleSheet(); story=[Paragraph("PEATRA Optimization Report",styles["Title"]),Paragraph("ILLUSTRATIVE DATASET",styles["Heading3"]),Spacer(1,8)]
    story += [Paragraph(f"Scenario: {payload['scenario']}",styles["BodyText"]),Paragraph(f"Solver status: {payload['solver_status']}",styles["BodyText"]),Paragraph(f"Total model benefit: {payload['total_score']:.2f}",styles["BodyText"]),Paragraph(f"Total cost: Rp {payload['total_cost']:,.0f}",styles["BodyText"]),Paragraph(f"Budget: Rp {payload['budget']:,.0f}",styles["BodyText"]),Spacer(1,12)]
    data=[["Site","Action","Cost","Score"]]+[[r["site_id"],r["action"],f"Rp {r['cost']:,.0f}",f"{r['weighted_score']:.2f}"] for r in payload["selected_interventions"]]
    t=Table(data,colWidths=[55,230,90,60]); t.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),colors.HexColor('#EFF8F3')),('TEXTCOLOR',(0,0),(-1,0),colors.HexColor('#213A75')),('GRID',(0,0),(-1,-1),.4,colors.HexColor('#DCE8E3')),('FONTNAME',(0,0),(-1,0),'Helvetica-Bold'),('VALIGN',(0,0),(-1,-1),'TOP'),('FONTSIZE',(0,0),(-1,-1),8),('LEFTPADDING',(0,0),(-1,-1),6),('RIGHTPADDING',(0,0),(-1,-1),6)])); story.append(t); story.append(Spacer(1,14)); story.append(Paragraph("Scores are modeled benefits and do not represent direct ecological impact measurements. Demo inputs are illustrative.",styles["BodyText"])); doc.build(story); buf.seek(0); return buf.getvalue()

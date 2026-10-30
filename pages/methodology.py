import streamlit as st
from modules.ui import topbar,section_heading

def render(ctx):
    topbar("Data & Methodology")
    section_heading("Dataset")
    st.caption("CSV demo data can be edited here. Click Save to persist changes to the project data files.")
    tab1,tab2=st.tabs(["Sites","Interventions"])
    with tab1:
        edited_sites=st.data_editor(ctx["data"]["sites"],use_container_width=True,num_rows="dynamic",hide_index=True,key="sites_editor")
        if st.button("Save site dataset",type="primary"):
            edited_sites.to_csv(__import__("modules.data_manager",fromlist=["SITES_FILE"]).SITES_FILE,index=False)
            ctx["data"]["sites"]=edited_sites.copy(); ctx["run_optimization"](); st.success("Site dataset saved and model recalculated."); st.rerun()
    with tab2:
        edited_int=st.data_editor(ctx["data"]["interventions"],use_container_width=True,num_rows="dynamic",hide_index=True,key="interventions_editor")
        if st.button("Save intervention dataset",type="primary"):
            edited_int.to_csv(__import__("modules.data_manager",fromlist=["INTERVENTIONS_FILE"]).INTERVENTIONS_FILE,index=False)
            ctx["data"]["interventions"]=edited_int.copy(); ctx["run_optimization"](); st.success("Intervention dataset saved and model recalculated."); st.rerun()
    section_heading("Data provenance")
    st.markdown("Dataset demo mengikuti struktur Master Brief dan seluruh enam lokasi diberi label **ILLUSTRATIVE**. Tidak ada koordinat resmi yang disimulasikan sebagai fakta.")
    section_heading("Scoring formulas")
    st.latex(r"\Delta F_{ia}=\max(0,F_i-F_{ia})")
    st.latex(r"D_i=\max(0,d_i-d_{target}),\quad G_{ia}=\min(\max(0,\Delta h_{ia}),D_i)")
    st.latex(r"V_{ia}=(s_i/100)\times A_{ia}")
    st.latex(r"S(v)=100\times\min(1,\max(0,v/v_{ref}))")
    st.latex(r"U_{ia}=w_RR_{ia}+w_WW_{ia}+w_EE_{ia}")
    section_heading("MILP")
    st.latex(r"\max \sum_i\sum_a U_{ia}x_{ia}")
    st.latex(r"\sum_i\sum_a C_{ia}x_{ia}\le B,\quad \sum_a x_{ia}\le1,\quad x_{ia}\le q_{ia},\quad x_{ia}\in\{0,1\}")
    st.markdown("Solver: `scipy.optimize.milp` dengan HiGHS. Setelah solusi optimal ditemukan, tahap kedua meminimalkan biaya sambil mempertahankan skor optimal untuk tie-break.")
    section_heading("Normalization")
    method=st.selectbox("Active normalization",["Reference scale","Linear-max / SAW","Min-max"],index=["Reference scale","Linear-max / SAW","Min-max"].index(ctx["normalization"]))
    st.caption(f"Session saat ini menggunakan: {ctx['normalization']}. Metode alternatif dapat mengubah pemeringkatan dan portofolio optimal.")
    if method!=ctx["normalization"] and st.button("Apply normalization",type="primary"): ctx["set_normalization"](method); st.rerun()
    section_heading("Scenario assumptions")
    st.markdown("Dry Season: groundwater depth penalty 0.10–0.30 m sesuai kondisi sekat, fire-risk ×1.25, intervention hydrological effectiveness ×1.30. Elevated Fire Risk: land-cover factors 1.40 / 1.30 / 1.15 / 1.05. Semua faktor adalah asumsi simulasi ilustratif.")
    section_heading("Limitations")
    st.markdown("Skor merupakan manfaat model, bukan dampak ekologis aktual. Observasi before/after tidak membuktikan kausalitas. Reference depth 0,40 m dapat dikonfigurasi dan harus dibaca bersama konteks regulasi serta fungsi gambut yang relevan.")

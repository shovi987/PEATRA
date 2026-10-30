# PEATRA — Adaptive Multi-Objective Peatland Restoration Optimizer

PEATRA is a Streamlit decision-support application for prioritising peatland restoration interventions under budget, technical feasibility, fire-risk, hydrological and ecological criteria. The pilot is **Kabupaten Pelalawan, Riau**. All bundled demo data are explicitly **ILLUSTRATIVE** and are not field-survey results.

## 1. Run locally

```bash
python -m venv .venv
# Windows: .venv\\Scripts\\activate
# macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```

Open the local URL shown by Streamlit, normally `http://localhost:8501`.

## 2. Test the mathematical model

```bash
pytest -q
```

The tests cover reference normalisation, weight normalisation, budget constraints, one-action-per-site, technical feasibility, zero-budget behaviour, greedy baseline, and a brute-force cross-check against MILP for a small instance.

## 3. Project structure

- `app.py` — Streamlit entry point and shared session state.
- `data/` — illustrative CSV dataset.
- `modules/data_manager.py` — loading, reset, validated monitoring updates.
- `modules/scoring.py` — benefit calculations, normalisation and weighted score.
- `modules/optimization.py` — SciPy HiGHS MILP, two-stage tie-break, greedy baseline and validation.
- `modules/scenarios.py` — environmental scenarios.
- `modules/sensitivity.py` — cost sensitivity, Monte Carlo stability and regret matrix.
- `modules/monitoring.py` — monitoring validation and append operations.
- `modules/visualizations.py` — Plotly visualisations and schematic map.
- `modules/reporting.py` — HTML/PDF/JSON report generation.
- `pages/` — the 11 application pages.
- `assets/` — UI reference image and visual assets.
- `tests/` — automated mathematical tests.

## 4. Mathematical model

The implementation follows the Master Brief:

- Fire-risk reduction: `max(0, F_i - F_ia)`.
- Hydrological improvement: `min(max(0, Δh_ia), max(0, d_i - d_target))`.
- Ecological benefit: `(s_i / 100) × A_ia`.
- Default fixed-reference normalisation: fire 40 points, hydrology 0.60 m, ecology 200 ha-equivalent.
- Weighted score: `w_R R + w_W W + w_E E`, with weights automatically normalised to 1.
- Binary MILP: maximise total weighted benefit subject to budget, at-most-one intervention per site and technical feasibility, plus optional intervention-count, mandatory-site and forbidden-action constraints.
- Solver: `scipy.optimize.milp` / HiGHS.
- Greedy baseline: descending `U/C`, with explicit handling for zero-cost actions.
- Two-stage tie-break: after an optimal benefit is proven, minimise total cost while preserving that benefit.

The UI reports the solver status instead of calling every result “optimal”.

## 5. Important modelling notes

The 0.40 m reference depth is configurable. The app deliberately does not present it as a universal legal threshold for every peatland function. Scenario multipliers are illustrative assumptions. A before/after monitoring comparison is not treated as causal proof.

If official geographic coordinates are unavailable, PEATRA uses a **schematic map** and labels it accordingly; it does not invent official KHG boundaries or field coordinates.

## 6. GitHub deployment

1. Create a new GitHub repository.
2. Add the entire `PEATRA` folder to the repository.
3. Commit and push:

```bash
git init
git add .
git commit -m "Build PEATRA restoration optimizer"
git branch -M main
git remote add origin YOUR_REPOSITORY_URL
git push -u origin main
```

## 7. Streamlit Community Cloud

1. Sign in to Streamlit Community Cloud.
2. Choose **Create app**.
3. Select the GitHub repository, branch `main`, and `app.py` as the main file.
4. Deploy.
5. Future GitHub pushes can trigger application updates.

No paid API key or external service is required for the bundled demo dataset.

## 8. Demo data editing

The CSV files under `data/` are the canonical demo dataset. Monitoring records can be added in-app and persisted to `data/monitoring.csv`; validated monitoring can be applied to the active site dataset. The Reports & Settings page can reset the demo data to the bundled defaults.

## 9. Disclaimer

PEATRA is a mathematical decision-support prototype. Its scores represent modelled benefits, not direct ecological impact measurements. Replace the illustrative inputs with validated field/official datasets before using the application for operational decisions.

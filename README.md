# Well Production & Forecasting Studio

An educational Python oil-and-gas engineering app using synthetic daily well production data.

## Quick start

```bash
python -m venv .venv
# Windows PowerShell:
.venv\Scripts\Activate.ps1
# macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
python generate_sample.py
streamlit run app.py
```

The included `sample_production.csv` can be used immediately. Upload another CSV with the columns `date`, `oil_bopd`, `gas_mscfd`, and `water_bwpd`.

## Engineering methods

- Water cut (%) = 100 × water rate / (oil rate + water rate)
- Producing GOR (scf/stb) = 1000 × gas rate (Mscf/day) / oil rate (stb/day)
- Exponential decline: q(t) = qi × exp(-D × t), with D in day⁻¹
- Fitting: bounded nonlinear least squares using SciPy
- Cumulative oil: sum of daily rates, assuming each rate represents a full day's average production

## Limitations

No well downtime, irregular reporting, production constraints, shut-in normalization, uncertainty, economics, model selection, or physical validation. An in-sample R² is not proof of predictive accuracy. Not approved for field decisions.

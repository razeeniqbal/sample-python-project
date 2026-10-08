import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from engineering import prepare_data, fit_decline, make_forecast, exponential_rate

st.set_page_config(page_title='Well Production Studio', layout='wide')
st.title('Well Production & Forecasting Studio')
st.caption('Educational engineering prototype · Synthetic data · Not for operational decisions')

uploaded = st.file_uploader('Upload daily production CSV', type='csv')
source = uploaded if uploaded is not None else 'sample_production.csv'
try:
    df = prepare_data(pd.read_csv(source))
    fit = fit_decline(df)
except (ValueError, RuntimeError, OSError, pd.errors.ParserError) as exc:
    st.error(f'Could not analyze data: {exc}')
    st.stop()

forecast_days = st.slider('Forecast horizon (days)', 30, 365, 180, 30)
forecast = make_forecast(df, fit, forecast_days)
latest = df.iloc[-1]
cols = st.columns(4)
cols[0].metric('Latest oil rate', f'{latest.oil_bopd:,.1f} bopd')
cols[1].metric('Latest water cut', f'{latest.water_cut_pct:.1f}%')
cols[2].metric('Latest GOR', f'{latest.gor_scf_stb:,.0f} scf/stb')
cols[3].metric('Cumulative oil*', f'{latest.cumulative_oil_stb:,.0f} stb')

fig = go.Figure()
fig.add_scatter(x=df.date, y=df.oil_bopd, name='Observed oil rate', mode='lines+markers')
elapsed = (df.date - df.date.min()).dt.days
fig.add_scatter(x=df.date, y=exponential_rate(elapsed, fit['qi_bopd'], fit['decline_per_day']), name='Fitted exponential', line={'dash':'dash'})
fig.add_scatter(x=forecast.date, y=forecast.forecast_oil_bopd, name='Forecast', line={'dash':'dot'})
fig.update_layout(title='Oil production and exponential decline forecast', xaxis_title='Date', yaxis_title='Oil rate (bopd)', height=470)
st.plotly_chart(fig, use_container_width=True)

left, right = st.columns(2)
with left:
    st.subheader('Decline model diagnostics')
    st.write(f"Initial fitted rate: **{fit['qi_bopd']:.1f} bopd**")
    st.write(f"Nominal decline: **{fit['decline_per_day'] * 365 * 100:.2f}% / year**")
    st.write(f"R² (in-sample): **{fit['r2']:.3f}**")
with right:
    st.subheader('Data preview')
    st.dataframe(df.tail(10), use_container_width=True)

st.download_button('Download forecast CSV', forecast.to_csv(index=False), 'forecast.csv', 'text/csv')
st.info('Assumptions: daily average rates represent one-day volumes; no downtime handling, operating constraints, uncertainty bands or economic limits. Forecast extrapolates a fitted exponential decline and must be reviewed by a qualified engineer.')

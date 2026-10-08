"""Transparent engineering calculations for a learning/demo application."""
import numpy as np
import pandas as pd
from scipy.optimize import curve_fit

REQUIRED = {'date', 'oil_bopd', 'gas_mscfd', 'water_bwpd'}


def prepare_data(frame: pd.DataFrame) -> pd.DataFrame:
    missing = REQUIRED - set(frame.columns)
    if missing:
        raise ValueError(f'Missing required columns: {", ".join(sorted(missing))}')
    df = frame.copy()
    df['date'] = pd.to_datetime(df['date'], errors='raise')
    for col in REQUIRED - {'date'}:
        df[col] = pd.to_numeric(df[col], errors='raise')
        if not np.isfinite(df[col]).all() or (df[col] < 0).any():
            raise ValueError(f'{col} must contain finite non-negative values')
    if df['date'].duplicated().any():
        raise ValueError('Duplicate dates detected; aggregate or resolve them first')
    df = df.sort_values('date').reset_index(drop=True)
    if len(df) < 6:
        raise ValueError('At least six daily records are required')
    df['water_cut_pct'] = np.where(df['oil_bopd'] + df['water_bwpd'] > 0,
                                    100 * df['water_bwpd'] / (df['oil_bopd'] + df['water_bwpd']), np.nan)
    df['gor_scf_stb'] = np.where(df['oil_bopd'] > 0,
                                 1000 * df['gas_mscfd'] / df['oil_bopd'], np.nan)
    df['cumulative_oil_stb'] = df['oil_bopd'].cumsum()  # assumes daily rates represent one-day volumes
    return df


def exponential_rate(t_days, qi, decline_per_day):
    return qi * np.exp(-decline_per_day * np.asarray(t_days))


def fit_decline(df: pd.DataFrame):
    # Oil rate must be positive; shut-in/zero-rate periods require separate engineering treatment.
    valid = df.loc[df['oil_bopd'] > 0].copy()
    if len(valid) < 6:
        raise ValueError('At least six positive-rate observations required for fitting')
    t = (valid['date'] - df['date'].min()).dt.days.to_numpy(dtype=float)
    q = valid['oil_bopd'].to_numpy(dtype=float)
    if len(np.unique(t)) < 6:
        raise ValueError('Not enough distinct time observations')
    pars, _ = curve_fit(exponential_rate, t, q, p0=[float(q[0]), 0.001],
                        bounds=([0, 0], [np.inf, 1.0]), maxfev=20000)
    predicted = exponential_rate(t, *pars)
    ss_res = float(np.sum((q - predicted) ** 2))
    ss_tot = float(np.sum((q - q.mean()) ** 2))
    r2 = 1 - ss_res / ss_tot if ss_tot > 0 else float('nan')
    return {'qi_bopd': float(pars[0]), 'decline_per_day': float(pars[1]), 'r2': r2}


def make_forecast(df: pd.DataFrame, fit: dict, days: int = 180):
    last_date = df['date'].max()
    dates = pd.date_range(last_date + pd.Timedelta(days=1), periods=days, freq='D')
    elapsed = (dates - df['date'].min()).days.to_numpy()
    return pd.DataFrame({'date': dates, 'forecast_oil_bopd': exponential_rate(elapsed, fit['qi_bopd'], fit['decline_per_day'])})

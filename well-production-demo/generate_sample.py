from pathlib import Path
import numpy as np
import pandas as pd
rng = np.random.default_rng(42)
t = np.arange(365)
oil = 1200 * np.exp(-0.0015*t) * np.clip(rng.normal(1, 0.035, len(t)), 0.8, 1.2)
water = 90 + 0.8*t + rng.uniform(0, 15, len(t))
gas = oil * (0.55 + 0.0003*t)
df = pd.DataFrame({'date': pd.date_range('2025-01-01', periods=len(t)), 'oil_bopd': oil.round(2), 'gas_mscfd': gas.round(2), 'water_bwpd': water.round(2)})
df.to_csv(Path(__file__).with_name('sample_production.csv'), index=False)

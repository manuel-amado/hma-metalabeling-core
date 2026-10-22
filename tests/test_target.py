import pandas as pd
import numpy as np
import xgboost as xgb
from sklearn.preprocessing import RobustScaler

df = pd.read_csv(r"C:\Users\Manuel\Desktop\HMA_MetaLabeling\python\data_processing\Alpha_Omni_V2_Dataset_XAUUSD.csv")

df['SL_ATR'] = np.where(df['Dir'] == 1, df['SwingLow20'], df['SwingHigh20'])
df['SL_ATR'] = df['SL_ATR'].clip(lower=1.0, upper=5.0)

# True if it hits 1.5x SL in profit before hitting SL in loss (DURING THE HMA WAVE)
df['Target'] = ((df['MFE_ATR'] >= df['SL_ATR'] * 1.5) & (df['MAE_ATR'] > -df['SL_ATR'])).astype(int)

print(f"Target Distribution: {df['Target'].mean():.2%}")

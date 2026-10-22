import pandas as pd
import numpy as np

df = pd.read_csv(r"C:\Users\Manuel\Desktop\HMA_MetaLabeling\python\data_processing\Alpha_Omni_V2_Dataset_XAUUSD.csv")

# Ensure valid structural levels (cap them so we don't have insane 50 ATR stops)
df['SL_ATR'] = np.where(df['Dir'] == 1, df['SwingLow20'], df['SwingHigh20'])
df['SL_ATR'] = df['SL_ATR'].clip(lower=1.0, upper=5.0)

# TP = 1.5 * SL
df['TP_ATR'] = df['SL_ATR'] * 1.5

# Hit logic (assuming worst case if both hit)
sl_hit = df['MAE_ATR'] <= -df['SL_ATR']
tp_hit = df['MFE_ATR'] >= df['TP_ATR']
wins = tp_hit & (~sl_hit)
losses = sl_hit

win_count = wins.sum()
loss_count = losses.sum()
win_rate = win_count / (win_count + loss_count + 1e-9)

pf = (df.loc[wins, 'TP_ATR'].sum()) / (df.loc[losses, 'SL_ATR'].sum() + 1e-9)

print(f"Structural TP (1.5x SL) / Structural SL")
print(f"Win Rate: {win_rate:.2%} | Profit Factor: {pf:.2f} | Wins: {win_count} | Losses: {loss_count}")

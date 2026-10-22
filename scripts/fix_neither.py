import pandas as pd
import numpy as np

df = pd.read_csv(r"C:\Users\Manuel\Desktop\HMA_MetaLabeling\python\data_processing\Alpha_Omni_Dataset_XAUUSD.csv")

def eval_fixed_rr_exact(df, tp_atr, sl_atr):
    sl_hit = df['MAE_ATR'] <= -sl_atr
    tp_hit = df['MFE_ATR'] >= tp_atr
    wins = tp_hit & (~sl_hit)
    losses = sl_hit
    neither = (~tp_hit) & (~sl_hit)
    
    # Neither trades close at Target_Cross_Ret (they wander until the HMA crosses back)
    # We will assume their return in ATR is Target_Cross_Ret / Spread_Ratio (rough estimate of entry ATR).
    # Actually, Target_Cross_Ret is a percentage. entry_price is not in the CSV.
    # Let's just calculate WR including neither as losses to be safe.
    win_count = wins.sum()
    loss_count = losses.sum()
    neither_count = neither.sum()
    
    win_rate_total = win_count / len(df)
    
    print(f"TP {tp_atr:04.1f} / SL {sl_atr:04.1f} | WR: {win_rate_total:05.2%} | Wins: {win_count:4d} | Losses: {loss_count:4d} | Neither: {neither_count:4d}")

eval_fixed_rr_exact(df, 3.0, 3.0)

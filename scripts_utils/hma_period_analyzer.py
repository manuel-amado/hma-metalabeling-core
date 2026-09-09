import numpy as np
import pandas as pd
import MetaTrader5 as mt5
import matplotlib.pyplot as plt
import time
import sys

def wma(series, period):
    weights = np.arange(1, period + 1)
    return series.rolling(period).apply(lambda x: np.dot(x, weights) / weights.sum(), raw=True)

def hma(series, period):
    half_length = int(period / 2)
    sqrt_length = int(np.sqrt(period))
    wmaf = wma(series, half_length)
    wmas = wma(series, period)
    diff = 2 * wmaf - wmas
    return wma(diff, sqrt_length)

def run_analysis():
    if not mt5.initialize():
        print("initialize() failed")
        return
    
    symbol = "XAUUSD"
    timeframe = mt5.TIMEFRAME_M15
    print(f"Fetching data for {symbol}...")
    rates = mt5.copy_rates_from_pos(symbol, timeframe, 0, 50000) # approx 2 years
    mt5.shutdown()
    
    if rates is None or len(rates) == 0:
        print("No data fetched.")
        return
        
    df = pd.DataFrame(rates)
    df['time'] = pd.to_datetime(df['time'], unit='s')
    
    # Calculate ATR (14)
    df['tr0'] = abs(df['high'] - df['low'])
    df['tr1'] = abs(df['high'] - df['close'].shift())
    df['tr2'] = abs(df['low'] - df['close'].shift())
    df['tr'] = df[['tr0', 'tr1', 'tr2']].max(axis=1)
    df['atr'] = df['tr'].rolling(14).mean()
    
    periods = list(range(14, 51, 2))
    results = []
    
    for p in periods:
        df_p = df[['time', 'open', 'high', 'low', 'close', 'atr']].copy()
        df_p['hma'] = hma(df_p['close'], p)
        
        # Conditions
        df_p['is_below'] = df_p['close'] < df_p['hma']
        df_p['is_above'] = df_p['close'] > df_p['hma']
        
        build_up_bars = 7
        df_p['buildup_buy'] = df_p['is_below'].shift(1).rolling(build_up_bars).sum() == build_up_bars
        df_p['buildup_sell'] = df_p['is_above'].shift(1).rolling(build_up_bars).sum() == build_up_bars
        
        df_p['trigger_buy'] = df_p['buildup_buy'] & (df_p['close'] > df_p['hma']) & df_p['is_below'].shift(1)
        df_p['trigger_sell'] = df_p['buildup_sell'] & (df_p['close'] < df_p['hma']) & df_p['is_above'].shift(1)
        
        buy_indices = df_p[df_p['trigger_buy']].index
        sell_indices = df_p[df_p['trigger_sell']].index
        
        total_trades = len(buy_indices) + len(sell_indices)
        if total_trades == 0:
            continue
            
        continuity_atrs = []
        
        for idx in buy_indices:
            future = df_p.loc[idx+1:]
            cross_down = future[future['close'] < future['hma']]
            end_idx = cross_down.index[0] if not cross_down.empty else future.index[-1]
            max_high = df_p.loc[idx+1:end_idx, 'high'].max()
            entry_price = df_p.loc[idx, 'close']
            atr = df_p.loc[idx, 'atr']
            if atr > 0:
                cont = (max_high - entry_price) / atr
                continuity_atrs.append(cont)
                
        for idx in sell_indices:
            future = df_p.loc[idx+1:]
            cross_up = future[future['close'] > future['hma']]
            end_idx = cross_up.index[0] if not cross_up.empty else future.index[-1]
            min_low = df_p.loc[idx+1:end_idx, 'low'].min()
            entry_price = df_p.loc[idx, 'close']
            atr = df_p.loc[idx, 'atr']
            if atr > 0:
                cont = (entry_price - min_low) / atr
                continuity_atrs.append(cont)
                
        avg_cont = np.mean(continuity_atrs) if continuity_atrs else 0
        win_rate = sum(1 for c in continuity_atrs if c >= 2.0) / len(continuity_atrs) if continuity_atrs else 0
        
        results.append({
            'Period': p,
            'Trades': total_trades,
            'Avg_Continuity_ATR': avg_cont,
            'Prob_Above_2R': win_rate * 100
        })
        
        print(f"HMA {p}: Trades={total_trades}, Avg_Continuity={avg_cont:.2f} ATR, P(>2R)={win_rate*100:.1f}%")
        
    res_df = pd.DataFrame(results)
    
    plt.figure(figsize=(10, 6))
    plt.bar(res_df['Period'], res_df['Avg_Continuity_ATR'], color='royalblue')
    plt.title('Continuity Edge (Momentum Ignition) by HMA Period (XAUUSD M15)')
    plt.xlabel('HMA Period (Trigger)')
    plt.ylabel('Average Maximum Excursion (ATRs)')
    plt.xticks(res_df['Period'])
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    plt.tight_layout()
    plt.savefig('hma_period_analysis.png')
    print("\nOptimal Period based on max ATR extension:", res_df.loc[res_df['Avg_Continuity_ATR'].idxmax(), 'Period'])
    print("Done. Saved hma_period_analysis.png")

if __name__ == '__main__':
    run_analysis()

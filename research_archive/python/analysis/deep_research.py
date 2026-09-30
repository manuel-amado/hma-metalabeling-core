import pandas as pd
import numpy as np
from numba import njit
import warnings
warnings.filterwarnings("ignore")

paths = {
    "XAUUSD": r"C:\Users\Manuel\AppData\Roaming\MetaQuotes\Terminal\Common\Files\XAUUSD_M15_10Years.csv",
    "USDJPY": r"C:\Users\Manuel\AppData\Roaming\MetaQuotes\Terminal\Common\Files\USDJPY_M15_11Years.csv"
}

def wma(s, period):
    weights = np.arange(1, period + 1)
    return s.rolling(period).apply(lambda x: np.dot(x, weights) / weights.sum(), raw=True)

def hma(s, period):
    return wma((2 * wma(s, int(period / 2))) - wma(s, period), int(np.sqrt(period)))

@njit
def fast_test_with_rollover(c, h, l, hma_arr, ema_arr, rsi_arr, atr_arr, hours_arr, days_arr, atr_mult, base_fric, rollover_fric):
    r_mults = []
    in_trade = False
    trade_dir = 0
    entry_price = sl = risk_dist = 0.0
    current_trade_rollovers = 0
    
    for i in range(1, len(c)):
        if days_arr[i] != days_arr[i-1]:
            if in_trade:
                current_trade_rollovers += 1
                
        if in_trade:
            total_fric = base_fric + (rollover_fric * current_trade_rollovers)
            
            if trade_dir == 1 and l[i] <= sl:
                r_mults.append(-(entry_price - sl + total_fric) / risk_dist)
                in_trade = False
            elif trade_dir == -1 and h[i] >= sl:
                r_mults.append(-(sl - entry_price + total_fric) / risk_dist)
                in_trade = False
            elif trade_dir == 1 and c[i] < hma_arr[i]:
                r_mults.append((c[i] - entry_price - total_fric) / risk_dist)
                in_trade = False
            elif trade_dir == -1 and c[i] > hma_arr[i]:
                r_mults.append((entry_price - c[i] - total_fric) / risk_dist)
                in_trade = False
        else:
            if c[i-1] < hma_arr[i-1] and c[i] > hma_arr[i] and c[i] > ema_arr[i] and rsi_arr[i] < 70:
                in_trade = True; trade_dir = 1; entry_price = c[i]; risk_dist = atr_mult * atr_arr[i]; sl = c[i] - risk_dist
                current_trade_rollovers = 0
            elif c[i-1] > hma_arr[i-1] and c[i] < hma_arr[i] and c[i] < ema_arr[i] and rsi_arr[i] > 30:
                in_trade = True; trade_dir = -1; entry_price = c[i]; risk_dist = atr_mult * atr_arr[i]; sl = c[i] + risk_dist
                current_trade_rollovers = 0
                
    gp = sum([r for r in r_mults if r > 0])
    gl = sum([abs(r) for r in r_mults if r <= 0])
    pf = gp/gl if gl > 0 else 0
    return len(r_mults), pf, gp - gl

results = []

for symbol, path in paths.items():
    print(f"Loading {symbol}...")
    df_raw = pd.read_csv(path)
    df_raw['time'] = pd.to_datetime(df_raw['time'], format='%Y.%m.%d %H:%M')
    df_raw.set_index('time', inplace=True)
    
    timeframes = {
        'M15': df_raw,
        'H1': df_raw.resample('1h').agg({'open':'first', 'high':'max', 'low':'min', 'close':'last'}).dropna(),
        'H4': df_raw.resample('4h').agg({'open':'first', 'high':'max', 'low':'min', 'close':'last'}).dropna()
    }
    
    for tf_name, df in timeframes.items():
        print(f"  Processing {tf_name}...")
        df['hma200'] = hma(df['close'], 200)
        df['ema400'] = df['close'].ewm(span=400, adjust=False).mean()
        
        delta = df['close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        df['rsi14'] = 100 - (100 / (1 + (gain/loss)))
        
        df['tr'] = np.maximum(df['high'] - df['low'], np.maximum(abs(df['high'] - df['close'].shift(1)), abs(df['low'] - df['close'].shift(1))))
        df['atr14'] = df['tr'].rolling(14).mean()
        
        df['hour'] = df.index.hour
        df['day'] = df.index.dayofyear
        df.dropna(inplace=True)
        
        c, h, l = df['close'].values, df['high'].values, df['low'].values
        hma200, ema400 = df['hma200'].values, df['ema400'].values
        rsi, atr = df['rsi14'].values, df['atr14'].values
        hours, days = df['hour'].values, df['day'].values
        
        base_fric = 0.35 if symbol == "XAUUSD" else 0.010
        rollover_fric = 0.15 if symbol == "XAUUSD" else 0.050 # Severe penalty for holding forex overnight
        
        t, pf, nr = fast_test_with_rollover(c, h, l, hma200, ema400, rsi, atr, hours, days, 1.5, base_fric, 0.0)
        t_real, pf_real, nr_real = fast_test_with_rollover(c, h, l, hma200, ema400, rsi, atr, hours, days, 1.5, base_fric, rollover_fric)
        
        results.append({
            'Symbol': symbol,
            'TF': tf_name,
            'Trades': t_real,
            'Ideal PF': round(pf, 2),
            'Ideal NetR': round(nr, 1),
            'Real PF (w/ Rollover)': round(pf_real, 2),
            'Real NetR (w/ Rollover)': round(nr_real, 1)
        })

df_res = pd.DataFrame(results)
report = "# 🧬 Deep Research: Anatomía de la Fricción y Temporalidad (10 Años)\n\n"
report += df_res.to_markdown(index=False)
with open(r"C:\Users\Manuel\Desktop\HMA_MetaLabeling\Alpha_Sniper_Vault\src\quant_scripts\deep_research_report.md", "w", encoding="utf-8") as f:
    f.write(report)
print("Deep research complete!")
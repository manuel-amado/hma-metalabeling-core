import MetaTrader5 as mt5
import pandas as pd
import numpy as np
import time
from datetime import datetime

def wma(s, period):
    weights = np.arange(1, period + 1)
    return s.rolling(period).apply(lambda x: np.dot(x, weights) / weights.sum(), raw=True)

def hma(s, period):
    wma_half = wma(s, int(period / 2))
    wma_full = wma(s, period)
    diff = (2 * wma_half) - wma_full
    return wma(diff, int(np.sqrt(period)))

if not mt5.initialize():
    print("MT5 init failed")
    quit()

symbols = ['EURUSD', 'GBPUSD', 'USDJPY', 'XAUUSD', 'BTCUSD', 'US30.cash']
timeframes = {
    'M15': mt5.TIMEFRAME_M15,
    'H1': mt5.TIMEFRAME_H1,
    'H4': mt5.TIMEFRAME_H4
}
hma_periods = [50, 100, 200]

results = []

print("Iniciando Macro-Screener con Riesgo 1% y Filtros...")

for sym in symbols:
    for tf_name, tf_val in timeframes.items():
        print(f"Descargando {sym} - {tf_name}...")
        rates = mt5.copy_rates_from_pos(sym, tf_val, 0, 99000)
        if rates is None or len(rates) < 2000:
            print(f"  -> Datos insuficientes.")
            continue
            
        df = pd.DataFrame(rates)
        df['time'] = pd.to_datetime(df['time'], unit='s')
        
        # Filtros e indicadores
        df['ema200'] = df['close'].ewm(span=200, adjust=False).mean()
        
        # ATR 14
        df['high_low'] = df['high'] - df['low']
        df['high_close'] = np.abs(df['high'] - df['close'].shift())
        df['low_close'] = np.abs(df['low'] - df['close'].shift())
        df['tr'] = df[['high_low', 'high_close', 'low_close']].max(axis=1)
        df['atr14'] = df['tr'].rolling(14).mean()
        
        # RSI 14
        delta = df['close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        df['rsi14'] = 100 - (100 / (1 + rs))
        
        start_time = df['time'].iloc[0]
        end_time = df['time'].iloc[-1]
        years_duration = (end_time - start_time).days / 365.25
        
        for period in hma_periods:
            df[f'hma_{period}'] = hma(df['close'], period)
            
            valid_df = df.dropna(subset=[f'hma_{period}', 'ema200', 'atr14', 'rsi14']).copy()
            if len(valid_df) == 0: continue
            
            c = valid_df['close'].values
            h = valid_df['high'].values
            l = valid_df['low'].values
            hma_arr = valid_df[f'hma_{period}'].values
            ema_arr = valid_df['ema200'].values
            atr_arr = valid_df['atr14'].values
            rsi_arr = valid_df['rsi14'].values
            
            r_multiples = []
            
            in_trade = False
            trade_dir = 0
            entry_price = 0.0
            sl = 0.0
            risk_dist = 0.0
            
            for i in range(1, len(valid_df)):
                if in_trade:
                    # Check SL
                    if trade_dir == 1 and l[i] <= sl:
                        r_multiples.append(-1.0)
                        in_trade = False
                    elif trade_dir == -1 and h[i] >= sl:
                        r_multiples.append(-1.0)
                        in_trade = False
                    # Check Exit (HMA Cross against)
                    elif trade_dir == 1 and c[i] < hma_arr[i]:
                        r_mult = (c[i] - entry_price) / risk_dist
                        r_multiples.append(r_mult)
                        in_trade = False
                    elif trade_dir == -1 and c[i] > hma_arr[i]:
                        r_mult = (entry_price - c[i]) / risk_dist
                        r_multiples.append(r_mult)
                        in_trade = False
                else:
                    # Entry logic
                    # BUY: Cross up + Above EMA200 + RSI < 70
                    if c[i-1] < hma_arr[i-1] and c[i] > hma_arr[i] and c[i] > ema_arr[i] and rsi_arr[i] < 70:
                        in_trade = True
                        trade_dir = 1
                        entry_price = c[i]
                        risk_dist = max(2 * atr_arr[i], 0.0001)
                        sl = entry_price - risk_dist
                    # SELL: Cross down + Below EMA200 + RSI > 30
                    elif c[i-1] > hma_arr[i-1] and c[i] < hma_arr[i] and c[i] < ema_arr[i] and rsi_arr[i] > 30:
                        in_trade = True
                        trade_dir = -1
                        entry_price = c[i]
                        risk_dist = max(2 * atr_arr[i], 0.0001)
                        sl = entry_price + risk_dist
                        
            if len(r_multiples) > 0:
                r_arr = np.array(r_multiples)
                wins = r_arr[r_arr > 0]
                losses = r_arr[r_arr <= 0]
                
                win_rate = len(wins) / len(r_arr) * 100
                total_return = r_arr.sum()  # 1R = 1%
                ann_return = total_return / years_duration if years_duration > 0 else 0
                
                gross_profit = wins.sum() if len(wins) > 0 else 0
                gross_loss = abs(losses.sum()) if len(losses) > 0 else 0
                pf = (gross_profit / gross_loss) if gross_loss != 0 else 99.9
                
                results.append({
                    'Symbol': sym,
                    'TF': tf_name,
                    'HMA': period,
                    'Years': round(years_duration, 1),
                    'Trades': len(r_arr),
                    'WinRate(%)': round(win_rate, 1),
                    'PF': round(pf, 2),
                    'TotalRet(%)': round(total_return, 1),
                    'AnnRet(%)': round(ann_return, 1)
                })

mt5.shutdown()

res_df = pd.DataFrame(results)
res_df.to_csv(r'C:\Users\Manuel\Desktop\HMA_MetaLabeling\Alpha_Sniper_Vault\src\hma_filtered_results.csv', index=False)

print("\n=== TOP 10 MEJORES ESTRATEGIAS FILTRADAS (Por Retorno Anualizado %) ===")
print(res_df.sort_values('AnnRet(%)', ascending=False).head(10).to_string(index=False))

print("\n=== TOP 10 PEORES ESTRATEGIAS FILTRADAS (Las que destrozan la cuenta) ===")
print(res_df.sort_values('AnnRet(%)', ascending=True).head(10).to_string(index=False))

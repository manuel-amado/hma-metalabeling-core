import MetaTrader5 as mt5
import pandas as pd
import numpy as np
import time

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
hma_periods = [20, 50, 100, 200]

results = []

print("Iniciando Macro-Screener HMA...")
for sym in symbols:
    for tf_name, tf_val in timeframes.items():
        print(f"Descargando {sym} - {tf_name}...")
        rates = mt5.copy_rates_from_pos(sym, tf_val, 0, 99000)
        if rates is None or len(rates) < 1000:
            print(f"  -> Fallo al descargar o datos insuficientes.")
            continue
            
        df = pd.DataFrame(rates)
        df['time'] = pd.to_datetime(df['time'], unit='s')
        df.set_index('time', inplace=True)
        closes = df['close']
        
        # Obtener multiplicador de pips/puntos para normalizar resultados
        info = mt5.symbol_info(sym)
        if info is None: continue
        point = info.point
        pip_mult = 10 if (info.digits == 5 or info.digits == 3) else 1
        if sym == 'XAUUSD': pip_mult = 10
        if sym == 'US30.cash': pip_mult = 1
        pip_val = point * pip_mult
        
        for period in hma_periods:
            df[f'hma_{period}'] = hma(closes, period)
            
            # Limpiar NaNs
            valid_df = df.dropna(subset=[f'hma_{period}']).copy()
            c = valid_df['close'].values
            h = valid_df[f'hma_{period}'].values
            
            # Detectar cruces: 1 (Precio cruza arriba de HMA = BUY), -1 (Precio cruza abajo = SELL)
            signals = np.zeros(len(valid_df))
            for i in range(1, len(valid_df)):
                if c[i-1] < h[i-1] and c[i] > h[i]: signals[i] = 1
                elif c[i-1] > h[i-1] and c[i] < h[i]: signals[i] = -1
                
            trades = []
            current_pos = 0 # 1 para BUY, -1 para SELL
            entry_price = 0.0
            
            for i in range(1, len(valid_df)):
                if signals[i] != 0:
                    if current_pos != 0:
                        # Cerrar posicion anterior
                        if current_pos == 1:
                            profit_pips = (c[i] - entry_price) / pip_val
                        else:
                            profit_pips = (entry_price - c[i]) / pip_val
                        trades.append(profit_pips)
                        
                    # Abrir nueva posicion (Stop & Reverse puro)
                    current_pos = signals[i]
                    entry_price = c[i]
                    
            if len(trades) > 0:
                trades_arr = np.array(trades)
                wins = trades_arr[trades_arr > 0]
                losses = trades_arr[trades_arr <= 0]
                
                win_rate = len(wins) / len(trades_arr) * 100
                avg_win = wins.mean() if len(wins) > 0 else 0
                avg_loss = abs(losses.mean()) if len(losses) > 0 else 0
                pf = (wins.sum() / abs(losses.sum())) if len(losses) > 0 and losses.sum() != 0 else 99.9
                expectancy = trades_arr.mean()
                
                results.append({
                    'Symbol': sym,
                    'TF': tf_name,
                    'HMA': period,
                    'Trades': len(trades_arr),
                    'WinRate(%)': round(win_rate, 1),
                    'Exp(Pips)': round(expectancy, 1),
                    'AvgWin(Pips)': round(avg_win, 1),
                    'AvgLoss(Pips)': round(avg_loss, 1),
                    'PF': round(pf, 2)
                })

mt5.shutdown()

res_df = pd.DataFrame(results)
res_df.to_csv(r'C:\Users\Manuel\Desktop\HMA_MetaLabeling\Alpha_Sniper_Vault\src\hma_macro_results.csv', index=False)

# Mostrar un resumen estructurado ordenado por Expectativa y Profit Factor
print("\n=== TOP 10 MEJORES CONFIGURACIONES (Por Expectativa Neta de Pips por Trade) ===")
print(res_df.sort_values('Exp(Pips)', ascending=False).head(10).to_string(index=False))

print("\n=== TOP 10 PEORES CONFIGURACIONES (Máquina de perder dinero / Rango Puro) ===")
print(res_df.sort_values('Exp(Pips)', ascending=True).head(10).to_string(index=False))

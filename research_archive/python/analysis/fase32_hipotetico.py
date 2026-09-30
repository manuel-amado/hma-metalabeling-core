import pandas as pd
import json
import os

DATA_DIR   = r'C:\Users\Manuel\Desktop\HMA_MetaLabeling\Alpha_Sniper_Vault\data'
MODELS_DIR = r'C:\Users\Manuel\Desktop\HMA_MetaLabeling\Alpha_Sniper_Vault\models'

SYMBOLS = ['EURUSD','USDJPY','EURJPY','XAUUSD','XAGUSD']
RISK    = 1.0          # % per trade
INITIAL = 100_000.0
SCALE_OUT_RR = 1.5

print("=== PORTFOLIO HIPOTÉTICO FASE 32.5 (5 ACTIVOS - SIN GBPUSD) ===")
print("Fuente: umbrales_universales_[SYMBOL]_20260612_002903.json | Perfil: B_Balanceado")
print()

total_net_usd = 0.0
all_stats = []

for sym in SYMBOLS:
    jpath = os.path.join(MODELS_DIR, f'umbrales_universales_{sym}_20260612_002903.json')
    with open(jpath, 'r') as f:
        d = json.load(f)['B_Balanceado']

    n       = int(d['n_trades'])
    wr_pct  = d['win_rate']       # e.g. 47.3
    avg_rr  = d['avg_rr']         # effective avg RR per trade including losses
    sharpe  = d['sharpe']
    max_dd  = d['max_dd']
    annual_r= d['annual_r']
    entry_t = d['entry_thresh']

    # Net PnL = n_trades * avg_rr * risk_per_trade
    # avg_rr already accounts for win/loss split (it's the expectancy per trade in R units)
    net_pct = n * avg_rr * RISK
    net_usd = net_pct * INITIAL / 100.0
    total_net_usd += net_usd

    row = {
        'Symbol'     : sym,
        'Entry_Thresh': entry_t,
        'Trades'     : n,
        'WR%'        : f"{wr_pct:.1f}",
        'Avg_RR'     : f"{avg_rr:.4f}",
        'Net_%'      : f"{net_pct:.2f}",
        'Net_USD'    : f"${net_usd:,.0f}",
        'Max_DD%'    : f"{max_dd:.1f}",
        'Sharpe'     : f"{sharpe:.3f}",
    }
    all_stats.append(row)

pd.set_option('display.width', 200)
df = pd.DataFrame(all_stats)
print(df.to_string(index=False))
print()
print(f"Portfolio Total Net (linear sum, no compounding): ${total_net_usd:,.0f}  ({total_net_usd/INITIAL*100:.1f}%)")
print()

# Compare with MT5 backtest
mt5_trades = 5722
mt5_net    = 71_509.26
mt5_dd_pct = 30.00
mt5_sharpe = 0.74
mt5_pf     = 1.05

total_json_trades = sum(int(d_item['Trades'].replace(',','')) for d_item in [{'Trades': str(r['Trades'])} for r in all_stats])

print("=" * 65)
print("COMPARATIVA MT5 REAL vs HIPOTÉTICO JSON (B_Balanceado)")
print("=" * 65)
print(f"{'Métrica':<35} {'MT5 Real':>12} {'JSON Esperado':>14}")
print("-" * 65)
print(f"{'Trades Ejecutados':<35} {mt5_trades:>12,} {sum(int(r['Trades']) for r in all_stats):>14,}")
print(f"{'Net Profit':<35} {'$71,509':>12} {f'${total_net_usd:,.0f}':>14}")
print(f"{'Max Drawdown %':<35} {mt5_dd_pct:>11.1f}% {'N/A':>14}")
print(f"{'Sharpe Ratio':<35} {mt5_sharpe:>12.2f} {'~1.5 (wtd)':>14}")
print(f"{'Profit Factor':<35} {mt5_pf:>12.2f} {'N/A':>14}")
print(f"{'Win Rate':<35} {'44.09%':>12} {'~43.9% (wtd)':>14}")
print()
print("=== DIAGNÓSTICO TRADE COUNTS por SÍMBOLO ===")
print(f"{'Symbol':<10} {'MT5 Real':>10} {'JSON Esperado':>14} {'Ratio':>8} {'Estado':>10}")
print("-" * 55)
mt5_by_sym = {'EURJPY': 5668, 'EURUSD': 1162, 'USDJPY': 1112, 'XAUUSD': 20, 'XAGUSD': 2422}
for r in all_stats:
    sym   = r['Symbol']
    n_exp = int(r['Trades'])
    n_mt5 = mt5_by_sym.get(sym, 0)
    ratio = n_mt5 / n_exp if n_exp > 0 else 999
    if ratio < 0.5:
        status = "⛔ COLAPSO"
    elif ratio > 3.0:
        status = "🔴 SATURADO"
    elif ratio > 1.5:
        status = "🟡 EXCESO"
    else:
        status = "✅ OK"
    print(f"{sym:<10} {n_mt5:>10,} {n_exp:>14,} {ratio:>8.1f}x  {status}")

print()
print("=== CONCLUSIÓN CUANTITATIVA ===")
print("""
El servidor FastAPI NO filtra correctamente durante el Strategy Tester.
Las probabilidades que llegan al EA son el umbral exacto del JSON (ej. 0.26),
NO las predicciones reales del XGBoost en memoria.

Esto indica una de dos causas:
  A) El servidor devuelve probabilidades_crudas sin umbral (fallback mode).
  B) El modelo XGBoost para EURJPY y XAGUSD colapsa en predict_proba()
     devolviendo exactamente el umbral, posiblemente por datos mal normalizados.

Resultado para XAUUSD (solo 20 trades) es especialmente alarmante:
  El modelo más rentable (Sharpe 4.45) está prácticamente mudo en el Tester.
  Esto sugiere que el modelo XAUUSD pkl NO se está cargando correctamente.
""")

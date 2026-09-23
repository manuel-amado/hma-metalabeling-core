import pandas as pd
import numpy as np

# Cargar el backtest más reciente validado (threshold 0.55, longs only)
file_path = r'C:\Users\Manuel\Documents\BACKTESTS\ReportTester-510237079.html'
df = pd.read_html(file_path)[1]
idx_deals = df[df[0].astype(str).str.contains('Transacciones', na=False)].index.tolist()
deals = df.iloc[idx_deals[0]+2:].copy()
deals.columns = ['Time', 'Deal', 'Symbol', 'Type', 'Dir', 'Volume', 'Price', 'Order', 'Commission', 'Swap', 'Profit', 'Balance', 'Comment']
deals = deals.dropna(subset=['Dir'])
outs = deals[deals['Dir'] == 'out'].copy()

def parse_val(x):
    if pd.isna(x): return 0.0
    try: return float(str(x).replace(' ', ''))
    except: return 0.0

outs['Profit'] = outs['Profit'].apply(parse_val)
outs['Balance'] = outs['Balance'].apply(parse_val)
outs['Time'] = pd.to_datetime(outs['Time'])
outs['Target'] = (outs['Profit'] > 0).astype(int)
outs['Year'] = outs['Time'].dt.year
outs['Month'] = outs['Time'].dt.to_period('M')

# === ESTADÍSTICAS MENSUALES COMPLETAS ===
print('=== ESTADÍSTICAS MENSUALES (2023 OOS en adelante) ===')
oos = outs[outs['Year'] >= 2023].copy()

monthly = []
for period, grp in oos.groupby('Month'):
    n = len(grp)
    wr = grp['Target'].mean()
    profit = grp['Profit'].sum()
    pf_pos = grp[grp['Profit']>0]['Profit'].sum()
    pf_neg = abs(grp[grp['Profit']<0]['Profit'].sum())
    pf = pf_pos / pf_neg if pf_neg > 0 else 0
    monthly.append({'Month': str(period), 'Trades': n, 'WR': wr, 'Profit': profit, 'PF': pf})
    print(f'  {str(period)} | Trades:{n:<3} | WR:{wr:.1%} | Profit:{profit:>9.2f} | PF:{pf:.2f}')

df_monthly = pd.DataFrame(monthly)
print()

# === ESTADÍSTICAS ANUALES OOS ===
print('=== ANUALES OOS (Ciego) ===')
for yr, grp in oos.groupby('Year'):
    n = len(grp)
    wr = grp['Target'].mean()
    profit = grp['Profit'].sum()
    pf_pos = grp[grp['Profit']>0]['Profit'].sum()
    pf_neg = abs(grp[grp['Profit']<0]['Profit'].sum())
    pf = pf_pos / pf_neg if pf_neg > 0 else 0
    ev = profit / n
    avg_win = grp[grp['Profit']>0]['Profit'].mean() if wr > 0 else 0
    avg_loss = grp[grp['Profit']<0]['Profit'].mean() if wr < 1 else 0
    print(f'  {yr} | Trades:{n:<3} | WR:{wr:.1%} | Profit:{profit:>9.2f} | PF:{pf:.2f} | EV:{ev:>7.2f}')
    print(f'       | Avg Win: {avg_win:.2f} | Avg Loss: {avg_loss:.2f}')

print()

# === 2026 ESPECÍFICO ===
yr2026 = oos[oos['Year'] == 2026]
print('=== 2026 DETALLE (Mercado Actual) ===')
print(f'Trades ejecutados: {len(yr2026)}')
print(f'Rango: {yr2026.Time.min().strftime("%Y-%m-%d")} a {yr2026.Time.max().strftime("%Y-%m-%d")}')
print(f'Meses cubiertos: {yr2026.Month.nunique()} meses (de enero a sep)')
if len(yr2026) > 0:
    wr_26 = yr2026['Target'].mean()
    profit_26 = yr2026['Profit'].sum()
    pf_pos_26 = yr2026[yr2026['Profit']>0]['Profit'].sum()
    pf_neg_26 = abs(yr2026[yr2026['Profit']<0]['Profit'].sum())
    pf_26 = pf_pos_26 / pf_neg_26 if pf_neg_26 > 0 else 0
    print(f'Win Rate: {wr_26:.1%}')
    print(f'Profit Total: {profit_26:.2f}')
    print(f'PF: {pf_26:.2f}')
    print(f'EV por trade: {profit_26/len(yr2026):.2f}')

print()

# === ESTADÍSTICAS DE DRAWDOWN Y RACHA ===
print('=== ANÁLISIS DE DRAWDOWN Y CONSISTENCIA ===')
oos_sorted = oos.sort_values('Time').copy()
oos_sorted['Cumulative'] = oos_sorted['Profit'].cumsum()
oos_sorted['Running_Max'] = oos_sorted['Cumulative'].cummax()
oos_sorted['DD'] = oos_sorted['Cumulative'] - oos_sorted['Running_Max']
max_dd = oos_sorted['DD'].min()
max_dd_pct = max_dd / 100000 * 100

# Consecutivas perdedoras
consecutive_losses = 0
max_consec_losses = 0
for p in oos_sorted['Profit']:
    if p < 0:
        consecutive_losses += 1
        max_consec_losses = max(max_consec_losses, consecutive_losses)
    else:
        consecutive_losses = 0

print(f'Max Drawdown OOS: ${max_dd:.2f} ({max_dd_pct:.2f}% sobre 100k)')
print(f'Max racha perdedoras consecutivas OOS: {max_consec_losses}')
print(f'Trades positivos mensuales promedio: {df_monthly[df_monthly["Profit"]>0]["Profit"].mean():.2f}')
print(f'Meses en positivo: {(df_monthly["Profit"]>0).sum()} de {len(df_monthly)}')

print()

# === PROYECCIÓN FORWARD ===
print('=== PROYECCIÓN ESTADÍSTICA FORWARD (Base: OOS 2023-2025) ===')
oos_stable = oos[oos['Year'].isin([2023, 2024, 2025])]
n_months = 36
n_total_trades = len(oos_stable)
trades_per_month = n_total_trades / n_months
ev_per_trade = oos_stable['Profit'].mean()
monthly_profit_expected = trades_per_month * ev_per_trade

print(f'Trades/mes historico (2023-2025): {trades_per_month:.1f}')
print(f'EV por trade historico: ${ev_per_trade:.2f}')
print(f'Ganancia mensual esperada (100k): ${monthly_profit_expected:.2f}')
print(f'ROI mensual esperado: {monthly_profit_expected / 100000 * 100:.2f}%')
print(f'ROI anual esperado: {monthly_profit_expected * 12 / 100000 * 100:.1f}%')

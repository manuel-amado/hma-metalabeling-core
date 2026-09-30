import pandas as pd
import numpy as np
import xgboost as xgb
from sklearn.metrics import roc_auc_score

file_path = r'C:\Users\Manuel\Documents\BACKTESTS\ReportTester-510237079.html'
df = pd.read_html(file_path)[1]
idx_deals = df[df[0].astype(str).str.contains('Transacciones', na=False)].index.tolist()
deals = df.iloc[idx_deals[0]+2:].copy()
deals.columns = ['Time', 'Deal', 'Symbol', 'Type', 'Dir', 'Volume', 'Price', 'Order', 'Commission', 'Swap', 'Profit', 'Balance', 'Comment']
deals = deals.dropna(subset=['Dir'])
outs = deals[deals['Dir'] == 'out'].copy()

def parse_profit(x):
    if pd.isna(x): return 0.0
    try: return float(str(x).replace(' ', ''))
    except: return 0.0

outs['Profit'] = outs['Profit'].apply(parse_profit)
outs['Time'] = pd.to_datetime(outs['Time'])
outs['TradeType'] = np.where(outs['Type'] == 'sell', 'Long', 'Short')
outs['Target'] = (outs['Profit'] > 0).astype(int)
outs['Zone'] = np.where(outs['Time'] < pd.to_datetime('2023-01-01'), 'IS', 'OOS')

def analyze(subset, name):
    if len(subset)==0:
        print(f'{name:<22} No trades')
        return
    n = len(subset)
    wins = subset['Target'].sum()
    wr = wins / n
    gross_p = subset[subset['Profit']>0]['Profit'].sum()
    gross_l = abs(subset[subset['Profit']<0]['Profit'].sum())
    pf = gross_p / gross_l if gross_l > 0 else 0
    ev = subset['Profit'].sum() / n
    total = subset['Profit'].sum()
    avg_win = subset[subset['Profit']>0]['Profit'].mean() if wins > 0 else 0
    avg_loss = subset[subset['Profit']<0]['Profit'].mean() if (n - wins) > 0 else 0
    rr = abs(avg_win / avg_loss) if avg_loss != 0 else 0
    print(f'{name:<22} | Trades:{n:<4} | WR:{wr:.1%} | Profit:{total:>9.2f} | PF:{pf:.2f} | EV:{ev:>7.2f} | R:R:{rr:.2f}')

print('=== REPORTE COMPLETO DE AUDITORÍA INSTITUCIONAL ===')
print()
print('--- DIRECCIONALIDAD ---')
analyze(outs, 'GLOBAL')
analyze(outs[outs['TradeType']=='Long'], 'LONGS')
analyze(outs[outs['TradeType']=='Short'], 'SHORTS')

print()
print('--- IS vs OOS ---')
is_set = outs[outs['Zone']=='IS']
oos_set = outs[outs['Zone']=='OOS']
analyze(is_set, 'IN-SAMPLE (2015-2022)')
analyze(oos_set, 'OUT-OF-SAMPLE (2023+)')

print()
print('--- DEGRADACION IS->OOS ---')
if len(is_set)>0 and len(oos_set)>0:
    is_pf = is_set[is_set['Profit']>0]['Profit'].sum() / abs(is_set[is_set['Profit']<0]['Profit'].sum())
    oos_pf = oos_set[oos_set['Profit']>0]['Profit'].sum() / abs(oos_set[oos_set['Profit']<0]['Profit'].sum())
    is_wr = is_set['Target'].mean()
    oos_wr = oos_set['Target'].mean()
    print(f'  WR: IS={is_wr:.1%} -> OOS={oos_wr:.1%} | Degradacion: {(oos_wr-is_wr)*100:+.1f} pp')
    print(f'  PF: IS={is_pf:.2f} -> OOS={oos_pf:.2f} | Degradacion: {((oos_pf/is_pf)-1)*100:+.1f}%')

print()
print('--- DRAWDOWN Y CONSISTENCIA TEMPORAL ---')
outs_sorted = outs.sort_values('Time')
outs_sorted['Cumulative'] = outs_sorted['Profit'].cumsum()
outs_sorted['Running_Max'] = outs_sorted['Cumulative'].cummax()
outs_sorted['Drawdown'] = outs_sorted['Cumulative'] - outs_sorted['Running_Max']
max_dd = outs_sorted['Drawdown'].min()
print(f'  Max Drawdown (en beneficio acumulado): {max_dd:.2f}')

# Analisis por año
print()
print('--- CONSISTENCIA ANUAL ---')
outs_sorted['Year'] = outs_sorted['Time'].dt.year
for yr, grp in outs_sorted.groupby('Year'):
    tag = ' [OOS]' if yr >= 2023 else ' [IS] '
    pf = grp[grp['Profit']>0]['Profit'].sum() / abs(grp[grp['Profit']<0]['Profit'].sum()) if abs(grp[grp['Profit']<0]['Profit'].sum()) > 0 else 0
    print(f'  {yr}{tag} Trades:{len(grp):<3} WR:{grp.Target.mean():.1%} Profit:{grp.Profit.sum():>9.2f} PF:{pf:.2f}')

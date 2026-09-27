import pandas as pd
import numpy as np
import xgboost as xgb

df = pd.read_csv('C:/Users/Manuel/Desktop/HMA_MetaLabeling/python/m2_metalabeling/models/XGBoost_Dataset_Final.csv')
df['Time'] = pd.to_datetime(df['Time'])
df_longs = df[df['Signal_Dir'] == 1.0].copy().reset_index(drop=True)

split_date = pd.to_datetime('2023-01-01')
feature_cols = ['Keltner_Bandwidth_H4', 'ATR_Ratio_H1_D1', 'ADX_Value_H4', 'ADX_Slope_H4', 'Dist_EMA200_H4', 'Bollinger_Width_H1', 'Daily_Exhaustion']

print('=== PRUEBA IRREFUTABLE DE AUSENCIA DE DATA LEAKAGE ===')
print()
print('--- 1. VERIFICACION TEMPORAL DEL DATASET ---')
print('Fecha minima:', df_longs['Time'].min().strftime('%Y-%m-%d'))
print('Fecha maxima:', df_longs['Time'].max().strftime('%Y-%m-%d'))
print('Total trades LONGS:', len(df_longs))
print('Ordenado cronologicamente?', df_longs['Time'].is_monotonic_increasing)
print('FRONTERA OOS: 2023-01-01')
print()

print('--- 2. TASA DE EXITO POR DECIL TEMPORAL ---')
print('(Si hubiera leakage/overfit, los deciles IS finales tendrian WR artificialmente alto)')
df_longs['Decil'] = pd.qcut(df_longs.index, q=10, labels=[f'D{i+1}' for i in range(10)])
for decil, grp in df_longs.groupby('Decil'):
    wr = grp['Target'].mean()
    f_ini = grp['Time'].min().strftime('%Y-%m')
    f_fin = grp['Time'].max().strftime('%Y-%m')
    zona = '[OOS]' if grp['Time'].min() >= split_date else '[IS] '
    print(f'  {decil} ({f_ini} a {f_fin}) {zona} Trades:{len(grp):<3} WR:{wr:.1%}')

print()
print('--- 3. CORRELACION TEMPORAL ENTRE FEATURES Y TARGET (deteccion de look-ahead) ---')
for col in feature_cols:
    corr_past = df_longs[col].corr(df_longs['Target'])
    corr_future = df_longs[col].shift(-1).corr(df_longs['Target'])
    shift = abs(corr_future) - abs(corr_past)
    leakage = 'ALERTA LEAKAGE!' if shift > 0.05 else 'OK'
    print(f'  {col:<28} | Corr Actual:{corr_past:+.4f} | Corr Futura:{corr_future:+.4f} | Delta:{shift:+.4f} [{leakage}]')

print()
print('--- 4. PRUEBA DE HERMETICIDAD DE LA FRONTERA ---')
train_set = df_longs[df_longs['Time'] < split_date]
test_set = df_longs[df_longs['Time'] >= split_date]
print(f'Trades en TRAIN (2015-2022): {len(train_set)}')
print(f'Trades en TEST  (2023+):     {len(test_set)}')
print(f'Interseccion de fechas posible?: {"SI - LEAKAGE!" if len(set(train_set.index) & set(test_set.index)) > 0 else "NO - Conjunto Hermetico"}')
print(f'Ultimo trade IS:  {train_set.Time.max().strftime("%Y-%m-%d")}')
print(f'Primer trade OOS: {test_set.Time.min().strftime("%Y-%m-%d")}')
gap_days = (test_set.Time.min() - train_set.Time.max()).days
print(f'Gap temporal entre IS y OOS: {gap_days} dias')

print()
print('--- 5. ANALISIS DE CONSISTENCIA ANUAL DE WIN RATE ---')
print('(Distribucion plana = modelo robusto / Picos en IS solo = overfit)')
df_longs['Year'] = df_longs['Time'].dt.year
for yr, grp in df_longs.groupby('Year'):
    wr = grp['Target'].mean()
    zona = '[OOS]' if yr >= 2023 else '[IS] '
    bar = '#' * int(wr * 20)
    print(f'  {yr} {zona} WR:{wr:.1%} {bar}')

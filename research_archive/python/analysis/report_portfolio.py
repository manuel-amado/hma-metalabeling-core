import pandas as pd
import numpy as np
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
PORT_FILE = os.path.join(DATA_DIR, "portfolio_trades_log.csv")

if not os.path.exists(PORT_FILE):
    print("El archivo de portfolio no existe todavia.")
    exit()

df = pd.read_csv(PORT_FILE)
df['Time'] = pd.to_datetime(df['Time'])
df['Year'] = df['Time'].dt.year

# 1% de riesgo por trade
RISK_PCT = 1.0

print("="*70)
print("  REPORTE DE SIMULACION: PORTAFOLIO GLOBAL ALPHA SNIPER")
print("="*70)

# Resumen General
total_trades = len(df)
total_rr = df['Final_RR'].sum()
win_rate = (df['Final_RR'] > 0).mean() * 100
total_pct = total_rr * RISK_PCT

print(f"Capital Simulado: Tasa Base = 1% Riesgo Fijo por Trade")
print(f"Total Operaciones en Backtest: {total_trades}")
print(f"Ganancia Neta Total: +{total_pct:.2f}% ( {total_rr:.2f} R )")
print(f"Win Rate Combinado: {win_rate:.2f}%")
print("")

# Agrupar por Año y Activo
grouped = df.groupby(['Year', 'Symbol'])['Final_RR'].agg(['count', 'sum']).reset_index()

print("== DESGLOSE ANUAL Y GANANCIAS POTENCIALES POR ACTIVO ==")
for year in sorted(df['Year'].unique()):
    print(f"\n[AÑO {year}]")
    y_df = grouped[grouped['Year'] == year]
    y_rr = y_df['sum'].sum()
    y_trades = y_df['count'].sum()
    for _, row in y_df.iterrows():
        sym_pct = row['sum'] * RISK_PCT
        print(f"  - {row['Symbol']}: {row['count']:4} trades | Ganancia: {sym_pct:>7.2f}%")
    print(f"  >>> TOTAL {year}: {y_trades:4} trades | Ganancia: {y_rr * RISK_PCT:>7.2f}%")

# Agrupar solo por Activo
print("\n== RENDIMIENTO TOTAL POR ACTIVO (2015-2026) ==")
sym_grp = df.groupby('Symbol')['Final_RR'].agg(['count', 'sum']).reset_index()
sym_grp = sym_grp.sort_values(by='sum', ascending=False)
for _, row in sym_grp.iterrows():
    sym_pct = row['sum'] * RISK_PCT
    print(f"  - {row['Symbol']}: {row['count']:4} trades | Aporte Total: {sym_pct:>7.2f}%")

print("="*70)

import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
from bs4 import BeautifulSoup
import pandas as pd
import numpy as np
import os, glob

# Leer el archivo
found = r"C:\Users\Manuel\Documents\BACKTESTS\[Alpha_Sniper_Master][XAUUSD][M15 (2022.01.01 - 2026.08.29)]\ReportTester-5102370101.html"
with open(found, "r", encoding="utf-16", errors="replace") as fh:
    content = fh.read()

soup = BeautifulSoup(content, "html.parser")
trades = []
for row in soup.find_all("tr"):
    cols = row.find_all("td")
    if len(cols) >= 10:
        t = [c.get_text(strip=True) for c in cols]
        if "out" in t:
            try:
                trades.append((t[0], float(t[-3].replace(" ","")), float(t[-4].replace(" ",""))))
            except: pass

df = pd.DataFrame(trades, columns=["Date","Profit","Swap"])
df["PnL"] = df["Profit"] + df["Swap"]
df["Date"] = pd.to_datetime(df["Date"], format="%Y.%m.%d %H:%M:%S")
df = df.sort_values("Date").reset_index(drop=True)

BALANCE = 100000.0
df["Cum"]     = df["PnL"].cumsum()
df["Peak"]    = df["Cum"].cummax()
df["DD_usd"]  = df["Peak"] - df["Cum"]
df["DD_pct"]  = df["DD_usd"] / BALANCE * 100

# Rachas perdedoras
streak = 0
streaks = []
for v in (df["PnL"] <= 0):
    streak = streak + 1 if v else 0
    streaks.append(streak)
df["loss_streak"] = streaks

print("=== ANATOMIA DE DRAWDOWNS - Master BASE (1705 trades) ===")
print()
print(f"Racha perdedora maxima: {df['loss_streak'].max()} perdidas consecutivas")
print()
print("Distribucion de rachas perdedoras:")
for n in range(5, int(df["loss_streak"].max())+1, 5):
    events = (df["loss_streak"] == n).sum()
    if events > 0:
        print(f"  Racha de {n:>2} consecutivas: ocurrio {events} vez/veces")
print()

print("Tiempo en drawdown:")
for thresh in [3, 5, 8, 10, 15]:
    n = (df["DD_pct"] > thresh).sum()
    print(f"  Trades en DD > {thresh:>2}%: {n:>4} ({n/len(df)*100:.1f}% de las operaciones)")
print()

# Episodios de drawdown severo
dd_events = []
in_dd, dd_start, dd_max, dd_peak_eq = False, None, 0.0, 0.0
for i, row in df.iterrows():
    if row["DD_pct"] > 5 and not in_dd:
        in_dd, dd_start, dd_max = True, row["Date"], row["DD_pct"]
    elif in_dd:
        dd_max = max(dd_max, row["DD_pct"])
        if row["DD_pct"] < 1.0:
            dd_events.append({
                "Inicio": dd_start.strftime("%Y-%m"),
                "Fin": row["Date"].strftime("%Y-%m"),
                "Duracion_dias": (row["Date"] - dd_start).days,
                "DD_max_%": round(dd_max,1),
                "DD_max_$": round(dd_max/100*BALANCE,0)
            })
            in_dd, dd_max = False, 0.0

df_ev = pd.DataFrame(dd_events).sort_values("DD_max_%", ascending=False)
print("TOP EPISODIOS DE DRAWDOWN (DD > 5%):")
print(df_ev.head(12).to_string(index=False))
print()

# Analisis anual
print("ANALISIS ANUAL:")
df["Year"] = df["Date"].dt.year
for yr, g in df.groupby("Year"):
    wins   = g[g["PnL"]>0]["PnL"]
    losses = g[g["PnL"]<=0]["PnL"]
    gp = wins.sum(); gl = abs(losses.sum())
    pf  = gp/gl if gl>0 else 9.99
    wr  = len(wins)/len(g)*100
    net = gp - gl
    max_streak_yr = g["loss_streak"].max()
    max_dd_yr     = g["DD_pct"].max()
    print(f"  {yr}: N={len(g):>4} | WR={wr:>5.1f}% | PF={pf:.3f} | Net={net:>9,.0f} | MaxStreak={max_streak_yr:>2} | MaxDD={max_dd_yr:.1f}%")

print()

# Cual es la perdida media y max por operacion perdedora
losses_abs = df[df["PnL"]<=0]["PnL"].abs()
print(f"Perdida media por trade perdedor: ${losses_abs.mean():.0f}")
print(f"Perdida max por trade perdedor:   ${losses_abs.max():.0f}")
print(f"Ganancia media por trade ganador: ${df[df['PnL']>0]['PnL'].mean():.0f}")
print(f"Ganancia max por trade ganador:   ${df[df['PnL']>0]['PnL'].max():.0f}")
print()

# Cuanto cuesta una racha de N perdidas
loss_mean = losses_abs.mean()
print("Coste acumulado de rachas perdedoras (sobre balance 100k):")
for n in [5, 10, 15, 20, 25]:
    coste = n * loss_mean
    pct   = coste / BALANCE * 100
    print(f"  {n:>2} perdidas seguidas -> coste aprox ${coste:>7,.0f} ({pct:.1f}% del balance)")
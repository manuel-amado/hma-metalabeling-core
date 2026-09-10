import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
from bs4 import BeautifulSoup
import pandas as pd
import numpy as np

def parse_html(path):
    for enc in ["utf-16","utf-8","latin-1"]:
        try:
            with open(path,"r",encoding=enc,errors="replace") as f:
                tmp = f.read()
            if "<html" in tmp.lower():
                content = tmp
                break
        except: pass
    soup = BeautifulSoup(content,"html.parser")
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
    return df

df = parse_html(r"C:\Users\Manuel\Documents\BACKTESTS\[Alpha_Sniper_Master][XAUUSD][M15 (2022.01.01 - 2026.08.29)]\ReportTester-510237101.html")
df = df.sort_values("Date").reset_index(drop=True)

# Calculo de equity y drawdown
df["Cum"] = df["PnL"].cumsum()
df["Peak"] = df["Cum"].cummax()
df["DD"] = df["Peak"] - df["Cum"]
df["DD_pct"] = df["DD"] / 100000 * 100  # sobre balance 100k

# Detectar rachas perdedoras
df["is_loss"] = df["PnL"] <= 0
streak = 0
streaks = []
for v in df["is_loss"]:
    if v: streak += 1
    else: streak = 0
    streaks.append(streak)
df["loss_streak"] = streaks

print("=== ANATOMIA DE DRAWDOWNS - Master BASE ===")
print()
print(f"Total operaciones: {len(df)}")
print(f"Ganadoras: {(df['PnL']>0).sum()} ({(df['PnL']>0).mean()*100:.1f}%)")
print(f"Perdedoras: {(df['PnL']<=0).sum()} ({(df['PnL']<=0).mean()*100:.1f}%)")
print()

# Max racha perdedora
max_streak = df["loss_streak"].max()
print(f"Racha perdedora maxima: {max_streak} operaciones consecutivas")

# Distribucion de rachas
for n in [5,10,15,20,25]:
    count = (df["loss_streak"] == n).sum()
    if count > 0:
        print(f"  Rachas de exactamente {n} perdidas consecutivas: {count} veces")

print()

# Drawdowns mayores al 5%, 10%, 15%
for thresh in [5, 8, 10, 15, 20]:
    n = (df["DD_pct"] > thresh).sum()
    print(f"  Barras de trades en DD > {thresh}%: {n} ({n/len(df)*100:.1f}% del tiempo)")

print()

# Top 10 drawdown peaks (periodos de DD severo)
dd_events = []
in_dd = False
dd_start = None
dd_max = 0
dd_start_eq = 0

for i, row in df.iterrows():
    if row["DD_pct"] > 5 and not in_dd:
        in_dd = True
        dd_start = row["Date"]
        dd_start_eq = row["Peak"]
        dd_max = row["DD_pct"]
    elif in_dd:
        if row["DD_pct"] > dd_max:
            dd_max = row["DD_pct"]
        if row["DD_pct"] < 1.0:  # Salida del DD
            dd_events.append({
                "Inicio": dd_start,
                "Fin": row["Date"],
                "Duracion_dias": (row["Date"] - dd_start).days,
                "DD_max_pct": round(dd_max,2),
                "DD_max_usd": round(dd_max/100*100000,0)
            })
            in_dd = False
            dd_max = 0

df_dd = pd.DataFrame(dd_events).sort_values("DD_max_pct", ascending=False)
print("TOP 10 EPISODIOS DE DRAWDOWN (>5%):")
print(df_dd.head(10).to_string(index=False))

print()

# Por año
print("=== ANALISIS ANUAL ===")
df["Year"] = df["Date"].dt.year
for yr, g in df.groupby("Year"):
    wins = g[g["PnL"]>0]["PnL"]
    losses = g[g["PnL"]<=0]["PnL"]
    gp = wins.sum(); gl = abs(losses.sum())
    pf = gp/gl if gl>0 else 9.99
    wr = len(wins)/len(g)*100
    max_dd_yr = g["DD"].max()
    print(f"  {yr}: Trades={len(g):>4} | WR={wr:>5.1f}% | PF={pf:.3f} | Net={gp-gl:>9,.0f} | MaxDD_USD={max_dd_yr:>9,.0f}")
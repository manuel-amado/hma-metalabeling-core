import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
from bs4 import BeautifulSoup
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import timedelta
import json

# --- Config ---
HTML_FILE = r"C:\Users\Manuel\Documents\BACKTESTS\ReportTester-510237093.html"
IMAGE_OUT = r"C:\Users\Manuel\.gemini\antigravity\brain\09f0d8f0-7381-4d51-ac24-8e482a1de163\ftmo_master5_chart.png"
BALANCE_INICIAL = 100000.0
DAILY_LOSS_LIMIT_PCT = 5.0
MAX_TOTAL_DD_PCT = 10.0
FASE1_TARGET_PCT = 10.0
FASE2_TARGET_PCT = 5.0
WITHDRAWAL_SPLIT = 0.80
FTMO_FEE = 540.0

# --- Parsear HTML ---
with open(HTML_FILE, "r", encoding="utf-16", errors="replace") as fh:
    content = fh.read()
soup = BeautifulSoup(content, "html.parser")
trades = []
for row in soup.find_all("tr"):
    cols = row.find_all("td")
    if len(cols) >= 10:
        t = [c.get_text(strip=True) for c in cols]
        if "out" in t:
            try: trades.append((t[0], float(t[-3].replace(" ","")), float(t[-4].replace(" ",""))))
            except: pass

df = pd.DataFrame(trades, columns=["Date","Profit","Swap"])
df["PnL"] = df["Profit"] + df["Swap"]
df["Date"] = pd.to_datetime(df["Date"], format="%Y.%m.%d %H:%M:%S")
df = df.sort_values("Date").reset_index(drop=True)
df["Day"] = df["Date"].dt.date
df["Raw_Cum_PnL"] = df["PnL"].cumsum()

# --- Simular Reglas FTMO ---
daily_eq = df.groupby("Day")["PnL"].sum().reset_index()
daily_eq.columns = ["Day","Daily_PnL"]
daily_eq["Day"] = pd.to_datetime(daily_eq["Day"])
daily_eq = daily_eq.sort_values("Day").reset_index(drop=True)

# Maxima perdida intra-dia aproximada
df["CumDay"] = df.groupby("Day")["PnL"].cumsum()
df["PeakDay"] = df.groupby("Day")["CumDay"].cummax()
df["IntraDayDD"] = df["PeakDay"] - df["CumDay"]
daily_max_dd = df.groupby("Day").agg(
    Min_PnL=("CumDay", "min")
).reset_index()
daily_max_dd["Day"] = pd.to_datetime(daily_max_dd["Day"])

state = "FASE1"
bal = BALANCE_INICIAL
peak_acc = BALANCE_INICIAL
fase_start = daily_eq["Day"].iloc[0]
fase_start_bal = bal
cuenta_num = 1

retiros = []
busts = []
fases_spans = [] # (start, end, type, status)

monthly_peak = bal
total_retirado = 0.0
fees = FTMO_FEE

i = 0
while i < len(daily_eq):
    row = daily_eq.iloc[i]
    day = row["Day"]
    pnl = row["Daily_PnL"]
    
    # DD diario asumiendo peor caso intra-dia
    min_pnl = daily_max_dd[daily_max_dd["Day"]==day]["Min_PnL"].values[0]
    daily_loss_pct = 0
    if min_pnl < 0:
        daily_loss_pct = (abs(min_pnl)) / BALANCE_INICIAL * 100
        
    bal += pnl
    if bal > peak_acc: peak_acc = bal
    
    dd_total_pct = (peak_acc - bal) / BALANCE_INICIAL * 100
    profit_pct = (bal - fase_start_bal) / BALANCE_INICIAL * 100
    
    busted = (daily_loss_pct >= DAILY_LOSS_LIMIT_PCT) or (dd_total_pct >= MAX_TOTAL_DD_PCT)
    
    # Evaluar fin de mes en funded para retiro
    is_end_of_month = (i == len(daily_eq)-1) or (daily_eq.iloc[i+1]["Day"].month != day.month)
    if state == "FUNDED" and is_end_of_month:
        mes_profit = bal - monthly_peak
        if mes_profit > 0:
            retiro = mes_profit * WITHDRAWAL_SPLIT
            total_retirado += retiro
            bal -= retiro
            retiros.append((day, retiro))
        monthly_peak = bal
    
    if busted:
        fases_spans.append((fase_start, day, state, "BUSTED"))
        busts.append(day)
        # Reiniciar
        state = "FASE1"
        bal = BALANCE_INICIAL
        peak_acc = BALANCE_INICIAL
        if i < len(daily_eq)-1:
            fase_start = daily_eq.iloc[i+1]["Day"]
        fase_start_bal = bal
        monthly_peak = bal
        cuenta_num += 1
        fees += FTMO_FEE
        i += 1
        continue
        
    if state == "FASE1" and profit_pct >= FASE1_TARGET_PCT:
        fases_spans.append((fase_start, day, state, "PASSED"))
        state = "FASE2"
        if i < len(daily_eq)-1: fase_start = daily_eq.iloc[i+1]["Day"]
        fase_start_bal = bal
        i += 1
        continue
        
    if state == "FASE2" and profit_pct >= FASE2_TARGET_PCT:
        fases_spans.append((fase_start, day, state, "PASSED"))
        state = "FUNDED"
        if i < len(daily_eq)-1: fase_start = daily_eq.iloc[i+1]["Day"]
        fase_start_bal = bal
        monthly_peak = bal
        i += 1
        continue
        
    i += 1

if fase_start < daily_eq["Day"].iloc[-1]:
    fases_spans.append((fase_start, daily_eq["Day"].iloc[-1], state, "ACTIVE"))

# --- Generar Grafico ---
plt.style.use("dark_background")
fig, ax = plt.subplots(figsize=(14, 7))

# Plot raw strategy equity curve (shifted to start at 0)
merged_df = pd.merge(df, daily_eq, on="Day", how="left")
ax.plot(df["Date"], df["Raw_Cum_PnL"], color="#e0e0e0", linewidth=1.5, label="Raw Strategy PnL")

colors = {"FASE1": "#5c5c5c", "FASE2": "#2b5c8f", "FUNDED": "#1c592d"}
labels_added = {"FASE1": False, "FASE2": False, "FUNDED": False}

for (start, end, phase, status) in fases_spans:
    # Ajustar para fechas extremas
    idx_s = df[df["Date"] >= start].index
    idx_e = df[df["Date"] <= end].index
    if len(idx_s)==0 or len(idx_e)==0: continue
    
    label = phase if not labels_added[phase] else ""
    labels_added[phase] = True
    ax.axvspan(start, end, color=colors[phase], alpha=0.4, label=label)

# Add markers
busted_dates = [b for b in busts if b in df["Date"].values or b in df["Day"].values]
y_busts = [df[df["Day"]==b]["Raw_Cum_PnL"].iloc[-1] for b in busted_dates if len(df[df["Day"]==b])>0]
valid_busts = [b for b in busted_dates if len(df[df["Day"]==b])>0]
if valid_busts:
    ax.scatter(valid_busts, y_busts, color="red", marker="x", s=100, zorder=5, label="Account Blown (DD > 10%)")

wd_dates = [w[0] for w in retiros]
wd_amounts = [w[1] for w in retiros]
y_wds = [df[df["Day"]==w]["Raw_Cum_PnL"].iloc[-1] for w in wd_dates if len(df[df["Day"]==w])>0]
valid_wds = [w for w in wd_dates if len(df[df["Day"]==w])>0]
if valid_wds:
    ax.scatter(valid_wds, y_wds, color="#00ff00", marker="$", s=150, zorder=5, label="Profit Withdrawal")

ax.set_title("Alpha Sniper Master5 ECT - Simulacion de Fondeo FTMO (2022-2026)", fontsize=16, pad=15)
ax.set_ylabel("Beneficio Acumulado Bruto (Raw PnL $)", fontsize=12)
ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
ax.grid(True, linestyle="--", alpha=0.2)
ax.legend(loc="upper left")

plt.tight_layout()
plt.savefig(IMAGE_OUT, dpi=150)
plt.close()

# --- Exportar Stats a JSON para el asistente ---
stats = {
    "challenges": cuenta_num,
    "fase1_passed": len([x for x in fases_spans if x[2]=="FASE1" and x[3]=="PASSED"]),
    "fase2_passed": len([x for x in fases_spans if x[2]=="FASE2" and x[3]=="PASSED"]),
    "funded_blown": len([x for x in fases_spans if x[2]=="FUNDED" and x[3]=="BUSTED"]),
    "total_fees": fees,
    "total_withdrawals": total_retirado,
    "net_profit": total_retirado - fees,
    "raw_pnl": df["Raw_Cum_PnL"].iloc[-1],
    "raw_max_dd": (df["Raw_Cum_PnL"].cummax() - df["Raw_Cum_PnL"]).max()
}
print("STATS_JSON:", json.dumps(stats))
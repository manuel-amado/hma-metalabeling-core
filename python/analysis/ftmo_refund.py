import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
from bs4 import BeautifulSoup
import pandas as pd
import numpy as np
import json

HTML_FILE = r"C:\Users\Manuel\Documents\BACKTESTS\ReportTester-510237093.html"
BALANCE_INICIAL = 100000.0
DAILY_LOSS_LIMIT_PCT = 5.0
MAX_TOTAL_DD_PCT = 10.0
FASE1_TARGET_PCT = 10.0
FASE2_TARGET_PCT = 5.0
WITHDRAWAL_SPLIT = 0.80
FTMO_FEE = 540.0

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
df["Day"] = pd.to_datetime(df["Date"].dt.date)

daily_eq = df.groupby("Day")["PnL"].sum().reset_index()
daily_eq.columns = ["Day","Daily_PnL"]
daily_eq["Day"] = pd.to_datetime(daily_eq["Day"])

df["CumDay"] = df.groupby("Day")["PnL"].cumsum()
df["PeakDay"] = df.groupby("Day")["CumDay"].cummax()
df["IntraDayDD"] = df["PeakDay"] - df["CumDay"]
daily_max_dd = df.groupby("Day").agg(Min_PnL=("CumDay", "min")).reset_index()

state = "FASE1"
bal = BALANCE_INICIAL
peak_acc = BALANCE_INICIAL
fase_start = daily_eq["Day"].iloc[0]
fase_start_bal = bal
cuenta_num = 1

monthly_peak = bal
total_retirado = 0.0
fees_pagados = FTMO_FEE
fees_devueltos = 0.0

i = 0
while i < len(daily_eq):
    row = daily_eq.iloc[i]
    day = row["Day"]
    pnl = row["Daily_PnL"]
    
    min_pnl = daily_max_dd[daily_max_dd["Day"]==day]["Min_PnL"].values[0]
    daily_loss_pct = (abs(min_pnl)) / BALANCE_INICIAL * 100 if min_pnl < 0 else 0
        
    bal += pnl
    if bal > peak_acc: peak_acc = bal
    
    dd_total_pct = (peak_acc - bal) / BALANCE_INICIAL * 100
    profit_pct = (bal - fase_start_bal) / BALANCE_INICIAL * 100
    
    busted = (daily_loss_pct >= DAILY_LOSS_LIMIT_PCT) or (dd_total_pct >= MAX_TOTAL_DD_PCT)
    
    is_end_of_month = (i == len(daily_eq)-1) or (daily_eq.iloc[i+1]["Day"].month != day.month)
    
    if state == "FUNDED" and is_end_of_month:
        mes_profit = bal - monthly_peak
        if mes_profit > 0:
            retiro = mes_profit * WITHDRAWAL_SPLIT
            total_retirado += retiro
            bal -= retiro
        monthly_peak = bal
    
    if busted:
        state = "FASE1"
        bal = BALANCE_INICIAL
        peak_acc = BALANCE_INICIAL
        if i < len(daily_eq)-1: fase_start = daily_eq.iloc[i+1]["Day"]
        fase_start_bal = bal
        monthly_peak = bal
        cuenta_num += 1
        fees_pagados += FTMO_FEE
        i += 1
        continue
        
    if state == "FASE1" and profit_pct >= FASE1_TARGET_PCT:
        state = "FASE2"
        if i < len(daily_eq)-1: fase_start = daily_eq.iloc[i+1]["Day"]
        fase_start_bal = bal
        i += 1
        continue
        
    if state == "FASE2" and profit_pct >= FASE2_TARGET_PCT:
        state = "FUNDED"
        if i < len(daily_eq)-1: fase_start = daily_eq.iloc[i+1]["Day"]
        fase_start_bal = bal
        monthly_peak = bal
        # --- AQUI ESTA LA DEVOLUCION DEL FEE ---
        fees_devueltos += FTMO_FEE
        i += 1
        continue
        
    i += 1

print(f"Total de Cuentas Iniciadas (Fees Pagados): {cuenta_num} = ${cuenta_num * FTMO_FEE:,.0f}")
print(f"Cuentas que llegaron a Funded (Fees Devueltos): {int(fees_devueltos/FTMO_FEE)} = ${fees_devueltos:,.0f}")
print(f"Coste Neto en Fees: ${(cuenta_num * FTMO_FEE) - fees_devueltos:,.0f}")
print(f"Total Beneficios Retirados: ${total_retirado:,.0f}")
print(f"Beneficio Neto Real (Retiros - Coste Fees Neto): ${total_retirado - ((cuenta_num * FTMO_FEE) - fees_devueltos):,.0f}")
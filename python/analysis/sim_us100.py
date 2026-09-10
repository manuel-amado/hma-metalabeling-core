import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
from bs4 import BeautifulSoup
import pandas as pd
import json

HTML_FILE = r"C:\Users\Manuel\Documents\BACKTESTS\ReportTester-5102370103.html"
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
        if "out" in t or "in/out" in t:
            try: trades.append((t[0], float(t[-3].replace(" ","")), float(t[-4].replace(" ",""))))
            except: pass
        elif len(cols) == 13 and "." in t[0] and ":" in t[0]:
            try: trades.append((t[0], float(t[-1].replace(" ","")), float(t[-2].replace(" ",""))))
            except: pass

if not trades:
    for row in soup.find_all("tr"):
        t = [c.get_text(strip=True) for c in row.find_all("td")]
        if len(t) >= 10 and "out" in t:
            try: trades.append((t[0], float(t[10].replace(" ","")), float(t[9].replace(" ",""))))
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
daily_max_dd = df.groupby("Day").agg(Min_PnL=("CumDay", "min")).reset_index()

state = "FASE1"
bal = BALANCE_INICIAL
peak_acc = BALANCE_INICIAL
cuenta_num = 1
total_retirado = 0.0
fees = FTMO_FEE
busts = 0

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
    profit_pct = (bal - BALANCE_INICIAL) / BALANCE_INICIAL * 100
    
    busted = (daily_loss_pct >= DAILY_LOSS_LIMIT_PCT) or (dd_total_pct >= MAX_TOTAL_DD_PCT)
    
    if busted:
        busts += 1
        state = "FASE1"
        bal = BALANCE_INICIAL
        peak_acc = BALANCE_INICIAL
        cuenta_num += 1
        fees += FTMO_FEE
        i += 1
        continue
    i += 1

print(f"US100 Raw PnL: ${df['PnL'].sum():.2f}")
print(f"Prop Firm Challenges Started: {cuenta_num}")
print(f"Prop Firm Accounts Blown: {busts}")
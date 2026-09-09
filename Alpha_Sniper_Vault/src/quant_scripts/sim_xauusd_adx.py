import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
from bs4 import BeautifulSoup
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

HTML_FILE = r"C:\Users\Manuel\Documents\BACKTESTS\ReportTester-510237106.html"
IMAGE_OUT = r"C:\Users\Manuel\.gemini\antigravity\brain\09f0d8f0-7381-4d51-ac24-8e482a1de163\xauusd_adx_chart.png"
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

if len(trades) == 0:
    print("No trades found. Check if the ADX filter blocked everything.")
    sys.exit(0)

df = pd.DataFrame(trades, columns=["Date","Profit","Swap"])
df["PnL"] = df["Profit"] + df["Swap"]
df["Date"] = pd.to_datetime(df["Date"], format="%Y.%m.%d %H:%M:%S")
df = df.sort_values("Date").reset_index(drop=True)
df["Day"] = pd.to_datetime(df["Date"].dt.date)
df["Raw_Cum_PnL"] = df["PnL"].cumsum()

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
cuenta_num = 1
total_retirado = 0.0
fees = FTMO_FEE
fee_refunded = False
busts = 0
fases_spans = []

if len(daily_eq) > 0:
    fase_start = daily_eq["Day"].iloc[0]
    fase_start_bal = bal
    monthly_peak = bal
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
                if not fee_refunded: retiro += FTMO_FEE; fee_refunded = True
                total_retirado += retiro
                bal -= (mes_profit * WITHDRAWAL_SPLIT)
            monthly_peak = bal
        
        if busted:
            busts += 1
            fases_spans.append((fase_start, day, state, "BUSTED"))
            state = "FASE1"
            bal = BALANCE_INICIAL
            peak_acc = BALANCE_INICIAL
            cuenta_num += 1
            fees += FTMO_FEE
            fee_refunded = False
            if i < len(daily_eq)-1: fase_start = daily_eq.iloc[i+1]["Day"]
            fase_start_bal = bal
            monthly_peak = bal
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
            fee_refunded = False
            i += 1
            continue
            
        i += 1

print(f"--- GOLD (XAUUSD) WITH ADX FILTER ---")
print(f"Total Trades: {len(trades)}")
print(f"Raw Strategy Profit: ${df['Raw_Cum_PnL'].iloc[-1]:,.2f}")
print(f"Raw Max DD: ${(df['Raw_Cum_PnL'].cummax() - df['Raw_Cum_PnL']).max():,.2f}")
print(f"Prop Firm Accounts Started: {cuenta_num}")
print(f"Prop Firm Accounts Blown: {busts}")
print(f"Prop Firm Funded Reached: {len([x for x in fases_spans if x[2]=='FUNDED'])}")
print(f"Total Withdrawn: ${total_retirado:,.2f}")
print(f"Total Fees Paid: ${fees:,.2f}")
print(f"NET PROFIT (Pocket): ${total_retirado - fees:,.2f}")

plt.style.use("dark_background")
fig, ax = plt.subplots(figsize=(15, 8))
ax.plot(df["Date"], df["Raw_Cum_PnL"], color="#ffd700", linewidth=1.5, label="XAUUSD (con Filtro ADX)")
ax.set_title("Alpha Sniper: XAUUSD Equity Curve (Filtro ADX D1 > 25)", fontsize=18, pad=15)
ax.set_ylabel("PnL Estrategia Base ($)", fontsize=14)
ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
ax.grid(True, linestyle=":", alpha=0.3)
ax.legend(loc="upper left", fontsize=12)
plt.tight_layout()
plt.savefig(IMAGE_OUT, dpi=150)
print(f"Chart saved to {IMAGE_OUT}")
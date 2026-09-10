import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
from bs4 import BeautifulSoup
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

def parse_html(file_path):
    with open(file_path, "r", encoding="utf-16", errors="replace") as fh:
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
    return daily_eq

# Parse both
df_xau = parse_html(r"C:\Users\Manuel\Documents\BACKTESTS\ReportTester-5102370101.html")
df_ndx = parse_html(r"C:\Users\Manuel\Documents\BACKTESTS\ReportTester-5102370103.html")

# Merge
df_port = pd.merge(df_xau, df_ndx, on="Day", how="outer").fillna(0)
df_port = df_port.sort_values("Day")
df_port["Cum_XAU"] = df_port["Daily_PnL_x"].cumsum()
df_port["Cum_NDX"] = df_port["Daily_PnL_y"].cumsum()
df_port["Portfolio_PnL"] = df_port["Daily_PnL_x"] + df_port["Daily_PnL_y"]
df_port["Cum_Portfolio"] = df_port["Portfolio_PnL"].cumsum()

plt.style.use("dark_background")
fig, ax = plt.subplots(figsize=(15, 8))
ax.plot(df_port["Day"], df_port["Cum_XAU"], label="XAUUSD (Oro)", color="#ffd700", alpha=0.7)
ax.plot(df_port["Day"], df_port["Cum_NDX"], label="US100 (Nasdaq)", color="#00aaff", alpha=0.7)
ax.plot(df_port["Day"], df_port["Cum_Portfolio"], label="Portfolio Combinado", color="#00ff00", linewidth=2.5)

ax.set_title("Portfolio Master6: XAUUSD + US100 (2022-2026)", fontsize=18)
ax.set_ylabel("Beneficio Acumulado ($)", fontsize=14)
ax.legend(loc="upper left", fontsize=12)
ax.grid(True, linestyle=":", alpha=0.3)

IMAGE_OUT = r"C:\Users\Manuel\.gemini\antigravity\brain\09f0d8f0-7381-4d51-ac24-8e482a1de163\portfolio_chart.png"
plt.tight_layout()
plt.savefig(IMAGE_OUT, dpi=150)
print(f"Chart saved to {IMAGE_OUT}")

# Portfolio FTMO Logic (Simplified to just see Max DD on daily basis)
df_port["Peak"] = df_port["Cum_Portfolio"].cummax()
df_port["DD"] = df_port["Peak"] - df_port["Cum_Portfolio"]
max_dd = df_port["DD"].max()
print(f"Portfolio Max Daily DD (Combined): ${max_dd:,.2f}")
print(f"Portfolio Total Profit: ${df_port['Cum_Portfolio'].iloc[-1]:,.2f}")

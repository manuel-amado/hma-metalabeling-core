import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
from bs4 import BeautifulSoup
import pandas as pd

paths = {
    "Master4 OOS only (25-26)":   r"C:\Users\Manuel\Documents\BACKTESTS\[Alpha_Sniper_Master4][XAUUSD][M15 (2025.01.01 - 2026.08.31)]\ReportTester-510237104.html",
    "Master4 FULL (22-26)":       r"C:\Users\Manuel\Documents\BACKTESTS\[Alpha_Sniper_Master4][XAUUSD][M15 (2022.01.01 - 2026.08.31)]\ReportTester-510237104.html",
}

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

def metrics(d, label):
    if len(d) == 0: return {"label":label,"N":0,"net":0,"PF":0,"WR":0,"avgW":0,"avgL":0,"RR":0,"MaxDD":0}
    wins = d[d["PnL"]>0]["PnL"]; losses = d[d["PnL"]<=0]["PnL"]
    gp = wins.sum(); gl = abs(losses.sum())
    return dict(label=label, N=len(d), net=gp-gl,
        PF=gp/gl if gl>0 else 9.99, WR=len(wins)/len(d)*100,
        avgW=wins.mean() if len(wins)>0 else 0,
        avgL=abs(losses.mean()) if len(losses)>0 else 0,
        RR=(wins.mean()/abs(losses.mean())) if (len(wins)>0 and len(losses)>0) else 0,
        MaxDD=(d["PnL"].cumsum().cummax()-d["PnL"].cumsum()).max())

print(f"{'Version':<35} {'N':>5} {'Net$':>10} {'PF':>7} {'WR':>6} {'AvgW':>7} {'AvgL':>7} {'RR':>6} {'MaxDD':>9}")
print("="*95)

# Master4 OOS puro (2025-2026)
try:
    df4_oos = parse_html(paths["Master4 OOS only (25-26)"])
    r = metrics(df4_oos, "Master4(3) OOS PURO 25-26")
    print(f"{r['label']:<35} {r['N']:>5} {r['net']:>10,.0f} {r['PF']:>7.3f} {r['WR']:>6.1f}% {r['avgW']:>7.0f} {r['avgL']:>7.0f} {r['RR']:>6.2f} {r['MaxDD']:>9,.0f}")
except Exception as e:
    print(f"ERROR OOS puro: {e}")

# Master4 FULL (2022-2026) - dividido IS/OOS
try:
    df4_full = parse_html(paths["Master4 FULL (22-26)"])
    for d, lbl in [
        (df4_full,                               "Master4(3) FULL  22-26"),
        (df4_full[df4_full["Date"]<"2025-01-01"],"Master4(3) IS    22-24"),
        (df4_full[df4_full["Date"]>="2025-01-01"],"Master4(3) OOS   25-26"),
    ]:
        r = metrics(d, lbl)
        print(f"{r['label']:<35} {r['N']:>5} {r['net']:>10,.0f} {r['PF']:>7.3f} {r['WR']:>6.1f}% {r['avgW']:>7.0f} {r['avgL']:>7.0f} {r['RR']:>6.2f} {r['MaxDD']:>9,.0f}")
except Exception as e:
    print(f"ERROR FULL: {e}")

print("-"*95)
# Baseline
for r in [
    {"label":"BASE TOTAL 22-26","N":1705,"net":349306,"PF":1.448,"WR":21.3,"avgW":3102,"avgL":582,"RR":5.33,"MaxDD":28057},
    {"label":"BASE IS    22-24","N":1091,"net":209637,"PF":1.418,"WR":21.4,"avgW":3053,"avgL":585,"RR":5.22,"MaxDD":25430},
    {"label":"BASE OOS   25-26","N": 614,"net":139669,"PF":1.502,"WR":21.3,"avgW":3190,"avgL":576,"RR":5.54,"MaxDD":18650},
]:
    print(f"{r['label']:<35} {r['N']:>5} {r['net']:>10,.0f} {r['PF']:>7.3f} {r['WR']:>6.1f}% {r['avgW']:>7.0f} {r['avgL']:>7.0f} {r['RR']:>6.2f} {r['MaxDD']:>9,.0f}")
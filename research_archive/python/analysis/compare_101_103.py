import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
from bs4 import BeautifulSoup
import pandas as pd

def parse_html(path, name):
    for enc in ["utf-16","utf-8"]:
        try:
            with open(path,"r",encoding=enc,errors="replace") as f:
                content = f.read()
            if "<html" in content.lower(): break
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
    wins   = d[d["PnL"]>0]["PnL"]
    losses = d[d["PnL"]<=0]["PnL"]
    gp = wins.sum(); gl = abs(losses.sum())
    pf  = gp/gl if gl>0 else float("inf")
    wr  = len(wins)/len(d)*100
    avgW= wins.mean() if len(wins)>0 else 0
    avgL= abs(losses.mean()) if len(losses)>0 else 0
    rr  = avgW/avgL if avgL>0 else float("inf")
    cum = d["PnL"].cumsum()
    dd  = (cum.cummax()-cum).max()
    net = gp-gl
    return dict(label=label, N=len(d), net=net, PF=pf, WR=wr, avgW=avgW, avgL=avgL, RR=rr, MaxDD=dd)

# --- Report 101 (Master Base - referencia) ---
df101 = parse_html(r"C:\Users\Manuel\Documents\BACKTESTS\ReportTester-5102370101.html","101")
r101_total = metrics(df101, "Master BASE - Total")
r101_is    = metrics(df101[df101["Date"]<"2025-01-01"],  "Master BASE - IS  (22-24)")
r101_oos   = metrics(df101[df101["Date"]>="2025-01-01"], "Master BASE - OOS (25-26)")

# --- Report 103 (Master4 accel salida, mejor pase) ---
df103 = parse_html(r"C:\Users\Manuel\Documents\BACKTESTS\ReportTester-5102370103.html","103")
r103_total = metrics(df103, "Master4 SALIDA - Total")
r103_is    = metrics(df103[df103["Date"]<"2025-01-01"],  "Master4 SALIDA - IS  (22-24)")
r103_oos   = metrics(df103[df103["Date"]>="2025-01-01"], "Master4 SALIDA - OOS (25-26)")

rows = [r101_total, r101_is, r101_oos, r103_total, r103_is, r103_oos]

print(f"{'Version':<30} {'N':>6} {'Net$':>10} {'PF':>6} {'WR':>6} {'AvgW':>7} {'AvgL':>7} {'RR':>6} {'MaxDD':>9}")
print("-"*95)
for r in rows:
    print(f"{r['label']:<30} {r['N']:>6} {r['net']:>10,.0f} {r['PF']:>6.3f} {r['WR']:>6.1f}% {r['avgW']:>7.0f} {r['avgL']:>7.0f} {r['RR']:>6.2f} {r['MaxDD']:>9,.0f}")
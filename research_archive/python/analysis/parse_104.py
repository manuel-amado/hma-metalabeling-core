import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
from bs4 import BeautifulSoup
import pandas as pd

def parse_html(path):
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
    if len(d) == 0: return None
    wins   = d[d["PnL"]>0]["PnL"]
    losses = d[d["PnL"]<=0]["PnL"]
    gp = wins.sum(); gl = abs(losses.sum())
    pf   = gp/gl if gl>0 else float("inf")
    wr   = len(wins)/len(d)*100
    avgW = wins.mean()  if len(wins)>0  else 0
    avgL = abs(losses.mean()) if len(losses)>0 else 0
    rr   = avgW/avgL if avgL>0 else float("inf")
    cum  = d["PnL"].cumsum()
    dd   = (cum.cummax()-cum).max()
    net  = gp - gl
    return dict(label=label, N=len(d), net=net, PF=pf, WR=wr, avgW=avgW, avgL=avgL, RR=rr, MaxDD=dd)

# Master4 AccelBars=3 - Reporte 104
df104 = parse_html(r"C:\Users\Manuel\Documents\BACKTESTS\ReportTester-510237104.html")
m_total = metrics(df104,                              "Master4 AccelBars=3 -- TOTAL (22-26)")
m_is    = metrics(df104[df104["Date"]<"2025-01-01"],  "Master4 AccelBars=3 -- IS    (22-24)")
m_oos   = metrics(df104[df104["Date"]>="2025-01-01"], "Master4 AccelBars=3 -- OOS   (25-26)")

# Baseline Master (Reporte 101)
baseline = {
    "label": "Master BASE        -- TOTAL (22-26)",
    "N": 1705, "net": 349306, "PF": 1.448, "WR": 21.3,
    "avgW": 3102, "avgL": 582, "RR": 5.33, "MaxDD": 28057
}
base_is  = {"label": "Master BASE        -- IS    (22-24)", "N": 1091, "net": 209637, "PF": 1.418, "WR": 21.4, "avgW": 3053, "avgL": 585, "RR": 5.22, "MaxDD": 25430}
base_oos = {"label": "Master BASE        -- OOS   (25-26)", "N":  614, "net": 139669, "PF": 1.502, "WR": 21.3, "avgW": 3190, "avgL": 576, "RR": 5.54, "MaxDD": 18650}

print(f"{'Version':<46} {'N':>5} {'Net$':>10} {'PF':>7} {'WR':>6} {'AvgW':>7} {'AvgL':>7} {'RR':>6} {'MaxDD':>9}")
print("=" * 108)

groups = [
    [baseline, base_is, base_oos],
    [m_total,  m_is,    m_oos   ],
]
for g in groups:
    for r in g:
        if r:
            print(f"{r['label']:<46} {r['N']:>5} {r['net']:>10,.0f} {r['PF']:>7.3f} {r['WR']:>6.1f}% {r['avgW']:>7.0f} {r['avgL']:>7.0f} {r['RR']:>6.2f} {r['MaxDD']:>9,.0f}")
    print("-" * 108)

# IS/OOS degradation analysis
print()
print("=== ANALISIS IS->OOS (Degradacion) ===")
for name, r_is, r_oos in [("Master BASE", base_is, base_oos), ("Master4 AccelBars=3", m_is, m_oos)]:
    if r_is and r_oos:
        delta_pf = r_oos["PF"] - r_is["PF"]
        ratio    = r_oos["PF"] / r_is["PF"]
        print(f"{name:<25} IS PF={r_is['PF']:.3f} | OOS PF={r_oos['PF']:.3f} | Delta={delta_pf:+.3f} | Ratio OOS/IS={ratio:.3f}")
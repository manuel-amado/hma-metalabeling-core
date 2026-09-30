import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
from bs4 import BeautifulSoup
import pandas as pd

def parse_html(path):
    content = ""
    for enc in ["utf-16","utf-8","latin-1"]:
        try:
            with open(path,"r",encoding=enc,errors="replace") as f:
                tmp = f.read()
            if "<html" in tmp.lower():
                content = tmp
                break
        except: pass
    if not content:
        raise ValueError(f"No se pudo leer: {path}")
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
    wins   = d[d["PnL"]>0]["PnL"]
    losses = d[d["PnL"]<=0]["PnL"]
    gp = wins.sum(); gl = abs(losses.sum())
    return dict(
        label=label, N=len(d), net=gp-gl,
        PF   = gp/gl if gl>0 else 9.99,
        WR   = len(wins)/len(d)*100,
        avgW = wins.mean()  if len(wins)>0  else 0,
        avgL = abs(losses.mean()) if len(losses)>0 else 0,
        RR   = (wins.mean()/abs(losses.mean())) if (len(wins)>0 and len(losses)>0) else 0,
        MaxDD= (d["PnL"].cumsum().cummax() - d["PnL"].cumsum()).max()
    )

df104  = parse_html(r"C:\Users\Manuel\Documents\BACKTESTS\ReportTester-510237104.html")
rows   = [
    metrics(df104,                              "Master4(3) TOTAL 22-26"),
    metrics(df104[df104["Date"]<"2025-01-01"],  "Master4(3) IS    22-24"),
    metrics(df104[df104["Date"]>="2025-01-01"], "Master4(3) OOS   25-26"),
    {"label":"BASE TOTAL 22-26",  "N":1705,"net":349306,"PF":1.448,"WR":21.3,"avgW":3102,"avgL":582,"RR":5.33,"MaxDD":28057},
    {"label":"BASE IS    22-24",  "N":1091,"net":209637,"PF":1.418,"WR":21.4,"avgW":3053,"avgL":585,"RR":5.22,"MaxDD":25430},
    {"label":"BASE OOS   25-26",  "N": 614,"net":139669,"PF":1.502,"WR":21.3,"avgW":3190,"avgL":576,"RR":5.54,"MaxDD":18650},
]

print(f"{'Version':<28} {'N':>5} {'Net$':>10} {'PF':>7} {'WR':>6} {'AvgW':>7} {'AvgL':>7} {'RR':>6} {'MaxDD':>9}")
print("="*88)
for i, r in enumerate(rows):
    if i == 3: print("-"*88)
    print(f"{r['label']:<28} {r['N']:>5} {r['net']:>10,.0f} {r['PF']:>7.3f} {r['WR']:>6.1f}% {r['avgW']:>7.0f} {r['avgL']:>7.0f} {r['RR']:>6.2f} {r['MaxDD']:>9,.0f}")

print()
print("=== DEGRADACION IS -> OOS ===")
pf_is4  = metrics(df104[df104["Date"]<"2025-01-01"],  "")["PF"]
pf_oos4 = metrics(df104[df104["Date"]>="2025-01-01"], "")["PF"]
print(f"Master4(3):  IS={pf_is4:.3f} -> OOS={pf_oos4:.3f}  | Delta={pf_oos4-pf_is4:+.3f} | Ratio={pf_oos4/pf_is4:.3f}")
print(f"Master BASE: IS=1.418    -> OOS=1.502  | Delta=+0.084   | Ratio=1.059")
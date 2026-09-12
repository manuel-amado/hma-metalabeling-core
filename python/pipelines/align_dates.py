import pandas as pd
import numpy as np

# 1. Load HTML trades
filepath = r'C:\Users\Manuel\Documents\BACKTESTS\ReportTester-1514246756.html'
with open(filepath, 'r', encoding='utf-16', errors='ignore') as f:
    html = f.read()

parsed = []
for line in html.split('\n'):
    if '>out<' in line:
        tds = line.split('<td')
        if len(tds) >= 12:
            try:
                time_str = tds[1].split('>')[1].split('<')[0].replace('.', '-')
                symbol = tds[3].split('>')[1].split('<')[0]
                profit = float(tds[11].split('>')[1].split('<')[0].replace(' ', ''))
                parsed.append({'Time': pd.to_datetime(time_str), 'Symbol': symbol, 'NetProfit': profit})
            except: pass
html_df = pd.DataFrame(parsed).sort_values('Time')

# 2. Load CSV trades for XAUUSD
csv_df = pd.read_csv(r'C:\Users\Manuel\Desktop\HMA_MetaLabeling\Alpha_Sniper_Vault\src\data\Alpha_Sweep_Dataset_v16_1_XAUUSD.csv')
print(f"XAUUSD HTML trades: {len(html_df[html_df['Symbol']=='XAUUSD'])}")
print(f"XAUUSD CSV signals: {len(csv_df)}")

# Get masks
def get_masks(n, nb=10, ob=[2,5,8], em=20):
    bs=n//nb; tr=np.zeros(n,bool); te=np.zeros(n,bool)
    for i in range(nb):
        s=i*bs; e=(i+1)*bs if i<nb-1 else n
        if i in ob: te[s:e]=True
        else: tr[s:e]=True
    return tr, te

tr, te = get_masks(len(csv_df))
csv_df['Is_OOS'] = te
csv_df['Index'] = csv_df.index

print(csv_df[csv_df['Is_OOS']].groupby((~csv_df['Is_OOS']).cumsum())['Index'].agg(['min', 'max', 'count']))

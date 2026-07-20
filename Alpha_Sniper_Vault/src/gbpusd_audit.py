import pandas as pd
import numpy as np

DATA_DIR = r'C:\Users\Manuel\Desktop\HMA_MetaLabeling\Alpha_Sniper_Vault\data'

def audit(sym):
    path = f'{DATA_DIR}\\Struct_Dataset_{sym}.csv'
    df = pd.read_csv(path)
    df.columns = [c.strip() for c in df.columns]

    print(f'\n=== {sym} DATASET AUDIT ===')
    print(f'Total rows: {len(df)}')

    time_col = next((c for c in df.columns if c.lower() in ['time','date','open_time']), None)
    if time_col:
        df['_time'] = pd.to_datetime(df[time_col], errors='coerce')
        print(f'Date range: {df["_time"].min()} -> {df["_time"].max()}')
        # Per-year trade count
        df['_year'] = df['_time'].dt.year
        yearly = df.groupby('_year').size()
        print(f'Signals per year: {dict(yearly)}')

    if 'Realized_RR' in df.columns:
        rr = df['Realized_RR'].dropna()
        print(f'Realized_RR: mean={rr.mean():.4f} | median={rr.median():.4f} | std={rr.std():.4f}')
        print(f'  Win(>0)={( rr>0).mean()*100:.1f}% | WinGood(>=0.5)={(rr>=0.5).mean()*100:.1f}% | SL(<-0.9)={(rr<-0.9).mean()*100:.1f}%')
        
        # Year-by-year Realized_RR mean (detect regime degradation)
        if '_year' in df.columns:
            yearly_rr = df.groupby('_year')['Realized_RR'].mean()
            print(f'  Mean RR by year:')
            for yr, val in yearly_rr.items():
                flag = ' <- NEGATIVO' if val < 0 else ''
                print(f'    {yr}: {val:.4f}{flag}')

    if 'Label' in df.columns:
        print(f'Label: positive_rate={(df["Label"].mean()*100):.1f}%')

    if 'Return_Pct' in df.columns:
        rp = df['Return_Pct'].dropna()
        print(f'Return_Pct: mean={rp.mean():.4f}% | SL_hits={(rp<-0.9).mean()*100:.1f}%')

print('COMPARISON: GBPUSD vs USDJPY vs XAUUSD')
for sym in ['GBPUSD', 'USDJPY', 'XAUUSD']:
    audit(sym)

import pandas as pd, numpy as np, os
DATA_DIR = r'C:\Users\Manuel\Desktop\HMA_MetaLabeling\Alpha_Sniper_Vault\src\data'
syms = ['XAUUSD','EURUSD','USDJPY','AUDUSD']
for sym in syms:
    fp = os.path.join(DATA_DIR, 'Alpha_Sweep_Dataset_v16_' + sym + '.csv')
    df = pd.read_csv(fp)
    n_before = len(df)
    mask_pos = (df['Label']==1) & (df['ReturnPct']<0)
    mask_neg = (df['Label']==0) & (df['ReturnPct']>0)
    df.loc[mask_pos, 'ReturnPct'] = df.loc[mask_pos, 'ReturnPct'].abs()
    df.loc[mask_neg, 'ReturnPct'] = -df.loc[mask_neg, 'ReturnPct'].abs()
    df.to_csv(fp, index=False)
    wr = round((df['Label']==1).mean()*100, 1)
    avg_win  = round(df[df['Label']==1]['ReturnPct'].mean(), 4)
    avg_loss = round(df[df['Label']==0]['ReturnPct'].mean(), 4)
    print('[' + sym + '] n=' + str(n_before) + ' | WR=' + str(wr) + '% | AvgRetWin=' + str(avg_win) + '% | AvgRetLoss=' + str(avg_loss) + '%')
print('CSVs corregidos.')

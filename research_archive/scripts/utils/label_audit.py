import pandas as pd, numpy as np, os
DATA_DIR = r'C:\Users\Manuel\Desktop\HMA_MetaLabeling\Alpha_Sniper_Vault\src\data'
for sym in ['XAUUSD','EURUSD','USDJPY','AUDUSD']:
    df = pd.read_csv(os.path.join(DATA_DIR, f'Alpha_Sweep_Dataset_v16_{sym}.csv'))
    n = len(df)
    pos = (df['Label']==1).sum()
    neg = (df['Label']==0).sum()
    ret_pos = df[df['Label']==1]['ReturnPct'].mean()
    ret_neg = df[df['Label']==0]['ReturnPct'].mean()
    ret_abs = df['ReturnPct'].abs().mean()
    zero_ret = (df['ReturnPct'].abs() < 0.0001).sum()
    print(f'[{sym}] n={n} | Label1={pos}({pos/n*100:.1f}%) | Label0={neg}({neg/n*100:.1f}%) | AvgRetWin={ret_pos:.4f}% | AvgRetLoss={ret_neg:.4f}% | AvgAbsRet={ret_abs:.4f}% | ZeroRet={zero_ret}')

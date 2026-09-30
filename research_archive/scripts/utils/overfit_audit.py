import os, pandas as pd, numpy as np, joblib
DATA_DIR = r'C:\Users\Manuel\Desktop\HMA_MetaLabeling\Alpha_Sniper_Vault\src\data'
MODEL_PATH = r'C:\Users\Manuel\Desktop\HMA_MetaLabeling\Alpha_Sniper_Vault\src\output\modelo_v16_universal.pkl'
FEATURES=['SignalType','HMAAccelF','MTFATRRatio','DistSynthH4','CandleDominance','TWAPZScore','ATRRatioH','RSI','DistAsianHigh','DistAsianLow','RSIExt','VolSpreadRatio','Spread','TrigRejTail','RibbonSpreadStd','Feature_RibbonAlign','Feature_VPivotMonotonic','RSI_Memory_State','OppositeBarsCount','Regime_ATR_D1','Regime_ADX_H1','PriceDevATR','BuildupLength','DayOfWeek','DistRunwayHMA200']
def get_masks(n,nb=10,ob=[2,5,8],em=20):
    bs=n//nb; tr=np.zeros(n,bool); te=np.zeros(n,bool)
    for i in range(nb):
        s=i*bs; e=(i+1)*bs if i<nb-1 else n
        if i in ob: te[s:e]=True
        else: tr[s:e]=True
    for i in range(1,nb):
        b=i*bs
        if ((i-1) in ob)!=(i in ob):
            tr[max(0,b-em):min(n,b+em)]=False; te[max(0,b-em):min(n,b+em)]=False
    return tr,te
art=joblib.load(MODEL_PATH); m=art['model']; sc=art['scaler']; thr=art['threshold']
print('Threshold:',round(thr,4),'| depth:',m.get_params()['max_depth'],'| trees:',m.get_params()['n_estimators'])
print()
RW=1.7; RL=-1.0
for sym in ['XAUUSD','EURUSD','USDJPY','AUDUSD']:
    fp=os.path.join(DATA_DIR,f'Alpha_Sweep_Dataset_v16_{sym}.csv')
    if not os.path.exists(fp): continue
    df=pd.read_csv(fp).dropna(subset=FEATURES+['Label']).reset_index(drop=True)
    n=len(df); tr,te=get_masks(n)
    X=pd.DataFrame(sc.transform(df[FEATURES]),columns=FEATURES)
    probs=m.predict_proba(X)[:,1]
    def ev(mask):
        pz=probs[mask]; yz=df['Label'].values[mask]; pred=pz>=thr
        tk=pred.sum()
        if tk==0: return 0,0,0,0
        wr=(yz[pred]==1).sum()/tk*100
        nr=np.where(pred,np.where(yz==1,RW,RL),0).sum()
        return int(tk),round(float(wr),1),round(float(nr),1),round(float(pz[pred].mean()),4)
    it,iwr,inr,iap=ev(tr); ot,owr,onr,oap=ev(te)
    deg=round(iwr-owr,1); pg=round(iap-oap,4)
    rat=round(onr/inr,2) if inr!=0 else 0
    verdict='ROBUSTO (<5pp)' if abs(deg)<5 else 'ACEPTABLE (5-10pp)' if abs(deg)<10 else 'OVERFIT SOSPECHADO (>10pp)'
    print(f'[{sym}] n={n} | IS_taken={it} | OOS_taken={ot}')
    print(f'  IS   WR={iwr}% Net={inr}R AvgProb={iap}')
    print(f'  OOS  WR={owr}% Net={onr}R AvgProb={oap}')
    print(f'  Degradacion={deg:+}pp ProbGap={pg:+} OOS/IS_ratio={rat} Veredicto={verdict}')
    print()

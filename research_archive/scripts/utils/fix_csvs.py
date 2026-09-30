import os
import pandas as pd
import glob

DATA_DIR = r"C:\Users\Manuel\Desktop\HMA_MetaLabeling\Alpha_Sniper_Vault\src\data"
csv_files = glob.glob(os.path.join(DATA_DIR, "Alpha_Sweep_Dataset_v17_*.csv"))

HEADER = [
    "Time", "SignalType", "HMAAccelF", "MTFATRRatio", "DistSynthH4", "CandleDominance", "TWAPZScore", 
    "ATRRatioH", "RSI", "DistAsianHigh", "DistAsianLow", "RSIExt", "VolSpreadRatio", "Spread",
    "TrigRejTail", "RibbonSpreadStd", "Feature_RibbonAlign", "VPivotMonotonic", "RSIMemory", 
    "OppositeBarsCount", "Regime_ATR_D1", "Regime_ADX_H1", "PriceDevATR", "BuildupLength", 
    "PandasDOW", "DistRunwayHMA200", "BarsVolShock", "Time_Sine", "Time_Cosine", "PainIndex",
    "ReturnPct", "Label"
]

for f in csv_files:
    # Read ignoring the corrupted first row
    df = pd.read_csv(f, skiprows=1, header=None)
    # If the file had 32 columns, assign our exact header
    if df.shape[1] == 32:
        df.columns = HEADER
        df.to_csv(f, index=False)
        print(f"Fixed {os.path.basename(f)}")
    else:
        print(f"Skipped {os.path.basename(f)} (found {df.shape[1]} columns)")

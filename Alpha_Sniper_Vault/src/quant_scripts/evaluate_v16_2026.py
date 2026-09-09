import os
import glob
import pandas as pd
import numpy as np
import joblib

DATA_DIR = r"C:\Users\Manuel\Desktop\HMA_MetaLabeling\Alpha_Sniper_Vault\src\data"
MODEL_PATH = r"C:\Users\Manuel\Desktop\HMA_MetaLabeling\Alpha_Sniper_Vault\src\output\modelo_v16_universal.pkl"

def main():
    print("=======================================================")
    print("   REPORTE DE ZONA OOS ABSOLUTA (AÑO 2026)             ")
    print("=======================================================")
    
    if not os.path.exists(MODEL_PATH):
        print("ERROR: Modelo no encontrado.")
        return
        
    artifact = joblib.load(MODEL_PATH)
    model = artifact['model']
    scaler = artifact['scaler']
    features = artifact['features_activas']
    threshold = artifact.get('threshold', 0.5)
    
    files_2026 = glob.glob(os.path.join(DATA_DIR, "Alpha_Sweep_Dataset_v16_*_2026.csv"))
    if not files_2026:
        print("No se encontraron archivos de validación _2026.csv")
        return
        
    total_trades = 0
    total_wins = 0
    total_gross_profit = 0.0
    total_gross_loss = 0.0
    
    for f in files_2026:
        sym = os.path.basename(f).replace('Alpha_Sweep_Dataset_v16_', '').replace('_2026.csv', '')
        df = pd.read_csv(f)
        
        if len(df) == 0:
            continue
            
        X = df[features]
        X_scaled = scaler.transform(X)
        proba = model.predict_proba(X_scaled)[:, 1]
        
        df['Pred'] = (proba >= threshold).astype(int)
        
        trades_df = df[df['Pred'] == 1]
        wins = trades_df[trades_df['Label'] == 1]
        losses = trades_df[trades_df['Label'] == 0]
        
        trades = len(trades_df)
        wr = len(wins) / trades * 100.0 if trades > 0 else 0.0
        
        gross_profit = sum([abs(x) for x in wins['ReturnPct']])
        gross_loss = sum([abs(x) if abs(x) > 0.001 else 0.001 for x in losses['ReturnPct']])
        pf = gross_profit / gross_loss if gross_loss > 0 else 999.0
        real_net = len(losses) * (pf - 1.0) * 1.0 # 1% risk per trade
        
        print(f"[{sym}] Trades OOS 2026: {trades} | Win Rate: {wr:.2f}% | PF: {pf:.3f} | Real Net Return (1% Risk): {real_net:+.2f}%")
        
        total_trades += trades
        total_wins += len(wins)
        total_gross_profit += gross_profit
        total_gross_loss += gross_loss

    print("-------------------------------------------------------")
    global_wr = total_wins / total_trades * 100.0 if total_trades > 0 else 0.0
    global_pf = total_gross_profit / total_gross_loss if total_gross_loss > 0 else 999.0
    global_real_net = (total_trades - total_wins) * (global_pf - 1.0) * 1.0
    
    print(f"[GLOBAL] Trades Totales: {total_trades} | Win Rate: {global_wr:.2f}% | PF: {global_pf:.3f} | Real Net Return: {global_real_net:+.2f}%")
    print("=======================================================\n")

if __name__ == "__main__":
    main()

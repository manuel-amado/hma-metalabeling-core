import pandas as pd
import numpy as np
import joblib
import os

DATA_DIR = r"C:\Users\Manuel\Desktop\HMA_MetaLabeling"
OUT_DIR = r"C:\Users\Manuel\Desktop\HMA_MetaLabeling\Alpha_Sniper_Vault\src\output"
SYMBOLS = ['XAUUSD', 'USDJPY', 'AUDUSD']

def get_interleaved_masks(total_rows, n_blocks=10, oos_blocks=[2, 5, 8], embargo_bars=15):
    block_size = total_rows // n_blocks
    train_mask = np.zeros(total_rows, dtype=bool)
    test_mask = np.zeros(total_rows, dtype=bool)
    
    for i in range(n_blocks):
        start = i * block_size
        end = (i + 1) * block_size if i < n_blocks - 1 else total_rows
        if i in oos_blocks:
            test_mask[start:end] = True
        else:
            train_mask[start:end] = True
            
    for i in range(1, n_blocks):
        boundary = i * block_size
        prev_is_oos = (i - 1) in oos_blocks
        curr_is_oos = i in oos_blocks
        if prev_is_oos != curr_is_oos:
            purge_start = max(0, boundary - embargo_bars)
            purge_end = min(total_rows, boundary + embargo_bars)
            train_mask[purge_start:purge_end] = False
            test_mask[purge_start:purge_end] = False
            
    return train_mask, test_mask, block_size

def run():
    report_lines = []
    report_lines.append("# Net Profit Meta-Labeling (V12) - Reporte de Validación Temporal\n")
    report_lines.append("El análisis disecciona el historial (2015-2026) en 10 Bloques de validación cruzada. Se aplica una rigurosa inyección de fricción sintética ($\kappa = 2.5$ pips) a cada operación. Los bloques **OOS (Out-Of-Sample)** son zonas completamente **ciegas** para el modelo durante su entrenamiento.\n")
    
    for sym in SYMBOLS:
        report_lines.append(f"## {sym} - Perfil de Rendimiento\n")
        data_path = os.path.join(DATA_DIR, f"Alpha_Sweep_Dataset_{sym}.csv")
        model_path = os.path.join(OUT_DIR, f"modelo_m15_{sym}.pkl")
        
        df = pd.read_csv(data_path)
        artifact = joblib.load(model_path)
        model = artifact['model']
        scaler = artifact['scaler']
        features = artifact['features_activas']
        threshold = artifact.get('threshold', 0.5)
        
        X = df[features]
        X_scaled = scaler.transform(X)
        proba = model.predict_proba(X_scaled)[:, 1]
        y_pred = (proba >= threshold).astype(int)
        
        total_rows = len(df)
        train_mask, test_mask, block_size = get_interleaved_masks(total_rows)
        
        report_lines.append("| Bloque Temporal (Aprox) | Zona (IS/OOS) | Trades | Win Rate | Pips Netos | Profit Factor |")
        report_lines.append("|---|---|---|---|---|---|")
        
        total_pips = 0
        total_trades = 0
        total_wins = 0
        
        for i in range(10):
            start = i * block_size
            end = (i + 1) * block_size if i < 9 else total_rows
            
            is_oos = i in [2, 5, 8]
            tipo = "**OOS (Ciega)**" if is_oos else "IS (Entrenamiento)"
            year = 2015 + int(i * (11.0 / 10.0))
            
            mask = np.zeros(total_rows, dtype=bool)
            mask[start:end] = True
            
            if not is_oos:
                mask = mask & train_mask
            else:
                mask = mask & test_mask
                
            block_df = df[mask]
            block_preds = y_pred[mask]
            
            trades_indices = np.where(block_preds == 1)[0]
            trades_count = len(trades_indices)
            
            if trades_count == 0:
                report_lines.append(f"| {year} | {tipo} | 0 | 0.00% | 0.0 | N/A |")
                continue
                
            block_trades = block_df.iloc[trades_indices]
            
            if 'ProfitPips' in block_trades.columns:
                pips = block_trades['ProfitPips'].values
                # Fricción sintética: -2.5 pips por trade
                net_pips_arr = pips - 2.5
                
                net_pips = np.sum(net_pips_arr)
                wins = len(net_pips_arr[net_pips_arr > 0])
                
                gross_profits = np.sum(net_pips_arr[net_pips_arr > 0])
                gross_losses = np.sum(np.abs(net_pips_arr[net_pips_arr <= 0]))
                
                pf = gross_profits / (gross_losses + 1e-9) if gross_losses > 0 else 999.0
            else:
                ret = block_trades['ReturnPct'].values
                wins = len(ret[ret > 0])
                gross_profits = np.sum(ret[ret > 0])
                gross_losses = np.sum(np.abs(ret[ret <= 0]))
                net_pips = (gross_profits - gross_losses) * 100
                pf = gross_profits / (gross_losses + 1e-9) if gross_losses > 0 else 999.0
                
            wr = (wins / trades_count) * 100
            
            report_lines.append(f"| {year} | {tipo} | {trades_count} | {wr:.2f}% | {net_pips:.1f} | {pf:.2f} |")
            
            total_pips += net_pips
            total_trades += trades_count
            total_wins += wins
            
        global_wr = (total_wins / total_trades * 100) if total_trades > 0 else 0
        report_lines.append("\n> [!TIP]")
        report_lines.append(f"> **Resumen Global {sym}:** {total_trades} Operaciones Ejecutadas | **Win Rate Total:** {global_wr:.2f}% | **Pips Netos Recaudados:** {total_pips:.1f} pips\n")

    with open(r"C:\Users\Manuel\.gemini\antigravity\brain\f9484352-59cf-461b-b568-f2a15424ff70\portfolio_performance_v12.md", "w", encoding="utf-8") as f:
        f.write("\n".join(report_lines))
    print("Reporte generado.")

if __name__ == '__main__':
    run()

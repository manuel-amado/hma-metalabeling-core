import os
import pandas as pd
import numpy as np
import joblib
import matplotlib.pyplot as plt
import matplotlib.patches as patches

DATA_DIR = r"C:\Users\Manuel\Desktop\HMA_MetaLabeling\Alpha_Sniper_Vault\src\data"
MODEL_PATH = r"C:\Users\Manuel\Desktop\HMA_MetaLabeling\Alpha_Sniper_Vault\src\output\modelo_v16_universal.pkl"

FEATURES = [
    "SignalType", "HMAAccelF", "MTFATRRatio", "DistSynthH4",
    "CandleDominance", "TWAPZScore", "ATRRatioH", "RSI",
    "DistAsianHigh", "DistAsianLow", "RSIExt", "VolSpreadRatio",
    "Spread", "TrigRejTail", "RibbonSpreadStd", "Feature_RibbonAlign",
    "Feature_VPivotMonotonic", "RSI_Memory_State", "OppositeBarsCount",
    "Regime_ATR_D1", "Regime_ADX_H1", "PriceDevATR", "BuildupLength", "DayOfWeek", "DistRunwayHMA200"
]

def get_interleaved_masks(total_rows, n_blocks=10, oos_blocks=[2, 5, 8]):
    block_size = total_rows // n_blocks
    train_mask = np.zeros(total_rows, dtype=bool)
    test_mask = np.zeros(total_rows, dtype=bool)
    oos_regions = []
    
    for i in range(n_blocks):
        start = i * block_size
        end = (i + 1) * block_size if i < n_blocks - 1 else total_rows
        if i in oos_blocks:
            test_mask[start:end] = True
            oos_regions.append((start, end))
        else:
            train_mask[start:end] = True

    return train_mask, test_mask, oos_regions

def main():
    artifact = joblib.load(MODEL_PATH)
    model = artifact['model']
    scaler = artifact['scaler']
    threshold = artifact['threshold']
    threshold = 0.5306
    
    symbols = ['XAUUSD', 'EURUSD', 'USDJPY', 'AUDUSD']
    colors = {'XAUUSD': 'gold', 'EURUSD': 'royalblue', 'USDJPY': 'crimson', 'AUDUSD': 'forestgreen'}
    
    plt.style.use('dark_background')
    fig, ax = plt.subplots(figsize=(14, 7))
    
    max_rows = 0
    oos_regions_global = []

    for sym in symbols:
        file_path = os.path.join(DATA_DIR, f"Alpha_Sweep_Dataset_v16_{sym}.csv")
        if not os.path.exists(file_path):
            print(f"No se encontro: {file_path}")
            continue
            
        df = pd.read_csv(file_path)
        # Limpiar NaNs
        df = df.dropna(subset=FEATURES + ['ReturnPct'])
        df = df.reset_index(drop=True)
        
        train_mask, test_mask, oos_regions = get_interleaved_masks(len(df))
        if len(df) > max_rows:
            max_rows = len(df)
            oos_regions_global = oos_regions # Para dibujar el sombreado basado en el activo mas largo
            
        X = pd.DataFrame(scaler.transform(df[FEATURES]), columns=FEATURES)
        
        # Prediccion
        probs = model.predict_proba(X)[:, 1]
        
        # Aplicar umbral y calcular retornos
        # Simulamos riesgo fijo 1% como en MT5
        returns = np.where(probs >= threshold, df['ReturnPct'], 0.0)
        
        # Cumulative return
        cumulative = returns.cumsum()
        
        # Normalizar el eje X (0 a 100%) para alinear los bloques OOS de todos los activos
        x_axis = np.linspace(0, 100, len(cumulative))
        
        ax.plot(x_axis, cumulative, label=sym, color=colors[sym], linewidth=2, alpha=0.9)

    # Shading OOS regions (normalize to 0-100%)
    if max_rows > 0:
        for (start, end) in oos_regions_global:
            start_pct = (start / max_rows) * 100
            end_pct = (end / max_rows) * 100
            ax.axvspan(start_pct, end_pct, color='red', alpha=0.15, lw=0)

    # Etiquetas
    ax.set_title("V16 Portfolio Cumulative Returns (IS/OOS Interleaved Validation)", fontsize=14, pad=15)
    ax.set_xlabel("Progreso Temporal / Transacciones (%)", fontsize=11)
    ax.set_ylabel("Retorno Acumulado Neto (En % de Cuenta)", fontsize=11)
    
    # Custom Legend para explicar colores de fondo
    import matplotlib.lines as mlines
    is_patch = patches.Patch(color='black', label='Zona IS (In-Sample)')
    oos_patch = patches.Patch(color='red', alpha=0.15, label='Zona OOS (Out-of-Sample)')
    
    handles, labels = ax.get_legend_handles_labels()
    handles.extend([is_patch, oos_patch])
    
    ax.legend(handles=handles, loc='upper left', frameon=True, facecolor='black', edgecolor='gray')
    ax.grid(color='gray', linestyle='--', alpha=0.3)
    
    out_file = r"C:\Users\Manuel\Desktop\HMA_MetaLabeling\v16_equity_curve_isos.png"
    plt.tight_layout()
    plt.savefig(out_file, dpi=150)
    print(f"Grafica guardada en {out_file}")

if __name__ == "__main__":
    main()


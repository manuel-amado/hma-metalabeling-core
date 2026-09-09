import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from xgboost import XGBClassifier

def main():
    df = pd.read_csv('../OmniApex_Dataset.csv')
    
    # Sort chronologically if needed (assume already sorted)
    
    features = [
        'Signal_Type', 
        'Micro_Velocity', 
        'Micro_Acceleration', 
        'Macro_Velocity', 
        'Tension_Ratio', 
        'ER_Kaufman', 
        'ADX_Value', 
        'RSI_Value'
    ]
    
    X = df[features].astype(np.float32)
    y = df['Target_Label'].astype(np.int64)
    profits = df['Profit'].values
    
    # Train the exact same model
    model = XGBClassifier(
        n_estimators=300,
        max_depth=6,
        learning_rate=0.03,
        subsample=0.8,
        colsample_bytree=0.8,
        random_state=42,
        use_label_encoder=False,
        eval_metric='logloss'
    )
    
    model.fit(X.values, y.values)
    probs = model.predict_proba(X.values)[:, 1]
    
    THRESHOLD = 0.65
    predictions = (probs >= THRESHOLD).astype(int)
    
    equity_base = [100000]
    equity_onnx = [100000]
    
    for i in range(len(profits)):
        equity_base.append(equity_base[-1] + profits[i])
        
        # ONNX only takes the trade if prediction == 1
        if predictions[i] == 1:
            equity_onnx.append(equity_onnx[-1] + profits[i])
        else:
            equity_onnx.append(equity_onnx[-1])
            
    plt.figure(figsize=(12, 6))
    plt.plot(equity_base, label='Capa 1 (Base Cinemática)', color='gray', alpha=0.7, linewidth=1.5)
    plt.plot(equity_onnx, label='Capa 2 (ONNX Meta-Labeling)', color='#00ff9d', linewidth=2.5)
    
    plt.title('Curva de Equidad: Impacto de Filtrado IA (XAUUSD)', fontsize=16, fontweight='bold', color='white')
    plt.xlabel('Número de Trades', color='white')
    plt.ylabel('Equidad (USD)', color='white')
    
    ax = plt.gca()
    ax.set_facecolor('#1e1e1e')
    plt.gcf().patch.set_facecolor('#121212')
    
    ax.spines['bottom'].set_color('#333333')
    ax.spines['top'].set_color('#333333')
    ax.spines['right'].set_color('#333333')
    ax.spines['left'].set_color('#333333')
    ax.tick_params(colors='white')
    
    legend = plt.legend(facecolor='#1e1e1e', edgecolor='#333333', labelcolor='white')
    plt.grid(True, color='#333333', linestyle='--', alpha=0.5)
    
    # Add stats
    total_trades_base = len(profits)
    total_trades_onnx = sum(predictions)
    
    profit_base = equity_base[-1] - 100000
    profit_onnx = equity_onnx[-1] - 100000
    
    stats_text = (f"Trades Base: {total_trades_base} | Profit: ${profit_base:.2f}\n"
                  f"Trades ONNX: {total_trades_onnx} | Profit: ${profit_onnx:.2f}")
    
    plt.text(0.02, 0.95, stats_text, transform=ax.transAxes, color='white', 
             fontsize=12, verticalalignment='top', bbox=dict(facecolor='#1e1e1e', alpha=0.8, edgecolor='#333333'))
    
    plt.tight_layout()
    # Save the plot to the artifact directory so it can be viewed in the UI!
    plt.savefig(r'C:\Users\Manuel\.gemini\antigravity\brain\3afd35dc-83ad-433d-935f-a417317b3673\equity_curve.png', dpi=300)
    print("Grafico generado en equity_curve.png")

if __name__ == '__main__':
    main()

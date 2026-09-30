import pandas as pd
import numpy as np
from xgboost import XGBClassifier
from sklearn.model_selection import TimeSeriesSplit
from sklearn.preprocessing import RobustScaler

def main():
    print(" Evaluando la V11.3 SIN SESGO DE SIMULACION (Usando Label de Beneficio Neto Real de MT5)")
    df = pd.read_csv(r"C:\Users\Manuel\Desktop\HMA_MetaLabeling\Alpha_Sniper_Vault\data\Alpha_Sweep_Dataset_XAUUSD.csv")
    
    # V11 Features
    FEATURES = [
        "SignalType", "HMAAccelF", "MTFATRRatio", "DistSynthH4",
        "BarsVolShock", "TWAPZScore", "ATRRatioH", "RSI",
        "DistAsianHigh", "DistAsianLow", "RSIExt", "VolSpreadRatio",
        "Spread", "TrigRejTail", "RibbonSpreadStd", "Feature_RibbonAlign",
        "Feature_VPivotMonotonic", "RSI_Memory_State", "OppositeBarsCount"
    ]
    
    X = df[FEATURES]
    # LA VERDAD: Usamos la columna Label (que incluye swap y comisiones) en lugar del viejo ProfitPips - 2.5
    y = df['Label']
    
    # Train / OOS Split (simplificado para demostracion)
    split_idx = int(len(X) * 0.7)
    X_train, X_test = X.iloc[:split_idx], X.iloc[split_idx:]
    y_train, y_test = y.iloc[:split_idx], y.iloc[split_idx:]
    df_test = df.iloc[split_idx:]
    
    scaler = RobustScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)
    
    model = XGBClassifier(
        n_estimators=100,
        max_depth=4,
        learning_rate=0.05,
        random_state=42,
        eval_metric='logloss'
    )
    
    model.fit(X_train_scaled, y_train)
    
    proba = model.predict_proba(X_test_scaled)[:, 1]
    threshold = np.percentile(model.predict_proba(X_train_scaled)[:, 1], 75)
    
    y_pred = (proba >= threshold).astype(int)
    
    wins = df_test[(y_pred == 1) & (df_test['Label'] == 1)]
    losses = df_test[(y_pred == 1) & (df_test['Label'] == 0)]
    
    trades = sum(y_pred)
    wr = len(wins) / trades * 100.0 if trades > 0 else 0.0
    
    gross_profit = sum(wins['ReturnPct'])
    gross_loss = sum([abs(x) if abs(x) > 0.05 else 0.05 for x in losses['ReturnPct']])
    pf = gross_profit / gross_loss if gross_loss > 0 else 999.0
    
    print(f"\n=======================================================")
    print(f"REPORTE V11.3 - VERDAD ABSOLUTA (SIN SESGO DE SIMULACION)")
    print(f"=======================================================")
    print(f"Operaciones Ejecutadas (OOS): {trades}")
    print(f"Win Rate OOS (Neto):          {wr:.2f}%")
    print(f"Profit Factor OOS (Neto):     {pf:.3f}")
    if pf > 1.05:
        print("ESTADO: ROBUSTO. El edge era real.")
    else:
        print("ESTADO: FALLO CRITICO (OVERFIT). V11.3 JAMAS FUE RENTABLE.")

if __name__ == "__main__":
    main()

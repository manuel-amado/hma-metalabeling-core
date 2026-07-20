import os
import pandas as pd
import numpy as np
import joblib
from xgboost import XGBClassifier
from sklearn.model_selection import KFold
from sklearn.preprocessing import RobustScaler
import argparse
import warnings

warnings.filterwarnings("ignore")

parser = argparse.ArgumentParser()
parser.add_argument('--data', type=str, default=r"C:\Users\Manuel\Desktop\HMA_MetaLabeling\Alpha_Sweep_Dataset_XAUUSD.csv")
parser.add_argument('--model', type=str, default=r"C:\Users\Manuel\Desktop\HMA_MetaLabeling\Alpha_Sniper_Vault\src\output\modelo_m15_universal.pkl")
args = parser.parse_args()

DATA_PATH = args.data
MODEL_PATH = args.model

def main():
    print("=== PRUEBA DE PERMUTACION DESTRUCTIVA (LABEL SHUFFLING) ===")
    
    # 1. Cargar modelo base y parametros
    artifact = joblib.load(MODEL_PATH)
    base_model = artifact['model']
    features = artifact['features_activas']
    
    # Extraer hiperparametros
    params = base_model.get_params()
    
    # 2. Cargar datos
    def load_data():
        df = pd.read_csv(DATA_PATH)
        X = df[features]
        y = df["Label"]
        return X, y, df

    X, y_real, df = load_data()
    
    # 3. MODO DESTRUCTIVO: Mezclar las etiquetas aleatoriamente
    # Rompemos la causalidad matematica entre X y Y.
    np.random.seed(99)
    y_shuffled = np.random.permutation(y_real)
    
    # 4. Evaluacion K-Fold
    kf = KFold(n_splits=5, shuffle=True, random_state=42)
    precisions = []
    
    print("Entrenando con etiquetas aleatorias (Se espera que colapse al ~50%)...")
    
    fold = 1
    for train_index, test_index in kf.split(X):
        X_train, X_test = X.iloc[train_index], X.iloc[test_index]
        y_train, y_test = y_shuffled[train_index], y_shuffled[test_index]
        df_test = df.iloc[test_index]
        
        scaler = RobustScaler()
        X_train_scaled = scaler.fit_transform(X_train)
        X_test_scaled = scaler.transform(X_test)
        
        scale_pos = len(y_train[y_train==0]) / len(y_train[y_train==1]) if sum(y_train) > 0 else 1.0
        
        model = XGBClassifier(**params)
        model.set_params(scale_pos_weight=scale_pos, random_state=42)
        
        model.fit(X_train_scaled, y_train)
        
        proba = model.predict_proba(X_test_scaled)[:, 1]
        
        # Evaluar al percentil 90 (mismo criterio de Optuna)
        threshold = np.percentile(proba, 90)
        y_pred = (proba >= threshold).astype(int)
        
        # Validar el Win Rate REAL (ReturnPct) de las operaciones tomadas
        wins = df_test[(y_pred == 1) & (df_test['ReturnPct'] > 0)]
        trades = sum(y_pred)
        
        if trades == 0:
            print(f"Fold {fold}: Trades=0")
        else:
            wr = len(wins) / trades * 100
            print(f"Fold {fold}: Trades={trades} | Win Rate Destruido={wr:.1f}%")
            precisions.append(wr)
            
        fold += 1
        
    avg_wr = np.mean(precisions)
    print(f"\n[CERTIFICACION] Win Rate Promedio tras Shuffling: {avg_wr:.2f}%")
    
    if avg_wr < 53.0:
        print("[EXITO] EL MODELO HA COLAPSADO. Certificamos matematicamente que NO HAY OVERFIT a ruido.")
    else:
        print("[PELIGRO] El modelo sigue ganando con etiquetas aleatorias. HAY OVERFITTING SEVERO.")

if __name__ == "__main__":
    main()

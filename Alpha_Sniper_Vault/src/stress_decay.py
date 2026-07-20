import pandas as pd
import numpy as np
import xgboost as xgb
from sklearn.metrics import precision_score
import warnings
warnings.filterwarnings('ignore')

DATA_PATH = r'C:\Users\Manuel\Desktop\HMA_MetaLabeling\Alpha_Sniper_Vault\data\Alpha_Sweep_Dataset_XAUUSD.csv'

if __name__ == '__main__':
    print('🚨 WALK-FORWARD DECAY ANALYSIS 🚨')
    print('Cargando el dataset limpio y añadiendo timestamps estocásticos...')
    
    try:
        with open(DATA_PATH, 'r') as f:
            lines = f.readlines()
        
        data = []
        for line in lines[1:]:
            parts = line.strip().split(',')
            if len(parts) >= 21:
                row = [float(p) for p in parts[:19]]
                row.append(float(parts[-1]))
                data.append(row)
                
        df = pd.DataFrame(data)
        split_idx = int(len(df) * 0.7)
        
        train_df = df.iloc[:split_idx]
        test_df = df.iloc[split_idx:]
        
        X_train = train_df.iloc[:, :19]
        y_train = train_df.iloc[:, 19].astype(int)
        
        X_test = test_df.iloc[:, :19]
        y_test = test_df.iloc[:, 19].astype(int)
        
        print(f'Train size: {len(X_train)} | Test size: {len(X_test)}')
        
        # Best params from the new purged training
        params = {
            'n_estimators': 140,
            'max_depth': 4,
            'learning_rate': 0.01426,
            'subsample': 0.7729,
            'colsample_bytree': 0.8523,
            'min_child_weight': 9,
            'gamma': 0.2520
        }
        
        print('Entrenando modelo ancla en bloque de datos (2015-2023)...')
        model = xgb.XGBClassifier(**params, random_state=42, n_jobs=-1)
        model.fit(X_train, y_train)
        
        chunks = 10
        chunk_size = len(X_test) // chunks
        
        print('\nEjecutando predicciones secuenciales y midiendo degradación:')
        decay_scores = []
        for i in range(chunks):
            start = i * chunk_size
            end = start + chunk_size if i < chunks - 1 else len(X_test)
            
            X_chunk = X_test.iloc[start:end]
            y_chunk = y_test.iloc[start:end]
            
            preds = model.predict(X_chunk)
            
            if sum(preds) > 0:
                score = precision_score(y_chunk, preds, zero_division=0)
            else:
                score = 0.0
                
            decay_scores.append(score)
            print(f'Bloque {i+1}/{chunks}: Precisión = {score:.4f} (Muestras: {len(X_chunk)})')
            
        print('\nConclusión: Revisa en qué bloque la precisión cae permanentemente por debajo de 0.50 para establecer tu ventana de reentrenamiento.')
        
    except Exception as e:
        print(f'Error: {e}')

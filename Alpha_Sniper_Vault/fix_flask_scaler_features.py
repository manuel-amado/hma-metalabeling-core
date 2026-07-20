# -*- coding: utf-8 -*-
import os

file_path = r'api\produccion_flask_server.py'
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Add scaler_features_entry and exit to storage
target_globals = '''entry_scalers = {}
exit_scalers = {}'''
replacement_globals = '''entry_scalers = {}
exit_scalers = {}
scaler_features_entry = {}
scaler_features_exit = {}'''
content = content.replace(target_globals, replacement_globals)

target_clear = '''    entry_scalers.clear()
    exit_scalers.clear()'''
replacement_clear = '''    entry_scalers.clear()
    exit_scalers.clear()
    scaler_features_entry.clear()
    scaler_features_exit.clear()'''
content = content.replace(target_clear, replacement_clear)

target_global2 = '''global entry_models, exit_models, entry_scalers, exit_scalers, thresholds_cache, regime_models, regime_scalers, toxic_regimes'''
replacement_global2 = '''global entry_models, exit_models, entry_scalers, exit_scalers, scaler_features_entry, scaler_features_exit, thresholds_cache, regime_models, regime_scalers, toxic_regimes'''
content = content.replace(target_global2, replacement_global2)

# Load headers
target_load_entry = '''        # 2. Cargar Entry Model y Scaler'''
replacement_load_entry = '''        # --- DYNAMIC SCALER FEATURES ---
        import pandas as pd
        csv_path = os.path.join(os.path.dirname(OUT_DIR), "data", f"Struct_Dataset_{activo_upper}.csv")
        if os.path.exists(csv_path):
            df_head = pd.read_csv(csv_path, nrows=0)
            scaler_features_entry[activo] = [c for c in ENTRY_FEATURES if c in df_head.columns]
        else:
            scaler_features_entry[activo] = ENTRY_FEATURES
            
        csv_exit_path = os.path.join(os.path.dirname(OUT_DIR), "data", f"Struct_Exit_Dataset_{activo_upper}.csv")
        if os.path.exists(csv_exit_path):
            df_head_exit = pd.read_csv(csv_exit_path, nrows=0)
            scaler_features_exit[activo] = [c for c in EXIT_FEATURES if c in df_head_exit.columns]
        else:
            scaler_features_exit[activo] = EXIT_FEATURES
            
        # 2. Cargar Entry Model y Scaler'''
content = content.replace(target_load_entry, replacement_load_entry)

# Prediction Entry Fix
target_predict_entry = '''        # 1. Recuperar TODAS las 30 features crudas en su orden original
        raw_row = []
        for f in ENTRY_FEATURES_30:
            if f in features_dict:
                raw_row.append(features_dict[f])
            else:
                # Si MT5 no la mando, imputamos 0
                raw_row.append(0.0)
                
        df_raw = pd.DataFrame([raw_row], columns=ENTRY_FEATURES_30)
        
        # 2. Aplicar QuantileTransformer
        if activo in entry_scalers:
            scaled_matrix = entry_scalers[activo].transform(df_raw)
            df_scaled = pd.DataFrame(scaled_matrix, columns=ENTRY_FEATURES_30)'''
replacement_predict_entry = '''        # 1. Recuperar las features del scaler dinamicamente
        s_features = scaler_features_entry.get(activo, ENTRY_FEATURES)
        raw_row = []
        for f in s_features:
            if f in features_dict:
                raw_row.append(features_dict[f])
            else:
                raw_row.append(0.0)
                
        df_raw = pd.DataFrame([raw_row], columns=s_features)
        
        # 2. Aplicar QuantileTransformer
        if activo in entry_scalers:
            scaled_matrix = entry_scalers[activo].transform(df_raw)
            df_scaled = pd.DataFrame(scaled_matrix, columns=s_features)'''
content = content.replace(target_predict_entry, replacement_predict_entry)

# Prediction Exit Fix
target_predict_exit = '''        # 1. Recuperar TODAS las 17 features crudas en su orden original
        raw_row = []
        for f in EXIT_FEATURES_17:
            if f in features_dict:
                raw_row.append(features_dict[f])
            else:
                raw_row.append(0.0)
                
        df_raw = pd.DataFrame([raw_row], columns=EXIT_FEATURES_17)
        
        # 2. Aplicar QuantileTransformer
        if activo in exit_scalers:
            scaled_matrix = exit_scalers[activo].transform(df_raw)
            df_scaled = pd.DataFrame(scaled_matrix, columns=EXIT_FEATURES_17)'''
replacement_predict_exit = '''        # 1. Recuperar las features del scaler dinamicamente
        s_features = scaler_features_exit.get(activo, EXIT_FEATURES)
        raw_row = []
        for f in s_features:
            if f in features_dict:
                raw_row.append(features_dict[f])
            else:
                raw_row.append(0.0)
                
        df_raw = pd.DataFrame([raw_row], columns=s_features)
        
        # 2. Aplicar QuantileTransformer
        if activo in exit_scalers:
            scaled_matrix = exit_scalers[activo].transform(df_raw)
            df_scaled = pd.DataFrame(scaled_matrix, columns=s_features)'''
content = content.replace(target_predict_exit, replacement_predict_exit)

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)
print('SUCCESS: Updated Flask server with Dynamic Scaler Features')

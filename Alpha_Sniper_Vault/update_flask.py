# -*- coding: utf-8 -*-
import os
import json
import joblib
import pandas as pd
from flask import Flask, request, jsonify
import sys

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
API_FILE = os.path.join(BASE_DIR, "api", "produccion_flask_server.py")

with open(API_FILE, 'r', encoding='utf-8') as f:
    content = f.read()

# Add entry_scalers and exit_scalers globally
target_globals = '''entry_models = {}
exit_models = {}'''
replacement_globals = '''entry_models = {}
exit_models = {}
entry_scalers = {}
exit_scalers = {}'''
content = content.replace(target_globals, replacement_globals)

target_clear = '''    entry_models.clear()
    exit_models.clear()'''
replacement_clear = '''    entry_models.clear()
    exit_models.clear()
    entry_scalers.clear()
    exit_scalers.clear()'''
content = content.replace(target_clear, replacement_clear)

target_global2 = '''global entry_models, exit_models, thresholds_cache, regime_models, regime_scalers, toxic_regimes'''
replacement_global2 = '''global entry_models, exit_models, entry_scalers, exit_scalers, thresholds_cache, regime_models, regime_scalers, toxic_regimes'''
content = content.replace(target_global2, replacement_global2)

# Load scalers
target_load_entry = '''        # 2. Cargar Entry Model
        entry_path = os.path.join(OUT_DIR, f"modelo_universal_{activo_upper}_entry{suffix}.pkl")'''
replacement_load_entry = '''        # 2. Cargar Entry Model y Scaler
        entry_scaler_path = os.path.join(OUT_DIR, f"scaler_universal_{activo_upper}_entry.pkl")
        if os.path.exists(entry_scaler_path):
            try:
                entry_scalers[activo] = joblib.load(entry_scaler_path)
                print(f"[INFO] Entry Scaler cargado: {activo_upper}")
            except Exception as e:
                print(f"[ERROR] Fallo al cargar Entry Scaler {activo_upper}: {e}")
                
        entry_path = os.path.join(OUT_DIR, f"modelo_universal_{activo_upper}_entry{suffix}.pkl")'''
content = content.replace(target_load_entry, replacement_load_entry)

target_load_exit = '''        # 3. Cargar Exit Model
        exit_path = os.path.join(OUT_DIR, f"modelo_universal_{activo_upper}_exit{suffix}.pkl")'''
replacement_load_exit = '''        # 3. Cargar Exit Model y Scaler
        exit_scaler_path = os.path.join(OUT_DIR, f"scaler_universal_{activo_upper}_exit.pkl")
        if os.path.exists(exit_scaler_path):
            try:
                exit_scalers[activo] = joblib.load(exit_scaler_path)
                print(f"[INFO] Exit Scaler cargado: {activo_upper}")
            except Exception as e:
                print(f"[ERROR] Fallo al cargar Exit Scaler {activo_upper}: {e}")
                
        exit_path = os.path.join(OUT_DIR, f"modelo_universal_{activo_upper}_exit{suffix}.pkl")'''
content = content.replace(target_load_exit, replacement_load_exit)

# Prediction Entry Logic
target_predict_entry = '''        row_data = {}
        for f in expected_features:
            if f in features_dict:
                row_data[f] = features_dict[f]
            else:
                return jsonify({"error": f"Falta la feature requerida: {f}"}), 400
                
        df_input = pd.DataFrame([row_data], columns=expected_features)
        
        # Predecir
        prob_ia = float(modelo.predict_proba(df_input)[0, 1])'''
replacement_predict_entry = '''        # 1. Recuperar TODAS las 30 features crudas en su orden original
        raw_row = []
        for f in ENTRY_FEATURES_30:
            if f in features_dict:
                raw_row.append(features_dict[f])
            else:
                # Si MT5 no la mandó por alguna razon, imputamos 0 (MT5 siempre deberia mandar todas)
                raw_row.append(0.0)
                
        df_raw = pd.DataFrame([raw_row], columns=ENTRY_FEATURES_30)
        
        # 2. Aplicar QuantileTransformer
        if activo in entry_scalers:
            scaled_matrix = entry_scalers[activo].transform(df_raw)
            df_scaled = pd.DataFrame(scaled_matrix, columns=ENTRY_FEATURES_30)
        else:
            df_scaled = df_raw
            
        # 3. Filtrar solo las features esperadas por el modelo (Ablation Survivors)
        for f in expected_features:
            if f not in df_scaled.columns:
                return jsonify({"error": f"Falta la feature requerida tras el escalado: {f}"}), 400
                
        df_input = df_scaled[expected_features]
        
        # Predecir
        prob_ia = float(modelo.predict_proba(df_input)[0, 1])'''
content = content.replace(target_predict_entry, replacement_predict_entry)

# Prediction Exit Logic
target_predict_exit = '''        # DataFrame con 1 fila y las features esperadas por el modelo específico
        row_data = {}
        for f in expected_features:
            if f in features_dict:
                row_data[f] = features_dict[f]
            else:
                return jsonify({"error": f"Falta la feature requerida: {f}"}), 400
                
        df_input = pd.DataFrame([row_data], columns=expected_features)
        
        # Predecir
        prob_ia = float(modelo.predict_proba(df_input)[0, 1])'''
replacement_predict_exit = '''        # 1. Recuperar TODAS las 17 features crudas en su orden original
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
            df_scaled = pd.DataFrame(scaled_matrix, columns=EXIT_FEATURES_17)
        else:
            df_scaled = df_raw
            
        # 3. Filtrar solo las features esperadas por el modelo
        for f in expected_features:
            if f not in df_scaled.columns:
                return jsonify({"error": f"Falta la feature requerida tras el escalado: {f}"}), 400
                
        df_input = df_scaled[expected_features]
        
        # Predecir
        prob_ia = float(modelo.predict_proba(df_input)[0, 1])'''
content = content.replace(target_predict_exit, replacement_predict_exit)

with open(API_FILE, 'w', encoding='utf-8') as f:
    f.write(content)
print('SUCCESS: Updated Flask server with QuantileTransformer routing')

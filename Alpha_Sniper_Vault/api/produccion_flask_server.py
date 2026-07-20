import os
import json
import joblib
import pandas as pd
from flask import Flask, request, jsonify

import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

# Fase 36.5: Las features sobrevivientes de la purga de ablación (OOF).
# El modelo XGBoost se entrenó con .values por lo que no guardó feature_names_in_
# Global list of all possible raw features
ENTRY_FEATURES_ALL = [
    "Z_Score", "ATR_Norm", "Cross_Vol_Regime", "Fract_Diff_Return",
    "Breakout_Force_ATR", "Trend_Align", "Dist_Macro_EMA", "Macro_ADX", 
    "Pullback_Dur", "Pullback_Depth_Pct", "SL_Dist_ATR", "Hour",
    "Session_Time", "H4_Trend_Align", "ATR_Ratio_High", "Energy_Accumulation",
    "Bars_Since_Asian_Sweep", "Bars_Since_Local_Sweep",
    "Dist_Asian_High_ATR", "Dist_Asian_Low_ATR", "Is_Asian_Sweep",
    "Spread_Expansion_Ratio", "Candle_Dominance", "Regime_Consistency_Count",
    "MTF_ATR_Ratio", "Trigger_Rejection_Tail", "Bollinger_Dev",
    "TWAP_Z_Score", "Breakout_Velocity", "Day_Of_Week",
    "ATR_Ratio", "Bollinger_Band_Width", "Dist_Synth_H4_EMA", "Dist_Synth_D1_EMA",
    "Ribbon_Compression_ATR", "Spectrum_Alignment", "Price_to_Macro_HMA_Dist", "Ribbon_Spread_StdDev"
]

EXIT_FEATURES_ALL = [
    "Bars_In_Trade", "Open_Profit_R", "Drawdown_From_Peak_R", "Macro_ADX_Exit",
    "Exit_Volatility_Ratio", "Spread_Impact_Exit", "Is_Trigger_Fast",
    "Is_Trigger_Slow", "Is_Trigger_RSI", "Is_Trigger_Profit",
    "Is_Trigger_Fast_HMA_Cross", "MTF_ATR_Ratio", "Trigger_Rejection_Tail",
    "Bollinger_Dev", "Peak_HMA_Stretch_ATR", "Current_HMA_Stretch_ATR",
    "Elastic_Retracement_Pct"
]

app = Flask(__name__)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
OUT_DIR = os.path.abspath(os.path.join(BASE_DIR, "..", "models"))

# In-memory storage
entry_models = {}
exit_models = {}
entry_scalers = {}
exit_scalers = {}
scaler_features_entry = {}
scaler_features_exit = {}
thresholds_cache = {}
regime_models = {}
regime_scalers = {}
toxic_regimes = {}

# FASE 39: Time-Travel WFO Storage
wfo_registries = {}
wfo_models = {}

def load_backend():
    """Carga los modelos .pkl y thresholds .json en memoria."""
    global entry_models, exit_models, entry_scalers, exit_scalers, scaler_features_entry, scaler_features_exit, thresholds_cache, regime_models, regime_scalers, toxic_regimes
    global wfo_registries, wfo_models
    
    # Limpiar estructuras antes de recargar
    entry_models.clear()
    exit_models.clear()
    entry_scalers.clear()
    exit_scalers.clear()
    scaler_features_entry.clear()
    scaler_features_exit.clear()
    thresholds_cache.clear()
    regime_models.clear()
    regime_scalers.clear()
    toxic_regimes.clear()
    wfo_registries.clear()
    wfo_models.clear()
    
    import glob
    import re
    json_files = glob.glob(os.path.join(OUT_DIR, "umbrales_universales_*.json"))
    
    # Agrupar por activo
    symbol_files = {}
    for f in json_files:
        base = os.path.basename(f)
        # Extraer activo ignorando el timestamp opcional
        m = re.match(r"umbrales_universales_([A-Za-z]+)", base)
        if m:
            sym = m.group(1).upper()
            if sym not in symbol_files:
                symbol_files[sym] = []
            symbol_files[sym].append(f)
            
    for activo_upper, files in symbol_files.items():
        # FASE 68: Lobo Solitario / Multi-Asset Unlocked
        # Ya no hay bloqueo por activo, se cargan todos los disponibles.

        activo = activo_upper.lower()
        
        # Ordenar alfabeticamente asegurara que el timestamp mas reciente quede al final
        files.sort()
        latest_config = files[-1]
        
        # Extraer el sufijo (timestamp) si existe
        base_name = os.path.basename(latest_config)
        prefix = f"umbrales_universales_{activo_upper}"
        suffix = base_name[len(prefix):-5] # quita prefijo y ".json"
        
        # 1. Cargar umbrales dinamicos
        if os.path.exists(latest_config):
            try:
                with open(latest_config, "r") as f:
                    data = json.load(f)
                    if "B_Balanceado" in data:
                        thresholds_cache[activo] = data["B_Balanceado"]
                    elif "A_Agresivo" in data:
                        thresholds_cache[activo] = data["A_Agresivo"]
                    else:
                        first_key = list(data.keys())[0]
                        thresholds_cache[activo] = data[first_key]
                print(f"[INFO] Umbrales cargados para {activo_upper} (Sufijo: '{suffix}')")
            except Exception as e:
                print(f"[ERROR] No se pudo leer {latest_config}: {e}")
        
        # --- DYNAMIC SCALER FEATURES ---
        import pandas as pd
        csv_path = os.path.join(os.path.dirname(OUT_DIR), "data", f"Struct_Dataset_{activo_upper}.csv")
        if os.path.exists(csv_path):
            df_head = pd.read_csv(csv_path, nrows=0)
            scaler_features_entry[activo] = [c for c in ENTRY_FEATURES_ALL if c in df_head.columns]
        else:
            scaler_features_entry[activo] = ENTRY_FEATURES_ALL
            
        csv_exit_path = os.path.join(os.path.dirname(OUT_DIR), "data", f"Struct_Exit_Dataset_{activo_upper}.csv")
        if os.path.exists(csv_exit_path):
            df_head_exit = pd.read_csv(csv_exit_path, nrows=0)
            scaler_features_exit[activo] = [c for c in EXIT_FEATURES_ALL if c in df_head_exit.columns]
        else:
            scaler_features_exit[activo] = EXIT_FEATURES_ALL
            
        # FASE 55.5: Desactivar carga de modelos WFO Legacy.
        # Los modelos universales de Fase 54/55 son el "Gold Master" y deben usarse 
        # en todas las inferencias y backtests mecánicos para garantizar la homogeneidad.
        wfo_registries.clear()
        wfo_models.clear()
            
        # 2. Cargar Entry Model y Scaler
        entry_scaler_path = os.path.join(OUT_DIR, f"scaler_universal_{activo_upper}_entry.pkl")
        if os.path.exists(entry_scaler_path):
            try:
                entry_scalers[activo] = joblib.load(entry_scaler_path)
                print(f"[INFO] Entry Scaler cargado: {activo_upper}")
            except Exception as e:
                print(f"[ERROR] Fallo al cargar Entry Scaler {activo_upper}: {e}")
                
        entry_path = os.path.join(OUT_DIR, f"modelo_universal_{activo_upper}_entry{suffix}.pkl")
        if os.path.exists(entry_path):
            try:
                entry_models[activo] = joblib.load(entry_path)
                print(f"[INFO] Entry Model cargado: {activo_upper}")
            except Exception as e:
                print(f"[ERROR] Fallo al cargar Entry Model {activo_upper}: {e}")
                
        # 4. Cargar Regime Engine
        scaler_path = os.path.join(OUT_DIR, f"scaler_universal_{activo_upper}_regimen{suffix}.pkl")
        kmeans_path = os.path.join(OUT_DIR, f"regimen_universal_{activo_upper}_kmeans{suffix}.pkl")
        toxic_path = os.path.join(OUT_DIR, f"toxic_universal_{activo_upper}{suffix}.json")
        
        if os.path.exists(scaler_path) and os.path.exists(kmeans_path) and os.path.exists(toxic_path):
            try:
                regime_scalers[activo] = joblib.load(scaler_path)
                regime_models[activo] = joblib.load(kmeans_path)
                with open(toxic_path, "r") as f:
                    toxic_data = json.load(f)
                    toxic_regimes[activo] = toxic_data
                print(f"[INFO] Regime Engine cargado: {activo_upper} (Toxic ID: {toxic_data['toxic_id']})")
            except Exception as e:
                print(f"[ERROR] Fallo al cargar Regime Engine {activo_upper}: {e}")

        # 5. Cargar WFO Registry y Modelos Históricos (FASE 39)
        wfo_reg_path = os.path.join(OUT_DIR, f"wfo_registry_entry_{activo_upper}.json")
        if os.path.exists(wfo_reg_path):
            try:
                with open(wfo_reg_path, "r") as f:
                    wfo_reg = json.load(f)
                    wfo_registries[activo_upper] = wfo_reg
                
                wfo_models[activo_upper] = {}
                for oos_date_str, model_name in wfo_reg.items():
                    m_path = os.path.join(OUT_DIR, model_name)
                    if os.path.exists(m_path):
                        wfo_models[activo_upper][oos_date_str] = joblib.load(m_path)
                print(f"[INFO] Time-Travel WFO cargado para {activo_upper}: {len(wfo_models[activo_upper])} modelos históricos.")
            except Exception as e:
                print(f"[ERROR] Fallo al cargar WFO Registry {activo_upper}: {e}")

        # 3. Cargar Exit Model y Scaler
        exit_scaler_path = os.path.join(OUT_DIR, f"scaler_universal_{activo_upper}_exit.pkl")
        if os.path.exists(exit_scaler_path):
            try:
                exit_scalers[activo] = joblib.load(exit_scaler_path)
                print(f"[INFO] Exit Scaler cargado: {activo_upper}")
            except Exception as e:
                print(f"[ERROR] Fallo al cargar Exit Scaler {activo_upper}: {e}")
                
        exit_path = os.path.join(OUT_DIR, f"modelo_universal_{activo_upper}_exit{suffix}.pkl")
        if os.path.exists(exit_path):
            try:
                exit_models[activo] = joblib.load(exit_path)
                print(f"[INFO] Exit Model cargado: {activo_upper}")
            except Exception as e:
                print(f"[ERROR] Fallo al cargar Exit Model {activo_upper}: {e}")

@app.route('/reload', methods=['POST'])
def reload_models():
    """Endpoint para recargar los modelos y config sin reiniciar el servidor."""
    load_backend()
    return jsonify({
        "status": "success", 
        "message": "Modelos y configuracion recargados en memoria.",
        "activos_entry": list(entry_models.keys()),
        "activos_exit": list(exit_models.keys())
    })

@app.route('/predict_entry', methods=['POST'])
def predict_entry():
    """Endpoint para predecir si tomar el trade (Entry)."""
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No JSON payload provided."}), 400
        
        if "features" in data:
            activo = data.get("activo", "usdjpy").lower()
            features_dict = data["features"]
        else:
            activo = data.pop("activo", "usdjpy").lower()
            features_dict = data
            
        req_time_str = features_dict.pop("Time", None)
            
        if activo not in entry_models:
            return jsonify({"error": f"Entry Model para {activo.upper()} no esta cargado."}), 404
            
        modelo = entry_models[activo]
        
        # --- FASE 39: Time-Travel WFO Routing ---
        is_wfo_routed = False
        if req_time_str:
            try:
                # req_time_str format: "YYYY.MM.DD HH:MI"
                req_date = pd.to_datetime(req_time_str.replace(".", "-")).date()
                
                # Encontrar el modelo correspondiente:
                # El registry mapea oos_end -> model
                # Buscamos el primer oos_end que sea estrictamente mayor a la fecha solicitada
                # (lo que significa que la fecha solicitada cae DENTRO del periodo OOS de ese modelo)
                activo_upper = activo.upper()
                if activo_upper in wfo_registries:
                    sorted_dates = sorted([pd.to_datetime(d).date() for d in wfo_registries[activo_upper].keys()])
                    selected_oos_date = None
                    for d in sorted_dates:
                        if req_date <= d:
                            selected_oos_date = d
                            break
                    
                    if selected_oos_date:
                        date_str = str(selected_oos_date)
                        if date_str in wfo_models[activo_upper]:
                            modelo = wfo_models[activo_upper][date_str]
                            is_wfo_routed = True
                            print(f"[WFO ROUTING] Request de {req_date} routeado a WFO OOS: {date_str}")
            except Exception as e:
                print(f"[ERROR] Fallo en Time-Travel WFO routing: {e}")
                
        if not is_wfo_routed and req_time_str:
            # Si envió Time pero cayó fuera de los periodos OOS (muy en el futuro)
            print(f"[LIVE ROUTING] Request de {req_time_str} routeado a modelo Live (Últimos 24m).")
        # ----------------------------------------
        
        # Ejecutar Filtro de Régimen (K-Means) si está disponible
        if activo in regime_models and activo in regime_scalers and activo in toxic_regimes:
            try:
                toxic_data = toxic_regimes[activo]
                toxic_id = toxic_data["toxic_id"]
                regime_feats = toxic_data["features"]
                
                row_regime = []
                missing_regime = False
                for rf in regime_feats:
                    if rf in features_dict:
                        row_regime.append(features_dict[rf])
                    else:
                        missing_regime = True
                        break
                        
                if not missing_regime:
                    # Crear DataFrame con nombres de features para que el scaler no de warnings
                    df_reg = pd.DataFrame([row_regime], columns=regime_feats).fillna(0)
                    X_scaled = regime_scalers[activo].transform(df_reg)
                    cluster_pred = regime_models[activo].predict(X_scaled)[0]
                    
                    if cluster_pred == toxic_id:
                        print(f"[PREDICT ENTRY] {activo.upper()} - Régimen Tóxico Detectado (Cluster {toxic_id}) - IGNORADO (XGBoost maneja purga).")
                        # return jsonify({"probability": 0.0, "regime": "Toxic", "cluster_id": int(cluster_pred)})
            except Exception as e:
                print(f"[WARNING] Fallo al evaluar Régimen: {e}. Procediendo a XGBoost.")
        # ----------------------------------------

        # --- SELECCION DINAMICA DE FEATURES ---
        # WFO Models esperaran 30, Live Models pueden esperar 9 o 5 (segun el activo y la fase)
        n_feat = getattr(modelo, "n_features_in_", 0)
        
        ENTRY_FEATURES_30 = [
            "Z_Score", "ATR_Norm", "Cross_Vol_Regime", "Fract_Diff_Return",
            "Breakout_Force_ATR", "Trend_Align", "Dist_Macro_EMA", "Macro_ADX", 
            "Pullback_Dur", "Pullback_Depth_Pct", "SL_Dist_ATR", "Hour",
            "Session_Time", "H4_Trend_Align", "ATR_Ratio_High", "Energy_Accumulation",
            "Bars_Since_Asian_Sweep", "Bars_Since_Local_Sweep",
            "Dist_Asian_High_ATR", "Dist_Asian_Low_ATR", "Is_Asian_Sweep",
            "Spread_Expansion_Ratio", "Candle_Dominance", "Regime_Consistency_Count",
            "MTF_ATR_Ratio", "Trigger_Rejection_Tail", "Bollinger_Dev",
            "TWAP_Z_Score", "Breakout_Velocity", "Day_Of_Week"
        ]
        ENTRY_FEATURES_9 = [
            "ATR_Norm", "Macro_ADX", "SL_Dist_ATR", "Bars_Since_Asian_Sweep",
            "Bars_Since_Local_Sweep", "Dist_Asian_High_ATR", "Dist_Asian_Low_ATR",
            "TWAP_Z_Score", "Breakout_Velocity"
        ]
        ENTRY_FEATURES_5 = [
            "Breakout_Force_ATR", "SL_Dist_ATR", "Bars_Since_Local_Sweep", 
            "Candle_Dominance", "MTF_ATR_Ratio"
        ]
        
        if hasattr(modelo, "expected_features_"):
            expected_features = list(modelo.expected_features_)
        elif hasattr(modelo, "feature_names_in_"):
            expected_features = list(modelo.feature_names_in_)
        elif n_feat == 30:
            expected_features = ENTRY_FEATURES_30
        elif n_feat == 5:
            expected_features = ENTRY_FEATURES_5
        else:
            expected_features = ENTRY_FEATURES_9
            
        # 1. Recuperar las features del scaler dinamicamente
        s_features = scaler_features_entry.get(activo, ENTRY_FEATURES_ALL)
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
            df_scaled = pd.DataFrame(scaled_matrix, columns=s_features)
        else:
            df_scaled = df_raw
            
        # 3. Filtrar solo las features esperadas por el modelo (Ablation Survivors)
        for f in expected_features:
            if f not in df_scaled.columns:
                return jsonify({"error": f"Falta la feature requerida tras el escalado: {f}"}), 400
                
        df_input = df_scaled[expected_features]
        
        # Predecir
        prob_ia = float(modelo.predict_proba(df_input)[0, 1])
        # FASE 64: Devolver probabilidad cruda, el EA gestiona los umbrales (Sniper Mode)
        print(f"[PREDICT ENTRY] {activo.upper()} - Proba Cruda: {prob_ia:.4f}")
        # --- PROTOCOLO ALPHA FASE 29: AUDITORIA PYTHON ---
        try:
            from datetime import datetime
            audit_path = os.path.join(BASE_DIR, "python_received_audit.txt")
            with open(audit_path, "a") as f:
                f.write(f"{datetime.now()};{activo.upper()};JSON_IN:{json.dumps(features_dict)};PROBA_OUT:{prob_ia}\n")
        except Exception as e:
            print(f"Error escribiendo audit de Python: {e}")
        # -------------------------------------------------
        
        # Devolver prob cruda si supera el threshold, o 0.0 si es descartada
        return jsonify({"probability": prob_ia})

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/predict_exit', methods=['POST'])
def predict_exit():
    """Endpoint para predecir si salir del trade prematuramente (Exit)."""
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No JSON payload provided."}), 400
        
        if "features" in data:
            activo = data.get("activo", "usdjpy").lower()
            features_dict = data["features"]
        else:
            activo = data.pop("activo", "usdjpy").lower()
            features_dict = data
            
        req_time_str = features_dict.pop("Time", None)
            
        if activo not in exit_models:
            return jsonify({"error": f"Exit Model para {activo.upper()} no esta cargado."}), 404
            
        modelo = exit_models[activo]
        # (El Filtro de Régimen K-Means es exclusivo de Entry, aquí solo evaluamos la táctica de salida)
        
        # --- SELECCION DINAMICA DE FEATURES DE SALIDA ---
        n_feat = getattr(modelo, "n_features_in_", 0)
        
        EXIT_FEATURES_17 = [
            "Bars_In_Trade", "Open_Profit_R", "Drawdown_From_Peak_R", "Macro_ADX_Exit",
            "Exit_Volatility_Ratio", "Spread_Impact_Exit", "Is_Trigger_Fast",
            "Is_Trigger_Slow", "Is_Trigger_RSI", "Is_Trigger_Profit",
            "Is_Trigger_Fast_HMA_Cross", "MTF_ATR_Ratio", "Trigger_Rejection_Tail",
            "Bollinger_Dev", "Peak_HMA_Stretch_ATR", "Current_HMA_Stretch_ATR",
            "Elastic_Retracement_Pct"
        ]
        EXIT_FEATURES_2 = [
            "Open_Profit_R", "Spread_Impact_Exit"
        ]
        
        if hasattr(modelo, "expected_features_"):
            expected_features = list(modelo.expected_features_)
        elif hasattr(modelo, "feature_names_in_"):
            expected_features = list(modelo.feature_names_in_)
        elif n_feat == 17:
            expected_features = EXIT_FEATURES_17
        else:
            expected_features = EXIT_FEATURES_2

        # DataFrame con 1 fila y las features esperadas por el modelo específico
        # 1. Recuperar las features del scaler dinamicamente
        s_features = scaler_features_exit.get(activo, EXIT_FEATURES_ALL)
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
            df_scaled = pd.DataFrame(scaled_matrix, columns=s_features)
        else:
            df_scaled = df_raw
            
        # 3. Filtrar solo las features esperadas por el modelo
        for f in expected_features:
            if f not in df_scaled.columns:
                return jsonify({"error": f"Falta la feature requerida tras el escalado: {f}"}), 400
                
        df_input = df_scaled[expected_features]
        
        # Predecir
        prob_ia = float(modelo.predict_proba(df_input)[0, 1])
        # FASE 64: Devolver probabilidad cruda, el EA gestiona los umbrales (Fat Tails Mode)
        print(f"[PREDICT EXIT] {activo.upper()} - Proba Cruda: {prob_ia:.4f}")
        
        # FASE 64: Devolver la probabilidad cruda directamente
        return jsonify({"probability": prob_ia})

    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    print("=" * 80)
    print("  INICIANDO SERVIDOR FLASK DE PRODUCCION (DUAL MODEL) - FASE 10.8")
    print("=" * 80)
    
    load_backend()
    
    print("-" * 80)
    print("  Escuchando peticiones en: http://0.0.0.0:8000")
    print("  Endpoints disponibles:")
    print("   - POST /predict_entry : Recibe {'activo': '...', 'features': {...}}")
    print("   - POST /predict_exit  : Recibe {'activo': '...', 'features': {...}}")
    print("   - POST /reload        : Recarga modelos .pkl")
    print("-" * 80)
    
    # Run the Flask app
    app.run(host='0.0.0.0', port=8000)

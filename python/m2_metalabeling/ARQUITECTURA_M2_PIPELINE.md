# M2 Meta-Labeling — Data Pipeline Architecture
# WS-Mavericks | StrategyQuant + XGBoost + MetaTrader 5

---

## 🏛️ Árbol de Directorios (M2 Model Factory)

```text
python/
├── m2_metalabeling/                 # EL CORAZÓN DEL PIPELINE
│   ├── ingestion/
│   │   └── mt5_reader.py            # Lee CSV Multi-Asset de MT5 → DataFrame UTC
│   ├── features/
│   │   └── feature_engineering.py   # Variables: HMA kinematics, ATR, RSI...
│   ├── labeling/
│   │   └── triple_barrier.py        # Etiquetado Triple Barrera (PT, SL, Timeout)
│   ├── cross_validation/
│   │   └── purged_cv.py             # Purged K-Fold & Walk-Forward Montecarlo (WFM)
│   ├── models/                      # MODEL FACTORY
│   │   ├── train_xgboost.py         # Entrenamiento con Purged CV
│   │   ├── retrain_longs.py         # Modelos de sesgo asimétrico (Longs-Only)
│   │   ├── rolling_window_retrain.py# Validación continua simulando paso a producción
│   │   ├── audit_report.py          # Auditoría estricta contra Fuga de Datos (Data Leakage)
│   │   └── export_factory_oracle.py # Orquestación de exportación
│   ├── calibration/
│   │   └── probability_calibration.py # Isotonic Regression
│   └── export/
│       └── export_mql5.py           # .pkl → M2_XGBoost_Oracle_XAUUSD.mqh (vía m2cgen)
```

---

## 🔄 Flujo de Datos (Data Pipeline V3)

### Paso 1 — Multi-Asset Ingestion (`Pipeline_Extractor_M1.mq5`)
El extractor primario ya no es un bot rígido, sino un `Pipeline_Extractor_M1` dinámico operando en MT5 en modo ciego. Extrae las características del activo (XAUUSD, EURUSD, etc.) y genera el CSV base.

### Paso 2 — Labeling & Feature Engineering
Se unifican los datos crudos con la Cinemática HMA y el Triple Barrera.
- **Data Leakage Proofing:** Módulo `audit_report.py` escanea la matriz de correlación temporal. Si una feature tiene un desplazamiento futuro accidental (ej. un `shift(-1)`), el pipeline se aborta.

### Paso 3 — Purged Walk-Forward Montecarlo (WFM)
Se sustituye el K-Fold estático por **Rolling Windows**.
En lugar de entrenar el modelo en 2015-2022 y testear en 2023-2026, el oráculo se entrena en ventanas móviles (ej. entrena 2 años, opera 6 meses, re-entrena 2 años, opera 6 meses). Se aplica **Purging** y **Embargo** en cada límite de ventana.
Esto proporciona un **Equity Curve WFM** mucho más realista al entorno de producción institucional.

### Paso 4 — Asymmetric Retraining & Regime Injection
El mercado de oro (XAUUSD) probó tener una asimetría extrema (los largos se comportan diferente a los cortos).
El script `retrain_longs.py` genera modelos especializados por dirección.
Además, el `ADX Regime Filter` (ADX > 14 en H4) se inyecta directamente como un multiplicador lógico dentro del árbol de decisión del oráculo antes de ser exportado.

### Paso 5 — C++ Transpilation & Production Vaults
Mediante `m2cgen`, el oráculo XGBoost se convierte en arrays de C++ (`M2_XGBoost_Oracle_XAUUSD.mqh`).
Este archivo se compila dentro de `Strategy_XAUUSD_Production.mq5` (Production Vault) en MT5. Al ser código nativo, las reglas de Machine Learning se ejecutan en 0 milisegundos sin latencia de red ni puentes Python.

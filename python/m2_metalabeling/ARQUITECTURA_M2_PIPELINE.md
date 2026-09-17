# M2 Meta-Labeling — Data Pipeline Architecture
# WS-Mavericks | StrategyQuant + XGBoost + MetaTrader 5

---

## Árbol de Directorios

```
python/
├── requirements.txt
├── config/
│   └── pipeline_config.yaml         # Hyperparámetros, thresholds, rutas
│
├── data/
│   ├── raw/                         # CSVs exportados por HMA_Extractor_*.mq5
│   │   ├── breakout/                # Para familia HMA_BRK_*
│   │   ├── trend/                   # Para familia HMA_TF_*
│   │   └── sqx/                     # Para familia HMA_SQX_*
│   └── processed/
│       ├── features/                # X_train.parquet, X_test.parquet
│       ├── labels/                  # y_train.parquet (Triple Barrier output)
│       └── calibration/             # Held-out set para calibración de probabilidades
│
├── m2_metalabeling/                 # EL CORAZÓN DEL PIPELINE
│   ├── ingestion/
│   │   └── mt5_reader.py            # Lee CSV de MT5 → DataFrame limpio e indexado UTC
│   ├── features/
│   │   └── feature_engineering.py  # Genera variables: HMA kinematics, ATR, RSI...
│   ├── labeling/
│   │   └── triple_barrier.py        # Etiquetado Triple Barrera (PT, SL, Timeout)
│   ├── cross_validation/
│   │   └── purged_cv.py             # Purged K-Fold + Embargo (anti-Data Leakage)
│   ├── models/
│   │   └── train_xgboost.py         # Entrenamiento con Purged CV → .pkl
│   ├── calibration/
│   │   └── probability_calibration.py # Isotonic Regression + Reliability Diagram
│   ├── evaluation/
│   │   └── metrics.py               # AUC, Precision@Recall, PSR, Brier Score
│   └── export/
│       ├── to_onnx.py               # .pkl → .onnx (para HMA_TF_v6_ONNX)
│       └── to_mqh.py                # .pkl → XGBoost_Model_*.mqh (para HMA_BRK_*)
│
├── models/                          # Artefactos entrenados (ignorados en git si >50MB)
│   ├── breakout/
│   ├── trend/
│   └── sqx/
│
├── reports/
│   ├── figures/                     # Reliability diagrams, curvas ROC, Feature Importance
│   └── metrics/                     # CSVs de métricas OOS por fold
│
└── tests/                           # Pytest: unit tests de cada módulo
```

---

## Flujo de Datos (Data Pipeline Completo)

### Paso 1 — Ingestion (`mt5_reader.py`)
El `HMA_Extractor_Orchestrator.mq5` opera en MT5 en modo ciego (sin abrir posiciones) y exporta en cada barra un CSV con columnas:
```
timestamp, open, high, low, close, volume, hma, hma_slope, hma_accel, hma_jerk, atr, rsi, ema200
```
→ `mt5_reader.py` consume ese CSV, normaliza el índice a UTC, elimina duplicados y devuelve un DataFrame limpio.

### Paso 2 — Feature Engineering (`feature_engineering.py`)
Calcula las variables predictorias del modelo:
- **Cinemática HMA:** `slope / atr`, `accel / atr`, `jerk / atr` (normalizadas por volatilidad)
- **Distancia al EMA200:** `(close - ema200) / atr`
- **Régimen de mercado:** `hma_slope > 0` (tendencia alcista)
- **Features Temporales:** hora del día, día de semana (sin mirar el futuro)

### Paso 3 — Labeling Triple Barrera (`triple_barrier.py`)
Para cada señal primaria del bot (cruce de HMA), asignamos la etiqueta:
- `+1` si el precio alcanza el PT antes del SL y del timeout
- `-1` si toca el SL primero
- `0` si expira el tiempo sin tocar ninguna barrera

El **Meta-Label** (`bin`) = `1` si el trade fue rentable, `0` si no. **Esto es lo que XGBoost aprende a predecir.**

### Paso 4 — Purged K-Fold CV (`purged_cv.py`)
**El paso más crítico.** Antes de evaluar el modelo:
1. **Purging:** Elimina del TRAIN cualquier muestra cuyo período de etiqueta (t0→t1) se solape con el TEST set.
2. **Embargo:** Elimina además un buffer de barras adicionales después del TEST para aislar la correlación serial.
Sin esto, el AUC reportado es una mentira.

### Paso 5 — Entrenamiento XGBoost (`train_xgboost.py`)
Entrena con los splits purged, reporta AUC por fold, y ajusta el modelo final con todos los datos. Guarda `.pkl` en `models/`.

### Paso 6 — Calibración de Probabilidades (`probability_calibration.py`)
El `.pkl` crudo de XGBoost produce scores, no probabilidades. Usando un **Calibration Set** (holdout del 15% nunca visto) aplicamos **Isotonic Regression**:
- Antes: XGBoost dice `p=0.7` pero el 70% de los trades no ganan.
- Después: `p=0.7` significa realmente que gana el 70%.
Generamos el **Reliability Diagram** para verificar visualmente.

### Paso 7 — Export a MT5 (`to_mqh.py` / `to_onnx.py`)
- Para **HMA_BRK_*:** el modelo se serializa como arrays hardcoded en C++ (`.mqh`) → compilación nativa en MetaEditor sin dependencias.
- Para **HMA_TF_v6_ONNX:** el modelo se convierte a formato ONNX → cargado en tiempo real con `OnnxCreate()` en MQL5.

---

## Reglas de Data Leakage (Estrictas)

> [!CAUTION]
> **NUNCA** incluyas datos futuros en las features de una barra pasada.
> Toda operación (ATR, RSI, EMA) debe calcularse usando únicamente barras `<= t0`.

| ✅ Correcto | ❌ Incorrecto (Filtración) |
|---|---|
| `atr = ATR(close[:t0], 14)` | `atr = ATR(close, 14)` con datos del futuro |
| `label_t0` usando `close[t0+1:]` | `label_t0` usando `close` incluyendo `t0` |
| Calibration set completamente separado | Calibrar con datos usados en entrenamiento |

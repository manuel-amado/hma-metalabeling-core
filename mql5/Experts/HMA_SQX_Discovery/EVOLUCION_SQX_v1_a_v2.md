# Avances y Evolución de Minería SQX (v1 a v2 + M2 Meta-Labeling)

Este documento detalla el salto cualitativo e institucional logrado en el laboratorio **SQX Discovery**, validando las hipótesis de investigación multitemporal, la corrección de zona horaria y la integración del oráculo **XGBoost Meta-Labeling (M2)**.

---

## 1. Problemas Identificados en v1 (`HMA_SQX_Ribbon_v1`)

En la primera versión minada en SQX:
- **Desfase Horario (GMT Offset):** La minería original fue ejecutada en datos GMT+0. Al ejecutarse en brokers de MetaTrader 5 (que operan en GMT+2/EET), los cierres de vela de H1 no coincidían, provocando discrepancias severas en las señales de entrada.
- **Falta de Filtro de Régimen Macro:** La estrategia operaba en cualquier condición de mercado, acumulando más de 3,400 operaciones en 10 años. Esto generaba un rozamiento excesivo con el spread y la comisión del broker, erosionando la esperanza matemática (Profit Factor ~ 1.01).

---

## 2. Los Avances Logrados en v2 (`HMA_SQX_v2_MTF_ADX`)

Para la generación de la versión v2 (`Strategy 2.91.69` en SQX), aplicamos los siguientes avances técnicos:

### A. Alineación de Zona Horaria (UTC+2)
Se configuró el motor de minería de StrategyQuant X utilizando un feed de ticks ajustado a **UTC+2 (EET)** desde 2015 hasta 2026. Las señales de apertura de vela en SQX ahora coinciden al 100% con los servidores de MT5.

### B. Validación de la Hipótesis Multitemporal (MTF)
En lugar de forzar un filtro rígido a mano, permitimos a SQX evaluar la interacción entre múltiples marcos temporales (**H1, H4 y D1**):
1. **Trigger Base (H1):** Alineación de la cinta HMA (*HMA Ribbon*: periodos 10, 21, 50 y 100).
2. **Filtro de Régimen Macro (H4):** Integración del indicador **ADX en H4 (periodo 14)** para filtrar mercados laterales y en rango antes de permitir entradas.
3. **Pivotes V-Shape (HMA V-Pivot):** Inclusión de filtros de cambio de pendiente HMA (*HMANexus_VPivot*) en periodos 11 y 110 para confirmar giros de tendencia en marcos superiores.
4. **Salidas Multinivel ATR (H1 y D1):** Take Profit y Stop Loss basados en múltiplos de ATR combinados entre la volatilidad de H1 y la macrovolatilidad de D1.

---

## 3. Hito Alcanzado: Oráculo XGBoost M2 Transpilado a MQL5 (`M2_XGBoost_Oracle.mqh`)

Hemos completado con éxito la fase de **Meta-Labeling (M2)** sobre las señales generadas por SQX:

### A. Extracción de Features Multitemporales
Se construyó el dataset `XGBoost_Dataset_Final.csv` capturando 7 sensores cinemáticos y macroestructurales:
- `Keltner_Bandwidth_H4`
- `ATR_Ratio_H1_D1`
- `ADX_Value_H4`
- `ADX_Slope_H4`
- `Dist_EMA200_H4`
- `Bollinger_Width_H1`
- `Daily_Exhaustion`

### B. Entrenamiento & Optimización Out-Of-Sample (OOS)
- **División Cronológica:** Split 70% In-Sample / 30% Out-Of-Sample (sin fuga de datos / Data Leakage).
- **Modelo:** `XGBClassifier` (100 estimadores, profundidad 3, learning rate 0.05).
- **Calibración de Umbral:** Optimización de Esperanza Matemática (EV). El umbral óptimo de probabilidad de victoria se fijó en `0.36`.

### C. Transpilación Nativa a C++ (`m2cgen`)
Mediante el script `python/m2_metalabeling/export/export_mql5.py`, el modelo de XGBoost se convirtió directamente a código C++ nativo dentro del encabezado:
📁 `mql5/Include/M2_XGBoost_Oracle.mqh`

Función de inferencia nativa:
```cpp
void GetXGBoostProbability(const double &input[], double &output[])
```
**Ventaja:** Latencia 0ms, cero dependencias de DLLs o Python externo durante la ejecución en tiempo real o backtesting en MT5.

---

## 4. Matriz Comparativa de Avances

| Métrica / Característica | v1 (`HMA_SQX_Ribbon_v1`) | v2 (`HMA_SQX_v2_MTF_ADX`) | v2 + Oráculo M2 (`M2_XGBoost_Oracle`) |
| :--- | :--- | :--- | :--- |
| **Zona Horaria** | UTC+0 | **UTC+2 (MT5 EET)** | **UTC+2 (MT5 EET)** |
| **Marcos Temporales** | Monotemporal (H1) | **Multitemporal (H1/H4/D1)** | **Multitemporal (H1/H4/D1)** |
| **Filtro Primario** | Ninguno | **ADX H4 (14) + HMA V-Pivot** | **ADX H4 (14) + HMA V-Pivot** |
| **Filtro Secundario (ML)** | Inexistente | Inexistente | **XGBoost M2 (7 Features MTF)** |
| **Inferencia MT5** | Manual | Manual | **Nativa en C++ (0ms vía `.mqh`)** |
| **Umbral Óptimo** | N/A | N/A | **0.36 (Máxima Esperanza EV)** |

---

## 5. Scripts de Automatización M2 Creados
- `python/m2_metalabeling/models/xgboost_train.py`: Entrenamiento cronológico y evaluación OOS.
- `python/m2_metalabeling/models/xgboost_optimize.py`: Optimización del umbral de decisión por Esperanza Matemática.
- `python/m2_metalabeling/export/export_mql5.py`: Transpilador automatizado de modelos XGBoost a C++ (`.mqh`).

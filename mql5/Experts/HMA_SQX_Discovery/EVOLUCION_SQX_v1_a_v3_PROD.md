# Evolución de Minería SQX y Despliegue en Producción (v1 a v3 PROD)

Este documento detalla el salto cualitativo e institucional logrado en el laboratorio **SQX Discovery**, validando las hipótesis de investigación multitemporal, la corrección de zona horaria, la integración del oráculo **XGBoost Meta-Labeling (M2)** y el despliegue del **Production Vault** (v3).

---

## 1. Problemas Identificados en v1 (`HMA_SQX_Ribbon_v1`)
- **Desfase Horario (GMT Offset):** Ejecutado en GMT+0. Al usar brokers MT5 (GMT+2/EET), los cierres H1 no coincidían (fricción de señales).
- **Falta de Filtro de Régimen Macro:** Acumulaba +3,400 trades, generando un rozamiento excesivo de spreads (Profit Factor ~ 1.01).

---

## 2. Los Avances Logrados en v2 (`HMA_SQX_v2_MTF_ADX`)
- **Alineación UTC+2:** Ticks ajustados a EET para 100% de correlación con MT5.
- **Validación Multitemporal (MTF):** H1 (Trigger HMA Ribbon) + H4 (Filtro ADX) + D1 (Volatilidad ATR Multinivel).
- **Oráculo XGBoost (M2):** Primer despliegue de `M2_XGBoost_Oracle.mqh`. Se transpilaron los árboles a C++ usando `m2cgen` alcanzando latencia 0ms.

---

## 3. Arquitectura Institucional de Producción (v3 PROD)

La evolución desde un experimento SQX hasta un activo de producción grado institucional culminó con la arquitectura `Strategy_XAUUSD_Production.mq5`.

### A. Segmentación Asimétrica (Longs-Only XGBoost)
El análisis estadístico demostró que el XAUUSD exhibía regímenes asimétricos. El modelo v3 separó los oráculos, re-entrenando un clasificador XGBoost exclusivo para operaciones en largo (`retrain_longs.py`), maximizando la Esperanza Matemática (EV).

### B. Inyección de Régimen Integrada en el Oráculo
En lugar de depender de sentencias `if(ADX > 14)` frágiles en el código MQL5, el filtro de régimen se vectorizó y se inyectó lógicamente dentro de la salida predictiva del Oráculo XGBoost. El modelo transpila en C++ no solo el árbol de decisión, sino también los umbrales macroeconómicos.

### C. Walk-Forward Montecarlo (WFM)
La validación se hizo inquebrantable mediante ventanas rodantes (Rolling Windows) con **Purged CV**. El modelo simula estar en producción real re-entrenándose periódicamente en el tiempo, asegurando un OOS (Out-Of-Sample) verdaderamente representativo.

### D. Production Vaults & Multi-Asset Extractor
El código de descubrimiento se desacopló en dos artefactos profesionales:
1. **`Pipeline_Extractor_M1.mq5`:** Opera en modo ciego, recolecta cinemática multitemporal (H1, H4, D1) de cualquier activo (EURUSD, XAUUSD, etc.) y genera la ingesta para Python.
2. **`Strategy_XAUUSD_Production.mq5`:** El "Vault" final. Un motor EMS (Execution Management System) puro que recibe la probabilidad del `M2_XGBoost_Oracle_XAUUSD.mqh`, aplica los controles de gestión de riesgo institucionales y dispara las órdenes a mercado sin latencia.

---

## 4. Matriz Comparativa de Madurez

| Métrica / Característica | v1 (Minería Base) | v2 (MTF + Oráculo M1) | v3 (`Production Vault XAUUSD`) |
| :--- | :--- | :--- | :--- |
| **Marcos Temporales** | H1 | H1/H4/D1 | **H1/H4/D1** |
| **Régimen Macro** | Ninguno | ADX H4 + HMA V-Pivot | **ADX Inyectado en Oráculo XGBoost** |
| **Validación OOS** | N/A | K-Fold (Split estático) | **Purged Walk-Forward Montecarlo** |
| **Asimetría de Sesgo** | N/A | Bidireccional unificado | **Modelos Especializados (Longs-Only)** |
| **Extracción de Datos** | Manual | Manual | **`Pipeline_Extractor_M1` (Dinámico)** |
| **Inferencia MT5** | Manual | Nativa en C++ (`.mqh`) | **Nativa en C++ (Safety/Sanity Checks)** |


---
## 🔗 Conexiones Transversales
- [[Teoria - XGBoost y GT-Score|XGBoost y GT-Score]]
- [[Teoria - Anclaje VWAP|Anclaje VWAP]]
- [[Sistema - ZeroMQ y HFT|ZeroMQ y HFT]]
- [[Sistema - MQL5 Execution Engine|MQL5 Execution Engine]]
- [[Sistema - Adaptacion SQX a MT5 FTMO|Adaptacion SQX a MT5 FTMO]]
- [[Sistema - Corrupcion de Datos y Huecos M1|Corrupcion de Datos y Huecos M1]]

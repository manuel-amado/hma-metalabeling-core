# Proyecto SQX Discovery (StrategyQuant X)

## Objetivo Principal
Este directorio nace con el objetivo de aislar y documentar las estrategias puras de "fuerza bruta" y minería algorítmica generadas mediante **StrategyQuant X (SQX)**. 

La meta es utilizar SQX como un motor de descubrimiento de *Alpha* automatizado, buscando ineficiencias de mercado y patrones base (Edges) que luego puedan ser refinados o meta-etiquetados con nuestros ecosistemas de Machine Learning (XGBoost / ONNX).

## Primera Estrategia Descubierta: HMA Ribbon (v1)
* **Archivo Original:** \Strategy 5.6.45.mq5\ (SQX Build 141)
* **Activo/Temporalidad:** \XAUUSD_TICK / H1\ (Test de 2018 a 2025)
* **Lógica Base Observada:** 
  La estrategia se fundamenta fuertemente en un concepto de alineación de HMA (Hull Moving Average), evaluando \CheckHMARibbonAlign()\ en múltiples periodos simultáneos (ej. periodos 3, 4, 6), además de incorporar Heiken Ashi y trailing stops basados en volatilidad (ATR de varios periodos: 30, 200, 270).

## Siguientes Pasos
1. **Validación:** Comprobar la robustez del modelo en In-Sample (IS) y Out-Of-Sample (OOS) en MT5.
2. **Hibridación:** Si el edge matemático es sólido, el siguiente paso lógico será extraer la lógica principal y modularla dentro de nuestra familia \HMA_BRK\ o \HMA_TF\ para inyectarle las capacidades de filtrado con Python (Meta-Labeling).


---
## 🔗 Conexiones Transversales
- [[Teoria - XGBoost y GT-Score|XGBoost y GT-Score]]
- [[Sistema - MQL5 Execution Engine|MQL5 Execution Engine]]
- [[Sistema - Adaptacion SQX a MT5 FTMO|Adaptacion SQX a MT5 FTMO]]

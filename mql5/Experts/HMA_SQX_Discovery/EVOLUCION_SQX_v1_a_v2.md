# Avances y Evolución de Minería SQX (v1 a v2)

Este documento detalla el salto cualitativo e institucional logrado en el laboratorio **SQX Discovery**, validando las hipótesis de investigación multitemporal y corrección de zona horaria.

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

## 3. Matriz Comparativa de Avances

| Métrica / Característica | v1 (`HMA_SQX_Ribbon_v1`) | v2 (`HMA_SQX_v2_MTF_ADX`) |
| :--- | :--- | :--- |
| **Zona Horaria de Minería** | UTC+0 (Descorrelacionado de MT5) | **UTC+2 (Alineado con MT5 EET)** |
| **Marcos Temporales** | Monotemporal (H1) | **Multitemporal (H1 + H4 + D1)** |
| **Filtro de Régimen** | Ninguno (Entradas continuas) | **ADX H4 (14) + HMA V-Pivot (11, 110)** |
| **Gestión de Salidas** | ATR Estático | **ATR Multinivel (H1/D1) + Trailing** |
| **Control de Fricción** | Alto número de trades afectables por spread | **Filtrado estricto de ruido de mercado** |

---

## 4. Siguientes Pasos (Integración con M2 Meta-Labeling)

Con la v2 de SQX habiendo demostrado la eficacia del filtrado multitemporal ADX H4 + HMA V-Pivot:
1. **Extracción de Dataset:** Ejecutaremos el orquestador `HMA_Extractor_Orchestrator.mq5` sobre el flujo de señales de esta v2.
2. **Etiquetado M2:** Ingestaremos los datos en el pipeline Python de **Meta-Labeling (M2)** usando el método de la Triple Barrera y la validación *Purged K-Fold CV*.
3. **Calibración e Inferencia:** Calibraremos las probabilidades con *Isotonic Regression* para generar la versión `.onnx` final lista para fondeo.

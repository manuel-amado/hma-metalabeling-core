# 🏛️ M2 Quant Pipeline: Meta-Labeling Framework

![Status](https://img.shields.io/badge/Status-Production_Ready-brightgreen)
![Architecture](https://img.shields.io/badge/Architecture-Python%20%7C%20C%2B%2B%20%7C%20MQL5-blue)
![Validation](https://img.shields.io/badge/Validation-Purged_WFM-orange)
![Execution](https://img.shields.io/badge/Latency-0ms_Native-success)

> **Veredicto Científico:** Este repositorio fue creado para probar el *Edge* de la estrategia Hull Moving Average (HMA). Las rigurosas pruebas de este pipeline demostraron que **las Medias Móviles sufren de *Alpha Decay* irreversible y no funcionan como gatillos de entrada en Forex**. Se documenta el fracaso de la HMA para evitar pérdidas de capital.

Aunque la estrategia HMA murió, **la infraestructura construida aquí sobrevivió**. Este repositorio es un plano maestro institucional (Blueprint) que demuestra cómo construir, validar y desplegar modelos de *Machine Learning* en MetaTrader 5 a latencia cero.

---

## 🗺️ Mapa del Repositorio (Cero Ruido)

El repositorio está estrictamente dividido en dos ecosistemas y una bóveda documental:

- 🐍 **`/python/m2_metalabeling/`**: El Motor de Machine Learning.
- 📈 **`/mql5/`**: Código fuente de MetaTrader 5 (Extractores y Bóvedas de Producción).
- 📚 **`/docs/`**: Documentación Científica (Post-Mortem, Metodología y Cronología).

---

## ⚙️ Guía de Trabajo: Flujo de Ejecución Paso a Paso

Si quieres entender cómo opera este ecosistema de principio a fin, aquí tienes la secuencia lógica de ejecución del **Pipeline M2**. Puedes replicarlo para cualquier otra estrategia base:

### Paso 1: Extracción de Datos (MQL5)
*El bot "ciego" recopila la cinemática del mercado.*
* **Script:** `mql5/Experts/HMA_SQX_Discovery/Pipeline_Extractor_M1.mq5`
* **Acción:** Se ejecuta en el Strategy Tester de MT5. Genera masivamente archivos CSV con indicadores técnicos y resultados de trades (Deals) en la carpeta `Files` de MetaTrader.

### Paso 2: Ingesta y Etiquetado (Python)
*López de Prado's Triple Barrier Method.*
* **Scripts:** `python/m2_metalabeling/ingestion/mt5_reader.py` y `labeling/triple_barrier.py`
* **Acción:** Python lee los CSV crudos de MT5, alinea las fechas y etiqueta probabilísticamente cada trade (Éxito = 1, Fracaso = 0) basándose en si alcanzó la barrera de Take Profit o Stop Loss.

### Paso 3: Entrenamiento Walk-Forward (Python)
*Evitando el Data Leakage y el Overfitting.*
* **Script:** `python/m2_metalabeling/models/rolling_window_retrain.py`
* **Acción:** Se entrena el modelo **XGBoost**. Se usa validación de ventanas rodantes (*Walk-Forward*) con reglas estrictas de *Purging* y *Embargo* para asegurar que el modelo no memoriza el pasado ni mira hacia el futuro.

### Paso 4: Auditoría de Fuga de Datos (Python)
*Sanity Checks institucionales.*
* **Script:** `python/m2_metalabeling/models/audit_report.py`
* **Acción:** Verifica algorítmicamente que no existe correlación cruzada entre los sets de Entrenamiento y Prueba. Si la prueba falla, el modelo se descarta inmediatamente.

### Paso 5: Transpilación a Latencia Cero (Python ➡️ C++)
*Eliminando los cuellos de botella de red.*
* **Script:** `python/m2_metalabeling/models/export_factory_oracle.py`
* **Acción:** Convierte los árboles de decisión entrenados de XGBoost en código C++ puro (`.mqh`) a través de la librería `m2cgen`. El archivo resultante se deposita directamente en la carpeta `Include` de MT5.

### Paso 6: Ejecución en Bóveda de Producción (MQL5)
*Tradeo en vivo.*
* **Script:** `mql5/Experts/portfolio/XAUUSD/Strategy_XAUUSD_Production.mq5`
* **Acción:** El Expert Advisor lee el mercado, consulta el oráculo matemático en C++ incrustado en su código, y si la probabilidad de éxito es alta, dispara la orden al bróker en **0 milisegundos**.

---

## 📚 Documentación Esencial

Si deseas profundizar en las lecciones matemáticas y estructurales aprendidas en este proyecto, lee los siguientes documentos:

1. [☠️ POST MORTEM: Por qué falló la estrategia (Alpha Decay)](docs/POST_MORTEM.md)
2. [🧪 METODOLOGÍA: El Framework de Meta-Labeling](docs/METHODOLOGY.md)
3. [📅 CRONOLOGÍA: La evolución completa del Proyecto](docs/CRONOLOGIA_PROYECTO_HMA.md)

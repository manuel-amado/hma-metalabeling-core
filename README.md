# ðŸ›ï¸ M2 Quant Pipeline: Meta-Labeling Framework

![Status](https://img.shields.io/badge/Status-Production_Ready-brightgreen)
![Architecture](https://img.shields.io/badge/Architecture-Python%20%7C%20C%2B%2B%20%7C%20MQL5-blue)
![Validation](https://img.shields.io/badge/Validation-Purged_WFM-orange)
![Execution](https://img.shields.io/badge/Latency-0ms_Native-success)

> **Veredicto CientÃ­fico:** Este repositorio fue creado para probar el *Edge* de la estrategia Hull Moving Average (HMA). Las rigurosas pruebas de este pipeline demostraron que **las Medias MÃ³viles sufren de *Alpha Decay* irreversible y no funcionan como gatillos de entrada en Forex**. Se documenta el fracaso de la HMA para evitar pÃ©rdidas de capital.

Aunque la estrategia HMA muriÃ³, **la infraestructura construida aquÃ­ sobreviviÃ³**. Este repositorio es un plano maestro institucional (Blueprint) que demuestra cÃ³mo construir, validar y desplegar modelos de *Machine Learning* en MetaTrader 5 a latencia cero.

---

## ðŸ—ºï¸ Mapa del Repositorio (Cero Ruido)

El repositorio estÃ¡ estrictamente dividido en dos ecosistemas y una bÃ³veda documental:

- ðŸ **`/python/m2_metalabeling/`**: El Motor de Machine Learning.
- ðŸ“ˆ **`/mql5/`**: CÃ³digo fuente de MetaTrader 5 (Extractores y BÃ³vedas de ProducciÃ³n).
- ðŸ“š **`/docs/`**: DocumentaciÃ³n CientÃ­fica (Post-Mortem, MetodologÃ­a y CronologÃ­a).

---

## âš™ï¸ GuÃ­a de Trabajo: Flujo de EjecuciÃ³n Paso a Paso

Si quieres entender cÃ³mo opera este ecosistema de principio a fin, aquÃ­ tienes la secuencia lÃ³gica de ejecuciÃ³n del **Pipeline M2**. Puedes replicarlo para cualquier otra estrategia base:

### Paso 1: ExtracciÃ³n de Datos (MQL5)
*El bot "ciego" recopila la cinemÃ¡tica del mercado.*
* **Script:** `mql5/Experts/HMA_SQX_Discovery/Pipeline_Extractor_M1.mq5`
* **AcciÃ³n:** Se ejecuta en el Strategy Tester de MT5. Genera masivamente archivos CSV con indicadores tÃ©cnicos y resultados de trades (Deals) en la carpeta `Files` de MetaTrader.

### Paso 2: Ingesta y Etiquetado (Python)
*LÃ³pez de Prado's Triple Barrier Method.*
* **Scripts:** `python/m2_metalabeling/ingestion/mt5_reader.py` y `labeling/triple_barrier.py`
* **AcciÃ³n:** Python lee los CSV crudos de MT5, alinea las fechas y etiqueta probabilÃ­sticamente cada trade (Ã‰xito = 1, Fracaso = 0) basÃ¡ndose en si alcanzÃ³ la barrera de Take Profit o Stop Loss.

### Paso 3: Entrenamiento Walk-Forward (Python)
*Evitando el Data Leakage y el Overfitting.*
* **Script:** `python/m2_metalabeling/models/rolling_window_retrain.py`
* **AcciÃ³n:** Se entrena el modelo **XGBoost**. Se usa validaciÃ³n de ventanas rodantes (*Walk-Forward*) con reglas estrictas de *Purging* y *Embargo* para asegurar que el modelo no memoriza el pasado ni mira hacia el futuro.

### Paso 4: AuditorÃ­a de Fuga de Datos (Python)
*Sanity Checks institucionales.*
* **Script:** `python/m2_metalabeling/models/audit_report.py`
* **AcciÃ³n:** Verifica algorÃ­tmicamente que no existe correlaciÃ³n cruzada entre los sets de Entrenamiento y Prueba. Si la prueba falla, el modelo se descarta inmediatamente.

### Paso 5: TranspilaciÃ³n a Latencia Cero (Python âž¡ï¸ C++)
*Eliminando los cuellos de botella de red.*
* **Script:** `python/m2_metalabeling/models/export_factory_oracle.py`
* **AcciÃ³n:** Convierte los Ã¡rboles de decisiÃ³n entrenados de XGBoost en cÃ³digo C++ puro (`.mqh`) a travÃ©s de la librerÃ­a `m2cgen`. El archivo resultante se deposita directamente en la carpeta `Include` de MT5.

### Paso 6: EjecuciÃ³n en BÃ³veda de ProducciÃ³n (MQL5)
*Tradeo en vivo.*
* **Script:** `mql5/Experts/portfolio/XAUUSD/Strategy_XAUUSD_Production.mq5`
* **AcciÃ³n:** El Expert Advisor lee el mercado, consulta el orÃ¡culo matemÃ¡tico en C++ incrustado en su cÃ³digo, y si la probabilidad de Ã©xito es alta, dispara la orden al brÃ³ker en **0 milisegundos**.

---

## ðŸ“š DocumentaciÃ³n Esencial

Si deseas profundizar en las lecciones matemÃ¡ticas y estructurales aprendidas en este proyecto, lee los siguientes documentos:

1. [â˜ ï¸ POST MORTEM: Por quÃ© fallÃ³ la estrategia (Alpha Decay)](docs/POST_MORTEM.md)
2. [ðŸ§ª METODOLOGÃA: El Framework de Meta-Labeling](docs/METHODOLOGY.md)
3. [ðŸ“… CRONOLOGÃA: La evoluciÃ³n completa del Proyecto](docs/CRONOLOGIA_PROYECTO_HMA.md
4. [🕵️ ARQUEOLOGÍA: Evolución y análisis estructural (v3 a v26)](docs/ANALISIS_VERSIONES_HMA.md))


# WS-Mavericks: Nexus AHMA (Adaptive Hull Moving Average) & Meta-Labeling

Este repositorio contiene la infraestructura completa para la generación, entrenamiento y despliegue de sistemas de trading algorítmicos institucionales en MQL5 (MetaTrader 5), potenciados por modelos de Machine Learning (XGBoost) utilizando el método de **Meta-Etiquetado** (López de Prado).

Actualmente nos encontramos en la rama de desarrollo: **`dev`**.

## Arquitectura Híbrida del Sistema

El ecosistema está construido sobre un flujo de trabajo que integra la extrema velocidad de ejecución de C++ (MQL5) con el ecosistema de Data Science de Python (Scikit-Learn, XGBoost, ONNX).

1. **Generación de Señales:** Un motor base (`HMA_ML_Orchestrator`) caza anomalías e ineficiencias matemáticas usando la pendiente y cinemática de la *Hull Moving Average*.
2. **Método de Triple Barrera:** No predecimos el precio. Etiquetamos las ejecuciones basándonos en volatilidad dinámica (Take Profit superior, Stop Loss inferior, y Expiración por tiempo).
3. **Machine Learning Meta-Labeling:** Python audita el dataset histórico y entrena un modelo XGBoost como filtro secundario. El modelo clasifica la probabilidad matemática de que la señal primaria sea un falso positivo o un trade ganador.
4. **Despliegue Nativo:** El modelo de IA entrenado se exporta como `.onnx` o arreglos nativos (`.mqh`) para operar en MetaTrader 5 en tiempo real.

---

## Estructura y Segmentación del Repositorio

El proyecto ha sido rigurosamente segmentado en las siguientes carpetas para asegurar mantenibilidad y escalabilidad en los procesos de "Quant Research" y despliegue:

### 📁 1. `Alpha_Sniper_Vault` (El Núcleo de Machine Learning)
Este es el motor de Inteligencia Artificial y Backtesting.
*   **`src/training/`**: Scripts dedicados exclusivamente al entrenamiento y optimización de hiperparámetros de los modelos XGBoost.
*   **`src/data_processing/`**: Herramientas críticas para limpiar y esterilizar archivos CSV, además de pipelines de preprocesamiento de características (*Feature Engineering*).
*   **`src/analysis/`**: Auditores de métricas, simuladores de equidad, ploteo de gráficas 3D y evaluación del ratio Riesgo/Beneficio.
*   **`src/exports_mql5/`**: Código puente para convertir los modelos en Python directamente a código C++ (`.mqh`) o al estándar `.onnx`.
*   **`mql5/`**: Copia exacta de los Expert Advisors activos (versiones V16, V17, WFO) y la subcarpeta `Models/` con los modelos binarios activos.
*   **`docs/`**: Documentación profunda, reportes de "Out-Of-Sample" y diferenciaciones entre versiones del orquestador.

### 📁 2. `docs_reports`
Almacén de conocimiento central. Contiene el **`ARCHITECTURE_MASTER_CONTEXT.md`** (biblia técnica del funcionamiento paso a paso), reportes generados de auditorías históricas, diagramas MFE/MAE y reportes de rentabilidad realista en formato Markdown y texto.

### 📁 3. `configs`
Contenedor centralizado para todos los archivos de configuración `.ini` y `.set` necesarios para lanzar miles de backtests masivos o tests unitarios desde las herramientas CLI de MetaTrader. Evita la polución visual del código fuente.

### 📁 4. `launchers`
Archivos ejecutables por lotes (`.bat`) y scripts de PowerShell (`.ps1`) para automatizar procesos del día a día, como sincronizar el calendario económico, lanzar optimizaciones masivas en paralelo o testear configuraciones visuales con un solo clic.

### 📁 5. `scripts_utils`
Caja de herramientas de Python para utilidades rápidas (e.g. chequeo de paridad de CSVs, parseo rápido de HTMLs producidos por MT5, scripts de autoguardado en Git).

---

## Flujo de Trabajo (Git Workflow)
* Toda la investigación sobre características nuevas, filtrado AHMA (Adaptive Hull) y *Walk Forward Optimization (WFO)* ocurre en la rama actual (`dev`).
* Antes de hacer *merge* a `main`, el modelo debe sobrevivir la simulación estresada de Out-Of-Sample y demostrar nulo *Overfitting* en el umbral seleccionado por el calibrador.

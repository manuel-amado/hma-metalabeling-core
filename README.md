# WS-Mavericks: HMA Algorithmic Trading & Meta-Labeling

Este repositorio contiene la infraestructura completa para la generación, investigación y despliegue de sistemas de trading algorítmico institucionales en MQL5 (MetaTrader 5), potenciados por modelos de Machine Learning (XGBoost / RL / ONNX) utilizando el método de **Meta-Etiquetado** (López de Prado) y Minería Genética (SQX).

## Arquitectura de Sincronización (SSOT)

Para garantizar un entorno **Single Source of Truth (SSOT)** y evitar descorrelaciones, este repositorio utiliza **Directory Junctions** (Enlaces Simbólicos) en Windows. 
Las carpetas \MQL5\ de los terminales locales de MetaTrader (\D0E8...\ y \D8FB...\) apuntan *físicamente* a la carpeta \mql5/\ de este repositorio. Cualquier cambio realizado en MetaEditor se guarda instantáneamente en Git, y cualquier rama descargada de Git se aplica instantáneamente a los terminales.

## Estructura del Repositorio

El ecosistema ha sido rigurosamente segmentado en las siguientes ramas operativas:

### 1. \mql5/Experts\ (Los Motores Algorítmicos)
* **\HMA_Breakout/\**: Familia de bots basados en reversión a la media y aceleración HMA (v16 a v30). Incluyen filtrado macro D1 (DX) y Walk-Forward Optimization (WFO).
* **\HMA_TrendFollowing/\**: Bots de seguimiento tendencial puro (Familia Master). Basados en alineación de EMA, HMA pullback y filtros de agotamiento RSI.
* **\HMA_Omni/\**: Proyecto de arquitectura avanzada utilizando modelos continuos y Reinforcement Learning (PPO).
* **\HMA_SQX_Discovery/\**: Laboratorio de minería algorítmica y fuerza bruta utilizando **StrategyQuant X**. Aísla patrones puros (ej. HMA Ribbon) para integrarlos posteriormente al ecosistema de ML.
* **\HMA_Data_Extractors/\**: Orquestadores de Meta-Etiquetado encargados de operar en "modo ciego" para exportar la cinemática del mercado a CSVs.

### 2. \mql5/Indicators\ & \mql5/Scripts\
Contiene todos los indicadores personalizados requeridos para operar (incluyendo la inmensa librería de 40+ indicadores \Sq*.mq5\ generados por StrategyQuant X para asegurar autonomía del código).

### 3. \python/\ (Data Science & Machine Learning — M2 Architecture)
* **\m2_metalabeling/\**: Framework modular basado en Marcos López de Prado:
  * **\ingestion/\**: Consumo e indexación UTC de CSVs exportados desde MT5.
  * **\labeling/\**: Método de la Triple Barrera (Profit Taking, Stop Loss, Timeout).
  * **\cross_validation/\**: Purged K-Fold Cross-Validation con Embargo anti-Data Leakage.
  * **\models/\**: Entrenadores XGBoost con validación por folds.
  * **\calibration/\**: Calibración de probabilidades mediante Isotonic Regression & Reliability Diagrams.
  * **\export/\**: Serialización de modelos a \.mqh\ (C++) y \.onnx\.
* **\pipelines/\**, **\	raining/\**, **\nalysis/\**: Pipelines legados y utilidades de auditoría.

### 4. \scripts/\ (Automatización y DevOps)
* **\launchers/\**: Ejecutables en PowerShell para compilar bots masivamente (\watcher_ex5.ps1\), ejecutar optimizaciones o sincronizar bases de datos de forma paralela.

---

## Reglas Críticas del Repositorio
1. **Ignorar Datos Masivos:** Los archivos \.csv\, \.log\, \.parquet\ e históricos de tick jamás deben subirse a Git. El archivo \.gitignore\ ya está configurado para rechazar estos pesos pesados automáticamente.
2. **Documentación Intercalada:** Cada vez que una familia de bots realiza un cambio de paradigma (ej. pasar de SL estático a Trailing ATR, o introducir la arquitectura M2), la lógica matemática se documenta en un archivo \.md\ directamente en su directorio correspondiente.

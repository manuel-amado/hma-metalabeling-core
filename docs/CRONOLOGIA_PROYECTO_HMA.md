# Cronología del Proyecto HMA (Hull Moving Average)
*Evolución del framework algorítmico: De reglas manuales a Machine Learning Institucional*

Este documento traza el recorrido técnico y evolutivo del proyecto **HMA**, evidenciando cómo una estrategia direccional basada en medias móviles de Hull maduró hasta convertirse en una arquitectura Cuantitativa con *Meta-Labeling*.

---

## 🏛️ Era 1: HMA Breakout (Versiones v1 a v16)
**El Origen:** Todo comenzó con la programación manual en MQL5 de la cinemática de la Media Móvil de Hull (HMA).
*   **Lógica Core:** El sistema medía la aceleración y los cambios de pendiente (*V-Pivots*) de la HMA para detectar inicios de tendencia.
*   **Gestor de Volatilidad:** Se integró el Ancho de Banda de Keltner (*Keltner Bandwidth*) para cazar rupturas de volatilidad (*Breakouts*).
*   **El Principio de la Sobre-Operativa:** Para entrenar el modelo de Machine Learning, inicialmente programamos los bots (`Alpha_Sniper.mq5`) para ser **sumamente irrentables y poco restrictivos**. Al tomar miles de *trades* malos a propósito, logramos inflar masivamente el tamaño de la muestra de datos, dándole a XGBoost el ecosistema perfecto para aprender de una infinidad de errores y aciertos.
*   **El Cuello de Botella:** A pesar de los buenos *triggers*, el mercado generaba demasiados "falsos rompimientos". Aquí nació la necesidad formal de implementar el método de **Triple Barrera (Meta-Labeling)** de Marcos López de Prado para que XGBoost filtrara probabilísticamente si una señal de la HMA iba a tocar el Take Profit o el Stop Loss.

---

## 🏛️ Era 2: HMA Trend Following (HMA_TF, Versiones v17 a v21)
**El Pivote Estratégico:** Al observar que los *Breakouts* eran muy vulnerables a barridas de liquidez, la estrategia HMA pivotó hacia el **Seguimiento de Tendencia (Trend Following)**.
*   Se eliminaron las rupturas de canales estrechos en favor de capturar movimientos macro.
*   **Reinforcement Learning (Proyecto Omni):** Durante esta fase, hubo un experimento ambicioso para usar Agentes de Aprendizaje por Refuerzo (PPO) con el fin de crear un bot universal (*Omni*). Aunque innovador, el modelo era muy opaco ("caja negra") y difícil de auditar en producción.

---

## 🏛️ Era 3: SQX Discovery Engine (HMA v1)
**Delegando el Descubrimiento:** Decidimos dejar de programar reglas lógicas a mano. Integramos **StrategyQuant X (SQX)** para usar algoritmos genéticos y fuerza bruta computacional que descubrieran las anomalías del mercado usando la HMA como bloque base (*Primary Model*).
*   **El Problema Técnico:** La versión 1 minada en SQX operaba en huso horario GMT+0. Al conectarlo a MetaTrader 5 (que usa husos UTC+2/EET), los cierres de las velas de 1 Hora (H1) se desincronizaron completamente, causando rozamiento en el *spread* y arruinando el factor de beneficio.

---

## 🏛️ Era 4: HMA MTF + Regime Filters (HMA v2)
**Estructura Macro:** 
*   **Sincronización:** Se regeneró la base de datos de ticks en UTC+2 para lograr una congruencia del 100% entre SQX y MetaTrader 5.
*   **Multi-Timeframe (MTF):** La estrategia HMA dejó de evaluar el precio en el vacío. Se implementó un filtro de régimen en un marco temporal superior: **ADX en H4**. Si el ADX indicaba que el mercado estaba lateral, las señales de la HMA en H1 eran silenciadas.

---

## 🏛️ Era 5: Production Vaults & WFM (HMA v3)
**El Cénit Institucional:** La arquitectura final del proyecto HMA.
*   **Walk-Forward Montecarlo (WFM):** El modelo de Machine Learning ya no se valida en un solo bloque estático de tiempo, sino mediante ventanas rodantes continuas, aplicando *Purging* y *Embargo* para evitar *Data Leakage*.
*   **Transpilación a C++ (Latencia Cero):** El oráculo XGBoost de Meta-Labeling se convierte nativamente a `.mqh` a través de `m2cgen` (ej. `M2_XGBoost_Oracle_XAUUSD.mqh`).
*   **Production Vaults:** Todo culmina en `Strategy_XAUUSD_Production.mq5`, un entorno aislado de ejecución pura (EMS) que recibe las señales HMA y usa el oráculo en milisegundos para gestionar el capital.

---

## ☠️ Era 6: El Veredicto (Post-Mortem)
**El Fin de la HMA:** Al ejecutar el WFM purgado, se descubrió que las estrategias rentables eran solo producto del sobreajuste (Overfitting) o del Beta direccional del mercado. El Alpha de la HMA se había desvanecido.
*   Se canceló la ejecución en real para proteger el capital.
*   El código base del "Discovery" se migrará a un nuevo repositorio (`Anomaly Detector Setup`).
*   Este repositorio queda como una obra maestra arquitectónica (*Blueprint* del Pipeline M2) abierta a la comunidad.


---
## 🔗 Conexiones Transversales
- [[Teoria - XGBoost y GT-Score|XGBoost y GT-Score]]
- [[Teoria - Anclaje VWAP|Anclaje VWAP]]
- [[Teoria - VPIN y Microestructura|VPIN y Microestructura]]
- [[Sistema - ZeroMQ y HFT|ZeroMQ y HFT]]
- [[Sistema - MQL5 Execution Engine|MQL5 Execution Engine]]
- [[Teoria - Market Beta vs Alpha|Market Beta vs Alpha]]
- [[Teoria - Robustez Inter-Mercado y Husos Horarios|Robustez Inter-Mercado y Husos Horarios]]
- [[Sistema - Adaptacion SQX a MT5 FTMO|Adaptacion SQX a MT5 FTMO]]

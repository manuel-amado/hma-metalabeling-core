# CronologÃ­a del Proyecto HMA (Hull Moving Average)
*EvoluciÃ³n del framework algorÃ­tmico: De reglas manuales a Machine Learning Institucional*

Este documento traza el recorrido tÃ©cnico y evolutivo del proyecto **HMA**, evidenciando cÃ³mo una estrategia direccional basada en medias mÃ³viles de Hull madurÃ³ hasta convertirse en una arquitectura Cuantitativa con *Meta-Labeling*.

---

## ðŸ“… Era 1: HMA Breakout (Versiones v1 a v16)
**El Origen:** Todo comenzÃ³ con la programaciÃ³n manual en MQL5 de la cinemÃ¡tica de la Media MÃ³vil de Hull (HMA).
*   **LÃ³gica Core:** El sistema medÃ­a la aceleraciÃ³n y los cambios de pendiente (*V-Pivots*) de la HMA para detectar inicios de tendencia.
*   **Gestor de Volatilidad:** Se integrÃ³ el Ancho de Banda de Keltner (*Keltner Bandwidth*) para cazar rupturas de volatilidad (*Breakouts*).
*   **El Cuello de Botella:** A pesar de los buenos *triggers*, el mercado generaba demasiados "falsos rompimientos". AquÃ­ naciÃ³ la necesidad de integrar *Machine Learning*. Se implementÃ³ el mÃ©todo de **Triple Barrera (Meta-Labeling)** de Marcos LÃ³pez de Prado para que XGBoost filtrara probabilÃ­sticamente si una seÃ±al de la HMA iba a tocar el Take Profit o el Stop Loss.

---

## ðŸ“… Era 2: HMA Trend Following (HMA_TF, Versiones v17 a v21)
**El Pivote EstratÃ©gico:** Al observar que los *Breakouts* eran muy vulnerables a barridas de liquidez, la estrategia HMA pivotÃ³ hacia el **Seguimiento de Tendencia (Trend Following)**.
*   Se eliminaron las rupturas de canales estrechos en favor de capturar movimientos macro.
*   **Reinforcement Learning (Proyecto Omni):** Durante esta fase, hubo un experimento ambicioso para usar Agentes de Aprendizaje por Refuerzo (PPO) con el fin de crear un bot universal (*Omni*). Aunque innovador, el modelo era muy opaco ("caja negra") y difÃ­cil de auditar en producciÃ³n.

---

## ðŸ“… Era 3: SQX Discovery Engine (HMA v1)
**Delegando el Descubrimiento:** Decidimos dejar de programar reglas lÃ³gicas a mano. Integramos **StrategyQuant X (SQX)** para usar algoritmos genÃ©ticos y fuerza bruta computacional que descubrieran las anomalÃ­as del mercado usando la HMA como bloque base (*Primary Model*).
*   **El Problema TÃ©cnico:** La versiÃ³n 1 minada en SQX operaba en huso horario GMT+0. Al conectarlo a MetaTrader 5 (que usa husos UTC+2/EET), los cierres de las velas de 1 Hora (H1) se desincronizaron completamente, causando rozamiento en el *spread* y arruinando el factor de beneficio.

---

## ðŸ“… Era 4: HMA MTF + Regime Filters (HMA v2)
**Estructura Macro:** 
*   **SincronizaciÃ³n:** Se regenerÃ³ la base de datos de ticks en UTC+2 para lograr una congruencia del 100% entre SQX y MetaTrader 5.
*   **Multi-Timeframe (MTF):** La estrategia HMA dejÃ³ de evaluar el precio en el vacÃ­o. Se implementÃ³ un filtro de rÃ©gimen en un marco temporal superior: **ADX en H4**. Si el ADX indicaba que el mercado estaba lateral, las seÃ±ales de la HMA en H1 eran silenciadas.

---

## ðŸ“… Era 5: Production Vaults & WFM (HMA v3)
**El CÃ©nit Institucional:** La arquitectura final del proyecto HMA.
*   **Walk-Forward Montecarlo (WFM):** El modelo de Machine Learning ya no se valida en un solo bloque estÃ¡tico de tiempo, sino mediante ventanas rodantes continuas, aplicando *Purging* y *Embargo* para evitar *Data Leakage*.
*   **TranspilaciÃ³n a C++ (Latencia Cero):** El orÃ¡culo XGBoost de Meta-Labeling se convierte nativamente a `.mqh` a travÃ©s de `m2cgen` (ej. `M2_XGBoost_Oracle_XAUUSD.mqh`).
*   **Production Vaults:** Todo culmina en `Strategy_XAUUSD_Production.mq5`, un entorno aislado de ejecuciÃ³n pura (EMS) que recibe las seÃ±ales HMA y usa el orÃ¡culo en milisegundos para gestionar el capital.

---

## 📅 Era 6: El Veredicto (Alpha Decay y Obsolescencia)
**El Final del Experimento HMA:** A pesar de dotar a la estrategia con la infraestructura de Machine Learning más avanzada (Walk-Forward, C++, Filtros de Régimen), el modelo demostró carecer de ventaja estadística real (*Edge*).
*   **Alpha Decay:** Las investigaciones finales demostraron que el uso de Medias Móviles (como la HMA) como "gatillos" (*triggers*) de entrada está obsoleto. El retraso matemático (*lag*) de las medias hace que el bot compre la cima del movimiento, justo cuando los algoritmos de Alta Frecuencia (HFT) institucionales comienzan a operar a la contra (reversión a la media).
*   **El Verdadero Triunfo:** Aunque la estrategia HMA murió, **la construcción del Pipeline de M2 sobrevivió como un éxito rotundo**. El pipeline fue tan riguroso que logró hacer exactamente lo que se le pide a un sistema de gestión de riesgo institucional: destrozar una mala idea antes de que cueste un solo dólar en el mercado real.

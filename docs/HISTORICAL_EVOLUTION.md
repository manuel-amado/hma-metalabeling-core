# Evolución de la Investigación: De Heurísticas a Machine Learning

Este documento traza el recorrido técnico del proyecto HMA. El objetivo es clarificar la transición desde las conclusiones iniciales (basadas en premisas que resultaron ser erróneas) hasta la arquitectura cuantitativa final, detallando por qué se tomaron decisiones de diseño clave a lo largo del tiempo.

---

## Fase 1: La Era Heurística (Modelos MQL5 Estáticos)

**Premisa Inicial:** Se hipotetizó que la cinemática de la Media Móvil de Hull (HMA), específicamente sus cambios de pendiente (*V-Pivots*) y aceleración, poseía ventaja estadística predictiva (*Alpha*) para detectar inicios de tendencia.

**Implementación:** 
*   Desarrollo de bots clásicos (`Alpha_Sniper.mq5`) basados estrictamente en código MQL5 tradicional. 
*   Se iteraban combinaciones de periodos de HMA cruzando canales de volatilidad (Keltner Bandwidth).

**Conclusión de la Fase:** Las optimizaciones en MetaTrader 5 resultaron ineficientes. Las reglas estáticas demostraron ser extremadamente frágiles: funcionaban en regímenes de tendencia pero colapsaban en mercados laterales. 
*Acción tomada:* Se decidió abandonar la toma de decisiones basada en indicadores estáticos y delegar la inteligencia a modelos probabilísticos (Machine Learning).

---

## Fase 2: Transición al Meta-Labeling y Recolección de Datos

**Premisa Inicial:** Para que un modelo de Machine Learning (XGBoost) aprenda eficazmente, necesita un volumen masivo de datos que contenga tanto casos de éxito como de fracaso.

**Implementación (El Principio del Caos Intencionado):**
*   Se reconfiguraron los bots primarios para ser deliberadamente poco restrictivos. El objetivo ya no era que el bot de MQL5 fuera rentable, sino maximizar el número de ejecuciones (Alto *Recall*).
*   Se implementó por primera vez el método de **Triple Barrera** (Take Profit, Stop Loss, Tiempo) para etiquetar esta ingente cantidad de operaciones.

**Conclusión de la Fase:** La extracción de datos en tiempo real mediante APIs (Python a MT5) introducía latencias inaceptables y cuellos de botella en la red.
*Acción tomada:* Se desarrolló el concepto de *Harvesting* offline. Se crearon extractores ciegos (`TestHarvest_Massive_Hybrid.mq5`) que operaban en el modo de optimización local de MT5 para extraer años de cinemática a archivos CSV a máxima velocidad.

---

## Fase 3: Delegación a StrategyQuant X (SQX)

**Premisa Inicial:** Si el modelo primario no necesita ser inteligente sino generar buenas entradas base, es más eficiente que un algoritmo genético lo descubra mediante fuerza bruta.

**Implementación:**
*   Se integró **StrategyQuant X** para minar anomalías del mercado usando la HMA como bloque fundamental.
*   Se resolvieron discrepancias críticas de husos horarios (sincronización de datos GMT+0 de SQX frente a UTC+2 de los brókeres de MT5).

**Conclusión de la Fase:** Se lograron modelos primarios más estables, pero seguían fallando en el largo plazo debido a los cambios de régimen macroeconómico.
*Acción tomada:* Se implementaron filtros de régimen Multi-Timeframe (ej. ADX en H4) para silenciar el modelo primario en entornos desfavorables, antes de pasar los datos al oráculo de XGBoost.

---

## Fase 4: Consolidación Arquitectónica (M2 Pipeline)

**El Estado Final:** La arquitectura evolucionó hacia un sistema puramente institucional.
1.  **Orquestador Central:** Se eliminó la fragmentación de decenas de EAs obsoletos. Un único orquestador gestiona la operativa (`Strategy_XAUUSD_Production.mq5`).
2.  **Transpilación a C++:** Para evadir la latencia de red, los modelos XGBoost entrenados en Python se exportan directamente a cabeceras de C++ (`.mqh`) mediante `m2cgen`, ejecutándose en MetaTrader en menos de 0.1 microsegundos.
3.  **Walk-Forward Montecarlo (WFM):** La validación estática fue reemplazada por ventanas rodantes purgadas, eliminando el *Data Leakage*.

*Esta fase final permitió realizar las pruebas de robustez definitivas que culminaron en el veredicto del proyecto, detallado en el documento de Post-Mortem.*

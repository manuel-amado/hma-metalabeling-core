# ARCHITECTURE MASTER CONTEXT - HMA Meta-Labeling System

## 1. Identidad y Filosofía del Proyecto (El Paradigma Quant)
Este proyecto abandona el enfoque clásico del trading algorítmico (donde un bot intenta adivinar el mercado y gestionar el riesgo simultáneamente) para adoptar la teoría de **Meta-Labeling (Corrective AI) de Marcos López de Prado**.

La arquitectura se divide en dos fases innegociables:
* **Fase 1: Modelo Primario (MQL5 - Bot HMA):** Es "tonto pero valiente". Su objetivo NO es ganar dinero, sino tener un **Alto Recall (Alta Sensibilidad)**. Busca configuraciones matemáticas específicas y captura la "foto" de los indicadores sin censurarlos.
* **Fase 2: Modelo Secundario (Python - ML):** Es "inteligente y cobarde". Ingiere el dataset generado por MQL5 y aprende a discriminar los falsos positivos. Decidirá ejecutar el trade solo si la probabilidad matemática de éxito es alta (ej. `P(Profit) >= 0.60`).

**REGLA DE ORO DE LOS DATOS:** "Garbage In, Garbage Out" (GIGO). 
* **Prohibido el Volumen:** El "Tick Volume" de los CFDs es falso y ruidoso. Está estrictamente eliminado del sistema.
* **Prohibidos los Precios Absolutos:** Se exportan datos estacionarios (Z-Scores, distancias porcentuales, pendientes) porque el Machine Learning falla con precios absolutos.
* **Resiliencia a Mechas (Cacerías de Liquidez):** Las señales de entrada se basan en precios de Cierre (`Close`), mientras que el Stop Loss y el MAE/MFE utilizan los extremos (`High/Low`).

---

## 2. Síntesis de la Estrategia (La Física del Trade) y "Cliff Effects"
La estrategia busca capturar "Reversiones a la Media con Inercia" (HMA + RSI). En el trading clásico, usábamos filtros booleanos rígidos. Aquí, hemos desmantelado esos "Cliff Effects" (Efectos Acantilado) para evitar el Sesgo de Supervivencia. En lugar de bloquear la operación, **medimos la variable y disparamos**.

### A. Contexto Macro (Filtro de Tendencia EMAs)
* *Clásico:* Si EMA50 < EMA200 en H4, prohibido comprar.
* *Meta-Labeling:* Operamos igual. Exportamos `trend_alignment` (1 a favor, -1 en contra) y `Dist_to_Macro_EMA` (tensión elástica macro). La IA descubrirá si la contra-tendencia es rentable bajo ciertas anomalías.

### B. El Agotamiento (El Resorte RSI)
* *Clásico:* Disparo condicionado a un límite rígido de tiempo (`MaxRsiToCrossMinutes`) y a un nivel exacto (<35).
* *Meta-Labeling:* Escaneamos la ventana reciente y medimos la física del resorte. Exportamos `rsi_extreme_val` (profundidad exacta del agotamiento) y `bars_since_extreme` (latencia del gatillo). Así la IA diferencia un rebote en forma de "V" rápida de uno en "U" lenta.

### C. La Estructura de Consolidación (El Pullback)
* *Clásico:* El precio debía estar X velas al otro lado de la media (`MinOppositeBars`).
* *Meta-Labeling:* Medimos la energía potencial acumulada. Exportamos `pullback_duration` (velas totales en el lado opuesto) y `pullback_max_depth_pct` (distancia máxima alcanzada durante el retroceso).

### D. El Disparo y la Inercia (HMA Cross)
* *Clásico:* El precio debía cerrar a un `DeviationATRPercent` alto para confirmar fuerza, de lo contrario se abortaba.
* *Meta-Labeling:* Bajamos el filtro a un 2-3% solo para evitar ruido plano. Exportamos `hma_slope_pct` (inercia de la pendiente), `hma_acceleration` (derivada de la curva) y `breakout_force_atr` (fuerza de ruptura normalizada por ATR).

### E. Microestructura y Entorno (Spread y Noticias)
* *Clásico:* Se bloqueaba el bot si el spread era alto o había noticias.
* *Meta-Labeling:* Subimos el spread a un margen de seguridad anti-broker (5.0 pips) y NO bloqueamos noticias. Exportamos `spread_pips`, `hour_of_day` y eliminamos el bloqueo de noticias, transformando esa volatilidad en aprendizaje para la IA.

---

## 3. Diccionario de Features Exportadas (Variables Independientes 'X')

| Variable ML | Tipo de Dato | Significado para la Inteligencia Artificial |
| :--- | :--- | :--- |
| `Z_Score_Close` | Estacionaria | Grado de sobreextensión. La IA aprende si un precio "demasiado alejado" de su media (SMA20) tiende a la regresión (Mean Reversion). |
| `ATR_Normalized` | Estacionaria | Estado de nerviosismo. Ayuda a saber si el setup de HMA50 se "rompe" por exceso de volatilidad (ruido) o estancamiento. |
| `RSI_Extreme_Val` | Cinemática | Umbral exacto de energía potencial acumulada (No es lo mismo rebotar desde RSI 34 que desde RSI 15). |
| `Bars_Since_Ext` | Cinemática | Geometría del rebote (Latencia). Tiempo entre el máximo agotamiento y el cruce. |
| `HMA_Slope_Pct` | Física | Indica la inercia. Un cruce con pendiente casi plana es propenso a ser un fakeout. |
| `HMA_Acceleration`| Física | Derivada de la pendiente. Nos dice si la HMA se está volviendo más pronunciada a nuestro favor al momento de cruzar. |
| `Trend_Align` | Contexto | 1 (A favor), -1 (En contra). Fuerza macro para aprender la viabilidad de la contra-tendencia. |
| `Dist_Macro_EMA` | Contexto | Tensión elástica. Distancia del Close al EMA200 normalizada por el ATR. |
| `Pullback_Dur` | Estructura | Cantidad de velas que el precio pasó al otro lado de la HMA antes de cruzarla de vuelta. |
| `Pullback_Depth`| Estructura | Máxima profundidad de ese retroceso medida en múltiplos de ATR. |
| `Breakout_Force`| Física | La desviación exacta del precio sobre la HMA en el momento del cruce (en ATRs). |
| `SL_Distance_ATR` | Riesgo | Tamaño del SL normalizado. La IA aprenderá si un SL demasiado apretado (ej. <0.5 ATR) es cazado por el ruido inevitablemente. |
| `Spread_Pips` | Microestructura| Introduce liquidez. Un "error" técnico puede ser en realidad una falta de liquidez intradiaria. |
| `Hour_of_Day` | Temporal | Hora del servidor en la que ocurrió la señal. |

---

## 4. Gestión del Desenlace: El Etiquetado Rico (Targets 'y')
No basta con saber si el trade ganó o perdió. Necesitamos la "Ruta del Dolor".

### El Método de la Triple Barrera:
1.  **Stop Loss (Estructura):** Se calcula con `GetLowestLow(LookbackBars)` (no 1 vela, para evitar cierres prematuros por ruido).
2.  **Take Profit (Recompensa):** Multiplicador fijo (`TakeProfitMultiplier`) sobre la distancia del SL.
3.  **Barrera Vertical (Tiempo):** Si el mercado lateraliza por $N$ velas (`VerticalBarrierBars`), se cierra la operación. Evita coste de oportunidad y etiqueta señales sin momentum.

### Rich Labeling (MAE y MFE):
En la función `OnTradeTransaction`, al detectar el cierre, el sistema revisa los precios absolutos (`CopyHigh`/`CopyLow`) que existieron durante la vida del trade para calcular:
* **MAE_Pct (Maximum Adverse Excursion):** Drawdown máximo sufrido. Permite a la IA filtrar trades que, aunque ganadores, estuvieron a punto de tocar el SL.
* **MFE_Pct (Maximum Favorable Excursion):** Beneficio máximo flotante.
* **Exact_Return_Pct:** El retorno neto final de la operación.
* **Label_Binary:** 1 (Éxito TP), 0 (Fracaso SL), -1 (Cierre por Tiempo).

---

## 5. Anatomía del Algoritmo: El Recorrido Paso a Paso

Para comprender exactamente cómo se construyen los datos que consumirá la Inteligencia Artificial, es crucial detallar el ciclo de vida de cada evaluación del mercado. El Orchestrator ejecuta las siguientes fases cronológicas y matemáticas:

### FASE 1: El Latido (Sincronización y Barreras)
El algoritmo despierta en la función `OnTick()`. 
1. **Barrera de CPU:** Solo se ejecuta al nacimiento de una nueva vela (evaluación al cierre de la vela anterior). 
2. **Auditoría de Tiempo (Triple Barrera):** Revisa todas las posiciones abiertas. Si alguna operación ha estado viva más velas que el límite establecido (`VerticalBarrierBars`), se ejecuta un cierre de mercado forzoso para evitar el estancamiento de capital (coste de oportunidad).
3. **Filtro de Concurrencia:** Verifica que no exista ya una operación abierta en este símbolo.
4. **Filtro Anti-Broker (Microestructura):** Mide el spread exacto en ese milisegundo. Si excede los 5.0 pips de seguridad, aborta la evaluación para evitar ejecuciones abusivas por parte del proveedor de liquidez.

### FASE 2: La Extracción de Estado
Se consultan todos los búferes de indicadores para obtener la "Física del Entorno" de las últimas velas cerradas:
* Precios de Cierre, Apertura, Máximos y Mínimos (`CopyRates`).
* HMA50 (El núcleo inercial).
* EMA50 y EMA200 (El contexto macro).
* RSI de 14 periodos (El resorte del momentum).
* ATR de 14 periodos (El termómetro de volatilidad).
* SMA20 y Desviación Estándar (Para cálculos de anomalías estadísticas Z-Score).

### FASE 3: El Gatillo (High-Recall Signal)
En este punto, el sistema busca un único evento detonante: **El Cruce del Precio de Cierre sobre la HMA50**.
1. **Cruce Estricto:** La penúltima vela debe haber cerrado por debajo de la HMA, y la última vela por encima (o viceversa). Todo basado en el Cierre (`Close`), ignorando las mechas engañosas que ocurren intradía.
2. **Anti-Ruido Matemático:** Calcula la distancia absoluta entre el Precio de Cierre y la HMA en el instante del cruce. Si esta desviación es menor al 2% del ATR actual, se considera ruido plano y se ignora.

### FASE 4: El Escáner de Geometría (Generación de Features X)
Si se confirma el gatillo, en lugar de evaluar si el trade "es bueno" (como haría un bot clásico), el Orchestrator se limita a **medir meticulosamente la geometría del momento** utilizando las funciones en `HMA_FUNCTIONS.mqh`:
* **Estadística Estacionaria:** Calcula el `Z_Score` y normaliza el `ATR`.
* **Cinemática del Resorte:** Rastrea hacia atrás `RsiLookbackBars` velas buscando el punto máximo de tensión (`RSI_Extreme_Val`) y cuenta cuántas velas han pasado desde ese punto máximo hasta hoy (`Bars_Since_Ext`).
* **Física de Inercia:** Mide la primera derivada (Pendiente) y la segunda derivada (Aceleración) de la curva de la HMA.
* **Estructura del Retroceso:** Analiza cuántas velas pasó el precio ahogado debajo de la HMA antes de romperla (`Pullback_Dur`) y cuál fue la máxima profundidad que alcanzó ese buceo en múltiplos de ATR (`Pullback_Depth`).
* **Contexto Fractal:** Evalúa a qué distancia en ATR se encuentra el precio de la EMA200 Macro (`Dist_Macro_EMA`) y si las EMAs están alineadas.

### FASE 5: Estructuración del Riesgo y Ejecución
1. **Definición de Fronteras:** Se escanea el historial reciente (ignorando el ruido intradiario) usando `GetLowestLow()` o `GetHighestHigh()` para encontrar el refugio estructural más sólido y fijar el Stop Loss. 
2. **Proyección Asimétrica:** Se establece el Take Profit multiplicando matemáticamente la distancia del SL por `TakeProfitMultiplier`.
3. **Ejecución:** Se dispara una orden a mercado con un lotaje fijo.
4. **Respaldo en RAM:** Toda la información recolectada en la Fase 4 (junto con la hora, el ticket y el spread) se empaqueta en una estructura `MarketSnapshot` y queda suspendida en la memoria volátil del Data Logger, a la espera del desenlace.

### FASE 6: El Desenlace y Etiquetado Rico (Targets Y)
El sistema monitoriza pasivamente el mercado en la función `OnTradeTransaction`. Cuando detecta que un ticket previamente abierto acaba de cerrarse, entra en acción para completar el rompecabezas:
1. **Recuperación del Historial:** Encuentra el `MarketSnapshot` correspondiente en RAM mediante el Position ID.
2. **Cálculo de Retorno Neto:** Calcula con precisión el porcentaje de ganancia o pérdida final.
3. **Mapeo de la Ruta del Dolor (MAE / MFE):** Extrae todas las velas (Highs y Lows absolutos) que existieron entre la apertura y el cierre de la operación usando `CopyHigh` y `CopyLow`.
   * Identifica el punto máximo de sufrimiento (`MAE_Pct`): Cuánto estuvo a punto de saltar el SL antes de revertir.
   * Identifica el pico de codicia (`MFE_Pct`): Cuánto beneficio flotante se evaporó antes del cierre.
4. **Etiquetado Binario:** Asigna la clase objetivo para el modelo de Machine Learning (`1` para TP, `0` para SL, `-1` para Time Limit).
5. **Consolidación en Disco:** Une las Variables X (Fase 4) con las Variables Y (Fase 6), escribe la fila completa de 22 columnas en el disco SSD usando `FileWrite` y vacía la memoria para evitar fragmentación.

---

## 6. Arquitectura de Software y HPC (MQL5)
El código está diseñado con POO y optimizado exhaustivamente para evitar cuellos de botella durante backtests de años de duración:

1.  **Motor Lógico (`HMA_ML_Orchestrator`):** Toma la "foto" exacta en el milisegundo en que se cumplen las condiciones de apertura.
2.  **Sincronización:** El Ticket de MetaTrader actúa como *Foreign Key* uniendo el inicio (RAM) con el desenlace (Disco).
3.  **Optimización de RAM (Cero Fragmentación):** El array dinámico `m_active_signals[]` se redimensiona usando bloques de memoria (`ArrayResize(..., size + 1, 500)`).
4.  **Optimización de Disco (I/O):** Se mantiene un único `file_handle` global. Se escribe con `FileWrite` y se vacía el buffer seguro con `FileFlush()`. El archivo solo se cierra en `OnDeinit`.
5.  **Cero Fugas de Memoria:** Instancias creadas con `new` (`CMLDataLogger`) son destruidas explícitamente con `delete` en la desinicialización.
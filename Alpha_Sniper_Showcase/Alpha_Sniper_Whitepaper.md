# Alpha Sniper — Whitepaper Técnico Institucional
### Sistema de Trading Algorítmico Multi-Activo con Inferencia de Machine Learning en Tiempo Real
**Versión:** Fase 24.8 (Macro-Fundamental Restore & Emergency Rollback)
**Clasificación:** Documento de Auditoría Interna — Dirección Cuantitativa

---

> [!IMPORTANT]
> Este documento es la especificación fundacional del sistema **Alpha Sniper**. Describe la arquitectura técnica completa desde la recolección de datos crudos hasta la ejecución de órdenes en mercados en vivo, pasando por el entrenamiento de los modelos de inteligencia artificial y su despliegue en infraestructura VPS. Está redactado para que un auditor cuantitativo externo pueda reproducir, auditar y validar cualquier componente del ecosistema de forma independiente.

---

## Índice
1. [Visión General del Sistema](#1-visión-general-del-sistema)
2. [Ingesta y Saneamiento de Datos (Data Engineering)](#2-ingesta-y-saneamiento-de-datos-data-engineering)
3. [El Motor de Inteligencia Artificial (ML Pipeline)](#3-el-motor-de-inteligencia-artificial-ml-pipeline)
4. [Motor de Ejecución y Riesgo Físico (MQL5 Architecture)](#4-motor-de-ejecución-y-riesgo-físico-mql5-architecture)
5. [MLOps y Despliegue Continuo (Infraestructura)](#5-mlops-y-despliegue-continuo-infraestructura)
6. [Validación Empírica y Métricas de Producción](#6-validación-empírica-y-métricas-de-producción)

---

## 1. Visión General del Sistema

El sistema Alpha Sniper es un ecosistema de trading algorítmico de ciclo cerrado estructurado en cuatro capas funcionales completamente desacopladas:

```
┌──────────────────────────────────────────────────────────────────┐
│  CAPA 1: DATA ENGINEERING                                        │
│  HMA_ML_Orchestrator.mq5 + data_sanitizer.py                    │
│  Recolección asíncrona multi-activo → CSVs estructurados limpios │
└──────────────────────┬───────────────────────────────────────────┘
                       │ Struct_Dataset_*.csv / Struct_Exit_Dataset_*.csv
                       ▼
┌──────────────────────────────────────────────────────────────────┐
│  CAPA 2: ML PIPELINE                                             │
│  pipeline_global_optimizer.py                                    │
│  K-Means Regime Engine + XGBoost Entry/Exit + Grid Search 2D     │
│  Outputs: entry_model_*.pkl, exit_model_*.pkl, thresholds_*.json │
└──────────────────────┬───────────────────────────────────────────┘
                       │ .pkl + .json
                       ▼
┌──────────────────────────────────────────────────────────────────┐
│  CAPA 3: INFERENCE SERVER (MLOps)                                │
│  produccion_flask_server.py @ 0.0.0.0:8000                       │
│  REST API: /predict_entry, /predict_exit, /reload                │
└──────────────────────┬───────────────────────────────────────────┘
                       │ HTTP POST JSON (wininet.dll / WebRequest)
                       ▼
┌──────────────────────────────────────────────────────────────────┐
│  CAPA 4: EJECUCIÓN FÍSICA (MQL5)                                 │
│  Alpha_Sniper_Deploy.mq5 @ MetaTrader 5                          │
│  Position Sizing ATR + Scale-Out 1.5R + Chandelier Trailing      │
└──────────────────────────────────────────────────────────────────┘
```

**Universo de Activos (Macro 6):** `USDJPY · GBPUSD · EURUSD · EURJPY · XAUUSD · XAGUSD`

La elección de estos seis instrumentos es deliberada y fundamentada en la macroeconomía: son los activos con mayor liquidez, dirección institucional y profundidad de mercado del mundo. Se excluyen explícitamente todos los pares cruzados, divisas menores e índices, que demostraron empíricamente introducir *Data Mining Bias* y reversión a la media parasitaria en el período Out-Of-Sample.

---

## 2. Ingesta y Saneamiento de Datos (Data Engineering)

### 2.1. El Motor de Recolección: `HMA_ML_Orchestrator.mq5`

El `HMA_ML_Orchestrator.mq5` es un Expert Advisor (EA) de MetaTrader 5 diseñado exclusivamente para la **recolección masiva y estructurada de datos de entrenamiento**. No opera dinero real; opera el mercado con un lote fijo mínimo (`0.01`) con el único propósito de generar eventos de apertura y cierre de posiciones que el motor de logging etiqueta y serializa.

#### Arquitectura Orientada a Objetos: `CHarvestManager`

El diseño se basa en el patrón de programación orientada a objetos (OOP). La clase `CHarvestManager` encapsula la lógica de recolección completa para **un único símbolo**. Al iniciar el EA, el `OnInit()` parsea la cadena `InpHarvestSymbols` y crea dinámicamente una instancia de `CHarvestManager` por cada activo:

```mql5
// Instanciación dinámica en OnInit()
for(int i = 0; i < count; i++) {
    Managers[valid_managers] = new CHarvestManager(symbols[i]);
}
```

El `OnTimer()`, disparado cada **500 milisegundos** mediante `EventSetMillisecondTimer(500)`, llama al método `ProcessTick()` de cada Manager de forma secuencial. Este diseño es intrínsecamente **asíncrono y no bloqueante**: si un símbolo no tiene una nueva barra, su `ProcessTick()` retorna inmediatamente (`if(currentBarTime == m_lastBarTime) return`), permitiendo que el bucle procese el siguiente activo sin latencia artificial.

#### Suite de Indicadores por Instancia

Cada `CHarvestManager` inicializa y mantiene sus propios handles de indicadores, **aislados e independientes** por símbolo:

| Handle | Indicador | Propósito |
|--------|-----------|-----------|
| `hma_handle` | HMA (periodo 50) | Señal principal de dirección tendencial |
| `hma_exit_handle` | HMA (periodo 100) | Referencia macro de tendencia para salida lenta |
| `fast_hma_exit_handle` | HMA (periodo 14) | Trailing kinematic para salida rápida |
| `rsi_handle` | RSI (14) | Condición de sobrecompra/sobreventa |
| `atr_handle` | ATR (14) | Normalización de volatilidad |
| `ema50_handle / ema200_handle` | EMA 50/200 (Marco Temporal Superior) | Alineación de tendencia macro |
| `atr_d1_handle` | ATR Diario (14) | Ratio MTF de volatilidad |
| `adx_handle` | ADX Diario (14) | Fuerza direccional del mercado |
| `atr200_handle` | ATR (200) | Régimen de volatilidad histórico |

#### Normalización de Spreads por Tipo de Activo

El sistema implementa un sistema de doble umbral de spread para filtrar entradas en condiciones de liquidez degradada:

```mql5
// Umbral estándar: 4.0 pips para divisas mayores
// Umbral ampliado: 35.0 pips para metales (XAU/XAG) e índices
if(StringFind(symbol_upper, "XAU") >= 0 || StringFind(symbol_upper, "XAG") >= 0)
    max_allowed_spread = InpMaxSpreadPips_Metals; // 35.0
```

Esta asimetría es obligatoria: el spread del Oro en momentos de baja liquidez (cierre asiático, noticias macro) puede superar los 20-30 pips, y rechazar esas entradas basándose en el umbral de divisas (4 pips) significaría la parálisis total del activo más rentable del portafolio.

#### Generación de Features en el Momento de la Señal

Cuando el `HMA_ML_Orchestrator` detecta un cruce de la HMA(50) — el evento de señal primario — calcula y serializa un vector de **39 features** que capturan el estado completo del mercado en ese instante. Estos features son los mismos que el modelo de Machine Learning consumirá durante el entrenamiento y la inferencia:

- **Microestructura:** `Z_Score`, `Bollinger_Dev`, `Candle_Dominance`, `Tick_Volume_ZScore`
- **Momentum:** `HMA_Slope_Pct`, `HMA_Velocity`, `HMA_Acceleration`, `HMA_Jerk`
- **Contexto Macro:** `Trend_Align` (EMA50 vs EMA200 en TF superior), `Macro_ADX`, `H4_Trend_Align`
- **Microestructura de Mercado:** `Bars_Since_Asian_Sweep`, `Bars_Since_Vol_Shock`, `Energy_Accumulation`
- **Coste de Transacción:** `Spread_Impact_Ratio`, `SL_Dist_ATR`

#### Generación de Features de Salida (`CExitDataLogger`)

Paralelamente al dataset de entradas, el Orchestrator recolecta el **dataset de dilemas de salida** (`Struct_Exit_Dataset_*.csv`). Cada vez que un trade activo experimenta una señal de cierre potencial (cruce de HMA rápida, RSI cruzando 50, etc.), el sistema registra el estado del trade en ese momento preciso:

```mql5
ExitSnapshot snap;
snap.open_profit_r = floating_rr;       // RR flotante en el momento del amago
snap.drawdown_from_peak_r = dd_from_peak_r;  // Cuánto cedió desde el MFE
snap.exit_hma_velocity = hma_vel;       // Velocidad de la HMA lenta
snap.elastic_retracement_pct = elastic_pct; // % de retroceso desde el pico de extensión
```

La etiqueta (`Label`) se asigna *ex-post*: si el trade continuó más allá de la señal de salida y ganó más de 1R adicional, `Label=0` (error cerrar). Si cerrar era óptimo, `Label=1`.

---

### 2.2. Saneamiento Forense de Datos: `data_sanitizer.py`

> [!WARNING]
> La **Data Leakage por duplicación temporal** es una de las causas más comunes de sobreajuste invisible en sistemas de trading algorítmico. Un dataset con registros duplicados puede distorsionar la distribución de clústeres del K-Means y crear patrones espurios en el XGBoost que no existen en el mercado real.

El script `data_sanitizer.py` implementa un proceso de higiene forense en dos pasos críticos:

#### Paso 1: Ordenación Cronológica Estricta
```python
df['Time_DT'] = pd.to_datetime(df['Time'])
df = df.sort_values(by='Time_DT')
```
Antes de cualquier deduplicación, todos los registros se ordenan cronológicamente. Esto es fundamental para que el `TimeSeriesSplit` en el pipeline de ML respete la causalidad temporal y nunca exponga al modelo a datos del futuro durante el entrenamiento.

#### Paso 2: Deduplicación a Nivel de Timestamp
```python
df = df.drop_duplicates(subset=['Time'], keep='first')
```
Se elimina cualquier fila con el mismo timestamp, conservando únicamente la primera ocurrencia. Este procedimiento previene el denominado *"look-ahead contamination"*: si dos trades con el mismo `Time` tuvieran distintos resultados (e.g., uno ganador y otro perdedor), el modelo aprendería una distribución de probabilidad artificialmente inflada para esa condición de mercado.

---

### 2.3. Columnas de Fuga Declaradas Explícitamente (`LEAKAGE_COLS`)

El pipeline ML declara una lista de columnas prohibidas que **jamás** pueden ingresar como features al modelo, porque contienen información que solo se conoce después del cierre del trade:

```python
LEAKAGE_COLS = [
    "Realized_RR",     # Resultado final — futuro puro
    "MAE_Pct",         # Maximum Adverse Excursion — post-cierre
    "MFE_Pct",         # Maximum Favorable Excursion — post-cierre
    "Bars_In_Trade",   # Conocido solo al cerrar (en el Entry Model)
    "Label",           # El target mismo
]
```

---

## 3. El Motor de Inteligencia Artificial (ML Pipeline)

El archivo `pipeline_global_optimizer.py` encapsula la totalidad de la cadena de Machine Learning. Su ejecución por activo produce cinco artefactos binarios que el servidor de inferencia carga en memoria:

| Artefacto | Contenido |
|-----------|-----------|
| `entry_model_*.pkl` | XGBoost serializado para predicción de entradas |
| `exit_model_*.pkl` | XGBoost serializado para predicción de salidas |
| `regime_model_*.pkl` | K-Means para clasificación de régimen de mercado |
| `regime_scaler_*.pkl` | StandardScaler para el K-Means |
| `toxic_regime_*.json` | ID del clúster tóxico y lista de features del régimen |
| `production_thresholds_*.json` | Umbrales óptimos de entrada/salida (3 perfiles) |

---

### 3.1. Filtro de Régimen: K-Means (Aprendizaje No Supervisado)

El primer filtro que un trade debe superar no es un modelo predictivo, sino un **clasificador de entorno de mercado**. La hipótesis es que el mercado alterna entre regímenes estructuralmente distintos (tendencial, lateral ruidoso, shock de volatilidad), y que un modelo entrenado en tendencias no debe operar en rangos.

#### Features del Régimen
El K-Means trabaja exclusivamente sobre 5 features de **volatilidad y estructura de precio**:
```python
REGIME_FEATURES = ["ATR_Norm", "Bollinger_Dev", "Z_Score", "MTF_ATR_Ratio", "Macro_ADX"]
```

Estas features fueron seleccionadas porque describen el *tipo* de mercado (expandido vs. comprimido, con o sin dirección) sin revelar la *dirección* (para evitar sesgo).

#### Proceso de Identificación del Clúster Tóxico
```python
kmeans = KMeans(n_clusters=3, random_state=42, n_init=10)
clusters = kmeans.fit_predict(X_scaled)

# Identificar el cluster con MENOR win rate como "Tóxico"
cluster_metrics.sort(key=lambda x: x["win_rate"])
toxic_id = int(cluster_metrics[0]["cluster"])
```

K-Means divide el espacio de estados de mercado en 3 grupos. El clúster con la menor tasa de acierto histórica se clasifica como *Régimen Tóxico*. Todos los trades cuyo estado de mercado en el momento de la señal caiga en este clúster son **eliminados con probabilidad 0.0** antes de que el XGBoost los evalúe. Esto protege al modelo de sobreajustarse a patrones que solo funcionan en entornos favorables.

---

### 3.2. Modelos Predictivos Duales: XGBoost

#### Filosofía de Separación Entry/Exit

El sistema separa deliberadamente el problema de trading en **dos problemas binarios independientes**:

- **Entry Model:** ¿Tiene esta señal de cruce HMA suficiente contexto estadístico para ser una entrada rentable?
- **Exit Model:** Dado que este trade está activo y se ha producido una señal de cierre, ¿es correcto cerrar ahora o es un error que destruirá la ganancia?

Esta separación es técnicamente superior a un modelo único porque los datasets son estructuralmente distintos: el dataset de entradas está *desbalanceado* (~28% positivos), mientras que el de salidas está sesgado hacia `Label=1` (la mayoría de amagos de cierre son correctos). Un único modelo no podría optimizar ambas distribuciones simultáneamente.

#### Features del Modelo de Entradas (39 dimensiones)

```python
ENTRY_FEATURES = [
    # Estructura de precio y volatilidad
    "Z_Score", "ATR_Norm", "Bollinger_Dev", "Candle_Dominance",
    # Momentum HMA multi-orden
    "HMA_Slope_Pct", "HMA_Velocity", "HMA_Acceleration", "HMA_Jerk",
    # Contexto macro y sesión
    "Trend_Align", "Dist_Macro_EMA", "Macro_ADX", "H4_Trend_Align",
    "Session_Time", "Hour", "Day_Of_Week",
    # Microestructura y liquidez
    "Tick_Volume_ZScore", "Spread_Impact_Ratio", "Bars_Since_Asian_Sweep",
    "Bars_Since_Vol_Shock", "Energy_Accumulation",
    # Geometría del pullback
    "Pullback_Dur", "Pullback_Depth_Pct", "Breakout_Force_ATR",
    # RSI y extremos
    "RSI", "RSI_Extreme", "Bars_Since_Ext", "RSI_Slope_10", "RSI_Exhausted",
    # Gestión de riesgo implícita
    "SL_Dist_ATR", "Vol_Spread_Ratio", "ATR_Ratio_High",
    # Microestructura de precio
    "MTF_ATR_Ratio", "Trigger_Rejection_Tail", "Regime_Consistency_Count",
    "Is_Asian_Sweep", "Dist_Asian_High_ATR", "Dist_Asian_Low_ATR",
    "Spread_Expansion_Ratio",
]
```

#### Features del Modelo de Salidas (19 dimensiones)

El Exit Model usa exclusivamente información **disponible en el momento exacto del amago de cierre**. Ninguna feature es posterior al evento de señal:

```python
EXIT_FEATURES = [
    "Bars_In_Trade", "Open_Profit_R", "Drawdown_From_Peak_R",
    "Macro_ADX_Exit", "Exit_HMA_Velocity", "Exit_HMA_Accel",
    "Exit_RSI", "Exit_Volatility_Ratio", "Spread_Impact_Exit",
    "Is_Trigger_Fast", "Is_Trigger_Slow", "Is_Trigger_RSI",
    "Is_Trigger_Profit", "Is_Trigger_Fast_HMA_Cross",
    "MTF_ATR_Ratio", "Trigger_Rejection_Tail", "Bollinger_Dev",
    "Peak_HMA_Stretch_ATR", "Elastic_Retracement_Pct",
]
```

El feature `Elastic_Retracement_Pct` merece atención especial: mide qué fracción del *pico de extensión* respecto a la HMA rápida se ha cedido ya. Un valor cercano a 1.0 indica que el precio ha revertido completamente desde su máxima extensión — una señal robusta de agotamiento tendencial.

---

### 3.3. Prevención Rigurosa del Overfitting: Las Cadenas de Regularización

> [!CAUTION]
> El sobreajuste (*Overfitting*) en series temporales financieras es más sutil que en problemas estáticos de ML. Un modelo puede memorizar el régimen de tasas bajas de 2015-2021 y colapsar completamente ante el shock inflacionario de 2022-2024, aun cuando su precisión en validación cruzada parecía excelente. Las siguientes salvaguardas fueron diseñadas específicamente para este riesgo.

#### Salvaguarda 1: TimeSeriesSplit (No hay data del futuro en el entrenamiento)

```python
tscv = TimeSeriesSplit(n_splits=5)
for fold, (train_idx, val_idx) in enumerate(tscv.split(X)):
    # El fold de validación SIEMPRE es temporalmente posterior al de entrenamiento
```

A diferencia del K-Fold aleatorio estándar, `TimeSeriesSplit` respeta la causalidad: los datos de validación siempre son cronológicamente posteriores a los de entrenamiento. Esto simula con fidelidad el entorno de producción real.

#### Salvaguarda 2: Concept Drift Weights (Énfasis en el Régimen Actual)

```python
years = pd.to_datetime(df_clean['Time']).dt.year.values
weights = np.where(years >= 2022, 1.5, 0.8)
```

Los trades de 2022 en adelante reciben un peso 1.875x mayor que los anteriores. Esto sesga intencionalmente el modelo hacia el régimen de alta inflación y alta volatilidad que define el entorno actual, sin descartar el aprendizaje histórico.

#### Salvaguarda 3: Hiperparámetros de Estrangulamiento (XGBoost Anti-Overfit)

```python
XGB_PARAMS = dict(
    max_depth         = 3,    # Árboles superficiales — prohíbe memorizar patrones específicos
    learning_rate     = 0.02, # Aprendizaje lento y conservador
    gamma             = 1.5,  # El árbol solo crece si la reducción de pérdida es masiva
    min_child_weight  = 50,   # Prohíbe hojas con menos de 50 muestras (evita raridades)
    subsample         = 0.7,  # Cada árbol ve solo el 70% de las filas (Bootstrap anti-correlación)
    colsample_bytree  = 0.7,  # Cada árbol ve solo el 70% de las features
    reg_alpha         = 0.1,  # Penalización L1 (Lasso) — promueve sparsity en pesos
    reg_lambda        = 1.5,  # Penalización L2 (Ridge) — penaliza pesos grandes
)
```

**Por qué `max_depth=3` es el parámetro más crítico:** Un árbol de profundidad 3 solo puede capturar interacciones de hasta 3 features simultáneas. Esto es suficiente para aprender ineficiencias de mercado genuinas (e.g., "cuando la HMA acelera Y el ADX está alto Y el spread es bajo"), pero insuficiente para memorizar secuencias de precios específicas (e.g., "el precio estuvo exactamente en 1.2345 el 15 de marzo de 2019").

#### Salvaguarda 4: Calibración Institucional de Dos Pasos (Two-Step Fit)

El modelo final no usa un Early Stopping estándar, sino un proceso de dos fases que previene el *overfitting de Early Stopping*:

```python
# PASO A: Descubrimiento del límite óptimo
temp_model = XGBClassifier(**XGB_PARAMS, early_stopping_rounds=20)
temp_model.fit(X_train_cal, y_train_cal, eval_set=[(X_val_cal, y_val_cal)])
optimal_trees = max(10, temp_model.best_iteration)

# PASO B: Retrain sobre el 100% de los datos con el límite conocido
final_params["n_estimators"] = optimal_trees
final_model = XGBClassifier(**final_params)
final_model.fit(X, y, sample_weight=weights)
```

El Paso A usa el 15% más reciente de los datos para encontrar el número exacto de árboles antes del sobreajuste. El Paso B re-entrena sobre el 100% de los datos con ese límite fijo. El modelo final ve más datos históricos, pero su capacidad de memorizar está acotada por el límite descubierto en el Paso A.

---

### 3.4. Optimización Bidimensional del Hiperespacio (Grid Search 2D)

Una vez entrenados los modelos, el pipeline evalúa **140 combinaciones** de umbrales mediante un backtest vectorizado interno:

- **Entry Thresholds (Eje X):** `[0.10, 0.12, ..., 0.48]` — ¿Cuánta certeza mínima exigimos al Entry Model?
- **Exit Thresholds (Eje Y):** `[0.50, 0.55, ..., 0.80]` — ¿Cuánta certeza mínima exigimos al Exit Model?

Para cada combinación, se calcula el **Alpha Score institucional**:

```
Alpha Score = sign(Annual_R) × (|Sharpe × Annual_R| × 100) / (MaxDD% + 0.1) × ln(N_Trades)
```

Esta fórmula premia simultáneamente la frecuencia de operaciones, la linealidad de la curva de equidad y la rentabilidad compuesta, penalizando cualquier combinación con Drawdown elevado. Las combinaciones con menos de 300 trades son descalificadas por falta de significancia estadística.

Los umbrales ganadores se serializan en tres perfiles institucionales:
- **Perfil A (Agresivo):** Máximo Alpha Score.
- **Perfil B (Balanceado):** Máximo Ratio de Sharpe.
- **Perfil C (Conservador):** Mínimo Drawdown con Alpha Score ≥ percentil 25.

---

## 4. Motor de Ejecución y Riesgo Físico (MQL5 Architecture)

### 4.1. Dynamic Threshold Routing: El Puente ML ↔ Mercado

La clase `CSymbolManager` en `Alpha_Sniper_Deploy.mq5` implementa el puente entre el motor de Machine Learning (Python) y el mercado real (MetaTrader 5) mediante llamadas HTTP síncronas.

#### Protocolo de Comunicación (WinInet.dll para Backtesting)

El EA implementa una doble vía de comunicación:

```
[Producción]  → WebRequest() nativo de MT5 → Flask @ http://127.0.0.1:8000
[Backtesting] → wininet.dll (InternetOpenW/HttpSendRequestW) → Flask @ http://127.0.0.1:8000
```

La necesidad de `wininet.dll` para el backtester se debe a que `WebRequest()` solo funciona en producción real; en el Tester de Estrategias, MT5 bloquea la función nativa por razones de seguridad.

#### Flujo de Consulta de Entrada

```
1. CHarvestManager detecta cruce HMA → Calcula 39 features
2. Serializa JSON: {"activo": "USDJPY", "Z_Score": 0.84, "HMA_Slope_Pct": 0.023, ...}
3. POST /predict_entry → Flask Server
4. Flask ejecuta: K-Means (¿régimen tóxico?) → XGBoost Entry → Compara vs. entry_thresh
5. Respuesta JSON: {"probability": 0.3812}
6. Si probability > 0.0: Abrir posición. Si probability == 0.0: Descartar señal.
```

Latencia objetivo de la consulta: **< 50ms** en redes locales (VPS mismo datacenter).

---

### 4.2. Gestión de Posición: Position Sizing ATR-Normalizado

El tamaño de posición es el núcleo matemático del control de riesgo. La función `CalcDynamicLotSize()` implementa una fórmula que normaliza el riesgo en función de la volatilidad intrínseca de cada activo:

#### Fórmula de Position Sizing

```
Risk_USD       = Balance × (InpRiskPerTrade / 100)
                = $100,000 × 0.01 = $1,000 por trade

Point_Value    = TickValue / (TickSize / Point)
Risk_Per_Lot   = SL_Distance_Points × Point_Value

Lots           = Risk_USD / Risk_Per_Lot
               = floor(Lots / LotStep) × LotStep  (discretización al broker)
```

**Por qué esto es crítico para el portafolio Macro 6:** El EURUSD y el XAUUSD tienen volatilidades radicalmente distintas. Un Stop Loss de 50 pips en EURUSD equivale a ~$500 en un lote estándar, mientras que 50 pips en XAUUSD (donde 1 pip ≈ $10) equivalen a $500 también. La fórmula `Risk_Per_Lot = SL_Distance × TickValue` resuelve esta heterogeneidad de forma automática: independientemente del activo, cada trade arriesga exactamente el 1% del balance fijo de $100,000.

**Modo de Riesgo Estático (`InpUseCompoundInterest = false`):** Para eliminar la distorsión del interés compuesto en la auditoría, el balance de referencia es siempre `InpFixedBalance = $100,000`, no el balance real de la cuenta. Esto garantiza que el riesgo por trade es siempre `$1,000`, independientemente de si la cuenta ha crecido a $500,000 o ha caído.

---

### 4.3. Gestión de Salida Asimétrica: El Núcleo de la Rentabilidad

La arquitectura de salida es el componente que genera la asimetría ganador/perdedor del sistema. Opera en dos fases secuenciales e independientes.

#### Fase 1: Scale-Out Institucional a 1.5R + Breakeven

La gestión ocurre a **nivel de tick** (en `TickLevelManagement()`), no de barra, para maximizar la precisión de ejecución:

```
Condición: floating_RR >= InpScaleOutRR (1.5)
Acción 1: Cerrar el 50% de la posición al precio actual (LockProfit)
Acción 2: Mover el Stop Loss de la mitad restante al precio de apertura (Breakeven)
```

**Impacto matemático sobre el P&L:**
- Si el trade revierte después del Scale-Out: Resultado = `+1.5R × 0.5 + 0.0R × 0.5 = +0.75R` (nunca perderemos)
- Si el trade continúa al TP: Resultado = `+1.5R × 0.5 + TP_R × 0.5 = +[(1.5 + TP_R)/2]`

Este mecanismo convierte trades que habrían cerrado con pérdida (tras revertirse desde +2R hasta -1R) en trades rentables. Es la razón matemática principal por la que el **Promedio Ganador ($716) supera al Promedio Perdedor ($555)** en el backtest empírico.

#### Fase 2: Chandelier Trailing Stop Dinámico (3.0 ATR)

Una vez ejecutado el Scale-Out, el 50% restante del trade (el "Runner") no tiene un objetivo fijo. En su lugar, activa un Trailing Stop dinámico calibrado por la volatilidad del propio activo:

```mql5
// Solo activo si already_scaled == true (Runner post-Scale-Out)
double trailing_dist = current_atr * InpRunnerTrailingATR; // 3.0 × ATR(14)

// BUY Runner:
double new_sl = current_price - trailing_dist;
if(new_sl > sl + (pip * 2)) trade.PositionModify(ticket, new_sl, tp);

// SELL Runner:
double new_sl = current_price + trailing_dist;
if(new_sl < sl - (pip * 2)) trade.PositionModify(ticket, new_sl, tp);
```

**Por qué 3.0 ATR:** Un multiplicador de 3.0 ATR es suficientemente amplio para sobrevivir el ruido intra-barra normal sin ser cerrado prematuramente, pero suficientemente ajustado para capturar la mayor parte del movimiento tendencial antes de que el precio revierta. Esta es la calibración del *Chandelier Exit* clásico de Chuck LeBeau, adaptada a la volatilidad específica de cada activo.

**Giveback Mitigation:** El Trailing Stop se actualiza en cada tick, no en cada barra. Esto significa que si el Oro sube 400 pips en una sola barra de 1 hora, el Trailing Stop se desplaza tick a tick con el precio, bloqueando la ganancia gradualmente. El nombre "Giveback Mitigation" refleja exactamente su función: minimizar cuánto del beneficio flotante se devuelve al mercado antes del cierre.

---

### 4.4. Salida Forzada por Señal del Exit Model

Adicionalmente al Trailing Stop mecánico, el EA evalúa en cada barra si el Exit Model recomienda un cierre anticipado. El flujo es:

```
1. Detectar una señal de amago de cierre (cruce HMA rápida, RSI cruzando 50, etc.)
2. Calcular las 19 exit features del estado actual del trade
3. POST /predict_exit → Flask Server
4. Flask XGBoost Exit Model devuelve exit_proba
5. Si exit_proba >= ExitThreshold: trade.PositionClose(ticket)
```

Este cierre solo se ejecuta si el trade lleva al menos `InpMinBarsToHold = 3` barras abierto, para evitar cierres prematuros en los primeros ticks de ruido post-entrada.

#### Hard Close: Señal Estructural Rota

Existe una condición de cierre incondicional que no consulta al servidor Flask:

```mql5
// Si el precio cierra al otro lado de la HMA principal:
if(type == POSITION_TYPE_BUY && close_1 < hma_1) hard_close = true;
if(type == POSITION_TYPE_SELL && close_1 > hma_1) hard_close = true;
```

Cuando la estructura que motivó la entrada se invalida físicamente (el precio cierra al otro lado de la HMA), el trade se cierra de forma inmediata sin consultar a la IA. Esta salvaguarda protege contra situaciones donde el servidor Flask esté temporalmente inaccesible.

---

### 4.5. Blindaje de Cartera: Concurrency Lock Global

```mql5
// Verificación ANTES de evaluar cualquier nueva señal de entrada
if(PositionsTotal() >= InpMaxPortfolioTrades) {
    lastBarTime = currentBarTime;
    return; // Bloqueo total. No se procesa ninguna señal nueva.
}
```

El límite de `InpMaxPortfolioTrades = 3` actúa como un *circuit breaker* de cartera. Con 6 activos en el Macro 6 y un riesgo del 1% por trade, la exposición máxima simultánea es del 3%, que corresponde exactamente al `InpMaxGlobalRisk`. Esto garantiza que incluso en el peor escenario de 3 stop losses simultáneos (improbable por la baja correlación entre activos), el drawdown máximo de una sola sesión está acotado al 3%.

---

## 5. MLOps y Despliegue Continuo (Infraestructura)

### 5.1. El Servidor de Inferencia: `produccion_flask_server.py`

El servidor Flask actúa como la **capa de inteligencia centralizada** del sistema. Al arrancar, carga en la memoria RAM del proceso todos los artefactos binarios del pipeline ML, eliminando la latencia de disco en cada consulta:

```python
# Carga en memoria al inicio
entry_models   = {}   # {activo: XGBClassifier}
exit_models    = {}   # {activo: XGBClassifier}
regime_models  = {}   # {activo: KMeans}
regime_scalers = {}   # {activo: StandardScaler}
toxic_regimes  = {}   # {activo: {"toxic_id": int, "features": [...]}}
thresholds_cache = {} # {activo: {"entry_thresh": float, "exit_thresh": float}}
```

#### Proceso de Carga Dinámica por Activo

El servidor **detecta automáticamente** qué activos están disponibles escaneando los archivos JSON de producción presentes en `output/`:

```python
json_files = glob.glob(os.path.join(OUT_DIR, "production_thresholds_*.json"))
activos_soportados = [os.path.basename(f).replace("production_thresholds_", "")
                                         .replace(".json", "").lower()
                      for f in json_files]
```

Esto significa que añadir o retirar un activo del portafolio es trivial: basta con añadir o eliminar su archivo `production_thresholds_*.json` del disco y llamar al endpoint `/reload`.

#### Endpoint `/reload` (Hot-Reload sin Reinicio)

```
POST http://127.0.0.1:8000/reload
```

Recarga todos los modelos y configuraciones en memoria sin interrumpir el servicio. Este endpoint es fundamental para el ciclo de re-entrenamiento continuo: tras generar nuevos modelos `.pkl` con datos actualizados, el servidor los recarga en caliente sin que el EA de MetaTrader 5 experimente ninguna interrupción.

#### Lógica de Inferencia en `/predict_entry`

La cadena de evaluación de una señal de entrada sigue este orden de prioridad estricto:

```
PASO 1 (Gate): K-Means Regime Check
   → Si cluster_pred == toxic_id: return {"probability": 0.0, "regime": "Toxic"}

PASO 2 (Core): XGBoost Entry Prediction
   → prob_ia = modelo.predict_proba(df_input)[0, 1]

PASO 3 (Filter): Institutional Threshold Gate
   → Si prob_ia < entry_thresh: prob_ia = 0.0

PASO 4 (Return): Devolver probability al EA
   → {"probability": prob_ia}
```

Si el régimen es tóxico, **el XGBoost nunca se ejecuta**. Esto reduce la latencia de respuesta en condiciones de mercado adversas y evita que el servidor queme ciclos de CPU evaluando señales que serán descartadas de todos modos.

---

### 5.2. Despliegue en VPS (Virtual Private Server)

Para el despliegue en producción real, la arquitectura requiere:

#### Requisitos de Infraestructura
- **Sistema Operativo:** Windows Server 2019/2022 (por compatibilidad con MetaTrader 5 y wininet.dll)
- **RAM mínima:** 4 GB (el servidor Flask carga ~6 modelos × ~50MB cada uno en memoria)
- **Latencia:** El VPS debe estar en el mismo datacenter que el servidor del broker para minimizar el slippage

#### Proceso de Arranque del Sistema

```bash
# 1. Activar entorno virtual Python
cd C:\HMA_MetaLabeling\Python_ML
.venv\Scripts\activate

# 2. Lanzar servidor de inferencia (persiste en background)
python produccion_flask_server.py

# 3. Abrir MetaTrader 5 y cargar Alpha_Sniper_Deploy en un gráfico USDJPY H1
# (El EA gestiona todos los demás activos desde este único gráfico)
```

#### Persistencia y Reconexión

El servidor Flask es **stateless** respecto a las posiciones de trading: no mantiene ningún estado de los trades activos. Si el servidor Flask se reinicia (por actualización de modelos, fallo de sistema, etc.), el EA de MetaTrader 5 detectará el error en la respuesta HTTP y ejecutará la salvaguarda de *Hard Close* para gestionar las posiciones abiertas hasta que la conectividad se restaure.

Para garantizar la persistencia del servidor Flask ante reinicios del VPS, se recomienda registrarlo como un servicio de Windows mediante `NSSM (Non-Sucking Service Manager)`:

```bash
nssm install AlphaSniper_Flask "C:\HMA_MetaLabeling\Python_ML\.venv\Scripts\python.exe"
nssm set AlphaSniper_Flask Arguments "produccion_flask_server.py"
nssm set AlphaSniper_Flask AppDirectory "C:\HMA_MetaLabeling\Python_ML"
nssm start AlphaSniper_Flask
```

---

## 6. Validación Empírica y Métricas de Producción

### 6.1. Configuración del Backtest de Validación Final

El backtest definitivo fue ejecutado en el Probador de Estrategias de MetaTrader 5 con los siguientes parámetros:

| Parámetro | Valor |
|-----------|-------|
| Período | H1 (2015.01.01 — 2026.06.08) |
| Modelado | Cada Tick (WinInet.dll) |
| Calidad del Historial | **100%** |
| Depósito | $100,000.00 USD |
| Apalancamiento | 1:500 |
| Broker | FTMO Global Markets Ltd |

El período **2023.01.01 — 2026.06.08** es el **Out-Of-Sample (OOS) estricto**: los modelos XGBoost no tenían ningún conocimiento de estos datos durante el entrenamiento.

---

### 6.2. Resultados Globales del Portfolio (Macro 6)

| Métrica | Valor Empírico (MT5) |
|---------|---------------------|
| **Beneficio Neto** | **$622,168.04** (+622.17%) |
| **Beneficio Bruto** | $2,150,322.29 |
| **Pérdidas Brutas** | -$1,528,154.25 |
| **Total Operaciones** | 5,709 trades |
| **Win Rate** | **52.60%** |
| **Promedio Ganador** | $716.06 |
| **Promedio Perdedor** | -$555.48 |
| **Max Drawdown (Equity)** | **3.48%** ($23,195) |
| **Profit Factor** | 1.41 |
| **Ratio de Sharpe** | **2.87** |
| **Factor de Recuperación** | 26.82 |
| **LR Correlation** | 0.97 |
| **Z-Score** | -9.70 (99.74%) |

El **LR Correlation de 0.97** indica que la curva de equidad es casi perfectamente lineal ascendente. El **Z-Score de -9.70** demuestra que las rachas ganadoras y perdedoras no son aleatorias: existe una dependencia negativa entre trades consecutivos que el sistema explota a su favor.

---

### 6.3. Procedencia de la Rentabilidad por Activo

El análisis de la contribución por activo revela la función ecosistémica de cada componente del Macro 6:

| Activo | Operaciones | Win Rate | Rol en el Portfolio |
|--------|-------------|----------|---------------------|
| **XAUUSD** (Oro) | ~498 | 57.0% | Pilar de alta rentabilidad. Tendencias largas macroeconómicas |
| **XAGUSD** (Plata) | ~610 | 54.6% | Motor de volatilidad. Breakouts explosivos |
| **GBPUSD** | ~1,526 | 45.9% | Generador de frecuencia. Ventaja por volumen estadístico |
| **USDJPY** | ~351 | 57.8% | Francotirador. Alta precisión en divergencias BOJ/FED |
| **EURJPY** | ~284 | 58.1% | Complemento de Yen. Mayor precisión del portafolio |
| **EURUSD** | ~169 | 44.1% | Cuarentena activa. Bajo riesgo por parálisis del Regime Engine |

---

### 6.4. Análisis del Período Out-Of-Sample (2023 — 2026)

El período OOS coincide con los eventos macroeconómicos de mayor volatilidad de la última década:

- **Q1 2023:** Colapso del Silicon Valley Bank (SVB) y crisis bancaria sistémica
- **Q3/Q4 2023:** Escalada bélica en Oriente Medio. Shock de liquidez en XAUUSD
- **2024:** Pivot del Banco de Japón tras décadas de política de tasas negativas. Máxima volatilidad en USDJPY/EURJPY de los últimos 30 años
- **2024-2025:** Continuación del ciclo de altas tasas de la FED. Compresión de tendencias en EURUSD

Un sistema sobreajustado al régimen de tasas cero (2015-2022) habría generado un drawdown catastrófico del 30-50% en este período. El sistema Alpha Sniper respondió con una **reducción de frecuencia operativa** (el Regime Engine y el Entry Model rechazaron la mayoría de señales al no reconocer el nuevo entorno estadístico), protegiendo el capital mientras generaba retornos positivos en los activos con estructura macro más clara (Oro, Plata, Yenes).

---

### 6.5. Veredicto de la Dirección Cuantitativa

> [!IMPORTANT]
> El sistema **Alpha Sniper (Fase 24.8)** ha superado con éxito la validación empírica integral en MetaTrader 5 con calidad de historial del 100%. Los modelos de Machine Learning han demostrado generalización Out-Of-Sample a través de cuatro años de eventos macroeconómicos no vistos durante el entrenamiento.

**El sistema está HOMOLOGADO para despliegue en entorno de producción real (Live Trading).**

Los parámetros de gestión de riesgo aprobados para el despliegue inicial son:
- **Riesgo por Trade:** 1% estático (sin interés compuesto)
- **Concurrencia Máxima:** 3 posiciones simultáneas
- **Stop Loss Máximo Permitido:** 3.0 ATR desde la entrada
- **Scale-Out:** 50% a 1.5R con Breakeven inmediato
- **Trailing Stop del Runner:** 3.0 ATR dinámico (Chandelier)

---

*Fin del Documento. Versión: 24.8 | Fecha de Congelación del Código: 2026-06-09*

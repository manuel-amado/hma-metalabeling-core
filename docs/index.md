# M2 Quant Pipeline: Institutional Research Framework & Post-Mortem Blueprint

![Type](https://img.shields.io/badge/Type-Research_Framework-blue)
![Standard](https://img.shields.io/badge/Standard-Institutional_Quant-003b6f)
![Architecture](https://img.shields.io/badge/Architecture-Python%20%7C%20C%2B%2B%20%7C%20MQL5-blue)
![Validation](https://img.shields.io/badge/Validation-Purged_WFM-orange)
![Execution](https://img.shields.io/badge/Latency-Sub_Microsecond_C%2B%2B-success)
![Verdict](https://img.shields.io/badge/Verdict-Scientific_Falsification-red)

> **Veredicto Institucional:** Este repositorio documenta la investigación, falsación empírica y post-mortem cuantitativo de la estrategia de rupturas basada en la Media Móvil de Hull (HMA). Las evaluaciones empíricas de este pipeline demostraron que **las Medias Móviles sufren de Alpha Decay terminal y que el Meta-Labeling no puede rescatar un modelo primario sin ventaja estadística intrínseca**. Lejos de comercializar sistemas opacos o pretender desplegar portafolios comerciales automáticos, este repositorio se presenta como un **Research Framework & Blueprint Arquitectónico Educativo**, demostrando cómo desacoplar la investigación en Python del motor de ejecución C++ en MetaTrader 5 a latencia cero (<0.1 μs).

Aunque la estrategia HMA murió, **la infraestructura construida aquí sobrevivió**. Este repositorio es un plano maestro institucional (*Blueprint*) que demuestra cómo diseñar, validar, transpolar a C++ y auditar modelos de *Machine Learning* para MetaTrader 5 a latencia cero (<0.1 μs).

---

## Panel Resumen del Pipeline Cuantitativo

<div class="grid cards" markdown>

<div class="metric-card" markdown>
### Latencia de Inferencia C++
**< 0.1 µs (< 100 ns)**  
<span class="badge badge--success">Sub-Microsegundo</span>  
Transpilación AST a C++ nativo compilado en la memoria caché L1 de MetaTrader 5.
</div>

<div class="metric-card" markdown>
### Cobertura de Recall en M1
**Recall ≥ 0.85 (N > 3.000)**  
<span class="badge badge--info">Alto Recall</span>  
Sobre-operativa deliberada para nutrir al modelo secundario con población densa.
</div>

<div class="metric-card" markdown>
### Paridad de Microestructura
**EET (NY 5:00 PM Close)**  
<span class="badge badge--success">5 Velas Diarias</span>  
Eliminación de la vela espuria de domingo y sincronización de spreads de rollover.
</div>

<div class="metric-card" markdown>
### Validación Purged Walk-Forward
**Cero Fuga Temporal**  
<span class="badge badge--success">Purge & Embargo</span>  
Aislamiento absoluto de solapamiento de barreras y persistencia autorregresiva.
</div>

<div class="metric-card" markdown>
### Veredicto Científico Final
**AUC OOS = 0.518 (α = 0)**  
<span class="badge badge--danger">Market Beta Trap</span>  
Desmontaje empírico de la HMA: 100% Beta de mercado en Oro, cero Alpha genuino.
</div>

</div>

---

## Arquitectura Core (M2 Pipeline)

El framework desacopla el ciclo cuantitativo en cuatro capas interconectadas:

```mermaid
flowchart TD
    classDef stage fill:#0f172a,stroke:#3b82f6,stroke-width:2px,color:#f8fafc
    classDef data fill:#1e293b,stroke:#64748b,stroke-width:1px,color:#f8fafc
    classDef model fill:#1e1b4b,stroke:#818cf8,stroke-width:2px,color:#f8fafc
    classDef transpile fill:#042f2e,stroke:#14b8a6,stroke-width:2px,color:#f8fafc
    classDef vault fill:#064e3b,stroke:#10b981,stroke-width:2px,color:#f8fafc
    classDef fail fill:#450a0a,stroke:#ef4444,stroke-width:2px,color:#f8fafc

    A["MT5 Data Extractor<br/>Primary Model M1 (Alto Recall)"]:::stage -->|"CSV: Features + Deals (Huso EET)"| B["Python Ingestion Engine<br/>Triple Barrier Labeling"]:::stage
    B --> C{"Purged Walk-Forward CV<br/>Rolling XGBoost Retrain"}:::model
    C -->|"Data Leakage / Overfit"| E["Abort Pipeline & Veto Institucional"]:::fail
    C -->|"Sanity Checks Aprobados"| D["m2cgen AST Transpiler<br/>Árboles a C++ ANSI"]:::transpile
    D -->|"Export Headers .mqh"| F["C++ Oracle Headers<br/>Inferencia < 0.1 µs"]:::transpile
    F --> G["MT5 Canonical Blueprint<br/>Reference EA & C++ Oracle"]:::vault
```

---

## Crónica de Investigación en 4 Etapas

El ciclo de investigación se documenta en profundidad a lo largo de cuatro etapas cronológicas:

1.  **[Etapa 1: Hipótesis Cinemática HMA y Alto Recall en $M_1$](RESEARCH_JOURNAL.md#etapa-1-cinematica-de-la-hma-y-el-principio-de-alto-recall-en-meta-labeling):** Formulación de derivadas discretas (velocidad, aceleración y tirón) sobre la HMA de Alan Hull y la decisión anti-intuitiva de forzar sobre-operatividad en el modelo primario ($\text{Recall} \ge 0.85$) para nutrir con datos densos ($N > 3.000$) al modelo secundario.
2.  **[Etapa 2: Minería con StrategyQuant X y Sincronización Horaria](RESEARCH_JOURNAL.md#etapa-2-mineria-con-strategyquant-x-sincronizacion-horaria-gmt0eet-y-filtros-mtf):** Minería de alineaciones de cintas (*HMA Ribbons*), identificación de la trampa de huso horario GMT+0 vs EET (vela espuria de domingo y ensanchamiento de spreads en rollover) e inyección de 7 features continuas de régimen multitemporal (ADX H4, Keltner Bandwidth, ATR Ratio).
3.  **[Etapa 3: Transpilación a C++ a Latencia Cero (<0.1 μs)](RESEARCH_JOURNAL.md#etapa-3-transpilacion-a-c-a-latencia-cero-en-metatrader-5):** Eliminación de puentes REST y sockets en Python. Transpilación del grafo AST de XGBoost a cabeceras nativas C++/MQL5 (`M2_XGBoost_Oracle.mqh`) con evaluación sub-microsegundo protegida contra desbordamiento numérico (`MathExpSafe`).
4.  **[Etapa 4: Falsación Matemática Definitiva](RESEARCH_JOURNAL.md#etapa-4-falsacion-matematica-definitiva-alpha-decay-y-la-trampa-del-market-beta):** Validación cruzada Purged Walk-Forward Montecarlo que desmanteló la ilusión de rentabilidad, demostrando que el balance alcista era $100\%$ *Market Beta* en Oro ($AUC_{\text{OOS}} = 0.518$) y exponiendo el retardo insalvable frente a algoritmos HFT.

---

## Principios Cuantitativos Universales Transferibles

A partir de los hallazgos de este proyecto, se han formulado cinco principios universales transferibles a cualquier desarrollo algorítmico institucional en [Principios Cuantitativos Universales](UNIVERSAL_PRINCIPLES.md):

*   **Principio 1: Descomposición Rigurosa de Alpha vs. Market Beta:** Descomposición formal multifactorial ($R_{p} = \alpha + \beta R_{m} + \epsilon$), pruebas de simetría direccional y aplicación del *Deflated Sharpe Ratio* (DSR) para neutralizar el sesgo de selección en minería genética.
*   **Principio 2: Diseño del Tradeoff Precision/Recall en Meta-Labeling:** Por qué el modelo primario debe optimizar exhaustividad ($\text{Recall} \to 1.0$) aceptando ruido, mientras el modelo secundario optimiza la precisión calibrada en función del Valor Esperado ($EV$) y modula el dimensionamiento continuo (*Bet Sizing*).
*   **Principio 3: Protocolo Institucional de Auditoría Previa a Capital Real:** El checklist de 5 puertas de auditoría (Cero Fuga Temporal, Paridad Horaria EET, Purged CV con $AUC_{\text{OOS}} \ge 0.55$, Degradación IS/OOS $\le 30\%$ con Zona de Colapso ECN para $PF \le 1.15$, y Latencia Nativa $<1\ \mu\text{s}$) antes de asignar capital real.
*   **Principio 4: Desacoplamiento Estricto de Capas (MQL5 Ejecución vs. Python Investigación):** Delimitación infranqueable entre la bóveda de ejecución y telemetría OnTick (<0.1 µs) y el motor de análisis matemático y aprendizaje automático en Python.
*   **Principio 5: Preservación de Factoría y Mitigación del Sesgo de Sobre-Minería (*Data Snooping Bias*):** Protocolo para congelar arquetipos líderes validados y neutralizar la inflación artificial de métricas mediante la formulación de valores extremos y DSR.

---

## Mapa del Repositorio

El repositorio se organiza estrictamente en dos ecosistemas técnicos y una bóveda documental:

```text
HMA_MetaLabeling/
├── python/                         # Motor Estadístico y de Machine Learning (Python 3.11/3.12)
│   ├── main.py                     # Panel de control orquestador institucional (CLI / Headless)
│   └── m2_metalabeling/            # Paquete modular de investigación cuantitativa
│       ├── ingestion/              # Ingesta y saneamiento de datos MT5 (mt5_reader.py)
│       ├── labeling/               # Etiquetado Triple Barrera dinámico (triple_barrier.py)
│       ├── cross_validation/       # Purged K-Fold con Embargo temporal (purged_cv.py)
│       ├── calibration/            # Calibración isotónica y Bet Sizing continuo
│       ├── export/                 # Transpilador AST a C++/MQL5 nativo (to_mqh.py)
│       └── models/                 # Modelos Walk-Forward y auditoría cross-asset
├── mql5/                           # Ecosistema MetaTrader 5 (Blueprint Canónico de Referencia)
│   ├── Include/                    # Oráculo C++ transpilado (M2_XGBoost_Oracle.mqh)
│   └── Experts/                    # EA Canónico de Referencia y Extractor de Telemetría M1
├── docs/                           # Portal de Documentación Científica (MkDocs Material)
│   ├── index.md                    # Portada del portal
│   ├── METHODOLOGY.md              # Formulación matemática del framework M2
│   ├── RESEARCH_JOURNAL.md         # Crónica de investigación en 4 etapas
│   ├── UNIVERSAL_PRINCIPLES.md     # Cinco principios cuantitativos universales
│   ├── HISTORICAL_EVOLUTION.md     # Evolución histórica de prototipos algorítmicos
│   ├── POST_MORTEM.md              # Análisis forense y veredicto científico
│   └── assets/                     # Gráficas empíricas (WFM Equity, IS/OOS Robustness)
└── tests/                          # Suite integral de pruebas automatizadas (pytest)
```

---

## Guía de Trabajo: Flujo de Ejecución (Panel CLI)

Para orquestar el flujo de datos sin necesidad de invocar scripts individuales, el repositorio proporciona una consola CLI con soporte tanto interactivo como desatendido (*Headless*):

```bash
# Modo interactivo
python python/main.py

# Modo desatendido para pipelines CI/CD
python python/main.py --all --non-interactive
python python/main.py --step 1 --non-interactive
```

Al iniciarse en modo interactivo, se despliega el panel de control:

```text
============================================================
    M2 QUANT PIPELINE - INSTITUTIONAL CONTROL PANEL     
============================================================
 Basado en Marcos López de Prado (Advances in Financial ML)
 Framework de latencia cero para MetaTrader 5
============================================================

[ FLUJO DE EJECUCIÓN (WORKFLOW) ]
  1. Ingestar Datos y Aplicar Triple-Barrera (Meta-Labeling)
  2. Entrenar Modelos (Purged Walk-Forward Montecarlo)
  3. Auditoría Estricta contra Fuga de Datos (Sanity Check)
  4. Transpilar Oráculo a C++ (MQL5 0ms Latency)
  5. Auditoría Cross-Asset y Diagnóstico OOS
```

---

## Navegación del Portal Documental

*   **[Metodología Cuantitativa](METHODOLOGY.md):** Formulación matemática completa de la Triple Barrera, Purged CV con Embargo y transpilación C++.
*   **[Cuaderno de Investigación](RESEARCH_JOURNAL.md):** Crónica detallada de las 4 etapas del proyecto, desde la hipótesis cinemática hasta la falsación.
*   **[Principios Cuantitativos Universales](UNIVERSAL_PRINCIPLES.md):** Guía institucional transferible sobre descomposición de Alpha/Beta, Meta-Labeling y auditoría pre-live.
*   **[Evolución Histórica de Prototipos](HISTORICAL_EVOLUTION.md):** Recorrido por las versiones de asesores expertos, modelos ONNX y experimentos de RL.
*   **[Veredicto y Post-Mortem](POST_MORTEM.md):** Análisis forense de la defunción del Alpha de la HMA y el examen de microestructura HFT.

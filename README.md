# WS-Mavericks: Quantitative Meta-Labeling Framework

Marco de trabajo institucional para el desarrollo, validación y despliegue de sistemas de trading algorítmico de alta frecuencia y latencia cero. El repositorio integra algoritmos genéticos (StrategyQuant X) para el descubrimiento de anomalías de mercado (*Primary Models*), y modelos de Machine Learning (XGBoost) basados en el método de **Meta-Etiquetado** de Marcos López de Prado (*Secondary Models*) para la gestión dinámica de exposición.

---

## 🏛️ Estado Actual y Capacidades Core (V3 - Production Vaults)

El desarrollo actual se centra en la erradicación del ruido de mercado y la optimización de la Esperanza Matemática (EV) mediante pipelines de *Machine Learning* rigurosos y pruebas de estrés institucionales.

### 1. Descubrimiento Algorítmico Multitemporal (Primary Model)
- **Extracción de Señales:** Minería genética sobre datos de tick alineados con el huso horario del broker (UTC+2/EET) para garantizar congruencia absoluta en cierres de vela.
- **Convergencia H1/H4/D1:** Los modelos primarios de producción (`Strategy_XAUUSD_Production`) no evalúan el precio en el vacío; requieren alineación macroestructural mediante filtros de régimen en marcos temporales superiores (ej. `ADX H4 > 14`, Pivotes HMA Direccionales) y salidas dinámicas.

### 2. M2 Meta-Labeling Pipeline (Secondary Model)
La señal base pasa por un orquestador de ML en Python (`Model Factory`) diseñado para evitar la fuga de datos (*Data Leakage*):
- **Purged Walk-Forward Montecarlo (WFM):** El modelo no se valida en un solo split, sino mediante ventanas rodantes (*Rolling Windows*) que simulan el reentrenamiento continuo que tendría en producción, aplicando purga y embargo en cada ventana.
- **Filtros de Régimen Asimétricos:** Entrenamiento específico de oráculos XGBoost segmentados (ej. *Longs-Only*) cuando el análisis estadístico demuestra asimetrías severas en el mercado.
- **Auditorías de Fuga de Datos (Sanity Checks):** Scripts automatizados que verifican la ausencia de variables futuras antes de la generación del modelo C++.

### 3. Inferencia de Latencia Cero (C++ Transpilation)
El pipeline M2 exporta el modelo XGBoost optimizado (100 árboles de decisión) y lo transpila directamente a código nativo **C++ / MQL5** mediante `m2cgen`.
- **Artefacto:** `M2_XGBoost_Oracle_XAUUSD.mqh`
- **Impacto:** Ejecución en el servidor de MetaTrader en **0 milisegundos**, sin requerir llamadas a APIs externas ni Python. El oráculo dictamina el tamaño de posición y filtra *falsos positivos* en tiempo real.

---

## 📂 Arquitectura del Repositorio (SSOT)

El ecosistema mantiene una topología de **Single Source of Truth (SSOT)** utilizando *Directory Junctions* en Windows para mantener paridad en tiempo real entre MetaEditor y Git.

```text
WS-Mavericks/
├── mql5/
│   ├── Experts/HMA_SQX_Discovery/     # Production Vaults y Extractores Multi-Asset
│   ├── Include/M2_XGBoost_Oracle*.mqh # Oráculos XGBoost transpilados a C++ nativo
│   └── Indicators/                    # Dependencias nativas generadas por SQX
│
├── python/m2_metalabeling/            # Framework de Machine Learning Cuantitativo (M2)
│   ├── ingestion/                     # Parsers de series temporales (Multi-Asset)
│   ├── features/                      # Ingeniería de variables (Cinemática, ADX, Distancias)
│   ├── labeling/                      # Implementación de Triple Barrera
│   ├── cross_validation/              # Purged WFM & Embargo
│   ├── models/                        # Model Factory, Retraining y Sanity Checks
│   └── export/                        # Transpilador m2cgen (Python -> C++)
│
└── reports/figures/                   # Equity Curves (WFM), Precision-Recall y Data Leakage Audits
```

---

## 🔒 Control de Calidad y DevOps
- **Protección de Datos Masivos:** Los datasets tabulares crudos (`.csv`), y binarios pesados están rígidamente excluidos mediante `.gitignore`.
- **Continuous Integration (Local):** Los modelos exportados (ej. `M2_XGBoost_Oracle_XAUUSD.mqh`) se enlazan automáticamente a las carpetas `MQL5` de las instancias locales para pruebas inmediatas en el Strategy Tester.

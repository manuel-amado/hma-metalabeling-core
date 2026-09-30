# 🕵️ Análisis Arqueológico: Evolución del HMA Breakout

Este documento preserva la memoria técnica de las decenas de iteraciones y scripts desarrollados durante la fase **HMA Breakout** (versiones 3 a la 26). En lugar de mantener el repositorio inundado con código fuente obsoleto (*código en bruto*), hemos extraído las lecciones de diseño estructural de cada salto de versión.

---

## 🔬 Evolución de las Lógicas (De V3 a V26)

El análisis del directorio histórico de versiones revela una clara transición de reglas estáticas hacia una infraestructura cuantitativa automatizada:

### 1. La Era Manual (v3 - v10): `HMA_BOT.mq5` y `Alpha_Sniper.mq5`
*   **Lógica:** Basada estrictamente en código MQL5 tradicional. Se iteraban combinaciones de Periodos de HMA (Hull Moving Average) cruzando canales de volatilidad.
*   **Conclusión Estructural:** La optimización en MT5 era lenta e ineficiente. Las reglas estáticas eran frágiles y sufrían caídas drásticas cuando el régimen del mercado cambiaba (ej. de tendencia a consolidación).

### 2. La Era del Meta-Labeling Primitivo (v11 - v15)
*   **Archivos Clave:** `XGBoost_Model_v11...mqh` a `XGBoost_Model_v15_1...mqh`.
*   **Innovación:** El sistema dejó de tomar decisiones por sí mismo y se conectó a oráculos de Machine Learning (XGBoost). Se exportaban las condiciones del mercado y un script externo generaba árboles de decisión transpilados a C++ (`.mqh`).
*   **Fricción:** Se desarrollaban modelos específicos por temporalidad y par (ej. `AUDCAD_M15`, `USDJPY_M15`). El código base estaba extremadamente fragmentado y sobreajustado a pares individuales.

### 3. La Era de la Cosecha (Harvesting) y Multi-Asset (v16 - v19)
*   **Archivos Clave:** `Data_Extractor_EA.mq5`, `TestHarvest_Massive_Hybrid.mq5`.
*   **Innovación:** Se entendió que extraer datos en tiempo real mediante APIs (Python <-> MT5) introducía latencias inaceptables y errores de *sockets*. Se creó el modelo **TestHarvest**, el cual utilizaba el Modo Optimización de MetaTrader para extraer años de cinemática (OHLCV + Indicadores) a CSVs a máxima velocidad usando todos los núcleos del procesador.
*   **Impacto:** Permitió la construcción rápida de *datasets* inmensos para alimentar a XGBoost sin bloqueos de red.

### 4. La Era del Orquestador y Escáner (v20 - v26)
*   **Archivos Clave:** `HMA_ML_Orchestrator.mq5`, `HMA_Period_Scanner.mq5`.
*   **Innovación:** El código MQL5 se refactorizó para ser modular. En lugar de tener EAs independientes, un "Orquestador" central gestionaba el ciclo de vida del *trade* e integraba dinámicamente el modelo XGBoost correspondiente según el símbolo operado. Además, se integró el `v11_3_news_pipeline.md` (Filtro de Calendario Económico) para evadir picos de volatilidad programados.

---

## 🏛️ Conclusiones Estructurales para el Repositorio Actual

Gracias a las iteraciones observadas en el archivo histórico, la arquitectura moderna del pipeline M2 adoptó las siguientes decisiones irrefutables de diseño:

1.  **Código Modular, no Fragmentado:** Ya no existen 50 archivos `Alpha_Sniper_vX.mq5`. Se construyó un **Orquestador Central** (`Strategy_XAUUSD_Production.mq5`) y la inteligencia de "versiones" se delegó puramente a las actualizaciones del archivo `.mqh` de XGBoost.
2.  **Extracción Offline:** La ingesta de datos siempre debe hacerse con bots ciegos de "Harvesting" (`Pipeline_Extractor_M1.mq5`) utilizando el motor de optimización local de MT5. No se recomiendan puentes REST API en tiempo real.
3.  **Prevención de Basura (Code Bloat):** Mantener archivos obsoletos (`v12`, `v13`, `v14`) en la carpeta del IDE MetaEditor causa errores de compilación masivos, duplicidad de librerías y pérdida de foco. **Solución:** Una vez extraído su valor (documentado aquí), el código obsoleto se elimina de la base activa para asegurar limpieza institucional (0 ruido).

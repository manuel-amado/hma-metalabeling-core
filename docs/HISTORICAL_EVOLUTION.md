# Evolución de la Investigación: De Heurísticas a Machine Learning

Este documento traza el recorrido técnico y experimental del proyecto HMA. Su propósito es clarificar la transición desde las premisas heurísticas iniciales hasta la arquitectura cuantitativa final, detallando las lecciones aprendidas y cómo se abordaron los cuellos de botella técnicos.

---

## 1. La Era Heurística: Modelos MQL5 Estáticos

### Premisa Inicial
Se planteó la hipótesis de que la cinemática de la Media Móvil de Hull (HMA) —en particular sus puntos de inflexión (*V-Pivots*) y su aceleración— ofrecía una ventaja estadística predictiva (*Alpha*) para detectar rupturas de volatilidad e inicios de tendencia.

### Implementación y Experimentación
*   **Desarrollo Manual (`Alpha_Sniper.mq5`, `HMA_BOT.mq5`):** Implementación directa en MQL5 con combinaciones estáticas de periodos de HMA y canales de volatilidad (*Keltner Bandwidth*).
*   **Modelos de Salida Rígidos:** Los primeros prototipos dependían de Stop Loss y Take Profit fijos en puntos/pips. Se observó que la rigidez en las salidas destruía la esperanza matemática del sistema. Las iteraciones intermedias incorporaron trailing dinámico basado en la volatilidad instantánea (ATR) para evaluar la señal en condiciones estandarizadas.

### Conclusiones y Limitaciones
Las optimizaciones nativas en MetaTrader 5 resultaron altamente ineficientes y propensas al sobreajuste paramétrico. Las reglas heurísticas funcionaban exclusivamente en regímenes tendenciales definidos y colapsaban durante fases de consolidación.
*   **Decisión:** Abandonar la lógica de decisión basada en reglas fijas y delegar el filtrado de entradas a modelos probabilísticos supervisados (Machine Learning).

---

## 2. Transición al Meta-Labeling y Recolección Offline de Datos

### Premisa Inicial
Para que un clasificador supervisado (XGBoost) aprenda a discriminar entre señales válidas y falsas, requiere un volumen de datos masivo que contenga tanto éxitos como una variedad amplia de fallos de mercado.

### Implementación: El Principio del Alto Recall (Caos Controlado)
*   **Permisividad en el Modelo Primario:** Los bots en MQL5 se reconfiguraron deliberadamente para ser sumamente permisivos. El objetivo no era la rentabilidad de la señal primaria, sino maximizar la frecuencia de disparo (Alto *Recall*) para alimentar al clasificador secundario con un dataset denso.
*   **Etiquetado Triple Barrera:** Se implementó el etiquetado basado en barreras horizontales (Take Profit / Stop Loss dinámicos por ATR) y una barrera vertical temporal (*Timeout*), según la metodología de Marcos López de Prado.

### Cuello de Botella y Solución de Ingesta
El intento inicial de transmitir estados de mercado en tiempo real mediante APIs y sockets (Python <-> MT5) generó latencias inaceptables y fallos de sincronización.
*   **Decisión:** Migración a extracción *offline* (*Data Harvesting*). Se diseñó `Pipeline_Extractor_M1.mq5`, un bot colector que aprovecha el motor de optimización multiproceso de MetaTrader 5 para generar archivos CSV con cinemática multitemporal (H1, H4, D1) a máxima velocidad.

---

## 3. Exploración de Alternativas: Trend-Following, ONNX y Reinforcement Learning

Durante la fase intermedia de investigación se exploraron arquitecturas alternativas para evaluar si el problema radicaba en la naturaleza del *Breakout* o en el tipo de aprendizaje:

### Exploración Trend-Following y Modelos ONNX (`HMA_TF`)
Se formuló la hipótesis de que seguir tendencias macro reducía la tasa de falsos rompimientos. Se introdujeron filtros de acumulación (*buildup*) y restricciones de sobrecompra/sobreventa mediante RSI antes de evaluar la señal. Paralelamente, se experimentó con la exportación de modelos neuronales en formato ONNX (`.onnx`) para capturar asimetrías de distribución. Aunque mejoró la estabilidad en tendencias claras, persistía la vulnerabilidad a los cambios de régimen.

### Experimento de Aprendizaje por Refuerzo (`HMA_Omni`)
Se exploró el uso de Proximal Policy Optimization (PPO) con el objetivo de superar la rigidez del etiquetado binario y permitir al agente aprender una política de ejecución continua basada en la maximización de la curva de equity local.
*   **Conclusión:** Aunque conceptualmente elegante, el modelo PPO introdujo opacidad excesiva ("caja negra"), alta sensibilidad a la semilla aleatoria y dificultades insalvables para auditar la fuga de datos y el riesgo en producción. Se descartó en favor de modelos supervisados interpretables y auditables (XGBoost).

---

## 4. Minería Algorítmica con StrategyQuant X (SQX) y Filtros de Régimen

### Premisa Inicial
Dado que el modelo primario no requiere alta precisión sino un patrón base consistente, se recurrió a algoritmos genéticos y minería por fuerza bruta con StrategyQuant X para identificar estructuras de alineación (*HMA Ribbon*) más estables.

### Desafíos Técnicos Resueltos
*   **Alineación de Zona Horaria (GMT Offset):** Las estrategias minadas en SQX con histórico GMT+0 presentaban fricciones severas al ejecutarse en brokers MT5 (huso GMT+2/EET), provocando desajustes en las velas H1 y un rozamiento excesivo de spreads. La base de datos se reconstruyó íntegramente en huso EET para garantizar paridad absoluta.
*   **Inyección de Régimen Macro:** La versión inicial acumulaba miles de operaciones con bajo factor de beneficio por operar en cualquier contexto. Se introdujo una condición de régimen en temporalidad superior (ADX en H4 / D1). Posteriormente, en lugar de filtros condicionales frágiles en MQL5, esta restricción macro se vectorizó e inyectó directamente como variable en el espacio de decisión del clasificador.

---

## 5. Arquitectura de Producción y Protocolo de Auditoría (Pipeline M2)

La culminación técnica del repositorio resolvió los tres pilares de un despliegue cuantitativo:

1.  **Orquestador Modular en MT5:** Se eliminó la dispersión de asesores expertos individuales. Un único motor de ejecución (`Strategy_XAUUSD_Production.mq5`) gestiona la operativa y carga el oráculo C++.
2.  **Transpilación a C++ (0ms Latency):** Los árboles de decisión entrenados en Python se convierten a cabeceras nativas C++ (`.mqh`) mediante `m2cgen`. La inferencia se ejecuta en menos de 0.1 microsegundos, eliminando dependencias externas en tiempo de ejecución.
3.  **Auditoría Estricta contra Data Leakage:** Antes de aceptar cualquier oráculo, se audita que no exista *Lookahead Bias* (usar velas no cerradas), fuga por partición temporal (`shuffle=False` estricto) ni target leakage.
4.  **Validación Walk-Forward Montecarlo:** Se sustituyó el K-Fold clásico por ventanas rodantes con *Purging* y *Embargo*, simulando el paso secuencial a producción.

---

*Siguiente sección: Los resultados empíricos derivados de esta arquitectura final y las razones del rechazo estadístico de la estrategia se detallan en el [Veredicto y Post-Mortem](POST_MORTEM.md).*

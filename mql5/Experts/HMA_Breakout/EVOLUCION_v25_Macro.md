# Cambio de Paradigma: Filtro de Régimen Macro (v25)

## La Gran Conclusión
Al analizar los drawdowns históricos, se hizo evidente que operar Breakouts de HMA en mercados estancados o con ruido microscópico degradaba la métrica de Meta-Labeling. 

## Implementación
La versión **v25_MacroRegime** introduce el Filtro Sintético D1 y evalúa un umbral direccional estricto (ej. \DX > 25\). Este filtro macroscópico actúa como una compuerta: si la temporalidad superior no avala la fuerza tendencial, los micro-breakouts en temporalidades menores son vetados, independientemente de lo que opine el modelo ML local.


---
## 🔗 Conexiones Transversales
- [[Teoria - XGBoost y GT-Score|XGBoost y GT-Score]]
- [[Sistema - MQL5 Execution Engine|MQL5 Execution Engine]]

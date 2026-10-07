# Arquitectura Trend Following & ONNX (HMA_TF)

## Diferencia Filosófica
Mientras que la familia \HMA_BRK\ (Breakout) opera el cruce inmediato (momentum en corto plazo), la familia \HMA_TF\ asume que "la tendencia es tu amiga". 
El gatillo de entrada exige **alineación con la Macro EMA**.

## La Regla del Agotamiento
En lugar de depender exclusivamente de la aceleración, el \HMA_TF\ introduce filtros de "Buildup" (acumulación previa) y un filtro de agotamiento basado en RSI (\current_rsi < InpRSIMax\). Nunca compramos en sobrecompra, incluso si el modelo dice que es buena idea.

## Convergencia ONNX (v6)
A partir de la v6, el árbol de decisiones en \.mqh\ es sustituido por una Red Neuronal/Modelo Complejo \FatTail_Model.onnx\, evaluando distribuciones de cola gruesa para atrapar Cisnes Negros a favor de la tendencia.


---
## 🔗 Conexiones Transversales
- [[Sistema - MQL5 Execution Engine|MQL5 Execution Engine]]

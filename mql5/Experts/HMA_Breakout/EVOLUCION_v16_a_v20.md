# Evolución Arquitectónica: HMA Breakout (v16 a v20)

Esta familia de bots representa el core algorítmico original basado en Mean Reversion y aceleración sobre la Hull Moving Average (HMA).

## Cambios Principales (v16 -> v20)
1. **Modelado XGBoost (.mqh):** La v16 consolidó el uso de árboles de decisión inyectados nativamente en C++ para clasificar rupturas.
2. **Introducción WFO (v18):** Se descubrió que el mercado cambia de régimen constantemente, obligando a introducir la arquitectura Walk-Forward Optimization. 
3. **Salidas Dinámicas (v20):** La conclusión más importante de esta etapa fue que los Stop Loss estáticos arruinaban el expectancy. V20 implementa un trailing dinámico basado en la volatilidad instantánea (ATR), permitiendo capturar el edge predictivo de forma asilada usando lotaje fijo.


---
## 🔗 Conexiones Transversales
- [[Teoria - XGBoost y GT-Score|XGBoost y GT-Score]]
- [[Sistema - MQL5 Execution Engine|MQL5 Execution Engine]]

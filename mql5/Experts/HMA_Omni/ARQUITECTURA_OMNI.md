# Proyecto OMNI: Reinforcement Learning (PPO)

## El Problema del Etiquetado Estático
Los modelos XGBoost (Normal/Master) dependen de un meta-etiquetado binario histórico. Son ciegos a las consecuencias continuas de abrir o cerrar posiciones a la mitad del trayecto.

## La Solución Omni
La arquitectura OMNI reemplaza el aprendizaje supervisado por Reinforcement Learning (Proximal Policy Optimization - PPO). 
El bot \HMA_OMNI\ no predice "acierto/fallo", sino que maximiza una función de recompensa continua (Equity Curve, Ratio de Sharpe local). Converge los edges del Breakout y del TrendFollowing en un solo cerebro.

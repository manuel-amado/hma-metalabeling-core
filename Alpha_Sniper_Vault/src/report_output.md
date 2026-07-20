# 📊 Reporte de Rentabilidad del Portfolio (Fase 47: AI-Driven Exits)

**Condiciones de Simulación:**
- Riesgo por Operación: 1%
- Gestión de Salida: 100% controlada por la Inteligencia Artificial (Exit Model).
- Scale-Out: DESACTIVADO. Posición al 100% hasta la señal de salida.
- Break-Even: DESACTIVADO. Se permite el desarrollo íntegro del trade (Fat Tails).
- Umbrales de Entrada: USDJPY (0.10), EURJPY (0.48)
- Umbral de Salida ML: 0.55
- Modelos y Datasets: Tanda 4 OOS (`modelo_universal_*.pkl`)

## 📈 Desglose por Activo y Año

| Asset   |   Year |   Trades |   Total_R |   Compounded_% |   WinRate_% |
|:--------|-------:|---------:|----------:|---------------:|------------:|
| USDJPY  |   2015 |      195 |    -28.47 |         -25.69 |       32.31 |
| USDJPY  |   2016 |      188 |     15.06 |          13.62 |       32.98 |
| USDJPY  |   2017 |      172 |     26.86 |          26.43 |       37.79 |
| USDJPY  |   2018 |      175 |      5.4  |           4.22 |       40.57 |
| USDJPY  |   2019 |      192 |     46.04 |          54.45 |       39.58 |
| USDJPY  |   2020 |      106 |     18.79 |          18.71 |       33.96 |
| USDJPY  |   2021 |       57 |     -3.71 |          -3.94 |       33.33 |
| USDJPY  |   2022 |      166 |     17.8  |          17.71 |       34.94 |
| EURJPY  |   2015 |      184 |    -38.01 |         -32.78 |       29.35 |
| EURJPY  |   2016 |      183 |      7.4  |           6.37 |       36.07 |
| EURJPY  |   2017 |      203 |     38.37 |          43.59 |       44.33 |
| EURJPY  |   2018 |      193 |     -3.14 |          -4.15 |       33.68 |
| EURJPY  |   2019 |      176 |     -1.24 |          -2.72 |       35.23 |
| EURJPY  |   2020 |       87 |     -8.24 |          -8.3  |       33.33 |
| EURJPY  |   2021 |       61 |    -12.39 |         -11.91 |       29.51 |
| EURJPY  |   2022 |      165 |     36.64 |          40.22 |       37.58 |

## 🌐 Rentabilidad Agregada del Portfolio (Anual)

|   Year |   Total_Trades |   Total_R |   Compounded_% |
|-------:|---------------:|----------:|---------------:|
|   2015 |            379 |    -66.48 |         -50.05 |
|   2016 |            371 |     22.46 |          20.86 |
|   2017 |            375 |     65.23 |          81.54 |
|   2018 |            368 |      2.26 |          -0.11 |
|   2019 |            368 |     44.8  |          50.25 |
|   2020 |            193 |     10.55 |           8.86 |
|   2021 |            118 |    -16.1  |         -15.38 |
|   2022 |            331 |     54.44 |          65.05 |

**Total Trades (2015-2023):** 2503
**Total R Ganadas:** +117.16R
**Rentabilidad Total Compuesta (Global):** +150.09%

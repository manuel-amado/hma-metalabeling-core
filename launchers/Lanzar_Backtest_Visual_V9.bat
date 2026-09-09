@echo off
title ALPHA SNIPER V9.1 - BACKTEST VISUAL INSTITUCIONAL
echo ===============================================================================
echo   ALPHA SNIPER V9.1 - SIMULADOR VISUAL OOS (2020-2026)
echo ===============================================================================
echo  - Opcion seleccionada: OPCION 3 (Alta Eficiencia - Threshold 0.540)
echo  - Flota purgada:       XAUUSD, EURUSD, USDJPY, AUDUSD (4 Activos)
echo  - Parametros:          InpTrailingATR = 3.3 | InpMinBarsToHold = 5
echo  - Archivo SET:         C:\Users\Manuel\Desktop\HMA_MetaLabeling\Portafolio_Omega.set
echo  - Periodo OOS:         2020.01.01 hasta 2026.07.01
echo ===============================================================================
echo Iniciando MetaTrader 5 en Modo Backtest Visual...
start "" "C:\Program Files\MetaTrader 5\terminal64.exe" /config:"C:\Users\Manuel\Desktop\HMA_MetaLabeling\Visual_Backtest.ini"
echo MetaTrader 5 ha sido lanzado con la configuracion Visual_Backtest.ini.
pause

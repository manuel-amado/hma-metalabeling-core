@echo off
title ALPHA SNIPER V9.1 - DESPLIEGUE EN DIRECTO (EQUIPO LOCAL)
echo ===============================================================================
echo   ALPHA SNIPER V9.1 - PROTOCOLO DE DESPLIEGUE EN DIRECTO (LOCAL - NO VPS)
echo ===============================================================================
echo  - Opcion seleccionada: OPCION 3 (Alta Eficiencia - Threshold 0.540)
echo  - Flota purgada:       XAUUSD, EURUSD, USDJPY, AUDUSD (4 Activos)
echo  - Ejecutable EX5:      MQL5\Experts\Alpha_Sniper\Alpha_Sniper_v9.ex5
echo ===============================================================================
echo INSTRUCCIONES RAPIDAS DE ARRANQUE EN METATRADER 5:
echo 1. Verifica que el boton "Algorithmic Trading" (AutoTrading) este EN VERDE.
echo 2. Abre UN SOLO GRAFICO de XAUUSD en temporalidad M15.
echo 3. Arrastra "Alpha_Sniper_v9" desde el Navegador (Asesores Expertos) al grafico M15.
echo 4. En Parametros de Entrada, verifica que cargue la configuracion o selecciona:
echo    C:\Users\Manuel\Desktop\HMA_MetaLabeling\Portafolio_Omega.set
echo 5. Comprueba en la pestana "Expertos" (Caja de Herramientas) que aparezca:
echo    "PROTOCOLO V9.1: Flota 4 Activos Institucionales...".
echo ===============================================================================
echo Abriendo MetaTrader 5 en este equipo...
start "" "C:\Program Files\MetaTrader 5\terminal64.exe"
echo MetaTrader 5 ha sido abierto.
pause

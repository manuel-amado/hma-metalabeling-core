@echo off
color 0A
echo ==============================================================
echo       NEXUS PROTOCOL - VALIDACION OOS (OUT-OF-SAMPLE)
echo ==============================================================
echo Seleccione el bloque temporal OOS para ejecutar en modo visual:
echo.
echo [1] OOS Block 1: 2015 - 2017 (Regimen Lateral / Baja Volatilidad)
echo [2] OOS Block 2: 2018 - 2020 (Transicion y Rally Pre-Pandemia)
echo [3] OOS Block 3: Junio 2026 - Presente (Futuro Inmediato Post-Entrenamiento)
echo.
set /p option="Elija un bloque (1, 2 o 3): "

if "%option%"=="1" (
    set START_DATE=2015.01.01
    set END_DATE=2016.12.31
) else if "%option%"=="2" (
    set START_DATE=2018.01.01
    set END_DATE=2019.12.31
) else if "%option%"=="3" (
    set START_DATE=2026.06.01
    set END_DATE=2026.07.22
) else (
    echo Opcion invalida. Saliendo...
    pause
    exit
)

echo Generando configuracion para el periodo %START_DATE% a %END_DATE%...

echo [Tester] > "C:\Users\Manuel\Desktop\HMA_MetaLabeling\Project_Hull_Apex\visual_test.ini"
echo Expert=Project_Hull_Apex\Hull_Apex_Bot.ex5 >> "C:\Users\Manuel\Desktop\HMA_MetaLabeling\Project_Hull_Apex\visual_test.ini"
echo Symbol=XAUUSD >> "C:\Users\Manuel\Desktop\HMA_MetaLabeling\Project_Hull_Apex\visual_test.ini"
echo Period=M15 >> "C:\Users\Manuel\Desktop\HMA_MetaLabeling\Project_Hull_Apex\visual_test.ini"
echo Deposit=100000 >> "C:\Users\Manuel\Desktop\HMA_MetaLabeling\Project_Hull_Apex\visual_test.ini"
echo Currency=USD >> "C:\Users\Manuel\Desktop\HMA_MetaLabeling\Project_Hull_Apex\visual_test.ini"
echo Leverage=100 >> "C:\Users\Manuel\Desktop\HMA_MetaLabeling\Project_Hull_Apex\visual_test.ini"
echo Model=1 >> "C:\Users\Manuel\Desktop\HMA_MetaLabeling\Project_Hull_Apex\visual_test.ini"
echo ExecutionMode=0 >> "C:\Users\Manuel\Desktop\HMA_MetaLabeling\Project_Hull_Apex\visual_test.ini"
echo Optimization=0 >> "C:\Users\Manuel\Desktop\HMA_MetaLabeling\Project_Hull_Apex\visual_test.ini"
echo Visual=1 >> "C:\Users\Manuel\Desktop\HMA_MetaLabeling\Project_Hull_Apex\visual_test.ini"
echo FromDate=%START_DATE% >> "C:\Users\Manuel\Desktop\HMA_MetaLabeling\Project_Hull_Apex\visual_test.ini"
echo ToDate=%END_DATE% >> "C:\Users\Manuel\Desktop\HMA_MetaLabeling\Project_Hull_Apex\visual_test.ini"
echo Report=Report_Visual >> "C:\Users\Manuel\Desktop\HMA_MetaLabeling\Project_Hull_Apex\visual_test.ini"
echo ReplaceReport=1 >> "C:\Users\Manuel\Desktop\HMA_MetaLabeling\Project_Hull_Apex\visual_test.ini"
echo ShutdownTerminal=0 >> "C:\Users\Manuel\Desktop\HMA_MetaLabeling\Project_Hull_Apex\visual_test.ini"

echo Lanzando MetaTrader 5...
"C:\Program Files\MetaTrader 5\terminal64.exe" /config:"C:\Users\Manuel\Desktop\HMA_MetaLabeling\Project_Hull_Apex\visual_test.ini"

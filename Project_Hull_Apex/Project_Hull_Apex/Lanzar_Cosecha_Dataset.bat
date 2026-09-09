@echo off
color 0B
echo ==============================================================
echo       NEXUS PROTOCOL - COSECHA DE DATASET NORMALIZADO
echo ==============================================================
echo Iniciando MetaTrader 5 para recolectar el dataset de 2021 a 2026.
echo Por favor, pulse el boton "Start" en el probador de estrategias si no comienza automaticamente.
echo Asegurese de que la prueba termine para que el archivo CSV sea generado.
echo.

echo [Tester] > "C:\Users\Manuel\Desktop\HMA_MetaLabeling\Project_Hull_Apex\cosecha.ini"
echo Expert=Project_Hull_Apex\Hull_Apex_Bot.ex5 >> "C:\Users\Manuel\Desktop\HMA_MetaLabeling\Project_Hull_Apex\cosecha.ini"
echo Symbol=XAUUSD >> "C:\Users\Manuel\Desktop\HMA_MetaLabeling\Project_Hull_Apex\cosecha.ini"
echo Period=M15 >> "C:\Users\Manuel\Desktop\HMA_MetaLabeling\Project_Hull_Apex\cosecha.ini"
echo Deposit=100000 >> "C:\Users\Manuel\Desktop\HMA_MetaLabeling\Project_Hull_Apex\cosecha.ini"
echo Currency=USD >> "C:\Users\Manuel\Desktop\HMA_MetaLabeling\Project_Hull_Apex\cosecha.ini"
echo Leverage=100 >> "C:\Users\Manuel\Desktop\HMA_MetaLabeling\Project_Hull_Apex\cosecha.ini"
echo Model=1 >> "C:\Users\Manuel\Desktop\HMA_MetaLabeling\Project_Hull_Apex\cosecha.ini"
echo ExecutionMode=0 >> "C:\Users\Manuel\Desktop\HMA_MetaLabeling\Project_Hull_Apex\cosecha.ini"
echo Optimization=0 >> "C:\Users\Manuel\Desktop\HMA_MetaLabeling\Project_Hull_Apex\cosecha.ini"
echo Visual=0 >> "C:\Users\Manuel\Desktop\HMA_MetaLabeling\Project_Hull_Apex\cosecha.ini"
echo FromDate=2021.01.01 >> "C:\Users\Manuel\Desktop\HMA_MetaLabeling\Project_Hull_Apex\cosecha.ini"
echo ToDate=2026.07.01 >> "C:\Users\Manuel\Desktop\HMA_MetaLabeling\Project_Hull_Apex\cosecha.ini"
echo ReplaceReport=1 >> "C:\Users\Manuel\Desktop\HMA_MetaLabeling\Project_Hull_Apex\cosecha.ini"
echo ShutdownTerminal=0 >> "C:\Users\Manuel\Desktop\HMA_MetaLabeling\Project_Hull_Apex\cosecha.ini"
echo. >> "C:\Users\Manuel\Desktop\HMA_MetaLabeling\Project_Hull_Apex\cosecha.ini"
echo [TesterInputs] >> "C:\Users\Manuel\Desktop\HMA_MetaLabeling\Project_Hull_Apex\cosecha.ini"
echo InpDataHarvesting=1 >> "C:\Users\Manuel\Desktop\HMA_MetaLabeling\Project_Hull_Apex\cosecha.ini"
echo InpMetaLabeling=0 >> "C:\Users\Manuel\Desktop\HMA_MetaLabeling\Project_Hull_Apex\cosecha.ini"

"C:\Program Files\MetaTrader 5\terminal64.exe" /config:"C:\Users\Manuel\Desktop\HMA_MetaLabeling\Project_Hull_Apex\cosecha.ini"

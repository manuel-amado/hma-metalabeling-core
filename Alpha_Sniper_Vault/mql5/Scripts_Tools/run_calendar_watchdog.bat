@echo off
REM ============================================================================
REM run_calendar_watchdog.bat - Sincronización Autónoma del Calendario Macro
REM ============================================================================
echo [INFO] Ejecutando Pipeline 100% Autonomo de Calendario (API + Cache + Resiliencia)...
"C:\Users\Manuel\AppData\Local\Programs\Python\Python311\python.exe" "%~dp0update_news_calendar.py"
echo.
echo [SUCCESS] Proceso completado. Puede cerrar esta ventana.
pause

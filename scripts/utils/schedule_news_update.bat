@echo off
REM ============================================================================
REM schedule_news_update.bat - Tarea Automática de Windows Task Scheduler
REM Programación diaria a las 08:00 AM para sincronizar cualquier CSV descargado
REM de FXStreet en la carpeta Downloads y enviarlo limpio a MetaTrader 5.
REM ============================================================================

echo [INFO] Registrando Tarea Automática en el Programador de Tareas de Windows...
schtasks /create /tn "AlphaSniper_NewsCalendarSync" /tr "\"C:\Users\Manuel\AppData\Local\Programs\Python\Python311\python.exe\" \"C:\Users\Manuel\Desktop\HMA_MetaLabeling\scripts\utils\auto_sync_calendar.py\"" /sc daily /st 08:00 /f

if %ERRORLEVEL% EQU 0 (
    echo [SUCCESS] Tarea 'AlphaSniper_NewsCalendarSync' programada exitosamente para ejecutarse DIARIAMENTE a las 08:00 AM.
) else (
    echo [ERROR] No se pudo registrar la tarea. Ejecute como Administrador si es necesario.
)
pause

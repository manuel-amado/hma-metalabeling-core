import os
import time
import subprocess
import sys

# Paths to monitor
audit_file = r"C:\Users\Manuel\Desktop\HMA_MetaLabeling\Alpha_Sniper_Vault\api\python_received_audit.txt"

def get_process_cpu_usage(process_name="metatester64"):
    try:
        # Use powershell to get CPU of metatester64
        cmd = f'Get-Process -Name "{process_name}" -ErrorAction SilentlyContinue | Select-Object -ExpandProperty CPU'
        res = subprocess.run(["powershell", "-Command", cmd], capture_output=True, text=True)
        output = res.stdout.strip()
        if output:
            # CPU is cumulative CPU time in seconds.
            return float(output.split()[0].replace(',', '.'))
    except Exception:
        pass
    return None

def is_process_running(process_name="metatester64"):
    try:
        cmd = f'Get-Process -Name "{process_name}" -ErrorAction SilentlyContinue'
        res = subprocess.run(["powershell", "-Command", cmd], capture_output=True, text=True)
        return len(res.stdout.strip()) > 0
    except Exception:
        return False

print("=" * 80)
print("  MONITOR DE APAGADO AUTOMÁTICO POST-BACKTEST (Fase 30)")
print("=" * 80)
print(f"Monitoreando archivo de auditoría: {audit_file}")
print("Esperando a que el backtest comience a enviar predicciones...")

# Validar que el archivo exista o esperar
while not os.path.exists(audit_file):
    print("[INFO] Esperando a que se cree el archivo de auditoría...")
    time.sleep(5)

last_size = os.path.getsize(audit_file)
print(f"Tamaño inicial del log: {last_size} bytes.")

print("Comenzando bucle de detección de inicio...")
backtest_started = False
inactivity_counter = 0
check_interval = 10  # segundos
timeout_threshold = 90  # 90 segundos de inactividad total

last_cpu_time = None

while True:
    time.sleep(check_interval)
    
    # Check audit file modification
    current_size = os.path.getsize(audit_file) if os.path.exists(audit_file) else 0
    file_changed = (current_size > last_size)
    last_size = current_size
    
    # Check metatester64 activity
    running = is_process_running("metatester64")
    cpu_time = get_process_cpu_usage("metatester64")
    
    cpu_active = False
    if running and cpu_time is not None:
        if last_cpu_time is not None:
            # Si el tiempo acumulado de CPU se incrementó en el intervalo
            if cpu_time > last_cpu_time + 0.1:
                cpu_active = True
        last_cpu_time = cpu_time
    
    # Lógica de inicio del backtest
    if not backtest_started:
        if file_changed or cpu_active:
            backtest_started = True
            print("\n" + "*"*80)
            print("[INFO] ¡Actividad detectada! El backtest está en marcha. Iniciando monitoreo de finalización...")
            print("*"*80 + "\n")
        else:
            print("[INFO] Esperando inicio del backtest (sin cambios detectados)...")
            continue

    # Lógica de finalización
    print(f"[MONITOR] Tamaño Log: {current_size} bytes (Cambió: {file_changed}) | metatester64 activo: {running} (CPU Activo: {cpu_active})")
    
    if not file_changed and not cpu_active:
        inactivity_counter += check_interval
        remaining = timeout_threshold - inactivity_counter
        print(f"  --> ALERTA: Inactividad detectada. Apagado en {remaining} segundos si no hay cambios...")
    else:
        if inactivity_counter > 0:
            print("  --> Actividad reanudada. Reiniciando temporizador de apagado.")
        inactivity_counter = 0
        
    if inactivity_counter >= timeout_threshold:
        print("\n" + "!"*80)
        print("  BACKTEST COMPLETADO: INACTIVIDAD PROLONGADA DETECTADA.")
        print("  Apagando el equipo de forma segura en 15 segundos...")
        print("!"*80 + "\n")
        
        # Ejecutar apagado de Windows
        # /s = apagar, /f = forzar cierre de aplicaciones, /t 15 = 15s de espera
        subprocess.run(["shutdown", "/s", "/f", "/t", "15"])
        break

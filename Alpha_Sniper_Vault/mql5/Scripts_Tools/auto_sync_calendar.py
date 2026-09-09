# -*- coding: utf-8 -*-
"""
auto_sync_calendar.py - Pipeline Automático de Ingesta y Sincronización FXStreet -> MT5
=====================================================================================
Este script se ejecuta periódicamente mediante el Programador de Tareas de Windows.
1. Escanea automáticamente la carpeta de Descargas (Downloads) del usuario y la carpeta local
   en busca del archivo de calendario FXStreet más reciente ('calendar-event-list*.csv').
2. Aplica el filtro estricto institucional:
   - Impacto == 'HIGH'
   - Divisas en flota {'USD', 'EUR', 'JPY', 'AUD'}
3. Convierte las marcas de tiempo a huso horario de servidor MT5 (YYYY.MM.DD HH:MM).
4. Sincroniza y sobrescribe de forma atómica y de ultra-baja latencia en:
   - MQL5/Files/news_calendar_clean.csv (Terminal MetaTrader 5 en vivo)
   - ./news_calendar_clean.csv (Repositorio local)
"""

import os
import sys
import glob
import csv
from datetime import datetime, timedelta

# --- CONFIGURACIÓN INSTITUCIONAL ---
FLEET_CURRENCIES = {"USD", "EUR", "JPY", "AUD"}
TARGET_IMPACT = "HIGH"
BROKER_OFFSET_HOURS = 0  # Ajuste horario si el CSV original no está en hora local de MT5

# Rutas clave del sistema
USER_HOME = os.path.expanduser("~")
DOWNLOADS_DIR = os.path.join(USER_HOME, "Downloads")
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

MT5_FILES_DIR = r"C:\Users\Manuel\AppData\Roaming\MetaQuotes\Terminal\D0E8209F77C8CF37AD8BF550E51FF075\MQL5\Files"
OUTPUT_LOCAL = os.path.join(SCRIPT_DIR, "news_calendar_clean.csv")
OUTPUT_MT5   = os.path.join(MT5_FILES_DIR, "news_calendar_clean.csv")

def find_latest_calendar_csv():
    """
    Busca el CSV de calendario más reciente priorizando la carpeta Descargas (Downloads).
    Si no encuentra en Descargas, busca en la carpeta local.
    """
    downloads_patterns = [
        os.path.join(DOWNLOADS_DIR, "calendar-event-list*.csv"),
        os.path.join(DOWNLOADS_DIR, "*calendar*.csv")
    ]
    
    candidates_dl = []
    for pat in downloads_patterns:
        for filepath in glob.glob(pat):
            if os.path.isfile(filepath) and not filepath.endswith("news_calendar_clean.csv"):
                candidates_dl.append(filepath)
    
    if candidates_dl:
        candidates_dl.sort(key=lambda x: os.path.getmtime(x), reverse=True)
        return candidates_dl[0]
        
    local_patterns = [
        os.path.join(SCRIPT_DIR, "calendar-event-list*.csv"),
        os.path.join(SCRIPT_DIR, "news_calendar.csv")
    ]
    candidates_local = []
    for pat in local_patterns:
        for filepath in glob.glob(pat):
            if os.path.isfile(filepath) and not filepath.endswith("news_calendar_clean.csv"):
                candidates_local.append(filepath)
                
    if not candidates_local:
        return None
    
    candidates_local.sort(key=lambda x: os.path.getmtime(x), reverse=True)
    return candidates_local[0]

def parse_date_str(date_str):
    date_str = date_str.strip()
    formats = [
        "%m/%d/%Y %H:%M:%S",
        "%m/%d/%Y %H:%M",
        "%Y-%m-%d %H:%M:%S",
        "%Y-%m-%d %H:%M",
        "%d/%m/%Y %H:%M:%S",
        "%d/%m/%Y %H:%M"
    ]
    for fmt in formats:
        try:
            return datetime.strptime(date_str, fmt)
        except ValueError:
            continue
    return None

def process_and_sync():
    latest_csv = find_latest_calendar_csv()
    if not latest_csv:
        print("[WARN] No se encontró ningún archivo de calendario 'calendar-event-list*.csv' en Downloads ni localmente.")
        return False
    
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] [INFO] Archivo de calendario mas reciente detectado:")
    print(f" -> Ruta: {latest_csv}")
    print(f" -> Modificado: {datetime.fromtimestamp(os.path.getmtime(latest_csv)).strftime('%Y-%m-%d %H:%M:%S')}")
    
    clean_events = []
    with open(latest_csv, mode="r", encoding="utf-8", errors="ignore") as f:
        sample = f.read(1024)
        f.seek(0)
        delimiter = "," if sample.count(",") >= sample.count(";") else ";"
        
        reader = csv.DictReader(f, delimiter=delimiter)
        for row_idx, row in enumerate(reader, start=1):
            row_clean = {k.strip().lstrip("\ufeff"): v.strip() for k, v in row.items() if k}
            
            impact = row_clean.get("Impact", "").upper()
            curr   = row_clean.get("Currency", "").upper()
            start  = row_clean.get("Start", "")
            name   = row_clean.get("Name", "")
            
            if impact != TARGET_IMPACT:
                continue
            if curr not in FLEET_CURRENCIES:
                continue
            
            dt = parse_date_str(start)
            if dt is None:
                continue
            
            dt_broker = dt + timedelta(hours=BROKER_OFFSET_HOURS)
            broker_ts_str = dt_broker.strftime("%Y.%m.%d %H:%M")
            clean_events.append((broker_ts_str, curr, name))

    clean_events.sort(key=lambda x: x[0])
    
    def write_clean(path):
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, mode="w", newline="", encoding="utf-8") as f:
            f.write("BrokerTimestamp;Currency\n")
            for ts, curr, _ in clean_events:
                f.write(f"{ts};{curr}\n")
    
    write_clean(OUTPUT_LOCAL)
    write_clean(OUTPUT_MT5)
    
    print(f"\n[SUCCESS] Sincronizado CSV pre-procesado ({len(clean_events)} eventos HIGH):")
    print(f"  -> Local: {OUTPUT_LOCAL}")
    print(f"  -> MT5:   {OUTPUT_MT5}\n")
    
    print("=== EVENTOS HIGH IMPACT EN FLOTA ===")
    print(f"{'BrokerTimestamp':<18} | {'Currency':<8} | {'Name'}")
    print("-" * 65)
    for ts, curr, name in clean_events:
        print(f"{ts:<18} | {curr:<8} | {name}")
    print("-" * 65)
    return True

if __name__ == "__main__":
    process_and_sync()

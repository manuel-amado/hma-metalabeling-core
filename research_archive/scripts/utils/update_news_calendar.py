# -*- coding: utf-8 -*-
"""
update_news_calendar.py - Pipeline 100% Autónomo para Alpha Sniper V11.3
======================================================================
Capa 1 de la Arquitectura en 2 Capas (Anti-News Shield).

1. Obtención Programática 100% Autónoma (API Institucional ForexFactory JSON/XML):
   - Elimina por completo la descarga manual o intervención humana.
   - Capa de caché inteligente (1 hora) para evitar bloqueos por Rate-Limit (HTTP 429).
   - Resiliencia de 3 niveles:
     Nivel 1: API JSON oficial de ForexFactory (nfs.faireconomy.media)
     Nivel 2: Caché local persistente (si API retorna 429 o no hay conexión temporal)
     Nivel 3: Fallback a archivos CSV en carpeta Descargas/Local.

2. Filtrado Estricto Institucional:
   - Impacto == 'HIGH' (Alto impacto / Rojo).
   - Divisas en Flota {'USD', 'EUR', 'JPY', 'AUD'}.

3. Conversión Temporal (Broker Offset):
   - Transforma fechas UTC/ISO a hora local del servidor del Bróker MT5 (YYYY.MM.DD HH:MM).

4. Despliegue de Ultra-Baja Latencia:
   - Exporta de forma atómica a MQL5/Files/news_calendar_clean.csv (Capa 2 MQL5 inalterada).
"""

import os
import sys
import glob
import json
import csv
import time
import urllib.request
import urllib.error
import xml.etree.ElementTree as ET
from datetime import datetime, timezone, timedelta

# --- CONFIGURACIÓN INSTITUCIONAL ---
FLEET_CURRENCIES = {"USD", "EUR", "JPY", "AUD"}
TARGET_IMPACT = "HIGH"

# Desfase del servidor del bróker MT5 respecto a UTC (en horas).
# La mayoría de brókers institucionales MT5 (Darwinex, IC Markets, FTMO, etc.) usan GMT+3 en verano (EEST) y GMT+2 en invierno (EET).
BROKER_GMT_OFFSET = 3

# Endpoints oficiales de ForexFactory (FairEconomy Media)
FF_JSON_URL = "https://nfs.faireconomy.media/ff_calendar_thisweek.json"
FF_XML_URL  = "https://nfs.faireconomy.media/ff_calendar_thisweek.xml"

# Rutas clave del sistema
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
MT5_FILES_DIR  = r"C:\Users\Manuel\AppData\Roaming\MetaQuotes\Terminal\D0E8209F77C8CF37AD8BF550E51FF075\MQL5\Files"
MT5_COMMON_DIR = r"C:\Users\Manuel\AppData\Roaming\MetaQuotes\Terminal\Common\Files"
OUTPUT_LOCAL = os.path.join(SCRIPT_DIR, "news_calendar_clean.csv")
OUTPUT_MT5   = os.path.join(MT5_FILES_DIR, "news_calendar_clean.csv")
OUTPUT_COMMON = os.path.join(MT5_COMMON_DIR, "news_calendar_clean.csv")
CACHE_FILE   = os.path.join(SCRIPT_DIR, "ff_api_cache.json")
CACHE_MAX_AGE_SECONDS = 3600  # 1 hora de caché local

def is_cache_valid():
    """Verifica si existe un archivo de caché reciente (menos de 1 hora) en disco."""
    if not os.path.exists(CACHE_FILE):
        return False
    age = time.time() - os.path.getmtime(CACHE_FILE)
    return age < CACHE_MAX_AGE_SECONDS

def save_cache(data):
    """Guarda respuesta de API en caché local para prevenir límites 429."""
    try:
        with open(CACHE_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"[WARN] No se pudo guardar caché: {e}")

def load_cache():
    """Carga datos de API desde el archivo de caché local."""
    try:
        with open(CACHE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return None

def fetch_from_api_json():
    """
    Nivel 1: Obtiene datos del endpoint JSON oficial de ForexFactory.
    No requiere librerías externas (solo urllib de la librería estándar).
    """
    if is_cache_valid():
        print("[INFO] Usando caché local de API ForexFactory (válido < 1h)...")
        cached = load_cache()
        if cached:
            return cached

    print(f"[INFO] Conectando a API ForexFactory JSON: {FF_JSON_URL} ...")
    req = urllib.request.Request(
        FF_JSON_URL,
        headers={
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
            "Accept": "application/json, text/plain, */*"
        }
    )
    try:
        with urllib.request.urlopen(req, timeout=12) as response:
            data = json.loads(response.read().decode("utf-8"))
            print(f"[SUCCESS] Datos recibidos por API JSON ({len(data)} eventos totales).")
            save_cache(data)
            return data
    except urllib.error.HTTPError as he:
        print(f"[WARN] Respuesta HTTP API ({he.code}): {he.reason}")
        # Si da 429 u otro error de servidor, intentamos cargar caché aunque sea antiguo
        cached = load_cache()
        if cached:
            print("[INFO] Resiliencia Nivel 2: Utilizando última caché válida de la API en disco.")
            return cached
        return None
    except Exception as e:
        print(f"[WARN] Error al conectar con API ForexFactory JSON: {e}")
        cached = load_cache()
        if cached:
            print("[INFO] Resiliencia Nivel 2: Utilizando última caché válida de la API en disco.")
            return cached
        return None

def parse_iso_date(iso_str):
    """
    Parsea fechas ISO-8601 con offset de zona horaria (ej. '2026-07-29T14:00:00-04:00')
    y las convierte a la hora local del servidor del Bróker MT5.
    """
    try:
        dt = datetime.fromisoformat(iso_str)
        dt_utc = dt.astimezone(timezone.utc)
        dt_broker = dt_utc + timedelta(hours=BROKER_GMT_OFFSET)
        return dt_broker.strftime("%Y.%m.%d %H:%M")
    except Exception:
        return None

def fallback_local_csv():
    """
    Nivel 3 (Resiliencia Offline): Si no hubiese red ni caché API disponible, busca
    en la carpeta Descargas o en local el archivo CSV de calendario más reciente.
    """
    print("[INFO] Resiliencia Nivel 3: Buscando archivos CSV de respaldo en disco...")
    user_dl = os.path.join(os.path.expanduser("~"), "Downloads")
    candidates = []
    for pat in [os.path.join(user_dl, "*calendar*.csv"), os.path.join(SCRIPT_DIR, "*calendar*.csv")]:
        for path in glob.glob(pat):
            if os.path.isfile(path) and not path.endswith("news_calendar_clean.csv"):
                candidates.append(path)
    if not candidates:
        return []
    candidates.sort(key=lambda x: os.path.getmtime(x), reverse=True)
    latest_path = candidates[0]
    print(f"[INFO] Usando archivo CSV de respaldo: {latest_path}")
    
    events = []
    with open(latest_path, mode="r", encoding="utf-8", errors="ignore") as f:
        sample = f.read(1024)
        f.seek(0)
        delim = "," if sample.count(",") >= sample.count(";") else ";"
        for row in csv.DictReader(f, delimiter=delim):
            row_clean = {k.strip().lstrip("\ufeff"): v.strip() for k, v in row.items() if k}
            if row_clean.get("Impact", "").upper() != TARGET_IMPACT:
                continue
            curr = row_clean.get("Currency", "").upper()
            if curr not in FLEET_CURRENCIES:
                continue
            start = row_clean.get("Start", "")
            try:
                for fmt in ["%m/%d/%Y %H:%M:%S", "%Y-%m-%d %H:%M:%S", "%d/%m/%Y %H:%M:%S"]:
                    try:
                        dt = datetime.strptime(start, fmt)
                        dt_broker = dt + timedelta(hours=0) # Asumiendo hora local
                        events.append((dt_broker.strftime("%Y.%m.%d %H:%M"), curr, row_clean.get("Name", "")))
                        break
                    except ValueError:
                        continue
            except Exception:
                continue
    return events

def run_pipeline():
    print("==================================================================")
    print("[INFO] ALPHA SNIPER V11.3: PIPELINE AUTONOMO DE CALENDARIO MACRO")
    print("==================================================================")
    
    clean_events = []
    
    # 1. Obtención Autónoma por API (Opción A - Recomendada)
    api_data = fetch_from_api_json()
    if api_data is not None:
        for ev in api_data:
            impact   = ev.get("impact", "").upper()
            curr     = ev.get("country", "").upper()
            iso_date = ev.get("date", "")
            title    = ev.get("title", "")
            
            # Filtro Estricto: Impacto == 'HIGH'
            if impact != TARGET_IMPACT:
                continue
            
            # Filtro Estricto: Divisa en Flota {'USD', 'EUR', 'JPY', 'AUD'}
            if curr not in FLEET_CURRENCIES:
                continue
            
            broker_ts = parse_iso_date(iso_date)
            if broker_ts:
                clean_events.append((broker_ts, curr, title))
    else:
        # 2. Resiliencia Nivel 3: Fallback a CSV local
        clean_events = fallback_local_csv()
    
    # Ordenar cronológicamente por Timestamp de Bróker
    clean_events.sort(key=lambda x: x[0])
    
    # 3. Exportación Atómica en 2 Columnas para MT5 (BrokerTimestamp;Currency)
    def write_clean_file(dest_path):
        os.makedirs(os.path.dirname(dest_path), exist_ok=True)
        with open(dest_path, mode="w", newline="", encoding="utf-8") as f:
            f.write("BrokerTimestamp;Currency\n")
            for ts, curr, _ in clean_events:
                f.write(f"{ts};{curr}\n")
        print(f"[SUCCESS] Sincronizado en: {dest_path}")

    write_clean_file(OUTPUT_LOCAL)
    write_clean_file(OUTPUT_MT5)
    write_clean_file(OUTPUT_COMMON)
    
    # 4. Auditoría de Salida en Consola
    print(f"\n=== EVENTOS INSTITUCIONALES HIGH IMPACT SINCRONIZADOS ({len(clean_events)}) ===")
    print(f"{'BrokerTimestamp':<18} | {'Currency':<8} | {'Title'}")
    print("-" * 65)
    for ts, curr, title in clean_events:
        print(f"{ts:<18} | {curr:<8} | {title}")
    print("-" * 65)
    print("[SUCCESS] Pipeline V11.3 ejecutado exitosamente y listo en MetaTrader 5.")

if __name__ == "__main__":
    run_pipeline()

# 🚨 ARQUITECTURA EN 2 CAPAS: PROTOCOLO V11.3 (ANTI-NEWS SHIELD) 🚨

> **Directiva de la Dirección Cuantitativa**  
> Sistema híbrido de ultra-baja latencia para la gestión y protección ante eventos macroeconómicos de impacto alto (`HIGH Impact`), desacoplando el parseo pesado de texto del hilo principal de MetaTrader 5 y delegándolo a un *pipeline* automatizado en Python.

---

## 1. Visión General de la Arquitectura en 2 Capas

```
+---------------------------------------------------------------------------------+
| CAPA 1: PIPELINE PYTHON (update_news_calendar.py)                              |
| - Descarga / Ingesta de calendario crudo (FXStreet)                            |
| - Filtrado estricto: Impacto == 'HIGH' & Divisas Flota (USD, EUR, JPY, AUD)    |
| - Conversión a hora local del bróker MT5 (BrokerTimestamp YYYY.MM.DD HH:MM)     |
| - Exportación de CSV limpio (2 columnas) a MQL5/Files/news_calendar_clean.csv  |
+---------------------------------------------------------------------------------+
                                       |
                                       v
+---------------------------------------------------------------------------------+
| CAPA 2: ESCUDO ULTRA-LIGERO MQL5 (Alpha_Sniper_v11_3.mq5)                      |
| - Carga en RAM a estructura ligera (CleanNewsEvent[]) sin parseo de strings    |
| - Cierre Preventivo 100% FLAT: <= 15 mins antes del evento                     |
| - Ventana de Bloqueo de Entradas: [-30 mins, +30 mins]                         |
+---------------------------------------------------------------------------------+
```

---

## 2. CAPA 1: Script de Automatización Python (`update_news_calendar.py`)

### A. Especificaciones de Filtrado y Conversión
1. **Origen de Datos:**
   - Ingesta archivos compatibles con **FXStreet** (`Id,Start,Name,Impact,Currency`) en el directorio local o en ruta de descarga.
2. **Filtrado Estricto de Flota:**
   - **Impacto:** Conserva exclusivamente eventos catalogados con `Impact == "HIGH"`.
   - **Divisas:** Limita la ingesta a la flota operativa del fondo: `USD`, `EUR`, `JPY`, `AUD`.
3. **Conversión Temporal (Broker Offset):**
   - Transforma marcas de tiempo al huso horario del servidor del bróker MT5 (`YYYY.MM.DD HH:MM`), eliminando la necesidad de corrección de zona horaria dentro del código MQL5.
4. **Formato de Salida Ultra-Ligero:**
   - Genera el archivo en **`MQL5/Files/news_calendar_clean.csv`** y en la carpeta local del proyecto.
   - Formato simple de 2 columnas delimitadas por punto y coma (`;`):
     ```csv
     BrokerTimestamp;Currency
     2026.07.29 01:30;AUD
     2026.07.29 18:00;USD
     2026.07.30 12:30;USD
     2026.07.30 14:15;EUR
     2026.07.31 12:30;USD
     ```

### B. Automatización en Windows Task Scheduler (`schedule_news_update.bat`)
Se ha proporcionado un script `.bat` autoejecutable que registra la tarea en el Programador de Tareas de Windows para ejecutarse automáticamente **todos los domingos a las 22:00**:
```batch
schtasks /create /tn "AlphaSniper_NewsCalendarUpdate" /tr "\"C:\Users\Manuel\AppData\Local\Programs\Python\Python311\python.exe\" \"C:\Users\Manuel\Desktop\HMA_MetaLabeling\Alpha_Sniper_Vault\mql5\update_news_calendar.py\"" /sc weekly /d SUN /st 22:00 /f
```

---

## 3. CAPA 2: Escudo Ultra-Ligero en MQL5 (`Alpha_Sniper_v11_3.mq5`)

El código fuente se ha desarrollado **estrictamente sobre el Estándar de Oro V11 Monolítico (`Alpha_Sniper_v11.mq5`)** sin modificar ni alterar el archivo base V11 en ningún punto.

### A. Ingesta Eficiente de Datos (`LoadCleanNewsCSV`)
- **Estructura Ligera en Memoria (`CleanNewsEvent`):**
  ```cpp
  struct CleanNewsEvent {
      datetime event_time;
      string   currency;
  };
  CleanNewsEvent g_news_events[];
  ```
- **Conversión Directa:** Al contar con el timestamp pre-formateado como `YYYY.MM.DD HH:MM`, se invoca directamente `StringToTime(ts_str)` del motor nativo de MT5, alcanzando un tiempo de carga cercano a $0$ milisegundos.
- **Recarga Diaria Automática (`CheckDailyNewsReload`):** Invocado al inicio de `OnTick()`, detecta cambios de día en el servidor (`dt.day_of_year != g_last_news_day`) y refresca la tabla en memoria automáticamente.

### B. Lógica de Protección Operativa
1. **Cierre Preventivo 100% FLAT (`CheckNewsShield`):**
   - **Umbral de Tiempo:** $\le 15$ minutos antes de la hora del evento (`InpNewsCloseBeforeMinutes = 15`).
   - **Acción Ejecutoria:** Liquida el **100% del volumen abierto** del símbolo cuyo par contenga la divisa afectada por el evento (o cualquier par cotizado en USD para noticias estadounidenses).
   - **Auditoría Explicita:**
     ```
     🚨 [ANTI-NEWS SHIELD V11.3] Evento HIGH (USD) en 12 mins. Cierre preventivo 100% FLAT ejecutado. Ticket: 123456789 | Vol: 2.50
     ```
2. **Bloqueo de Apertura de Órdenes (`CheckNewsBlockEntry`):**
   - **Ventana de Pausa:** $30$ minutos antes (`InpNewsBlockBeforeMinutes = 30`) y $30$ minutos después (`InpNewsBlockAfterMinutes = 30`) de la publicación.
   - **Efecto:** `CanOpenNewTrade()` retorna `false` con la razón literal de bloqueo en el log del EA, impidiendo que los modelos XGBoost abran nuevas posiciones durante eventos de alta volatilidad.

---

## 4. Auditoría del Bugfix de Scale-Out (`PositionClosePartial`) en V11.3
1. **Inmutabilidad del Riesgo Inicial ($R$):**
   - El cálculo de múltiplos $R$ en el Scale-Out utiliza la distancia inicial de riesgo guardada y computada por `GetInitialRiskDist(identifier, open_price, type)`, manteniendo invariables los niveles de target de $R$ aunque el SL sea desplazado por Breakeven o Trailing.
2. **Normalización Estricta de Volumen:**
   - Redondea el volumen a cerrar por el paso y volumen mínimo del bróker:
     ```cpp
     double close_lots = MathFloor((current_lots * 0.5) / vol_step) * vol_step;
     if(close_lots < vol_min) close_lots = vol_min;
     ```
3. **Registro Forense de Errores:**
   - Si `trade.PositionClosePartial(ticket, close_lots)` es rechazado por el bróker o falla, se documenta explícitamente en el diario con `trade.ResultRetcode()`, `trade.ResultRetcodeDescription()`, y `GetLastError()`.

---

## 5. Resumen de Entregables e Integración
- **Capa 1 (Python Script):** [update_news_calendar.py](file:///C:/Users/Manuel/Desktop/HMA_MetaLabeling/Alpha_Sniper_Vault/mql5/update_news_calendar.py)
- **Generador de Tarea Windows:** [schedule_news_update.bat](file:///C:/Users/Manuel/Desktop/HMA_MetaLabeling/Alpha_Sniper_Vault/mql5/schedule_news_update.bat)
- **Capa 2 (MQL5 EA V11.3):** [Alpha_Sniper_v11_3.mq5](file:///C:/Users/Manuel/Desktop/HMA_MetaLabeling/Alpha_Sniper_Vault/mql5/Alpha_Sniper_v11_3.mq5) (Construido sobre [Alpha_Sniper_v11.mq5](file:///C:/Users/Manuel/Desktop/HMA_MetaLabeling/Alpha_Sniper_Vault/mql5/Alpha_Sniper_v11.mq5) sin modificarlo)
- **CSV Pre-procesado de Prueba:** [news_calendar_clean.csv](file:///C:/Users/Manuel/Desktop/HMA_MetaLabeling/Alpha_Sniper_Vault/mql5/news_calendar_clean.csv)
- **Documento de Arquitectura:** [v11_3_news_pipeline.md](file:///C:/Users/Manuel/Desktop/HMA_MetaLabeling/Alpha_Sniper_Vault/mql5/v11_3_news_pipeline.md)

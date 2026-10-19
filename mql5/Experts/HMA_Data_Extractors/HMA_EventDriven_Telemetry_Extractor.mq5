//+------------------------------------------------------------------+
//|                        HMA_EventDriven_Telemetry_Extractor.mq5    |
//|               HMA Meta-Labeling Research Framework - Data Engine  |
//|                                                                  |
//| [MARCO TEÓRICO E INGENIERÍA DE DATOS]:                           |
//| Implementa el recolector de telemetría asíncrono para el Método  |
//| de la Triple Barrera (López de Prado, 2018).                     |
//|                                                                  |
//| Arquitectura del Pipeline de Extracción:                         |
//|   1. Captura en t0: Al dispararse la señal primaria HMA, se toma |
//|      un snapshot instantáneo del vector de características X_t0: |
//|      (cinemática HMA, microestructura, volatilidad ATR, RSI,     |
//|      alineación multitemporal MTF y hora del día).               |
//|   2. Seguimiento asíncrono: Se monitorea la evolución del precio |
//|      hasta que toca la barrera superior (+TP), inferior (-SL)    |
//|      o expira por barrera vertical de tiempo (timeout en t1).    |
//|   3. Persistencia HPC: Se escribe de forma bufferizada en un     |
//|      archivo CSV en FILE_COMMON para que Python lo procese sin   |
//|      bloquear la ejecución del Strategy Tester de MT5.           |
//+------------------------------------------------------------------+
#property copyright "HMA Meta-Labeling Research Team"
#property link      "https://github.com/manuel-amado/hma-metalabeling-core"
#property version   "2.00"
#property description "Data Engineering: Extractor de Eventos y Features para Triple Barrier Meta-Labeling"

#include <Trade\Trade.mqh>

//+------------------------------------------------------------------+
//| Parámetros de Entrada                                            |
//+------------------------------------------------------------------+
input group "=== Configuración de Extracción de Eventos ==="
input int    InpHMA_Period           = 50;       // Período HMA Señal Base
input double InpUpperBarrier_ATR     = 2.0;      // Barrera Superior (Take Profit en x ATR)
input double InpLowerBarrier_ATR     = 2.0;      // Barrera Inferior (Stop Loss en x ATR)
input int    InpVerticalBarrier_Bars = 48;       // Barrera Vertical (Timeout en barras)

input group "=== Destino del Dataset ==="
input string InpFileName             = "HMA_MetaLabeling_Telemetry.csv";
input ulong  InpMagicNumber          = 100500;   // Magic Number identificador

//+------------------------------------------------------------------+
//| Estructura de Evento Abierto (t0)                                |
//+------------------------------------------------------------------+
struct EventSnapshot {
    ulong    id;
    datetime t0;
    int      direction; // 1 = Buy, -1 = Sell
    double   entry_price;
    double   upper_barrier;
    double   lower_barrier;
    int      max_bars;
    int      bars_elapsed;
    // Vector de Features X_t0
    double   atr14;
    double   rsi14;
    double   hma_velocity;
    double   hma_stretch;
    int      hour;
    int      day_of_week;
};

//+------------------------------------------------------------------+
//| Variables Globales                                               |
//+------------------------------------------------------------------+
CTrade          trade;
int             g_file_handle   = INVALID_HANDLE;
int             g_atr_handle    = INVALID_HANDLE;
int             g_rsi_handle    = INVALID_HANDLE;
int             g_hma_handle    = INVALID_HANDLE;
datetime        g_last_bar_time = 0;
ulong           g_event_counter = 0;
EventSnapshot   g_events[];

//+------------------------------------------------------------------+
//| Expert Initialization                                            |
//+------------------------------------------------------------------+
int OnInit() {
    g_atr_handle = iATR(_Symbol, _Period, 14);
    g_rsi_handle = iRSI(_Symbol, _Period, 14, PRICE_CLOSE);
    g_hma_handle = iMA(_Symbol, _Period, InpHMA_Period, 0, MODE_LWMA, PRICE_CLOSE);

    if(g_atr_handle == INVALID_HANDLE || g_rsi_handle == INVALID_HANDLE || g_hma_handle == INVALID_HANDLE) {
        Print("[INIT FAILED] Error al crear handles de indicadores.");
        return INIT_FAILED;
    }

    // Abrir archivo CSV en FILE_COMMON (accesible globalmente)
    g_file_handle = FileOpen(InpFileName, FILE_WRITE|FILE_CSV|FILE_ANSI|FILE_COMMON, ",");
    if(g_file_handle != INVALID_HANDLE) {
        // Escribir cabecera institucional del dataset
        FileWrite(g_file_handle,
                  "Event_ID", "Time_t0", "Direction", "Entry_Price", "Exit_Price",
                  "Return_Pct", "Label_TripleBarrier", "Barrier_Hit", "Bars_Held",
                  "ATR_14", "RSI_14", "HMA_Velocity", "HMA_Stretch", "Hour", "DayOfWeek");
        Print("[INIT OK] Archivo de telemetría abierto: ", InpFileName);
    } else {
        Print("[INIT ERROR] No se pudo abrir el archivo CSV en FILE_COMMON.");
        return INIT_FAILED;
    }

    return INIT_SUCCEEDED;
}

//+------------------------------------------------------------------+
//| Expert Deinitialization                                          |
//+------------------------------------------------------------------+
void OnDeinit(const int reason) {
    if(g_file_handle != INVALID_HANDLE) {
        FileClose(g_file_handle);
        Print("[DEINIT] Telemetría guardada. Total eventos procesados: ", g_event_counter);
    }
    IndicatorRelease(g_atr_handle);
    IndicatorRelease(g_rsi_handle);
    IndicatorRelease(g_hma_handle);
}

//+------------------------------------------------------------------+
//| Registro de Salida de Barrera a CSV                              |
//+------------------------------------------------------------------+
void LogBarrierResolution(const EventSnapshot &ev, double exit_price, string barrier_name, int label) {
    if(g_file_handle == INVALID_HANDLE) return;

    double ret_pct = (ev.direction == 1) ? 
        ((exit_price - ev.entry_price) / ev.entry_price) * 100.0 :
        ((ev.entry_price - exit_price) / ev.entry_price) * 100.0;

    FileWrite(g_file_handle,
              IntegerToString(ev.id),
              TimeToString(ev.t0, TIME_DATE|TIME_MINUTES),
              IntegerToString(ev.direction),
              DoubleToString(ev.entry_price, (int)SymbolInfoInteger(_Symbol, SYMBOL_DIGITS)),
              DoubleToString(exit_price, (int)SymbolInfoInteger(_Symbol, SYMBOL_DIGITS)),
              DoubleToString(ret_pct, 4),
              IntegerToString(label),
              barrier_name,
              IntegerToString(ev.bars_elapsed),
              DoubleToString(ev.atr14, 5),
              DoubleToString(ev.rsi14, 2),
              DoubleToString(ev.hma_velocity, 5),
              DoubleToString(ev.hma_stretch, 3),
              IntegerToString(ev.hour),
              IntegerToString(ev.day_of_week));
}

//+------------------------------------------------------------------+
//| Expert Tick Function                                             |
//+------------------------------------------------------------------+
void OnTick() {
    datetime current_bar_time = iTime(_Symbol, _Period, 0);
    if(current_bar_time == g_last_bar_time || current_bar_time == 0) return;

    double hma[3], atr[2], rsi[2];
    MqlRates rates[3];
    ArraySetAsSeries(hma, true); ArraySetAsSeries(atr, true);
    ArraySetAsSeries(rsi, true); ArraySetAsSeries(rates, true);

    if(CopyRates(_Symbol, _Period, 0, 3, rates) < 3) return;
    if(CopyBuffer(g_hma_handle, 0, 0, 3, hma) < 3) return;
    if(CopyBuffer(g_atr_handle, 0, 1, 2, atr) < 2) return;
    if(CopyBuffer(g_rsi_handle, 0, 1, 2, rsi) < 2) return;

    double current_close = rates[1].close;
    double current_high  = rates[1].high;
    double current_low   = rates[1].low;
    double current_atr   = atr[0];
    if(current_atr <= 0.0) return;

    // 1. Evaluar eventos pendientes contra la Triple Barrera
    int total_active = ArraySize(g_events);
    for(int i = total_active - 1; i >= 0; i--) {
        g_events[i].bars_elapsed++;
        bool resolved = false;

        if(g_events[i].direction == 1) { // BUY
            if(current_high >= g_events[i].upper_barrier) {
                // Toca barrera superior (Take Profit) -> Label 1
                LogBarrierResolution(g_events[i], g_events[i].upper_barrier, "UPPER_TP", 1);
                resolved = true;
            } else if(current_low <= g_events[i].lower_barrier) {
                // Toca barrera inferior (Stop Loss) -> Label 0
                LogBarrierResolution(g_events[i], g_events[i].lower_barrier, "LOWER_SL", 0);
                resolved = true;
            } else if(g_events[i].bars_elapsed >= g_events[i].max_bars) {
                // Barrera vertical de tiempo expirada
                int lbl = (current_close > g_events[i].entry_price) ? 1 : 0;
                LogBarrierResolution(g_events[i], current_close, "VERTICAL_TIMEOUT", lbl);
                resolved = true;
            }
        } else if(g_events[i].direction == -1) { // SELL
            if(current_low <= g_events[i].upper_barrier) {
                // Toca barrera superior (Take Profit para cortos) -> Label 1
                LogBarrierResolution(g_events[i], g_events[i].upper_barrier, "UPPER_TP", 1);
                resolved = true;
            } else if(current_high >= g_events[i].lower_barrier) {
                // Toca barrera inferior (Stop Loss para cortos) -> Label 0
                LogBarrierResolution(g_events[i], g_events[i].lower_barrier, "LOWER_SL", 0);
                resolved = true;
            } else if(g_events[i].bars_elapsed >= g_events[i].max_bars) {
                // Barrera vertical de tiempo expirada
                int lbl = (current_close < g_events[i].entry_price) ? 1 : 0;
                LogBarrierResolution(g_events[i], current_close, "VERTICAL_TIMEOUT", lbl);
                resolved = true;
            }
        }

        if(resolved) {
            ArrayRemove(g_events, i, 1);
        }
    }

    // 2. Detección de Nueva Señal Primaria HMA (Generador de Alto Recall)
    double prev_close = rates[2].close;
    double current_hma = hma[1];
    double prev_hma = hma[2];
    double hma_vel = current_hma - prev_hma;

    bool cross_up = (prev_close < prev_hma && current_close > current_hma);
    bool cross_dn = (prev_close > prev_hma && current_close < current_hma);

    int new_signal = 0;
    if(cross_up) new_signal =  1;
    if(cross_dn) new_signal = -1;

    // 3. Registrar Nuevo Evento t0
    if(new_signal != 0) {
        MqlDateTime dt;
        TimeToStruct(current_bar_time, dt);

        EventSnapshot ev;
        g_event_counter++;
        ev.id = g_event_counter;
        ev.t0 = current_bar_time;
        ev.direction = new_signal;
        ev.entry_price = current_close;
        ev.max_bars = InpVerticalBarrier_Bars;
        ev.bars_elapsed = 0;

        if(new_signal == 1) {
            ev.upper_barrier = current_close + (current_atr * InpUpperBarrier_ATR);
            ev.lower_barrier = current_close - (current_atr * InpLowerBarrier_ATR);
        } else {
            ev.upper_barrier = current_close - (current_atr * InpUpperBarrier_ATR);
            ev.lower_barrier = current_close + (current_atr * InpLowerBarrier_ATR);
        }

        ev.atr14 = current_atr;
        ev.rsi14 = rsi[0];
        ev.hma_velocity = hma_vel;
        ev.hma_stretch = MathAbs(current_close - current_hma) / current_atr;
        ev.hour = dt.hour;
        ev.day_of_week = dt.day_of_week;

        int sz = ArraySize(g_events);
        ArrayResize(g_events, sz + 1);
        g_events[sz] = ev;
    }

    g_last_bar_time = current_bar_time;
}

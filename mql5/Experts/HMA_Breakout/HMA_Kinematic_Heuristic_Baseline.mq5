//+------------------------------------------------------------------+
//|                               HMA_Kinematic_Heuristic_Baseline.mq5|
//|               HMA Meta-Labeling Research Framework - Milestone 1  |
//|                                                                  |
//| [MARCO TEÓRICO E HIPÓTESIS CUANTITATIVA]:                        |
//| Somete a prueba la hipótesis cinemática de Alan Hull (2005):     |
//| los puntos de inflexión (V-Pivots) y la aceleración angular de   |
//| la Media Móvil de Hull (HMA) poseen capacidad predictiva para    |
//| anticipar rupturas direccionales antes del arbitraje de mercado. |
//|                                                                  |
//| Formulación de derivadas discretas implementadas:                |
//|   Velocidad (v_t)      = HMA_t - HMA_{t-1}                       |
//|   Aceleración (a_t)    = v_t - v_{t-1} = HMA_t - 2HMA_{t-1} + HMA_{t-2}
//|   Tirón / Jerk (j_t)   = a_t - a_{t-1}                           |
//|   Rubber Band Stretch  = |Close_t - HMA_t| / ATR_t(14)           |
//|                                                                  |
//| [LECCIÓN INSTITUCIONAL & POST-MORTEM]:                           |
//| Este Asesor Experto documenta "La Trampa del Sobre-Filtrado      |
//| Heurístico". Al intentar forzar una tasa de acierto artificial   |
//| mediante reglas condicionales rígidas (RSI, horas, umbrales de   |
//| ATR), la muestra colapsó a N < 150 operaciones, induciendo       |
//| sobreajuste paramétrico severo en el probador de estrategias.    |
//| Esta limitación matemática motivó el cambio de paradigma hacia   |
//| Meta-Labeling (López de Prado) con modelo primario de alto Recall.|
//+------------------------------------------------------------------+
#property copyright "HMA Meta-Labeling Research Team"
#property link      "https://github.com/manuel-amado/hma-metalabeling-core"
#property version   "1.00"
#property description "Milestone 1: Heurística Cinemática Pura HMA & Evidencia de Sobre-Filtrado"

#include <Trade\Trade.mqh>

//+------------------------------------------------------------------+
//| Parámetros de Entrada                                            |
//+------------------------------------------------------------------+
input group "=== Configuración Cinemática HMA ==="
input int    InpHMA_Period           = 50;    // Período Base HMA (Señal Primaria)
input int    InpHMA_Exit_Period      = 20;    // Período HMA Rápida (Salida Asimétrica)
input double InpRubberBandThreshold  = 1.5;   // Umbral de Deformación Elástica (|P - HMA| / ATR)
input double InpMinAcceleration      = 0.0;   // Aceleración mínima angular requerida

input group "=== Filtros Heurísticos Clásicos (Sobreajuste IS) ==="
input bool   InpUseHeuristicFilters  = true;  // Activar filtros rígidos (Demuestra colapso de N)
input int    InpRSIPeriod            = 14;    // Período RSI
input double InpRSILongBound         = 45.0;  // RSI máximo para compras (Sobreventa relativa)
input double InpRSIShortBound        = 55.0;  // RSI mínimo para ventas (Sobrecompra relativa)
input int    InpStartHour            = 8;     // Hora inicio operativa (EET)
input int    InpEndHour              = 20;    // Hora fin operativa (EET)

input group "=== Gestión de Riesgo y Salidas ==="
input double InpRiskPct              = 1.0;   // Riesgo por Trade (%)
input double InpSL_ATR_Multiplier    = 2.0;   // Stop Loss estructural (x ATR)
input double InpTP_ATR_Multiplier    = 3.0;   // Take Profit estático (x ATR)
input ulong  InpMagicNumber          = 100101;// Magic Number identificador

//+------------------------------------------------------------------+
//| Variables Globales                                               |
//+------------------------------------------------------------------+
CTrade   trade;
datetime g_last_bar_time = 0;
int      g_atr_handle    = INVALID_HANDLE;
int      g_rsi_handle    = INVALID_HANDLE;

// Buffer dinámico para cálculo nativo autocontenido de WMA y HMA
double CalcWMA(const double &price[], int period, int shift) {
    double sum = 0.0;
    double weight_sum = 0.0;
    for(int i = 0; i < period; i++) {
        double weight = (double)(period - i);
        sum += price[shift + i] * weight;
        weight_sum += weight;
    }
    return (weight_sum > 0.0) ? (sum / weight_sum) : 0.0;
}

//+------------------------------------------------------------------+
//| Cálculo Matemático Directo de la Media Móvil de Hull             |
//| HMA = WMA( 2*WMA(n/2) - WMA(n), sqrt(n) )                       |
//+------------------------------------------------------------------+
double CalcHMA(const double &close_prices[], int period, int shift) {
    int half_period = period / 2;
    int sqrt_period = (int)MathFloor(MathSqrt((double)period));
    if(sqrt_period < 1) sqrt_period = 1;

    int total_needed = period + sqrt_period + 5;
    if(ArraySize(close_prices) < shift + total_needed) return 0.0;

    double diff_wma[];
    ArrayResize(diff_wma, sqrt_period);

    for(int i = 0; i < sqrt_period; i++) {
        double wma_half = CalcWMA(close_prices, half_period, shift + i);
        double wma_full = CalcWMA(close_prices, period, shift + i);
        diff_wma[i] = 2.0 * wma_half - wma_full;
    }

    // WMA final sobre el array sintético de diferencias
    double hma_val = 0.0;
    double weight_sum = 0.0;
    for(int i = 0; i < sqrt_period; i++) {
        double weight = (double)(sqrt_period - i);
        hma_val += diff_wma[i] * weight;
        weight_sum += weight;
    }
    return (weight_sum > 0.0) ? (hma_val / weight_sum) : 0.0;
}

//+------------------------------------------------------------------+
//| Expert Initialization                                            |
//+------------------------------------------------------------------+
int OnInit() {
    trade.SetExpertMagicNumber(InpMagicNumber);
    g_atr_handle = iATR(_Symbol, _Period, 14);
    g_rsi_handle = iRSI(_Symbol, _Period, InpRSIPeriod, PRICE_CLOSE);

    if(g_atr_handle == INVALID_HANDLE || g_rsi_handle == INVALID_HANDLE) {
        Print("[INIT FAILED] Error al crear indicadores base.");
        return INIT_FAILED;
    }

    Print("[INIT OK] HMA Kinematic Heuristic Baseline cargado. Magic: ", InpMagicNumber);
    return INIT_SUCCEEDED;
}

//+------------------------------------------------------------------+
//| Expert Deinitialization                                          |
//+------------------------------------------------------------------+
void OnDeinit(const int reason) {
    if(g_atr_handle != INVALID_HANDLE) IndicatorRelease(g_atr_handle);
    if(g_rsi_handle != INVALID_HANDLE) IndicatorRelease(g_rsi_handle);
}

//+------------------------------------------------------------------+
//| Expert Tick Function                                             |
//+------------------------------------------------------------------+
void OnTick() {
    datetime current_bar_time = iTime(_Symbol, _Period, 0);
    if(current_bar_time == g_last_bar_time || current_bar_time == 0) return;

    // Obtener series de precios recientes
    int bars_needed = InpHMA_Period + 30;
    MqlRates rates[];
    ArraySetAsSeries(rates, true);
    if(CopyRates(_Symbol, _Period, 0, bars_needed, rates) < bars_needed) return;

    double close_prices[];
    ArrayResize(close_prices, bars_needed);
    for(int i = 0; i < bars_needed; i++) close_prices[i] = rates[i].close;

    // 1. Cálculo cinemático de HMA en t-1, t-2, t-3, t-4
    double hma1 = CalcHMA(close_prices, InpHMA_Period, 1);
    double hma2 = CalcHMA(close_prices, InpHMA_Period, 2);
    double hma3 = CalcHMA(close_prices, InpHMA_Period, 3);
    double hma4 = CalcHMA(close_prices, InpHMA_Period, 4);

    if(hma1 == 0.0 || hma2 == 0.0 || hma3 == 0.0 || hma4 == 0.0) return;

    // Derivadas discretas (Velocidad, Aceleración, Jerk)
    double v1 = hma1 - hma2;
    double v2 = hma2 - hma3;
    double v3 = hma3 - hma4;

    double a1 = v1 - v2;
    double a2 = v2 - v3;

    double j1 = a1 - a2;

    // Lectura de ATR y RSI
    double atr_arr[2], rsi_arr[2];
    ArraySetAsSeries(atr_arr, true);
    ArraySetAsSeries(rsi_arr, true);
    if(CopyBuffer(g_atr_handle, 0, 1, 2, atr_arr) < 2) return;
    if(CopyBuffer(g_rsi_handle, 0, 1, 2, rsi_arr) < 2) return;

    double current_atr = atr_arr[0];
    double current_rsi = rsi_arr[0];
    if(current_atr <= 0.0) return;

    // Rubber Band Stretch (Deformación elástica normalizada)
    double rubber_band_stretch = MathAbs(rates[1].close - hma1) / current_atr;

    // 2. Gestión de Salidas Asimétricas
    int total_positions = PositionsTotal();
    for(int i = total_positions - 1; i >= 0; i--) {
        if(!PositionGetSymbol(i) || PositionGetString(POSITION_SYMBOL) != _Symbol) continue;
        if(PositionGetInteger(POSITION_MAGIC) != InpMagicNumber) continue;

        ENUM_POSITION_TYPE p_type = (ENUM_POSITION_TYPE)PositionGetInteger(POSITION_TYPE);
        ulong p_ticket = PositionGetInteger(POSITION_TICKET);

        // Giro de velocidad (V-Pivot contrario de salida)
        if(p_type == POSITION_TYPE_BUY && v1 < 0.0) {
            trade.PositionClose(p_ticket);
        } else if(p_type == POSITION_TYPE_SELL && v1 > 0.0) {
            trade.PositionClose(p_ticket);
        }
    }

    // Comprobar si ya existe posición abierta para este bot
    bool has_open = false;
    for(int i = PositionsTotal() - 1; i >= 0; i--) {
        if(PositionGetSymbol(i) && PositionGetString(POSITION_SYMBOL) == _Symbol &&
           PositionGetInteger(POSITION_MAGIC) == InpMagicNumber) {
            has_open = true;
            break;
        }
    }
    if(has_open) {
        g_last_bar_time = current_bar_time;
        return;
    }

    // 3. Generación de Señal Primaria Cinemática
    // Giro de velocidad instantánea de negativa a positiva (V-Pivot Alcista)
    bool v_pivot_buy  = (v2 < 0.0 && v1 > 0.0 && rubber_band_stretch >= InpRubberBandThreshold);
    // Giro de velocidad instantánea de positiva a negativa (V-Pivot Bajista)
    bool v_pivot_sell = (v2 > 0.0 && v1 < 0.0 && rubber_band_stretch >= InpRubberBandThreshold);

    int signal = 0;
    if(v_pivot_buy)  signal =  1;
    if(v_pivot_sell) signal = -1;

    // 4. Filtros Heurísticos Clásicos (El motivo del sobreajuste empírico)
    if(InpUseHeuristicFilters && signal != 0) {
        MqlDateTime dt;
        TimeToStruct(current_bar_time, dt);

        // Filtro de horario
        if(dt.hour < InpStartHour || dt.hour >= InpEndHour) signal = 0;

        // Filtro de RSI restrictivo
        if(signal == 1 && current_rsi > InpRSILongBound) signal = 0;
        if(signal == -1 && current_rsi < InpRSIShortBound) signal = 0;

        // Filtro de aceleración mínima
        if(signal == 1 && a1 < InpMinAcceleration) signal = 0;
        if(signal == -1 && a1 > -InpMinAcceleration) signal = 0;
    }

    // 5. Ejecución en MT5
    if(signal != 0) {
        double ask = SymbolInfoDouble(_Symbol, SYMBOL_ASK);
        double bid = SymbolInfoDouble(_Symbol, SYMBOL_BID);

        double sl_distance = current_atr * InpSL_ATR_Multiplier;
        double tp_distance = current_atr * InpTP_ATR_Multiplier;

        double entry_price = (signal == 1) ? ask : bid;
        double sl_price    = (signal == 1) ? (entry_price - sl_distance) : (entry_price + sl_distance);
        double tp_price    = (signal == 1) ? (entry_price + tp_distance) : (entry_price - tp_distance);

        // Dimensionamiento de posición por porcentaje de riesgo
        double tick_size = SymbolInfoDouble(_Symbol, SYMBOL_TRADE_TICK_SIZE);
        double tick_val  = SymbolInfoDouble(_Symbol, SYMBOL_TRADE_TICK_VALUE);
        double point     = SymbolInfoDouble(_Symbol, SYMBOL_POINT);
        double balance   = AccountInfoDouble(ACCOUNT_BALANCE);

        double risk_money = balance * (InpRiskPct / 100.0);
        double points_sl  = sl_distance / point;
        double lot_step   = SymbolInfoDouble(_Symbol, SYMBOL_VOLUME_STEP);
        double min_lot    = SymbolInfoDouble(_Symbol, SYMBOL_VOLUME_MIN);
        double max_lot    = SymbolInfoDouble(_Symbol, SYMBOL_VOLUME_MAX);

        double lot_size = min_lot;
        if(points_sl > 0.0 && tick_val > 0.0 && point > 0.0) {
            double raw_lots = risk_money / (points_sl * (tick_val / (tick_size / point)));
            lot_size = MathFloor(raw_lots / lot_step) * lot_step;
            lot_size = MathMax(min_lot, MathMin(max_lot, lot_size));
        }

        if(signal == 1) {
            trade.Buy(lot_size, _Symbol, ask, sl_price, tp_price, "Kinematic_HMA_Buy");
        } else if(signal == -1) {
            trade.Sell(lot_size, _Symbol, bid, sl_price, tp_price, "Kinematic_HMA_Sell");
        }
    }

    g_last_bar_time = current_bar_time;
}

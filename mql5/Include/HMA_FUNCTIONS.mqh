//+------------------------------------------------------------------+
//|                                              HMA_FUNCTIONS.mqh   |
//|        Funciones de Calculo de Features para Meta-Labeling       |
//|        v2.0 - Alineado con ARCHITECTURE_MASTER_CONTEXT           |
//+------------------------------------------------------------------+
//  PURGED: CheckVolumeFilter (tick volume = basura en CFDs)
//  PURGED: HasEnoughOppositeBars (cliff effect)
//  PURGED: News-skip logic in GetLowestLow/GetHighestHigh
//  PURGED: All extern NewsBlock references
//  ADDED:  CalcPullbackMetrics, CalcRsiExtremeMetrics,
//          CalcHmaAcceleration, CalcBreakoutForceATR,
//          CalcDistToMacroEMA
//+------------------------------------------------------------------+
#ifndef HMA_FUNCTIONS_MQH
#define HMA_FUNCTIONS_MQH

#property strict

//+------------------------------------------------------------------+
//| PHASE 16: DYNAMIC EXCURSION & RUBBER BAND TRACKER                |
//+------------------------------------------------------------------+
struct TTicketState {
    ulong  ticket;
    double peak_hma_stretch;
};
TTicketState g_ticket_states[];

void UpdatePeakStretch(ulong ticket, double current_stretch) {
    int size = ArraySize(g_ticket_states);
    for(int i = 0; i < size; i++) {
        if(g_ticket_states[i].ticket == ticket) {
            if(current_stretch > g_ticket_states[i].peak_hma_stretch) {
                g_ticket_states[i].peak_hma_stretch = current_stretch;
            }
            return;
        }
    }
    ArrayResize(g_ticket_states, size + 1, 100);
    g_ticket_states[size].ticket = ticket;
    g_ticket_states[size].peak_hma_stretch = current_stretch;
}

double GetPeakStretch(ulong ticket) {
    int size = ArraySize(g_ticket_states);
    for(int i = 0; i < size; i++) {
        if(g_ticket_states[i].ticket == ticket) {
            return g_ticket_states[i].peak_hma_stretch;
        }
    }
    return 0.0;
}

void CleanTicketStates() {
    int size = ArraySize(g_ticket_states);
    for(int i = size - 1; i >= 0; i--) {
        if(!PositionSelectByTicket(g_ticket_states[i].ticket)) {
            ArrayRemove(g_ticket_states, i, 1);
        }
    }
}

//+------------------------------------------------------------------+
//| SECCION 1: FUNCIONES DE FEATURES (Para el Orchestrator)          |
//+------------------------------------------------------------------+

//+------------------------------------------------------------------+
//| AMC 2C - Estructura de Consolidacion (Pullback)                  |
//| Mide la energia potencial acumulada antes del cruce              |
//+------------------------------------------------------------------+
void CalcPullbackMetrics(string sym, int h_hma, int lookback, double atr_val,
                         int &out_duration, double &out_max_depth_pct)
{
    out_duration = 0;
    out_max_depth_pct = 0.0;

    int needed = lookback + 1;
    double hmaArr[];
    MqlRates ratesArr[];
    ArraySetAsSeries(hmaArr, true);
    ArraySetAsSeries(ratesArr, true);

    if(CopyBuffer(h_hma, 0, 1, needed, hmaArr) < needed) return;
    if(CopyRates(sym, Period(), 1, needed, ratesArr) < needed) return;

    // Escanear desde barra 1 (la barra 0 es la del cruce en shift 1)
    double max_distance = 0;
    for(int i = 1; i < needed; i++)
    {
        double dist = ratesArr[i].close - hmaArr[i]; // Positivo = arriba de HMA
        double abs_dist = MathAbs(dist);

        // Contamos barras donde Close estaba al lado opuesto del cruce
        // (Si el cruce fue al alza, buscamos barras donde Close < HMA)
        // Pero como no sabemos la direccion aqui, contamos barras consecutivas
        // al mismo lado que la barra 1 (el lado opuesto al cruce)
        double ref_side = ratesArr[1].close - hmaArr[1];
        if((ref_side < 0 && dist < 0) || (ref_side > 0 && dist > 0))
        {
            out_duration++;
            if(abs_dist > max_distance) max_distance = abs_dist;
        }
        else
        {
            break; // Fin de la secuencia consecutiva
        }
    }

    // Normalizar profundidad como multiplo del ATR
    if(atr_val > 0)
        out_max_depth_pct = max_distance / atr_val;
}

//+------------------------------------------------------------------+
//| AMC 2B - El Resorte RSI (Agotamiento)                            |
//| Escanea la ventana y mide la fisica del resorte                  |
//+------------------------------------------------------------------+
void CalcRsiExtremeMetrics(int h_rsi, int lookback, int signal_type,
                           double &out_extreme_val, int &out_bars_since)
{
    out_extreme_val = 50.0; // Neutro por defecto
    out_bars_since = lookback; // Maximo por defecto

    double rsi[];
    ArraySetAsSeries(rsi, true);
    if(CopyBuffer(h_rsi, 0, 1, lookback, rsi) < lookback) return;

    // Buscar el valor mas extremo en la ventana
    for(int i = 0; i < lookback; i++)
    {
        if(signal_type == 0) // BUY: buscamos el RSI mas bajo (oversold)
        {
            if(rsi[i] < out_extreme_val)
            {
                out_extreme_val = rsi[i];
                out_bars_since = i;
            }
        }
        else // SELL: buscamos el RSI mas alto (overbought)
        {
            if(rsi[i] > out_extreme_val)
            {
                out_extreme_val = rsi[i];
                out_bars_since = i;
            }
        }
    }
}

//+------------------------------------------------------------------+
//| AMC 2D - Aceleracion HMA (2a derivada normalizada)               |
//| Dice si la HMA se esta volviendo mas pronunciada a nuestro favor |
//+------------------------------------------------------------------+
double CalcHmaAcceleration(int h_hma, double atr_val)
{
    if(atr_val <= 0) return 0.0;
    double hma[];
    ArraySetAsSeries(hma, true);
    if(CopyBuffer(h_hma, 0, 1, 3, hma) < 3) return 0.0;

    // 1a derivada normalizada por ATR
    // hma[0] = shift 1, hma[1] = shift 2, hma[2] = shift 3
    double slope0 = (hma[0] - hma[1]) / atr_val;
    double slope1 = (hma[1] - hma[2]) / atr_val;

    return slope0 - slope1;
}

//+------------------------------------------------------------------+
//| AMC 2D - Fuerza de Ruptura (Breakout Force)                      |
//| Desviacion del cruce normalizada por ATR                         |
//+------------------------------------------------------------------+
double CalcBreakoutForceATR(double close_price, double hma_val, double atr_val)
{
    if(atr_val <= 0) return 0.0;
    return MathAbs(close_price - hma_val) / atr_val;
}

//+------------------------------------------------------------------+
//| AMC 2A - Tension Elastica Macro                                  |
//| Distancia del precio al EMA200 H4 en multiplos de ATR            |
//+------------------------------------------------------------------+
double CalcDistToMacroEMA(double close_price, double ema200_h4, double atr_val)
{
    if(atr_val <= 0) return 0.0;
    return (close_price - ema200_h4) / atr_val;
}


//+------------------------------------------------------------------+
//| SECCION 2: FUNCIONES UTILITARIAS (SL con High/Low puros)         |
//+------------------------------------------------------------------+

//+------------------------------------------------------------------+
//| Obtener el minimo de las ultimas X velas (SIN filtro de noticias)|
//| AMC: High/Low para SL, MAE, MFE                                 |
//+------------------------------------------------------------------+
double GetLowestLow(string sym, int bars)
{
    double lowest = DBL_MAX;
    for(int i = 1; i <= bars; i++)
    {
        double low = iLow(sym, Period(), i);
        if(low < lowest) lowest = low;
    }
    return (lowest == DBL_MAX) ? 0 : lowest;
}

//+------------------------------------------------------------------+
//| Obtener el maximo de las ultimas X velas (SIN filtro de noticias)|
//+------------------------------------------------------------------+
double GetHighestHigh(string sym, int bars)
{
    double highest = -DBL_MAX;
    for(int i = 1; i <= bars; i++)
    {
        double high = iHigh(sym, Period(), i);
        if(high > highest) highest = high;
    }
    return (highest == -DBL_MAX) ? 0 : highest;
}

//+------------------------------------------------------------------+
//| SECCION 3: VALIDACION GEOMETRICA Y MEMORIA ESTRUCTURAL           |
//+------------------------------------------------------------------+

//+------------------------------------------------------------------+
//| Cuenta velas consecutivas de inmersión bajo HMA                  |
//+------------------------------------------------------------------+
int CountConsistentlyBelowHMA(const MqlRates &rates[], const double &hma[], int start_shift, int max_lookback=50)
{
    int count = 0;
    for(int i = start_shift; i < start_shift + max_lookback; i++)
    {
        if(rates[i].close >= hma[i]) break;
        count++;
    }
    return count;
}

//+------------------------------------------------------------------+
//| Cuenta velas consecutivas de inmersión sobre HMA                 |
//+------------------------------------------------------------------+
int CountConsistentlyAboveHMA(const MqlRates &rates[], const double &hma[], int start_shift, int max_lookback=50)
{
    int count = 0;
    for(int i = start_shift; i < start_shift + max_lookback; i++)
    {
        if(rates[i].close <= hma[i]) break;
        count++;
    }
    return count;
}

//+------------------------------------------------------------------+
//| Verifica memoria de sobreventa RSI (ej. < 35)                    |
//+------------------------------------------------------------------+
bool WasRSIOversold(const double &rsi[], int start_shift, int bars_to_check, double oversold_level)
{
    for(int i = start_shift; i < start_shift + bars_to_check; i++)
    {
        if(rsi[i] < oversold_level) return true;
    }
    return false;
}

//+------------------------------------------------------------------+
//| Verifica memoria de sobrecompra RSI (ej. > 65)                   |
//+------------------------------------------------------------------+
bool WasRSIOverbought(const double &rsi[], int start_shift, int bars_to_check, double overbought_level)
{
    for(int i = start_shift; i < start_shift + bars_to_check; i++)
    {
        if(rsi[i] > overbought_level) return true;
    }
    return false;
}

#endif // HMA_FUNCTIONS_MQH

//+------------------------------------------------------------------+
//| Calculate_HMA_Normalized_Angle: Normaliza la pendiente de HMA    |
//+------------------------------------------------------------------+
double Calculate_HMA_Normalized_Angle(double hma_current, double hma_previous, double current_atr) {
    if (current_atr <= 0.0) return 0.0;
    double delta_hma = hma_current - hma_previous;
    double normalized_ratio = delta_hma / current_atr;
    return MathArctan(normalized_ratio) * (180.0 / M_PI);
}

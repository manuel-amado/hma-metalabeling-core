//+------------------------------------------------------------------+
//|                                  HMA_Adaptive_Kaufman_AHMA.mq5    |
//|               HMA Meta-Labeling Research Framework - Exploratory  |
//|                                                                  |
//| [MARCO TEÓRICO E HIPÓTESIS: AHMA]:                               |
//| Somete a prueba la Media Móvil de Hull Adaptativa (AHMA)         |
//| modulada dinámicamente mediante el Ratio de Eficiencia de Kaufman|
//| (Kaufman Efficiency Ratio - ER).                                 |
//|                                                                  |
//| Formulación Matemática:                                          |
//|   1. Dirección neta (|Cambio Total|):   D = |Close_t - Close_{t-n}|
//|   2. Volatilidad absoluta (|Ruido|):    V = sum_{i=0}^{n-1} |Close_{t-i} - Close_{t-i-1}|
//|   3. Ratio de Eficiencia de Kaufman:    ER = D / V   (0.0 <= ER <= 1.0)
//|   4. Período Dinámico de Hull:          Período = Min_P + (Max_P - Min_P) * (1.0 - ER)
//|                                                                  |
//| [HIPÓTESIS VS RESULTADO EMPÍRICO]:                               |
//| - Hipótesis: En tendencias fuertes (ER -> 1.0), la HMA reduce su |
//|   período a Min_P para minimizar el retardo de señal. En rangos  |
//|   y consolidaciones (ER -> 0.0), amplía su período a Max_P para  |
//|   suavizar y filtrar whipsaws de volatilidad.                    |
//| - Veredicto Cuantitativo: Aunque el ER mejora la adaptación      |
//|   geométrica, la transición de regímenes produce cambios bruscos |
//|   de aceleración que generan falsas rupturas en los puntos de     |
//|   inflexión. El arbitraje HFT y el ensanchamiento de spreads en  |
//|   los retrocesos neutralizan la ventaja teórica.                 |
//+------------------------------------------------------------------+
#property copyright "HMA Meta-Labeling Research Team"
#property link      "https://github.com/manuel-amado/hma-metalabeling-core"
#property version   "1.00"
#property description "Exploratory: Adaptive Hull Moving Average (AHMA) modulada por Kaufman ER"

#include <Trade\Trade.mqh>

//+------------------------------------------------------------------+
//| Parámetros de Entrada                                            |
//+------------------------------------------------------------------+
input group "=== Configuración Adaptativa AHMA ==="
input int    InpMinPeriod        = 12;     // Período HMA Mínimo (Régimen Tendencial ER->1)
input int    InpMaxPeriod        = 60;     // Período HMA Máximo (Régimen Lateral ER->0)
input int    InpER_Period        = 14;     // Período de Eficiencia Kaufman (ER)
input double InpMinER_Threshold  = 0.35;   // Umbral de Eficiencia mínimo para operar

input group "=== Filtros de Microestructura ==="
input int    InpATR_Period       = 14;     // Período ATR
input double InpSL_ATR_Mult      = 2.0;    // Multiplicador Stop Loss (x ATR)
input double InpTP_ATR_Mult      = 3.0;    // Multiplicador Take Profit (x ATR)
input double InpRiskPct          = 1.0;    // Riesgo por Trade (%)
input ulong  InpMagicNumber      = 100400; // Magic Number identificador

//+------------------------------------------------------------------+
//| Variables Globales                                               |
//+------------------------------------------------------------------+
CTrade   trade;
int      g_atr_handle    = INVALID_HANDLE;
datetime g_last_bar_time = 0;

//+------------------------------------------------------------------+
//| Cálculo del Ratio de Eficiencia de Kaufman (ER)                  |
//+------------------------------------------------------------------+
double CalcKaufmanER(const double &prices[], int period, int shift) {
    if(ArraySize(prices) < shift + period + 1) return 0.0;

    double net_change = MathAbs(prices[shift] - prices[shift + period]);
    double total_sum = 0.0;
    for(int i = 0; i < period; i++) {
        total_sum += MathAbs(prices[shift + i] - prices[shift + i + 1]);
    }
    return (total_sum > 0.0) ? (net_change / total_sum) : 0.0;
}

//+------------------------------------------------------------------+
//| WMA Autocontenida                                                |
//+------------------------------------------------------------------+
double CalcWMA_Internal(const double &prices[], int period, int shift) {
    double sum = 0.0;
    double weight_sum = 0.0;
    for(int i = 0; i < period; i++) {
        double w = (double)(period - i);
        sum += prices[shift + i] * w;
        weight_sum += w;
    }
    return (weight_sum > 0.0) ? (sum / weight_sum) : 0.0;
}

//+------------------------------------------------------------------+
//| Cálculo de HMA con Período Dinámico                              |
//+------------------------------------------------------------------+
double CalcDynamicHMA(const double &prices[], int period, int shift) {
    if(period < 4) period = 4;
    int half_p = period / 2;
    int sqrt_p = (int)MathFloor(MathSqrt((double)period));
    if(sqrt_p < 1) sqrt_p = 1;

    if(ArraySize(prices) < shift + period + sqrt_p + 2) return 0.0;

    double diff_arr[];
    ArrayResize(diff_arr, sqrt_p);
    for(int i = 0; i < sqrt_p; i++) {
        double w_half = CalcWMA_Internal(prices, half_p, shift + i);
        double w_full = CalcWMA_Internal(prices, period, shift + i);
        diff_arr[i] = 2.0 * w_half - w_full;
    }

    double hma = 0.0;
    double w_sum = 0.0;
    for(int i = 0; i < sqrt_p; i++) {
        double w = (double)(sqrt_p - i);
        hma += diff_arr[i] * w;
        w_sum += w;
    }
    return (w_sum > 0.0) ? (hma / w_sum) : 0.0;
}

//+------------------------------------------------------------------+
//| Expert Initialization                                            |
//+------------------------------------------------------------------+
int OnInit() {
    trade.SetExpertMagicNumber(InpMagicNumber);
    g_atr_handle = iATR(_Symbol, _Period, InpATR_Period);

    if(g_atr_handle == INVALID_HANDLE) {
        Print("[INIT FAILED] Error al crear iATR.");
        return INIT_FAILED;
    }

    Print("[INIT OK] HMA Adaptive Kaufman AHMA inicializado. Magic: ", InpMagicNumber);
    return INIT_SUCCEEDED;
}

//+------------------------------------------------------------------+
//| Expert Deinitialization                                          |
//+------------------------------------------------------------------+
void OnDeinit(const int reason) {
    if(g_atr_handle != INVALID_HANDLE) IndicatorRelease(g_atr_handle);
}

//+------------------------------------------------------------------+
//| Expert Tick Function                                             |
//+------------------------------------------------------------------+
void OnTick() {
    datetime current_bar_time = iTime(_Symbol, _Period, 0);
    if(current_bar_time == g_last_bar_time || current_bar_time == 0) return;

    int total_bars_needed = InpMaxPeriod + InpER_Period + 20;
    MqlRates rates[];
    ArraySetAsSeries(rates, true);
    if(CopyRates(_Symbol, _Period, 0, total_bars_needed, rates) < total_bars_needed) return;

    double close_prices[];
    ArrayResize(close_prices, total_bars_needed);
    for(int i = 0; i < total_bars_needed; i++) close_prices[i] = rates[i].close;

    // 1. Ratio de Eficiencia Kaufman (ER) en barra 1
    double er_val = CalcKaufmanER(close_prices, InpER_Period, 1);

    // 2. Modulación Adaptativa del Período HMA
    // ER -> 1.0 (Tendencia pura)  => period -> InpMinPeriod
    // ER -> 0.0 (Ruido / lateral) => period -> InpMaxPeriod
    int dynamic_period = (int)MathRound(InpMinPeriod + (InpMaxPeriod - InpMinPeriod) * (1.0 - er_val));

    // 3. Cálculo de AHMA en t-1 y t-2
    double ahma1 = CalcDynamicHMA(close_prices, dynamic_period, 1);
    double ahma2 = CalcDynamicHMA(close_prices, dynamic_period, 2);
    if(ahma1 == 0.0 || ahma2 == 0.0) return;

    double atr_arr[2];
    ArraySetAsSeries(atr_arr, true);
    if(CopyBuffer(g_atr_handle, 0, 1, 2, atr_arr) < 2) return;
    double current_atr = atr_arr[0];
    if(current_atr <= 0.0) return;

    // 4. Gestión de Posiciones Abiertas
    for(int i = PositionsTotal() - 1; i >= 0; i--) {
        if(PositionGetSymbol(i) && PositionGetString(POSITION_SYMBOL) == _Symbol &&
           PositionGetInteger(POSITION_MAGIC) == InpMagicNumber) {
            ENUM_POSITION_TYPE p_type = (ENUM_POSITION_TYPE)PositionGetInteger(POSITION_TYPE);
            ulong p_ticket = PositionGetInteger(POSITION_TICKET);

            // Cierre por inversión de pendiente adaptativa
            if(p_type == POSITION_TYPE_BUY && rates[1].close < ahma1) trade.PositionClose(p_ticket);
            if(p_type == POSITION_TYPE_SELL && rates[1].close > ahma1) trade.PositionClose(p_ticket);
        }
    }

    // Comprobar si ya existe posición abierta
    bool has_open = false;
    for(int i = PositionsTotal() - 1; i >= 0; i--) {
        if(PositionGetSymbol(i) && PositionGetString(POSITION_SYMBOL) == _Symbol &&
           PositionGetInteger(POSITION_MAGIC) == InpMagicNumber) {
            has_open = true;
            break;
        }
    }
    if(has_open) { g_last_bar_time = current_bar_time; return; }

    // 5. Señal de Ruptura Adaptativa
    // Solo permitida si la eficiencia de mercado supera el umbral (filtro anti-chop)
    if(er_val >= InpMinER_Threshold) {
        bool cross_up = (rates[2].close < ahma2 && rates[1].close > ahma1);
        bool cross_dn = (rates[2].close > ahma2 && rates[1].close < ahma1);

        int signal = 0;
        if(cross_up) signal =  1;
        if(cross_dn) signal = -1;

        if(signal != 0) {
            double ask = SymbolInfoDouble(_Symbol, SYMBOL_ASK);
            double bid = SymbolInfoDouble(_Symbol, SYMBOL_BID);
            double sl_dist = current_atr * InpSL_ATR_Mult;
            double tp_dist = current_atr * InpTP_ATR_Mult;

            double entry_price = (signal == 1) ? ask : bid;
            double sl_price    = (signal == 1) ? (entry_price - sl_dist) : (entry_price + sl_dist);
            double tp_price    = (signal == 1) ? (entry_price + tp_dist) : (entry_price - tp_dist);

            double lot = SymbolInfoDouble(_Symbol, SYMBOL_VOLUME_MIN);
            if(signal == 1) trade.Buy(lot, _Symbol, ask, sl_price, tp_price, "AHMA_Kaufman_Buy");
            if(signal == -1) trade.Sell(lot, _Symbol, bid, sl_price, tp_price, "AHMA_Kaufman_Sell");
        }
    }

    g_last_bar_time = current_bar_time;
}

//+------------------------------------------------------------------+
//|                          HMA_Embedded_DecisionTree_Prototype.mq5|
//|               HMA Meta-Labeling Research Framework - Milestone 1.5|
//|                                                                  |
//| [MARCO TEÓRICO E HISTORIA EXPERIMENTAL]:                         |
//| Representa la transición desde reglas heurísticas manuales hacia |
//| Machine Learning supervisado (Meta-Labeling temprano).           |
//|                                                                  |
//| En esta fase preliminar, se entrenó un Árbol de Decisión en      |
//| Python (Scikit-Learn) para clasificar operaciones rentables vs   |
//| pérdidas, y se transpilaron manualmente las ramas condicionales   |
//| como código if/else nativo dentro de MQL5 (IsTradeAllowedByAI).  |
//|                                                                  |
//| [HALLAZGOS Y LIMITACIONES TÉCNICAS]:                             |
//| 1. Ventajas: Inferencia ultra-rápida sin dependencias externas.  |
//| 2. Limitaciones Críticas:                                        |
//|    - Inflexibilidad operativa: cualquier reentrenamiento semanal |
//|      exige reescribir y recompilar el archivo .mq5 completo.     |
//|    - Ausencia de calibración continua: produce decisiones binarias|
//|      (0/1) sin probabilidades suaves para dimensionamiento Kelly.|
//|    - Esta limitación motivó el desarrollo del pipeline M2 con    |
//|      transpilación automática AST a C++ (M2_XGBoost_Oracle.mqh). |
//+------------------------------------------------------------------+
#property copyright "HMA Meta-Labeling Research Team"
#property link      "https://github.com/manuel-amado/hma-metalabeling-core"
#property version   "1.50"
#property description "Milestone 1.5: Prototipo de Meta-Labeling con Árbol de Decisión Embebido"

#include <Trade\Trade.mqh>

//+------------------------------------------------------------------+
//| Parámetros de Entrada                                            |
//+------------------------------------------------------------------+
input group "=== Configuración Base HMA ==="
input int    InpHMA_Period       = 200;     // HMA Principal de Ruptura
input int    InpHMA_Exit_Period  = 50;      // HMA Rápida para Salidas Asimétricas
input int    InpEMA_Period       = 400;     // EMA Macro de Régimen Estructural
input int    InpRSIPeriod        = 14;      // Período RSI
input double InpRSIMin           = 30.0;    // RSI Mínimo
input double InpRSIMax           = 70.0;    // RSI Máximo
input double InpMinADX           = 20.0;    // ADX Mínimo de Inercia
input double InpATRMultiplier    = 1.5;     // Multiplicador ATR para SL

input group "=== Filtro de Machine Learning (Meta-Labeling) ==="
input bool   InpUseAI            = true;    // Activar filtro por Árbol de Decisión

input group "=== Gestión de Riesgo ==="
input double InpRiskPct          = 1.0;     // Riesgo por Operación (%)
input double InpFixedBalance     = 100000.0;// Balance de Referencia
input ulong  InpMagicNumber      = 100150;  // Magic Number identificador

//+------------------------------------------------------------------+
//| Variables Globales                                               |
//+------------------------------------------------------------------+
CTrade   trade;
int      hma_handle         = INVALID_HANDLE;
int      hma_exit_handle    = INVALID_HANDLE;
int      ema_handle         = INVALID_HANDLE;
int      rsi_handle         = INVALID_HANDLE;
int      atr_handle         = INVALID_HANDLE;
int      adx_handle         = INVALID_HANDLE;
datetime lastBarTime        = 0;

//+------------------------------------------------------------------+
//| INFERENCIA EMBEBIDA DEL ÁRBOL DE DECISIÓN (Python Scikit-Learn)  |
//| Entrenado con Triple Barrier Method sobre datos 2020-2024        |
//+------------------------------------------------------------------+
bool IsTradeAllowedByAI(double RSI, double ATR, double Dist_EMA, int Hour, int DayOfWeek, int Signal) {
    if (Hour <= 14.5000) {
        if (RSI <= 44.3391) {
            return false; // Subárbol de baja probabilidad
        } else {
            if (RSI <= 52.1705) {
                if (ATR <= 2.0954) {
                    return false;
                } else {
                    return true; // Probabilidad estimada > 65% en In-Sample
                }
            } else {
                return false;
            }
        }
    } else {
        if (RSI <= 40.6987) {
            if (Dist_EMA <= -1.2106) {
                if (RSI <= 38.8086) {
                    return true;
                } else {
                    return false;
                }
            } else {
                return false;
            }
        } else {
            if (RSI <= 42.0663) {
                return true;
            } else {
                if (RSI <= 44.7370) {
                    return false;
                } else {
                    return true;
                }
            }
        }
    }
}

//+------------------------------------------------------------------+
//| Expert Initialization                                            |
//+------------------------------------------------------------------+
int OnInit() {
    hma_handle      = iMA(_Symbol, _Period, InpHMA_Period, 0, MODE_LWMA, PRICE_CLOSE);
    hma_exit_handle = iMA(_Symbol, _Period, InpHMA_Exit_Period, 0, MODE_LWMA, PRICE_CLOSE);
    ema_handle      = iMA(_Symbol, _Period, InpEMA_Period, 0, MODE_EMA, PRICE_CLOSE);
    rsi_handle      = iRSI(_Symbol, _Period, InpRSIPeriod, PRICE_CLOSE);
    atr_handle      = iATR(_Symbol, _Period, 14);
    adx_handle      = iADX(_Symbol, _Period, 14);

    if(hma_handle == INVALID_HANDLE || hma_exit_handle == INVALID_HANDLE || 
       ema_handle == INVALID_HANDLE || rsi_handle == INVALID_HANDLE || 
       atr_handle == INVALID_HANDLE || adx_handle == INVALID_HANDLE) {
        Print("[INIT FAILED] Error al inicializar indicadores.");
        return INIT_FAILED;
    }

    trade.SetExpertMagicNumber(InpMagicNumber);
    Print("[INIT OK] HMA Embedded DecisionTree Prototype cargado. Magic: ", InpMagicNumber);
    return INIT_SUCCEEDED;
}

//+------------------------------------------------------------------+
//| Expert Deinitialization                                          |
//+------------------------------------------------------------------+
void OnDeinit(const int reason) {
    IndicatorRelease(hma_handle);
    IndicatorRelease(hma_exit_handle);
    IndicatorRelease(ema_handle);
    IndicatorRelease(rsi_handle);
    IndicatorRelease(atr_handle);
    IndicatorRelease(adx_handle);
}

//+------------------------------------------------------------------+
//| Cálculo de Loteaje por Riesgo                                    |
//+------------------------------------------------------------------+
double CalculateLotSize(double sl_distance_points, double price, double sl, int signal) {
    if(sl_distance_points <= 0) return 0.0;
    double balance = AccountInfoDouble(ACCOUNT_BALANCE);
    double risk_money = balance * (InpRiskPct / 100.0);
    double tick_val = SymbolInfoDouble(_Symbol, SYMBOL_TRADE_TICK_VALUE);
    double tick_size = SymbolInfoDouble(_Symbol, SYMBOL_TRADE_TICK_SIZE);
    double point = SymbolInfoDouble(_Symbol, SYMBOL_POINT);
    double lot_step = SymbolInfoDouble(_Symbol, SYMBOL_VOLUME_STEP);

    if(tick_val <= 0 || point <= 0 || tick_size <= 0) return SymbolInfoDouble(_Symbol, SYMBOL_VOLUME_MIN);
    double money_per_lot = (sl_distance_points * point / tick_size) * tick_val;
    if(money_per_lot <= 0) return SymbolInfoDouble(_Symbol, SYMBOL_VOLUME_MIN);

    double lots = MathFloor((risk_money / money_per_lot) / lot_step) * lot_step;
    double min_lot = SymbolInfoDouble(_Symbol, SYMBOL_VOLUME_MIN);
    double max_lot = SymbolInfoDouble(_Symbol, SYMBOL_VOLUME_MAX);
    return MathMax(min_lot, MathMin(max_lot, lots));
}

//+------------------------------------------------------------------+
//| Expert Tick Function                                             |
//+------------------------------------------------------------------+
void OnTick() {
    datetime currentBarTime = iTime(_Symbol, _Period, 0);
    if(currentBarTime == lastBarTime || currentBarTime == 0) return;

    double hma[], hma_exit[], ema[], rsi[], atr[], adx[];
    MqlRates rates[];

    ArraySetAsSeries(hma, true); ArraySetAsSeries(hma_exit, true);
    ArraySetAsSeries(ema, true); ArraySetAsSeries(rsi, true); 
    ArraySetAsSeries(atr, true); ArraySetAsSeries(adx, true);
    ArraySetAsSeries(rates, true);

    if(CopyRates(_Symbol, _Period, 0, 3, rates) < 3) return;
    if(CopyBuffer(hma_handle, 0, 0, 3, hma) < 3) return;
    if(CopyBuffer(hma_exit_handle, 0, 0, 3, hma_exit) < 3) return;
    if(CopyBuffer(ema_handle, 0, 0, 3, ema) < 3) return;
    if(CopyBuffer(rsi_handle, 0, 0, 3, rsi) < 3) return;
    if(CopyBuffer(atr_handle, 0, 0, 3, atr) < 3) return;
    if(CopyBuffer(adx_handle, 0, 0, 3, adx) < 3) return;

    double current_close = rates[1].close;
    double current_hma = hma[1];
    double current_hma_exit = hma_exit[1];
    double prev_close = rates[2].close;
    double prev_hma = hma[2];

    double current_ema = ema[1];
    double current_rsi = rsi[1];
    double current_atr = atr[1];
    double current_adx = adx[1];

    // 1. Gestión de Salidas Asimétricas con HMA Rápida
    int pos_total = PositionsTotal();
    bool has_open_pos = false;
    for(int i = pos_total - 1; i >= 0; i--) {
        if(PositionGetSymbol(i) && PositionGetString(POSITION_SYMBOL) == _Symbol &&
           PositionGetInteger(POSITION_MAGIC) == InpMagicNumber) {
            has_open_pos = true;
            ENUM_POSITION_TYPE pos_type = (ENUM_POSITION_TYPE)PositionGetInteger(POSITION_TYPE);
            ulong pos_ticket = PositionGetInteger(POSITION_TICKET);

            bool close_it = false;
            if(pos_type == POSITION_TYPE_BUY && current_close < current_hma_exit) close_it = true;
            if(pos_type == POSITION_TYPE_SELL && current_close > current_hma_exit) close_it = true;

            if(close_it) trade.PositionClose(pos_ticket);
        }
    }

    if(has_open_pos) { lastBarTime = currentBarTime; return; }

    // 2. Señal Primaria de Ruptura (Cruce de HMA confirmada por EMA macro y ADX)
    int signal = -1;
    bool cross_up = (prev_close < prev_hma && current_close > current_hma);
    bool cross_dn = (prev_close > prev_hma && current_close < current_hma);

    if(cross_up && current_close > current_ema && current_rsi < InpRSIMax && current_adx >= InpMinADX) signal = 1;
    if(cross_dn && current_close < current_ema && current_rsi > InpRSIMin && current_adx >= InpMinADX) signal = -1;

    if(signal != -1) {
        MqlDateTime dt;
        TimeToStruct(currentBarTime, dt);

        // 3. FILTRO META-LABELING (Árbol de Decisión Embebido)
        if(InpUseAI) {
            double dist_ema = (current_close - current_ema) / (current_atr > 0 ? current_atr : 1.0);
            if(!IsTradeAllowedByAI(current_rsi, current_atr, dist_ema, dt.hour, dt.day_of_week, signal)) {
                // Inferencia clasifica la señal como Falso Positivo -> Operación Vetada
                lastBarTime = currentBarTime;
                return;
            }
        }

        double ask = SymbolInfoDouble(_Symbol, SYMBOL_ASK);
        double bid = SymbolInfoDouble(_Symbol, SYMBOL_BID);
        double point = SymbolInfoDouble(_Symbol, SYMBOL_POINT);
        double sl_dist = current_atr * InpATRMultiplier;
        double points_dist = sl_dist / point;
        double sl = (signal == 1) ? ask - sl_dist : bid + sl_dist;

        double lots = CalculateLotSize(points_dist, signal == 1 ? ask : bid, sl, signal);
        if(lots > 0) {
            if(signal == 1) trade.Buy(lots, _Symbol, ask, sl, 0.0, "DecisionTree_AI_Buy");
            else trade.Sell(lots, _Symbol, bid, sl, 0.0, "DecisionTree_AI_Sell");
        }
    }

    lastBarTime = currentBarTime;
}

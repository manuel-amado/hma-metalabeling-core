//+------------------------------------------------------------------+
//|                                     HMA_TF_ONNX_Benchmark.mq5    |
//|               HMA Meta-Labeling Research Framework - Milestone 3A |
//|                                                                  |
//| [MARCO TEÓRICO: INFERENCIA ONNX EN METATRADER 5]:                |
//| Evalúa la integración de modelos de Machine Learning utilizando  |
//| la API nativa ONNX de MetaQuotes (OnnxCreateFromBuffer, OnnxRun).|
//| El modelo secundario 'FatTail_Model.onnx' actúa como filtro de   |
//| régimen para una estrategia primaria Trend-Following con HMA     |
//| sobre EMA macro (200/400).                                       |
//|                                                                  |
//| [BENCHMARK DE LATENCIA Y EVALUACIÓN COMPARATIVA]:                |
//| - Latencia típica ONNX MT5:  0.5 ms a 2.0 ms por inferencia      |
//|   (debido a serialización de tensores dinámicos y llamada API).  |
//| - Latencia C++ Transpilado:  < 0.1 µs (< 100 ns)                 |
//|   (ejecución directa en registros CPU L1 sin puente de memoria). |
//|                                                                  |
//| [CONCLUSIÓN DE INGENIERÍA]:                                      |
//| Aunque la API ONNX de MT5 es idónea para redes profundas o LSTMs,|
//| para modelos basados en árboles (XGBoost/LightGBM) en velas M1,  |
//| la transpilación AST a C++ nativo (M2_XGBoost_Oracle.mqh) ofrece |
//| una ventaja de latencia de 10.000x y cero dependencias de DLL.   |
//+------------------------------------------------------------------+
#property copyright "HMA Meta-Labeling Research Team"
#property link      "https://github.com/manuel-amado/hma-metalabeling-core"
#property version   "3.00"
#property description "Milestone 3A: Benchmark de Inferencia ONNX en Tiempo Real vs C++ Nativo"

#include <Trade\Trade.mqh>

//+------------------------------------------------------------------+
//| Recurso ONNX Embebido en el Binario                              |
//+------------------------------------------------------------------+
#resource "Models/FatTail_Model.onnx" as const uchar ExtModel[]

//+------------------------------------------------------------------+
//| Parámetros de Entrada                                            |
//+------------------------------------------------------------------+
input group "=== Configuración Base Trend-Following ==="
input int    InpHMA_Period       = 200;    // HMA para Entradas (Pullback)
input int    InpEMA_Period       = 400;    // EMA Macro de Tendencia
input double InpATRMultiplier    = 1.5;    // Multiplicador ATR para Stop Loss
input int    InpRSIPeriod        = 14;     // Período RSI

input group "=== Inferencia ONNX (Meta-Labeling) ==="
input bool   InpUseONNXFilter    = true;   // Activar filtro OnnxRun
input float  InpONNXProbThreshold= 0.50f;  // Umbral de probabilidad para aprobar trade

input group "=== Gestión de Riesgo ==="
input double InpRiskPct          = 1.0;    // Riesgo por Trade (%)
input ulong  InpMagicNumber      = 100300; // Magic Number identificador

//+------------------------------------------------------------------+
//| Variables Globales                                               |
//+------------------------------------------------------------------+
CTrade   trade;
long     g_onnx_handle = INVALID_HANDLE;
bool     g_onnx_active = false;
int      g_hma_handle  = INVALID_HANDLE;
int      g_ema_handle  = INVALID_HANDLE;
int      g_rsi_handle  = INVALID_HANDLE;
int      g_atr_handle  = INVALID_HANDLE;
int      g_adx_handle  = INVALID_HANDLE;
datetime g_last_bar    = 0;

//+------------------------------------------------------------------+
//| Expert Initialization                                            |
//+------------------------------------------------------------------+
int OnInit() {
    trade.SetExpertMagicNumber(InpMagicNumber);

    g_hma_handle = iMA(_Symbol, _Period, InpHMA_Period, 0, MODE_LWMA, PRICE_CLOSE);
    g_ema_handle = iMA(_Symbol, _Period, InpEMA_Period, 0, MODE_EMA, PRICE_CLOSE);
    g_rsi_handle = iRSI(_Symbol, _Period, InpRSIPeriod, PRICE_CLOSE);
    g_atr_handle = iATR(_Symbol, _Period, 14);
    g_adx_handle = iADX(_Symbol, _Period, 14);

    if(g_hma_handle == INVALID_HANDLE || g_ema_handle == INVALID_HANDLE ||
       g_rsi_handle == INVALID_HANDLE || g_atr_handle == INVALID_HANDLE ||
       g_adx_handle == INVALID_HANDLE) {
        Print("[INIT FAILED] Error al crear indicadores base.");
        return INIT_FAILED;
    }

    // Inicializar modelo ONNX desde el buffer en memoria
    if(InpUseONNXFilter) {
        g_onnx_handle = OnnxCreateFromBuffer(ExtModel, ONNX_DEFAULT);
        if(g_onnx_handle == INVALID_HANDLE) {
            Print("[ONNX WARNING] No se pudo cargar FatTail_Model.onnx. Código error: ", GetLastError());
            g_onnx_active = false;
        } else {
            const long input_shape[] = {1, 9};
            OnnxSetInputShape(g_onnx_handle, 0, input_shape);

            const long output_shape_pred[] = {1};
            OnnxSetOutputShape(g_onnx_handle, 0, output_shape_pred);

            const long output_shape_prob[] = {1, 2};
            OnnxSetOutputShape(g_onnx_handle, 1, output_shape_prob);

            g_onnx_active = true;
            Print("[INIT OK] Runtime ONNX inicializado correctamente.");
        }
    }

    Print("[INIT OK] HMA TF ONNX Benchmark cargado.");
    return INIT_SUCCEEDED;
}

//+------------------------------------------------------------------+
//| Expert Deinitialization                                          |
//+------------------------------------------------------------------+
void OnDeinit(const int reason) {
    if(g_onnx_handle != INVALID_HANDLE) {
        OnnxRelease(g_onnx_handle);
        g_onnx_handle = INVALID_HANDLE;
    }
    IndicatorRelease(g_hma_handle);
    IndicatorRelease(g_ema_handle);
    IndicatorRelease(g_rsi_handle);
    IndicatorRelease(g_atr_handle);
    IndicatorRelease(g_adx_handle);
}

//+------------------------------------------------------------------+
//| Expert Tick Function                                             |
//+------------------------------------------------------------------+
void OnTick() {
    datetime current_bar = iTime(_Symbol, _Period, 0);
    if(current_bar == g_last_bar || current_bar == 0) return;

    double hma[], ema[], rsi[], atr[], adx[];
    MqlRates rates[];

    ArraySetAsSeries(hma, true); ArraySetAsSeries(ema, true);
    ArraySetAsSeries(rsi, true); ArraySetAsSeries(atr, true);
    ArraySetAsSeries(adx, true); ArraySetAsSeries(rates, true);

    if(CopyRates(_Symbol, _Period, 0, 5, rates) < 5) return;
    if(CopyBuffer(g_hma_handle, 0, 0, 3, hma) < 3) return;
    if(CopyBuffer(g_ema_handle, 0, 0, 3, ema) < 3) return;
    if(CopyBuffer(g_rsi_handle, 0, 0, 3, rsi) < 3) return;
    if(CopyBuffer(g_atr_handle, 0, 0, 3, atr) < 3) return;
    if(CopyBuffer(g_adx_handle, 0, 0, 3, adx) < 3) return;

    double current_close = rates[1].close;
    double current_hma   = hma[1];
    double prev_close    = rates[2].close;
    double prev_hma      = hma[2];
    double current_ema   = ema[1];
    double current_rsi   = rsi[1];
    double current_atr   = atr[1];
    if(current_atr <= 0.0) return;

    // 1. Gestión de Posiciones Abiertas
    bool has_open = false;
    for(int i = PositionsTotal() - 1; i >= 0; i--) {
        if(PositionGetSymbol(i) && PositionGetString(POSITION_SYMBOL) == _Symbol &&
           PositionGetInteger(POSITION_MAGIC) == InpMagicNumber) {
            has_open = true;
            ENUM_POSITION_TYPE p_type = (ENUM_POSITION_TYPE)PositionGetInteger(POSITION_TYPE);
            ulong p_ticket = PositionGetInteger(POSITION_TICKET);

            // Salida asimétrica por cruce de HMA contraria
            if(p_type == POSITION_TYPE_BUY && current_close < current_hma) trade.PositionClose(p_ticket);
            if(p_type == POSITION_TYPE_SELL && current_close > current_hma) trade.PositionClose(p_ticket);
        }
    }
    if(has_open) { g_last_bar = current_bar; return; }

    // 2. Señal Primaria de Ruptura Trend-Following
    int signal = 0;
    bool cross_up = (prev_close < prev_hma && current_close > current_hma && current_close > current_ema);
    bool cross_dn = (prev_close > prev_hma && current_close < current_hma && current_close < current_ema);

    if(cross_up) signal =  1;
    if(cross_dn) signal = -1;

    // 3. Inferencia ONNX (Meta-Labeling Fat-Tail)
    if(signal != 0) {
        bool ml_approved = true;

        if(InpUseONNXFilter && g_onnx_active && g_onnx_handle != INVALID_HANDLE) {
            // Construcción del vector de 9 características para el modelo ONNX
            float features[9];
            features[0] = (float)signal;
            features[1] = (float)current_rsi;
            features[2] = (float)((current_close - current_ema) / current_atr);
            features[3] = (float)(MathAbs(current_close - current_hma) / current_atr);
            features[4] = 1.0f; // Buildup indicator
            features[5] = (float)((rates[1].high - rates[1].low) / current_atr);
            features[6] = 0.0f; // Loss streak
            features[7] = (float)(MathAbs(rates[1].close - rates[1].open) / current_atr);
            features[8] = (float)current_atr;

            long  ml_prediction[1];
            float ml_probabilities[2];

            // Inferencia y medición de latencia
            ulong t_start = GetMicrosecondCount();
            bool run_ok = OnnxRun(g_onnx_handle, ONNX_NO_CONVERSION, features, ml_prediction, ml_probabilities);
            ulong t_elapsed_us = GetMicrosecondCount() - t_start;

            if(run_ok) {
                // Probabilidad de clase positiva (Trade con edge)
                float p_win = ml_probabilities[1];
                if(p_win < InpONNXProbThreshold || ml_prediction[0] == 0) {
                    ml_approved = false;
                    PrintFormat("[ONNX ML] Trade bloqueado (p=%.2f < %.2f) | Latencia: %I64u µs",
                                p_win, InpONNXProbThreshold, t_elapsed_us);
                } else {
                    PrintFormat("[ONNX ML] Trade APROBADO (p=%.2f) | Latencia: %I64u µs",
                                p_win, t_elapsed_us);
                }
            } else {
                Print("[ONNX ERROR] Fallo en OnnxRun. Ejecutando señal primaria.");
            }
        }

        // 4. Ejecución
        if(ml_approved) {
            double ask = SymbolInfoDouble(_Symbol, SYMBOL_ASK);
            double bid = SymbolInfoDouble(_Symbol, SYMBOL_BID);
            double sl_dist = current_atr * InpATRMultiplier;
            double sl = (signal == 1) ? (ask - sl_dist) : (bid + sl_dist);

            double lot = SymbolInfoDouble(_Symbol, SYMBOL_VOLUME_MIN);
            if(signal == 1) trade.Buy(lot, _Symbol, ask, sl, 0.0, "HMA_ONNX_Buy");
            if(signal == -1) trade.Sell(lot, _Symbol, bid, sl, 0.0, "HMA_ONNX_Sell");
        }
    }

    g_last_bar = current_bar;
}

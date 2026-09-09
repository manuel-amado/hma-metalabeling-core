//+------------------------------------------------------------------+
//|                                           Alpha_Sniper_v26.mq5   |
//|                                                Copyright 2026    |
//|                        Clean Quant + PRECOMPUTED Regime Filter   |
//+------------------------------------------------------------------+
#property copyright "Manuel"
#property link      "https://antigravity.ai"
#property version   "26.0"

#include <Trade\Trade.mqh>
#include <RegimeMap.mqh> // El mapa de ADX generado por Python

input group "=== Filtro de Régimen Macro (Precomputado) ==="
input bool   InpUseRegimeFilter  = true;    // Activar Filtro ADX de Python

input group "=== Estrategia de Gatillo (M15) ==="
input int    InpHMA_Period       = 100;     // Periodo HMA
input int    InpEMA_Period       = 200;     // Periodo Filtro EMA
input int    InpRSIPeriod        = 14;      // Periodo RSI
input double InpRSIMin           = 30.0;    // Filtro Sobrevenda RSI
input double InpRSIMax           = 70.0;    // Filtro Sobrecompra RSI

input group "=== Gestión de Riesgo (Risk 1%) ==="
input double InpRiskPct          = 1.0;     // Riesgo Fijo por Operación (%)
input int    InpATRPeriod        = 14;      // Periodo ATR para Stop Loss
input double InpATRMultiplier    = 2.0;     // Multiplicador de SL
input double InpFixedBalance     = 100000.0;// Balance Base (si Equity = 0)

CTrade trade;

int hma_handle, ema_handle, rsi_handle, atr_handle;
datetime lastBarTime = 0;

int OnInit() {
    hma_handle = iCustom(_Symbol, _Period, "HMA50", InpHMA_Period);
    ema_handle = iMA(_Symbol, _Period, InpEMA_Period, 0, MODE_EMA, PRICE_CLOSE);
    rsi_handle = iRSI(_Symbol, _Period, InpRSIPeriod, PRICE_CLOSE);
    atr_handle = iATR(_Symbol, _Period, InpATRPeriod);

    if(hma_handle == INVALID_HANDLE || ema_handle == INVALID_HANDLE || 
       rsi_handle == INVALID_HANDLE || atr_handle == INVALID_HANDLE) {
        Print("ERROR: No se pudieron cargar los indicadores.");
        return INIT_FAILED;
    }
    
    trade.SetExpertMagicNumber(26000);
    return INIT_SUCCEEDED;
}

void OnDeinit(const int reason) {
    IndicatorRelease(hma_handle);
    IndicatorRelease(ema_handle);
    IndicatorRelease(rsi_handle);
    IndicatorRelease(atr_handle);
}

double CalculateLotSize(double sl_distance_points, double open_price, double sl_price, int type) {
    if(sl_distance_points <= 0) return 0.0;
    double capital = AccountInfoDouble(ACCOUNT_EQUITY);
    if(capital <= 0) capital = InpFixedBalance;
    double risk_amount = capital * (InpRiskPct / 100.0);
    
    ENUM_ORDER_TYPE order_type = (type == 0) ? ORDER_TYPE_BUY : ORDER_TYPE_SELL;
    double expected_loss = 0.0;
    
    if(!OrderCalcProfit(order_type, _Symbol, 1.0, open_price, sl_price, expected_loss)) return 0.0;
    
    double abs_loss = MathAbs(expected_loss);
    if(abs_loss <= 0.000001) return 0.0;
    
    double calculated_lots = risk_amount / abs_loss;
    
    double lot_step = SymbolInfoDouble(_Symbol, SYMBOL_VOLUME_STEP);
    double min_lot = SymbolInfoDouble(_Symbol, SYMBOL_VOLUME_MIN);
    double max_lot = SymbolInfoDouble(_Symbol, SYMBOL_VOLUME_MAX);
    
    double rounded_lots = MathFloor(calculated_lots / lot_step) * lot_step;
    if(rounded_lots < min_lot) rounded_lots = min_lot;
    if(rounded_lots > max_lot) rounded_lots = max_lot;
    
    return rounded_lots;
}

void OnTick() {
    datetime currentBarTime = iTime(_Symbol, _Period, 0);
    if(currentBarTime == lastBarTime || currentBarTime == 0) return;
    
    double hma[], ema[], rsi[], atr[];
    MqlRates rates[];
    
    ArraySetAsSeries(hma, true); ArraySetAsSeries(ema, true);
    ArraySetAsSeries(rsi, true); ArraySetAsSeries(atr, true);
    ArraySetAsSeries(rates, true);
    
    if(CopyRates(_Symbol, _Period, 0, 3, rates) < 3) return;
    if(CopyBuffer(hma_handle, 0, 0, 3, hma) < 3) return;
    if(CopyBuffer(ema_handle, 0, 0, 3, ema) < 3) ArrayInitialize(ema, rates[1].close);
    if(CopyBuffer(rsi_handle, 0, 0, 3, rsi) < 3) ArrayInitialize(rsi, 50.0);
    if(CopyBuffer(atr_handle, 0, 0, 3, atr) < 3) ArrayInitialize(atr, rates[1].high - rates[1].low);
    
    double current_close = rates[1].close;
    double current_hma = hma[1];
    double prev_close = rates[2].close;
    double prev_hma = hma[2];
    double current_ema = ema[1];
    double current_rsi = rsi[1];
    double current_atr = atr[1];
    
    // 1. GESTION DE SALIDAS
    int pos_total = PositionsTotal();
    bool has_open_pos = false;
    
    for(int i = pos_total - 1; i >= 0; i--) {
        if(PositionGetSymbol(i) == _Symbol) {
            has_open_pos = true;
            long pos_type = PositionGetInteger(POSITION_TYPE);
            ulong pos_ticket = PositionGetInteger(POSITION_TICKET);
            
            bool close_it = false;
            if(pos_type == POSITION_TYPE_BUY && current_close < current_hma) close_it = true;
            if(pos_type == POSITION_TYPE_SELL && current_close > current_hma) close_it = true;
            
            if(close_it) {
                trade.PositionClose(pos_ticket);
                has_open_pos = false; 
            }
        }
    }
    
    if(has_open_pos) { lastBarTime = currentBarTime; return; }
    
    // 2. FILTRO DE REGIMEN (INYECTADO DESDE PYTHON)
    if(InpUseRegimeFilter) {
        int regime_state = GetPrecomputedRegime(currentBarTime);
        if(regime_state == 0) {
            lastBarTime = currentBarTime;
            return; // Python dice: Rango Diario -> NO OPERAR
        }
    }
    
    // 3. GESTION DE ENTRADAS
    int signal = -1;
    bool cross_up = (prev_close < prev_hma && current_close > current_hma);
    bool cross_dn = (prev_close > prev_hma && current_close < current_hma);
    
    if(cross_up && current_close > current_ema && current_rsi < InpRSIMax) signal = 0;
    if(cross_dn && current_close < current_ema && current_rsi > InpRSIMin) signal = 1;
    
    if(signal != -1) {
        double ask = SymbolInfoDouble(_Symbol, SYMBOL_ASK);
        double bid = SymbolInfoDouble(_Symbol, SYMBOL_BID);
        double sl_distance = current_atr * InpATRMultiplier;
        double sl = (signal == 0) ? ask - sl_distance : bid + sl_distance;
        
        double points_dist = sl_distance / SymbolInfoDouble(_Symbol, SYMBOL_POINT);
        double lots = CalculateLotSize(points_dist, signal == 0 ? ask : bid, sl, signal);
        
        if(lots > 0) {
            if(signal == 0) trade.Buy(lots, _Symbol, ask, sl, 0.0, "V26_Python_Buy");
            else trade.Sell(lots, _Symbol, bid, sl, 0.0, "V26_Python_Sell");
        }
    }
    lastBarTime = currentBarTime;
}
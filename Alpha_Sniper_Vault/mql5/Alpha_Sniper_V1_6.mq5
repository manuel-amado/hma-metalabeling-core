//+------------------------------------------------------------------+
//|                                        Alpha_Sniper_V1_6.mq5     |
//|                                                Copyright 2026    |
//|    Clean Quant + Python ML 2.0 + Escudo Macro Tendencial (ADX)   |
//+------------------------------------------------------------------+
#property copyright "Manuel"
#property link      "https://antigravity.ai"
#property version   "1.6"

#include <Trade\Trade.mqh>

input group "=== Configuracion Base Python ==="
input int    InpHMA_Period       = 200;     
input int    InpEMA_Period       = 400;     
input int    InpStartHour        = 12;
input int    InpEndHour          = 21;
input double InpATRMultiplier    = 1.5;     

input group "=== Escudo de Volatilidad Macro ==="
input double InpMinDailyATR      = 15.0;    

input group "=== Escudo de Tendencia Macro (NUEVO) ==="
input bool   InpUseMacroADX      = true;    // Activar Escudo ADX Diario
input int    InpMacroADXPeriod   = 14;      // Periodos ADX
input double InpMacroADXMin      = 25.0;    // Minima fuerza tendencial para operar

input group "=== Logica de Agotamiento (RSI) ==="
input int    InpRSIPeriod        = 14;      
input int    InpRSILookback      = 20;      
input double InpRSILongOrigin    = 45.0;    
input double InpRSIShortOrigin   = 55.0;    
input double InpRSIMin           = 30.0;    
input double InpRSIMax           = 70.0;    

input group "=== Filtros Experimentales (Auditoria) ==="
input double InpMaxImpulseATR    = 100.0;   
input int    InpMinBuildupBars   = 0;       
input double InpMaxDistEMA       = 100.0;   
input double InpMinBreakout      = 0.0;     

input group "=== Inteligencia Artificial ==="
input bool   InpUseAI            = true;

input group "=== Gestion de Riesgo ==="
input bool   InpUseCompounding   = false;   
input double InpRiskPct          = 1.0;     
input double InpFixedBalance     = 100000.0;

CTrade trade;
int hma_handle, ema_handle, rsi_handle, atr_handle, atr_d1_handle, adx_d1_handle;
datetime lastBarTime = 0;

int OnInit() {
    hma_handle = iCustom(_Symbol, _Period, "HMA50", InpHMA_Period);
    ema_handle = iMA(_Symbol, _Period, InpEMA_Period, 0, MODE_EMA, PRICE_CLOSE);
    rsi_handle = iRSI(_Symbol, _Period, InpRSIPeriod, PRICE_CLOSE);
    atr_handle = iATR(_Symbol, _Period, 14);
    atr_d1_handle = iATR(_Symbol, PERIOD_D1, 14); 
    adx_d1_handle = iADX(_Symbol, PERIOD_D1, InpMacroADXPeriod);

    if(hma_handle == INVALID_HANDLE || ema_handle == INVALID_HANDLE || 
       rsi_handle == INVALID_HANDLE || atr_handle == INVALID_HANDLE || 
       atr_d1_handle == INVALID_HANDLE || adx_d1_handle == INVALID_HANDLE) {
        Print("ERROR: No se pudieron cargar los indicadores.");
        return INIT_FAILED;
    }
    
    trade.SetExpertMagicNumber(28006); // Magic actualizado para V1.6
    return INIT_SUCCEEDED;
}

void OnDeinit(const int reason) {
    IndicatorRelease(hma_handle);
    IndicatorRelease(ema_handle);
    IndicatorRelease(rsi_handle);
    IndicatorRelease(atr_handle);
    IndicatorRelease(atr_d1_handle);
    IndicatorRelease(adx_d1_handle);
}

// BLOQUE DE IA ROBUSTO V2.0 
bool IsTradeAllowedByAI(double RSI, double ATR, double Dist_EMA, int Hour, int DayOfWeek, int Signal) {
    if (ATR <= 2.9650) {
        return false;
    } else {
        if (Dist_EMA <= -2.7500) {
            return false;
        } else {
            return true;
        }
    }
}

double CalculateLotSize(double sl_distance_points, double open_price, double sl_price, int type) {
    if(sl_distance_points <= 0) return 0.0;
    
    double capital = InpFixedBalance;
    if(InpUseCompounding) {
        capital = AccountInfoDouble(ACCOUNT_EQUITY);
        if(capital <= 0) capital = InpFixedBalance;
    }
    
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
    
    double hma[], ema[], rsi[], atr[], atr_d1[], adx_d1[];
    MqlRates rates[];
    
    ArraySetAsSeries(hma, true); ArraySetAsSeries(ema, true);
    ArraySetAsSeries(rsi, true); ArraySetAsSeries(atr, true);
    ArraySetAsSeries(atr_d1, true); ArraySetAsSeries(adx_d1, true); 
    ArraySetAsSeries(rates, true);
    
    int max_lookback = InpRSILookback;
    if(InpMinBuildupBars > max_lookback) max_lookback = InpMinBuildupBars;
    if(20 > max_lookback) max_lookback = 20; 
    int copy_len = max_lookback + 2;
    if(copy_len < 3) copy_len = 3;

    if(CopyRates(_Symbol, _Period, 0, copy_len, rates) < copy_len) return;
    if(CopyBuffer(hma_handle, 0, 0, copy_len, hma) < copy_len) return;
    if(CopyBuffer(ema_handle, 0, 0, 3, ema) < 3) ArrayInitialize(ema, rates[1].close);
    if(CopyBuffer(rsi_handle, 0, 0, copy_len, rsi) < copy_len) return; 
    if(CopyBuffer(atr_handle, 0, 0, 3, atr) < 3) ArrayInitialize(atr, rates[1].high - rates[1].low);
    if(CopyBuffer(atr_d1_handle, 0, 0, 2, atr_d1) < 2) return;
    if(CopyBuffer(adx_d1_handle, 0, 0, 2, adx_d1) < 2) return; // 0 es el buffer principal de fuerza ADX
    
    double current_close = rates[1].close;
    double current_hma = hma[1];
    double prev_close = rates[2].close;
    double prev_hma = hma[2];
    double current_ema = ema[1];
    double current_rsi = rsi[1];
    double current_atr = atr[1];
    double current_daily_atr = atr_d1[1];
    double current_daily_adx = adx_d1[1];
    
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
    
    // 2. ESCUDOS MACRO Y HORARIO
    MqlDateTime dt;
    TimeToStruct(currentBarTime, dt);
    
    // Filtro de Volatilidad (ATR)
    if(current_daily_atr < InpMinDailyATR) { lastBarTime = currentBarTime; return; }
    
    // Filtro de Tendencia (ADX) - NUEVO
    if(InpUseMacroADX && current_daily_adx < InpMacroADXMin) { lastBarTime = currentBarTime; return; }
    
    if(dt.hour < InpStartHour || dt.hour >= InpEndHour) { lastBarTime = currentBarTime; return; }
    
    // 3. GESTION DE ENTRADAS
    int signal = 0;
    bool cross_up = (prev_close < prev_hma && current_close > current_hma);
    bool cross_dn = (prev_close > prev_hma && current_close < current_hma);
    
    bool valid_rsi_origin_long = false;
    bool valid_rsi_origin_short = false;

    if(cross_up) {
        for(int i = 1; i <= InpRSILookback; i++) {
            if(rsi[i] < InpRSILongOrigin) { valid_rsi_origin_long = true; break; }
        }
    }
    if(cross_dn) {
        for(int i = 1; i <= InpRSILookback; i++) {
            if(rsi[i] > InpRSIShortOrigin) { valid_rsi_origin_short = true; break; }
        }
    }
    
    bool valid_buildup = true;
    if(InpMinBuildupBars > 0) {
        if(cross_up) {
            for(int i = 2; i <= InpMinBuildupBars + 1; i++) {
                if(rates[i].close >= hma[i]) { valid_buildup = false; break; }
            }
        }
        else if(cross_dn) {
            for(int i = 2; i <= InpMinBuildupBars + 1; i++) {
                if(rates[i].close <= hma[i]) { valid_buildup = false; break; }
            }
        }
    }

    bool valid_impulse = true;
    if(InpMaxImpulseATR < 100.0) {
        if(cross_up) {
            double lowest_low = rates[1].low;
            for(int i=1; i<=20; i++) if(rates[i].low < lowest_low) lowest_low = rates[i].low;
            double impulse_size = (current_close - lowest_low) / current_atr;
            if(impulse_size > InpMaxImpulseATR) valid_impulse = false;
        }
        else if(cross_dn) {
            double highest_high = rates[1].high;
            for(int i=1; i<=20; i++) if(rates[i].high > highest_high) highest_high = rates[i].high;
            double impulse_size = (highest_high - current_close) / current_atr;
            if(impulse_size > InpMaxImpulseATR) valid_impulse = false;
        }
    }

    double dist_ema_atr = MathAbs(current_close - current_ema) / current_atr;
    double breakout_atr = MathAbs(current_close - current_hma) / current_atr;
    bool valid_structure = (dist_ema_atr <= InpMaxDistEMA && breakout_atr >= InpMinBreakout);

    if(cross_up && current_close > current_ema && current_rsi < InpRSIMax && valid_rsi_origin_long && valid_buildup && valid_impulse && valid_structure) signal = 1;
    if(cross_dn && current_close < current_ema && current_rsi > InpRSIMin && valid_rsi_origin_short && valid_buildup && valid_impulse && valid_structure) signal = -1;
    
    if(signal != 0) {
        if(InpUseAI) {
            double dist_ema_ai = (current_close - current_ema) / current_atr;
            if(!IsTradeAllowedByAI(current_rsi, current_atr, dist_ema_ai, dt.hour, dt.day_of_week, signal)) {
                lastBarTime = currentBarTime;
                return; 
            }
        }
        
        double ask = SymbolInfoDouble(_Symbol, SYMBOL_ASK);
        double bid = SymbolInfoDouble(_Symbol, SYMBOL_BID);
        double sl_distance = current_atr * InpATRMultiplier;
        double sl = (signal == 1) ? ask - sl_distance : bid + sl_distance;
        
        double points_dist = sl_distance / SymbolInfoDouble(_Symbol, SYMBOL_POINT);
        double lots = CalculateLotSize(points_dist, signal == 1 ? ask : bid, sl, signal);
        
        if(lots > 0) {
            if(signal == 1) trade.Buy(lots, _Symbol, ask, sl, 0.0, "V1.6_Buy");
            else trade.Sell(lots, _Symbol, bid, sl, 0.0, "V1.6_Sell");
        }
    }
    lastBarTime = currentBarTime;
}
//+------------------------------------------------------------------+
//| Bot: HMA_TF_v2_Filters.mq5                                
//| Familia: Trend Following (Macro EMA + HMA pullback + RSI Exhaustion)                      
//|                                                                  
//| [CHANGELOG & EVOLUCION]:                                         
//| Filtros adicionales de acumulacion (buildup) y distancia maxima a la EMA para evitar regresiones tardias.
//+------------------------------------------------------------------+
//+------------------------------------------------------------------+
//|                                     Alpha_Sniper_Master2.mq5     |
//|                                                Copyright 2026    |
//|    Clean Quant + Python ML 2.0 + Advanced Trade Management       |
//+------------------------------------------------------------------+
#property copyright "Manuel"
#property link      "https://antigravity.ai"
#property version   "2.1"

#include <Trade\Trade.mqh>

input group "=== Configuracion Base Python ==="
input int    InpHMA_Period       = 200;     
input int    InpEMA_Period       = 400;     
input int    InpStartHour        = 12;
input int    InpEndHour          = 21;
input double InpATRMultiplier    = 1.5;     

input group "=== Escudo de Regimen Macro ==="
input double InpMinDailyATR      = 15.0;    

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

input group "=== Gestion de Riesgo Base ==="
input bool   InpUseCompounding   = false;   
input double InpRiskPct          = 1.0;     
input double InpFixedBalance     = 100000.0;

input group "=== Trade Management (Master2) ==="
input bool   InpUseTradeManagement = false;   // Activar Gestion Avanzada (Master2)
input double InpBE_Trigger_R       = 0.0;     // R-Multiplo para Break-Even (0=Off)
input int    InpBE_Extra_Points    = 20;      // Puntos extra en Break-Even
input double InpPartialTP_R        = 0.0;     // R-Multiplo para Toma Parcial (0=Off)
input double InpPartialTP_Pct      = 50.0;    // Porcentaje del lote a cerrar
input double InpTrail_Activation_R = 0.0;     // R-Multiplo para Activar Trailing ATR (0=Off)
input double InpTrail_Distance_ATR = 1.5;     // Distancia del Trailing en ATRs

input group "=== Mitigacion Dinamica DD ==="
input bool   InpUseDynamicRisk     = false;   // Reducir riesgo si hay Drawdown
input double InpMaxDrawdown_DD     = 5.0;     // % Drawdown maximo antes de frenar
input double InpReducedRiskPct     = 0.5;     // % Riesgo reducido

CTrade trade;
int hma_handle, ema_handle, rsi_handle, atr_handle, atr_d1_handle;
datetime lastBarTime = 0;

// Estados de gestion
bool be_moved = false;
bool partial_taken = false;
double initial_risk_money = 0.0;
double high_water_mark = 0.0;

int OnInit() {
    hma_handle = iCustom(_Symbol, _Period, "HMA50", InpHMA_Period);
    ema_handle = iMA(_Symbol, _Period, InpEMA_Period, 0, MODE_EMA, PRICE_CLOSE);
    rsi_handle = iRSI(_Symbol, _Period, InpRSIPeriod, PRICE_CLOSE);
    atr_handle = iATR(_Symbol, _Period, 14);
    atr_d1_handle = iATR(_Symbol, PERIOD_D1, 14); 

    if(hma_handle == INVALID_HANDLE || ema_handle == INVALID_HANDLE || 
       rsi_handle == INVALID_HANDLE || atr_handle == INVALID_HANDLE || atr_d1_handle == INVALID_HANDLE) {
        Print("ERROR: No se pudieron cargar los indicadores.");
        return INIT_FAILED;
    }
    
    trade.SetExpertMagicNumber(28002);
    high_water_mark = AccountInfoDouble(ACCOUNT_EQUITY);
    return INIT_SUCCEEDED;
}

void OnDeinit(const int reason) {
    IndicatorRelease(hma_handle);
    IndicatorRelease(ema_handle);
    IndicatorRelease(rsi_handle);
    IndicatorRelease(atr_handle);
    IndicatorRelease(atr_d1_handle);
}

// IA ROBUSTA V2.0 (Equivalente exacto a V1.5)
bool IsTradeAllowedByAI(double RSI, double ATR, double Dist_EMA, int Hour, int DayOfWeek, int Signal) {
    if (ATR <= 2.9650) return false; 
    else if (Dist_EMA <= -2.7500) return false; 
    else return true;
}

double GetCurrentRiskPct() {
    if(!InpUseDynamicRisk) return InpRiskPct;
    double current_eq = AccountInfoDouble(ACCOUNT_EQUITY);
    if(current_eq > high_water_mark) high_water_mark = current_eq;
    double current_dd = (high_water_mark - current_eq) / high_water_mark * 100.0;
    if(current_dd >= InpMaxDrawdown_DD) return InpReducedRiskPct;
    return InpRiskPct;
}

double CalculateLotSize(double sl_distance_points, double open_price, double sl_price, int type, double &out_risk_money) {
    if(sl_distance_points <= 0) return 0.0;
    double capital = InpFixedBalance;
    if(InpUseCompounding) {
        capital = AccountInfoDouble(ACCOUNT_EQUITY);
        if(capital <= 0) capital = InpFixedBalance;
    }
    
    double active_risk_pct = GetCurrentRiskPct();
    double risk_amount = capital * (active_risk_pct / 100.0);
    
    ENUM_ORDER_TYPE order_type = (type == 1) ? ORDER_TYPE_BUY : ORDER_TYPE_SELL;
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
    
    out_risk_money = risk_amount; // Guardar riesgo monetario exacto
    return rounded_lots;
}

void OnTick() {
    datetime currentBarTime = iTime(_Symbol, _Period, 0);
    
    double hma[], ema[], rsi[], atr[], atr_d1[];
    MqlRates rates[];
    
    ArraySetAsSeries(hma, true); ArraySetAsSeries(ema, true);
    ArraySetAsSeries(rsi, true); ArraySetAsSeries(atr, true);
    ArraySetAsSeries(atr_d1, true); ArraySetAsSeries(rates, true);
    
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
    
    double current_close = rates[1].close;
    double current_hma = hma[1];
    double prev_close = rates[2].close;
    double prev_hma = hma[2];
    double current_ema = ema[1];
    double current_rsi = rsi[1];
    double current_atr = atr[1];
    
    // GESTION DE POSICION (MASTER2)
    if(PositionsTotal() > 0) {
        PositionSelect(_Symbol);
        long pos_type = PositionGetInteger(POSITION_TYPE);
        ulong pos_ticket = PositionGetInteger(POSITION_TICKET);
        double pos_price = PositionGetDouble(POSITION_PRICE_OPEN);
        double pos_sl = PositionGetDouble(POSITION_SL);
        double pos_vol = PositionGetDouble(POSITION_VOLUME);
        double profit = PositionGetDouble(POSITION_PROFIT) + PositionGetDouble(POSITION_SWAP);
        
        // Calcular R actual (Beneficio Neto / Riesgo Base)
        double current_R = (initial_risk_money > 0) ? (profit / initial_risk_money) : 0;
        
        // 1. Cierre HMA (Estructural - Identico a V1.5)
        bool close_hma = false;
        if(pos_type == POSITION_TYPE_BUY && current_close < current_hma) close_hma = true;
        if(pos_type == POSITION_TYPE_SELL && current_close > current_hma) close_hma = true;
        
        if(close_hma && currentBarTime != lastBarTime) {
            trade.PositionClose(pos_ticket);
            // Salimos del bloque de gestion pero NO hacemos return, 
            // permitiendo Stop & Reverse en la misma vela (Igual que V1.5)
        } else {
            if(InpUseTradeManagement) {
                double point = SymbolInfoDouble(_Symbol, SYMBOL_POINT);
                double ask = SymbolInfoDouble(_Symbol, SYMBOL_ASK);
                double bid = SymbolInfoDouble(_Symbol, SYMBOL_BID);

                // 2. Break-Even
                if(InpBE_Trigger_R > 0 && current_R >= InpBE_Trigger_R && !be_moved) {
                    double new_sl = 0;
                    if(pos_type == POSITION_TYPE_BUY) new_sl = pos_price + (InpBE_Extra_Points * point);
                    if(pos_type == POSITION_TYPE_SELL) new_sl = pos_price - (InpBE_Extra_Points * point);
                    
                    if(pos_type == POSITION_TYPE_BUY && new_sl > pos_sl) {
                        if(trade.PositionModify(pos_ticket, new_sl, 0)) be_moved = true;
                    }
                    if(pos_type == POSITION_TYPE_SELL && (new_sl < pos_sl || pos_sl == 0)) {
                        if(trade.PositionModify(pos_ticket, new_sl, 0)) be_moved = true;
                    }
                }
                
                // 3. Cierre Parcial
                if(InpPartialTP_R > 0 && current_R >= InpPartialTP_R && !partial_taken) {
                    double lot_step = SymbolInfoDouble(_Symbol, SYMBOL_VOLUME_STEP);
                    double close_vol = MathFloor((pos_vol * (InpPartialTP_Pct / 100.0)) / lot_step) * lot_step;
                    if(close_vol > 0 && close_vol < pos_vol) {
                        if(trade.PositionClosePartial(pos_ticket, close_vol)) partial_taken = true;
                    } else { partial_taken = true; } 
                }

                // 4. Trailing Stop ATR
                if(InpTrail_Activation_R > 0 && current_R >= InpTrail_Activation_R) {
                    double trail_dist = current_atr * InpTrail_Distance_ATR;
                    double new_sl = 0;
                    if(pos_type == POSITION_TYPE_BUY) {
                        new_sl = bid - trail_dist;
                        if(new_sl > pos_sl) trade.PositionModify(pos_ticket, new_sl, 0);
                    } else {
                        new_sl = ask + trail_dist;
                        if(new_sl < pos_sl || pos_sl == 0) trade.PositionModify(pos_ticket, new_sl, 0);
                    }
                }
                return; // Permite actualizaciones intrabarra de gestion
            } else {
                // MATCH EXACTO CON V1.5
                lastBarTime = currentBarTime; 
                return;
            }
        }
    }
    
    if(currentBarTime == lastBarTime) return;
    
    // GESTION DE ENTRADAS (IDENTICO A V1.5)
    MqlDateTime dt;
    TimeToStruct(currentBarTime, dt);
    
    if(atr_d1[1] < InpMinDailyATR) { lastBarTime = currentBarTime; return; }
    if(dt.hour < InpStartHour || dt.hour >= InpEndHour) { lastBarTime = currentBarTime; return; }
    
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
        
        double risk_money = 0;
        double points_dist = sl_distance / SymbolInfoDouble(_Symbol, SYMBOL_POINT);
        double lots = CalculateLotSize(points_dist, signal == 1 ? ask : bid, sl, signal, risk_money);
        
        if(lots > 0) {
            bool result = false;
            if(signal == 1) result = trade.Buy(lots, _Symbol, ask, sl, 0.0, "Master2_Buy");
            else result = trade.Sell(lots, _Symbol, bid, sl, 0.0, "Master2_Sell");
            
            if(result) {
                be_moved = false;
                partial_taken = false;
                initial_risk_money = risk_money;
            }
        }
    }
    lastBarTime = currentBarTime;
}

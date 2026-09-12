//+------------------------------------------------------------------+
//| Bot: HMA_BRK_v30_AI.mq5                                
//| Familia: Breakout (Mean Reversion over HMA)                      
//|                                                                  
//| [CHANGELOG & EVOLUCION]:                                         
//| Ultima generacion AI Breakout pre-Omni. Maxima rigurosidad en los filtros de entrada y correlaciones HMA.
//+------------------------------------------------------------------+
//+------------------------------------------------------------------+
//|                                        Alpha_Sniper_V30_AI.mq5   |
//|                                                Copyright 2026    |
//|               Clean Quant + Python MetaLabeling AI (Decision Tree)|
//+------------------------------------------------------------------+
#property copyright "Manuel"
#property link      "https://antigravity.ai"
#property version   "30.0"

#include <Trade\Trade.mqh>

input group "=== Configuracion Base Python ==="
input int    InpHMA_Period       = 200;     // HMA Lenta (Direccion Macro)
input int    InpHMA_Exit_Period  = 50;      // HMA Rapida (Salida Asimetrica)
input int    InpEMA_Period       = 400;     
input int    InpRSIPeriod        = 14;      
input double InpRSIMin           = 30.0;    
input double InpRSIMax           = 70.0;    
input int    InpStartHour        = 12;
input int    InpEndHour          = 21;
input double InpATRMultiplier    = 1.5;     

input group "=== Filtros de Ruido y Tendencia ==="
input int    InpADXPeriod        = 14;      // Periodo del ADX
input double InpMinADX           = 25.0;    // Minimo ADX para permitir operar (>25 = Tendencia)

input group "=== Inteligencia Artificial ==="
input bool   InpUseAI            = true;

input group "=== Gestion de Riesgo (Risk 1%) ==="
input double InpRiskPct          = 1.0;     
input double InpFixedBalance     = 100000.0;

CTrade trade;
int hma_handle, hma_exit_handle, ema_handle, rsi_handle, atr_handle, adx_handle;
datetime lastBarTime = 0;

int OnInit() {
    hma_handle = iCustom(_Symbol, _Period, "HMA50", InpHMA_Period);
    hma_exit_handle = iCustom(_Symbol, _Period, "HMA50", InpHMA_Exit_Period);
    ema_handle = iMA(_Symbol, _Period, InpEMA_Period, 0, MODE_EMA, PRICE_CLOSE);
    rsi_handle = iRSI(_Symbol, _Period, InpRSIPeriod, PRICE_CLOSE);
    atr_handle = iATR(_Symbol, _Period, 14);
    adx_handle = iADX(_Symbol, _Period, InpADXPeriod);

    if(hma_handle == INVALID_HANDLE || hma_exit_handle == INVALID_HANDLE || ema_handle == INVALID_HANDLE || 
       rsi_handle == INVALID_HANDLE || atr_handle == INVALID_HANDLE || adx_handle == INVALID_HANDLE) {
        Print("ERROR: No se pudieron cargar los indicadores.");
        return INIT_FAILED;
    }
    
    trade.SetExpertMagicNumber(30000);
    return INIT_SUCCEEDED;
}

void OnDeinit(const int reason) {
    IndicatorRelease(hma_handle);
    IndicatorRelease(hma_exit_handle);
    IndicatorRelease(ema_handle);
    IndicatorRelease(rsi_handle);
    IndicatorRelease(atr_handle);
    IndicatorRelease(adx_handle);
}

bool IsTradeAllowedByAI(double RSI, double ATR, double Dist_EMA, int Hour, int DayOfWeek, int Signal) {
    if (Hour <= 14.5000) {
        if (RSI <= 44.3391) {
            if (ATR <= 2.3229) {
                return false; 
            } else {
                return false; 
            }
        } else {
            if (RSI <= 52.1705) {
                if (ATR <= 2.0954) {
                    return false; 
                } else {
                    return true; 
                }
            } else {
                if (ATR <= 2.5179) {
                    return false; 
                } else {
                    return false; 
                }
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
                if (ATR <= 3.3679) {
                    return false; 
                } else {
                    return false; 
                }
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
    
    double hma[], hma_exit[], ema[], rsi[], atr[], adx[];
    MqlRates rates[];
    
    ArraySetAsSeries(hma, true); ArraySetAsSeries(hma_exit, true);
    ArraySetAsSeries(ema, true); ArraySetAsSeries(rsi, true); 
    ArraySetAsSeries(atr, true); ArraySetAsSeries(adx, true);
    ArraySetAsSeries(rates, true);
    
    if(CopyRates(_Symbol, _Period, 0, 3, rates) < 3) return;
    if(CopyBuffer(hma_handle, 0, 0, 3, hma) < 3) return;
    if(CopyBuffer(hma_exit_handle, 0, 0, 3, hma_exit) < 3) return;
    if(CopyBuffer(ema_handle, 0, 0, 3, ema) < 3) ArrayInitialize(ema, rates[1].close);
    if(CopyBuffer(rsi_handle, 0, 0, 3, rsi) < 3) ArrayInitialize(rsi, 50.0);
    if(CopyBuffer(atr_handle, 0, 0, 3, atr) < 3) ArrayInitialize(atr, rates[1].high - rates[1].low);
    if(CopyBuffer(adx_handle, 0, 0, 3, adx) < 3) ArrayInitialize(adx, 0.0);
    
    double current_close = rates[1].close;
    double current_hma = hma[1];
    double current_hma_exit = hma_exit[1];
    
    double prev_close = rates[2].close;
    double prev_hma = hma[2];
    
    double current_ema = ema[1];
    double current_rsi = rsi[1];
    double current_atr = atr[1];
    double current_adx = adx[1];
    
    // 1. GESTION DE SALIDAS (Activo 24/7 - Asimetrica)
    int pos_total = PositionsTotal();
    bool has_open_pos = false;
    for(int i = pos_total - 1; i >= 0; i--) {
        if(PositionGetSymbol(i) == _Symbol) {
            has_open_pos = true;
            long pos_type = PositionGetInteger(POSITION_TYPE);
            ulong pos_ticket = PositionGetInteger(POSITION_TICKET);
            
            bool close_it = false;
            // Salimos con la HMA RAPIDA en vez de la lenta
            if(pos_type == POSITION_TYPE_BUY && current_close < current_hma_exit) close_it = true;
            if(pos_type == POSITION_TYPE_SELL && current_close > current_hma_exit) close_it = true;
            
            if(close_it) {
                trade.PositionClose(pos_ticket);
                has_open_pos = false; 
            }
        }
    }
    
    if(has_open_pos) { lastBarTime = currentBarTime; return; }
    
    // 2. FILTRO DE HORARIO PARA ENTRADAS
    MqlDateTime dt;
    TimeToStruct(currentBarTime, dt);
    if(dt.hour < InpStartHour || dt.hour >= InpEndHour) {
        lastBarTime = currentBarTime;
        return;
    }
    
    // 3. GESTION DE ENTRADAS (Con filtro ADX)
    int signal = -1;
    bool cross_up = (prev_close < prev_hma && current_close > current_hma);
    bool cross_dn = (prev_close > prev_hma && current_close < current_hma);
    
    if(cross_up && current_close > current_ema && current_rsi < InpRSIMax && current_adx >= InpMinADX) signal = 1;
    if(cross_dn && current_close < current_ema && current_rsi > InpRSIMin && current_adx >= InpMinADX) signal = -1;
    
    if(signal != -1) {
        // --- META LABELING AI FILTER ---
        if(InpUseAI) {
            double dist_ema = (current_close - current_ema) / current_atr;
            if(!IsTradeAllowedByAI(current_rsi, current_atr, dist_ema, dt.hour, dt.day_of_week, signal)) {
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
            if(signal == 1) trade.Buy(lots, _Symbol, ask, sl, 0.0, "V30_Buy");
            else trade.Sell(lots, _Symbol, bid, sl, 0.0, "V30_Sell");
        }
    }
    lastBarTime = currentBarTime;
}

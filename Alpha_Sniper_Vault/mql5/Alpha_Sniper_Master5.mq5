//+------------------------------------------------------------------+
//|                                     Alpha_Sniper_Master5.mq5     |
//|                                                Copyright 2026    |
//|         Equity Curve Trading: Cooldowns & Circuit Breakers       |
//+------------------------------------------------------------------+
#property copyright "Manuel"
#property link      "https://antigravity.ai"
#property version   "5.0"

#include <Trade\Trade.mqh>

input group "=== Configuracion Base Python ==="
input int    InpHMA_Period       = 200;
input int    InpEMA_Period       = 400;
input int    InpStartHour        = 1;
input int    InpEndHour          = 23;
input double InpATRMultiplier    = 1.4;

input group "=== Escudo de Regimen Macro ==="
input double InpMinDailyATR      = 15.0;

input group "=== Logica de Agotamiento (RSI) ==="
input int    InpRSIPeriod        = 14;
input int    InpRSILookback      = 20;
input double InpRSILongOrigin    = 48.0;
input double InpRSIShortOrigin   = 60.0;
input double InpRSIMin           = 30.0;
input double InpRSIMax           = 70.0;

input group "=== Filtros Experimentales (Auditoria) ==="
input double InpMaxSignalBarATR  = 3.0; // Evita comprar puntas tras explosiones (Cisnes Negros)
input double InpMaxImpulseATR    = 4.0;
input int    InpMinBuildupBars   = 0;
input double InpMaxDistEMA       = 100.0;
input double InpMinBreakout      = 0.0;

input group "=== Escudos de Curva de Capital (ECT) ==="
input bool   InpUseECT                = true; // Activar modulo ECT
input int    InpPostWinCooldownBars   = 96;   // (Regla 1) OPTIMO OOS
input int    InpToxicStreakLevel      = 9;    // (Regla 2) OPTIMO OOS
input int    InpPostLossPauseBars     = 192;  // (Regla 3) OPTIMO OOS

input group "=== Gestion de Riesgo ==="
input bool   InpUseCompounding   = false;
input double InpRiskPct          = 1.0;
input double InpFixedBalance     = 100000.0;

CTrade trade;
int hma_handle, ema_handle, rsi_handle, atr_handle, atr_d1_handle;
datetime lastBarTime = 0;

// ECT Variables
datetime last_win_time     = 0;
datetime last_loss_time    = 0;
int      loss_streak       = 0;
double   last_trade_profit = 0;

int OnInit() {
    hma_handle    = iCustom(_Symbol, _Period, "HMA50", InpHMA_Period);
    ema_handle    = iMA(_Symbol, _Period, InpEMA_Period, 0, MODE_EMA, PRICE_CLOSE);
    rsi_handle    = iRSI(_Symbol, _Period, InpRSIPeriod, PRICE_CLOSE);
    atr_handle    = iATR(_Symbol, _Period, 14);
    atr_d1_handle = iATR(_Symbol, PERIOD_D1, 14);

    if(hma_handle == INVALID_HANDLE || ema_handle == INVALID_HANDLE ||
       rsi_handle == INVALID_HANDLE || atr_handle == INVALID_HANDLE || atr_d1_handle == INVALID_HANDLE) {
        Print("ERROR: No se pudieron cargar los indicadores.");
        return INIT_FAILED;
    }
    trade.SetExpertMagicNumber(28005);
    return INIT_SUCCEEDED;
}

void OnDeinit(const int reason) {
    IndicatorRelease(hma_handle); IndicatorRelease(ema_handle);
    IndicatorRelease(rsi_handle); IndicatorRelease(atr_handle);
    IndicatorRelease(atr_d1_handle);
}

// Analiza el historial de operaciones para actualizar el estado del ECT
void UpdateEquityState() {
    HistorySelect(0, TimeCurrent());
    loss_streak = 0;
    last_win_time = 0;
    last_loss_time = 0;
    last_trade_profit = 0;
    
    int total = HistoryDealsTotal();
    for(int i = total - 1; i >= 0; i--) {
        ulong ticket = HistoryDealGetTicket(i);
        long entry = HistoryDealGetInteger(ticket, DEAL_ENTRY);
        if(entry == DEAL_ENTRY_OUT || entry == DEAL_ENTRY_INOUT) {
            double pnl = HistoryDealGetDouble(ticket, DEAL_PROFIT) + 
                         HistoryDealGetDouble(ticket, DEAL_SWAP) + 
                         HistoryDealGetDouble(ticket, DEAL_COMMISSION);
            datetime dt = (datetime)HistoryDealGetInteger(ticket, DEAL_TIME);
            
            if(last_trade_profit == 0) last_trade_profit = pnl; // Guarda el resultado del ultimo trade
            
            if(pnl <= 0) {
                if(loss_streak == 0) last_loss_time = dt; // Registra el inicio del cooldown de la ultima perdida
                loss_streak++;
            } else if(pnl > 0) {
                if(last_win_time == 0) last_win_time = dt;
                break; // Rompe el bucle en cuanto encuentra la ultima ganancia (fin de la racha)
            }
        }
    }
}

double CalculateLotSize(double open_price, double sl_price, int type) {
    double capital = InpFixedBalance;
    if(InpUseCompounding) {
        capital = AccountInfoDouble(ACCOUNT_EQUITY);
        if(capital <= 0) capital = InpFixedBalance;
    }
    double risk_amount = capital * (InpRiskPct / 100.0);
    ENUM_ORDER_TYPE order_type = (type == 1) ? ORDER_TYPE_BUY : ORDER_TYPE_SELL;
    double expected_loss = 0.0;
    if(!OrderCalcProfit(order_type, _Symbol, 1.0, open_price, sl_price, expected_loss)) return 0.0;
    double abs_loss = MathAbs(expected_loss);
    if(abs_loss <= 0.000001) return 0.0;
    double calculated_lots = risk_amount / abs_loss;
    double lot_step = SymbolInfoDouble(_Symbol, SYMBOL_VOLUME_STEP);
    double min_lot  = SymbolInfoDouble(_Symbol, SYMBOL_VOLUME_MIN);
    double max_lot  = SymbolInfoDouble(_Symbol, SYMBOL_VOLUME_MAX);
    double rounded_lots = MathFloor(calculated_lots / lot_step) * lot_step;
    if(rounded_lots < min_lot) rounded_lots = min_lot;
    if(rounded_lots > max_lot) rounded_lots = max_lot;
    return rounded_lots;
}

void OnTick() {
    datetime currentBarTime = iTime(_Symbol, _Period, 0);
    if(currentBarTime == lastBarTime || currentBarTime == 0) return;

    int copy_len = MathMax(InpRSILookback, InpMinBuildupBars);
    copy_len = MathMax(copy_len, 25);
    
    double hma[], ema[], rsi[], atr[], atr_d1[];
    MqlRates rates[];
    ArraySetAsSeries(hma, true);  ArraySetAsSeries(ema, true);
    ArraySetAsSeries(rsi, true);  ArraySetAsSeries(atr, true);
    ArraySetAsSeries(atr_d1, true); ArraySetAsSeries(rates, true);

    if(CopyRates(_Symbol, _Period, 0, copy_len, rates) < copy_len) return;
    if(CopyBuffer(hma_handle, 0, 0, copy_len, hma) < copy_len) return;
    if(CopyBuffer(ema_handle, 0, 0, 4, ema) < 4) ArrayInitialize(ema, rates[1].close);
    if(CopyBuffer(rsi_handle, 0, 0, copy_len, rsi) < copy_len) return;
    if(CopyBuffer(atr_handle, 0, 0, 4, atr) < 4) ArrayInitialize(atr, rates[1].high - rates[1].low);
    if(CopyBuffer(atr_d1_handle, 0, 0, 2, atr_d1) < 2) return;

    double current_close = rates[1].close;
    double current_hma   = hma[1];
    double prev_close    = rates[2].close;
    double prev_hma      = hma[2];
    double current_ema   = ema[1];
    double current_rsi   = rsi[1];
    double current_atr   = atr[1];

    // ---- GESTION DE POSICION (Salida Base: Cruce HMA) ----
    if(PositionsTotal() > 0) {
        PositionSelect(_Symbol);
        long pos_type   = PositionGetInteger(POSITION_TYPE);
        ulong pos_ticket = PositionGetInteger(POSITION_TICKET);
        bool close_it = false;
        
        if(pos_type == POSITION_TYPE_BUY  && current_close < current_hma) close_it = true;
        if(pos_type == POSITION_TYPE_SELL && current_close > current_hma) close_it = true;
        
        if(close_it) trade.PositionClose(pos_ticket);
        lastBarTime = currentBarTime;
        return;
    }

    // ---- ESCUDOS MACRO Y HORARIO ----
    MqlDateTime dt;
    TimeToStruct(currentBarTime, dt);
    if(atr_d1[1] < InpMinDailyATR) { lastBarTime = currentBarTime; return; }
    if(dt.hour < InpStartHour || dt.hour >= InpEndHour) { lastBarTime = currentBarTime; return; }
    
    // ---- ANTI-CISNES NEGROS (V16) ----
    double candle_size = rates[1].high - rates[1].low;
    if(InpMaxSignalBarATR < 99.0 && candle_size > (current_atr * InpMaxSignalBarATR)) {
        lastBarTime = currentBarTime; 
        return; // Vela explosiva (FOMC/NFP), no perseguir el precio
    }

    // ---- EQUITY CURVE TRADING (Circuit Breakers) ----
    if(InpUseECT) {
        UpdateEquityState();
        
        // 1. Resaca Post-Ganancia
        if(last_trade_profit > 0 && last_win_time > 0) {
            if(TimeCurrent() < last_win_time + InpPostWinCooldownBars * PeriodSeconds()) {
                lastBarTime = currentBarTime; return; // Bloqueado por ganancia reciente
            }
        }
        
        // 2 y 3. Mercado Toxico (Circuit Breaker Post-Perdida)
        if(loss_streak >= InpToxicStreakLevel) {
            if(TimeCurrent() < last_loss_time + InpPostLossPauseBars * PeriodSeconds()) {
                lastBarTime = currentBarTime; return; // Bloqueado por racha perdedora activa
            }
        }
    }


    // ---- SEÑAL DE ENTRADA ----
    int signal = 0;
    bool cross_up = (prev_close < prev_hma && current_close > current_hma);
    bool cross_dn = (prev_close > prev_hma && current_close < current_hma);

    bool valid_rsi_long  = false, valid_rsi_short = false;
    if(cross_up) { for(int i=1; i<=InpRSILookback; i++) { if(rsi[i] < InpRSILongOrigin)  { valid_rsi_long  = true; break; } } }
    if(cross_dn) { for(int i=1; i<=InpRSILookback; i++) { if(rsi[i] > InpRSIShortOrigin) { valid_rsi_short = true; break; } } }

    bool valid_buildup = true;
    if(InpMinBuildupBars > 0) {
        if(cross_up) { for(int i=2; i<=InpMinBuildupBars+1; i++) { if(rates[i].close >= hma[i]) { valid_buildup = false; break; } } }
        if(cross_dn) { for(int i=2; i<=InpMinBuildupBars+1; i++) { if(rates[i].close <= hma[i]) { valid_buildup = false; break; } } }
    }

    bool valid_impulse = true;
    if(InpMaxImpulseATR < 99.0) {
        if(cross_up) {
            double lowest  = rates[1].low;
            for(int i=1; i<=20; i++) if(rates[i].low  < lowest)  lowest  = rates[i].low;
            if((current_close - lowest) / current_atr > InpMaxImpulseATR) valid_impulse = false;
        }
        if(cross_dn) {
            double highest = rates[1].high;
            for(int i=1; i<=20; i++) if(rates[i].high > highest) highest = rates[i].high;
            if((highest - current_close) / current_atr > InpMaxImpulseATR) valid_impulse = false;
        }
    }

    double dist_ema_atr  = MathAbs(current_close - current_ema) / current_atr;
    double breakout_atr  = MathAbs(current_close - current_hma) / current_atr;
    bool valid_structure = (dist_ema_atr <= InpMaxDistEMA && breakout_atr >= InpMinBreakout);

    if(cross_up && current_close > current_ema && current_rsi < InpRSIMax && valid_rsi_long  && valid_buildup && valid_impulse && valid_structure) signal =  1;
    if(cross_dn && current_close < current_ema && current_rsi > InpRSIMin && valid_rsi_short && valid_buildup && valid_impulse && valid_structure) signal = -1;

    if(signal != 0) {
        double ask = SymbolInfoDouble(_Symbol, SYMBOL_ASK);
        double bid = SymbolInfoDouble(_Symbol, SYMBOL_BID);
        double sl_dist = current_atr * InpATRMultiplier;
        double sl = (signal == 1) ? ask - sl_dist : bid + sl_dist;

        double lots = CalculateLotSize(signal == 1 ? ask : bid, sl, signal);
        if(lots > 0) {
            if(signal ==  1) trade.Buy (lots, _Symbol, ask, sl, 0.0, "Master5_Buy");
            if(signal == -1) trade.Sell(lots, _Symbol, bid, sl, 0.0, "Master5_Sell");
        }
    }
    lastBarTime = currentBarTime;
}
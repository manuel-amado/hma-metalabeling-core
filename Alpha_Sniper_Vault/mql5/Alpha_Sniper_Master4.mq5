//+------------------------------------------------------------------+
//|                                     Alpha_Sniper_Master4.mq5     |
//|                                                Copyright 2026    |
//|    Segunda Derivada como FILTRO DE ENTRADA (no de salida)        |
//+------------------------------------------------------------------+
#property copyright "Manuel"
#property link      "https://antigravity.ai"
#property version   "4.1"

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
input double InpMaxImpulseATR    = 4.0;
input int    InpMinBuildupBars   = 0;
input double InpMaxDistEMA       = 100.0;
input double InpMinBreakout      = 0.0;

input group "=== Inteligencia Artificial ==="
input bool   InpUseAI            = false;

input group "=== Filtro de Entrada: Segunda Derivada HMA (Master4) ==="
input bool   InpUseAccelEntry    = true;   // Solo entrar si la HMA tiene aceleracion positiva
input int    InpAccelConfirmBars = 1;      // Barras consecutivas de aceleracion positiva requeridas (1-5)

input group "=== Gestion de Riesgo ==="
input bool   InpUseCompounding   = false;
input double InpRiskPct          = 1.0;
input double InpFixedBalance     = 100000.0;

CTrade trade;
int hma_handle, ema_handle, rsi_handle, atr_handle, atr_d1_handle;
datetime lastBarTime = 0;

int OnInit() {
    hma_handle    = iCustom(_Symbol, _Period, "HMA50", InpHMA_Period);
    ema_handle    = iMA(_Symbol, _Period, InpEMA_Period, 0, MODE_EMA, PRICE_CLOSE);
    rsi_handle    = iRSI(_Symbol, _Period, InpRSIPeriod, PRICE_CLOSE);
    atr_handle    = iATR(_Symbol, _Period, 14);
    atr_d1_handle = iATR(_Symbol, PERIOD_D1, 14);
    if(hma_handle==INVALID_HANDLE || ema_handle==INVALID_HANDLE ||
       rsi_handle==INVALID_HANDLE || atr_handle==INVALID_HANDLE || atr_d1_handle==INVALID_HANDLE) {
        Print("ERROR: No se pudieron cargar los indicadores.");
        return INIT_FAILED;
    }
    trade.SetExpertMagicNumber(28004);
    return INIT_SUCCEEDED;
}

void OnDeinit(const int reason) {
    IndicatorRelease(hma_handle); IndicatorRelease(ema_handle);
    IndicatorRelease(rsi_handle); IndicatorRelease(atr_handle);
    IndicatorRelease(atr_d1_handle);
}

bool IsTradeAllowedByAI(double ATR, double Dist_EMA) {
    if(ATR <= 2.9650) return false;
    if(Dist_EMA <= -2.7500) return false;
    return true;
}

double CalculateLotSize(double open_price, double sl_price, int type) {
    double capital = InpUseCompounding ? AccountInfoDouble(ACCOUNT_EQUITY) : InpFixedBalance;
    if(capital <= 0) capital = InpFixedBalance;
    double risk_amount = capital * (InpRiskPct / 100.0);
    ENUM_ORDER_TYPE ot = (type==1) ? ORDER_TYPE_BUY : ORDER_TYPE_SELL;
    double exp_loss = 0.0;
    if(!OrderCalcProfit(ot, _Symbol, 1.0, open_price, sl_price, exp_loss)) return 0.0;
    double abs_loss = MathAbs(exp_loss);
    if(abs_loss <= 0.000001) return 0.0;
    double lots = MathFloor((risk_amount/abs_loss) / SymbolInfoDouble(_Symbol,SYMBOL_VOLUME_STEP)) * SymbolInfoDouble(_Symbol,SYMBOL_VOLUME_STEP);
    lots = MathMax(lots, SymbolInfoDouble(_Symbol,SYMBOL_VOLUME_MIN));
    lots = MathMin(lots, SymbolInfoDouble(_Symbol,SYMBOL_VOLUME_MAX));
    return lots;
}

bool CheckAcceleration(double &hma[], int signal, int confirmBars) {
    for(int k=1; k<=confirmBars; k++) {
        double accel = (hma[k]-hma[k+1]) - (hma[k+1]-hma[k+2]);
        if(signal== 1 && accel<=0) return false;
        if(signal==-1 && accel>=0) return false;
    }
    return true;
}

void OnTick() {
    datetime currentBarTime = iTime(_Symbol, _Period, 0);
    if(currentBarTime==lastBarTime || currentBarTime==0) return;

    int copy_len = MathMax(MathMax(InpRSILookback, InpMinBuildupBars), 20) + InpAccelConfirmBars + 5;

    double hma[], ema[], rsi[], atr[], atr_d1[];
    MqlRates rates[];
    ArraySetAsSeries(hma,true); ArraySetAsSeries(ema,true); ArraySetAsSeries(rsi,true);
    ArraySetAsSeries(atr,true); ArraySetAsSeries(atr_d1,true); ArraySetAsSeries(rates,true);

    if(CopyRates(_Symbol,_Period,0,copy_len,rates)<copy_len) return;
    if(CopyBuffer(hma_handle,0,0,copy_len,hma)<copy_len) return;
    if(CopyBuffer(ema_handle,0,0,4,ema)<4) ArrayInitialize(ema,rates[1].close);
    if(CopyBuffer(rsi_handle,0,0,copy_len,rsi)<copy_len) return;
    if(CopyBuffer(atr_handle,0,0,4,atr)<4) ArrayInitialize(atr,rates[1].high-rates[1].low);
    if(CopyBuffer(atr_d1_handle,0,0,2,atr_d1)<2) return;

    double current_close=rates[1].close, current_hma=hma[1], prev_close=rates[2].close, prev_hma=hma[2];
    double current_ema=ema[1], current_rsi=rsi[1], current_atr=atr[1];

    // GESTION DE POSICION: salida identica a Master base
    if(PositionsTotal()>0) {
        PositionSelect(_Symbol);
        long  pt = PositionGetInteger(POSITION_TYPE);
        ulong pk = PositionGetInteger(POSITION_TICKET);
        if((pt==POSITION_TYPE_BUY  && current_close<current_hma) ||
           (pt==POSITION_TYPE_SELL && current_close>current_hma))
            trade.PositionClose(pk);
        lastBarTime = currentBarTime;
        return;
    }

    // ESCUDOS
    MqlDateTime dt; TimeToStruct(currentBarTime, dt);
    if(atr_d1[1]<InpMinDailyATR || dt.hour<InpStartHour || dt.hour>=InpEndHour) { lastBarTime=currentBarTime; return; }

    // SEÑAL
    int signal=0;
    bool cross_up=(prev_close<prev_hma && current_close>current_hma);
    bool cross_dn=(prev_close>prev_hma && current_close<current_hma);

    bool rsi_long=false, rsi_short=false;
    if(cross_up) for(int i=1;i<=InpRSILookback;i++) { if(rsi[i]<InpRSILongOrigin)  { rsi_long =true; break; } }
    if(cross_dn) for(int i=1;i<=InpRSILookback;i++) { if(rsi[i]>InpRSIShortOrigin) { rsi_short=true; break; } }

    bool buildup=true;
    if(InpMinBuildupBars>0) {
        if(cross_up) for(int i=2;i<=InpMinBuildupBars+1;i++) { if(rates[i].close>=hma[i]) { buildup=false; break; } }
        if(cross_dn) for(int i=2;i<=InpMinBuildupBars+1;i++) { if(rates[i].close<=hma[i]) { buildup=false; break; } }
    }

    bool impulse=true;
    if(InpMaxImpulseATR<99.0) {
        if(cross_up) { double lo=rates[1].low;  for(int i=1;i<=20;i++) if(rates[i].low <lo) lo=rates[i].low;  if((current_close-lo)/current_atr>InpMaxImpulseATR) impulse=false; }
        if(cross_dn) { double hi=rates[1].high; for(int i=1;i<=20;i++) if(rates[i].high>hi) hi=rates[i].high; if((hi-current_close)/current_atr>InpMaxImpulseATR) impulse=false; }
    }

    bool structure = (MathAbs(current_close-current_ema)/current_atr<=InpMaxDistEMA &&
                      MathAbs(current_close-current_hma)/current_atr>=InpMinBreakout);

    if(cross_up && current_close>current_ema && current_rsi<InpRSIMax && rsi_long  && buildup && impulse && structure) signal= 1;
    if(cross_dn && current_close<current_ema && current_rsi>InpRSIMin && rsi_short && buildup && impulse && structure) signal=-1;

    if(signal!=0) {
        if(InpUseAccelEntry && !CheckAcceleration(hma, signal, InpAccelConfirmBars)) { lastBarTime=currentBarTime; return; }
        if(InpUseAI) {
            double d=(current_close-current_ema)/current_atr;
            if(!IsTradeAllowedByAI(current_atr,d)) { lastBarTime=currentBarTime; return; }
        }
        double ask=SymbolInfoDouble(_Symbol,SYMBOL_ASK), bid=SymbolInfoDouble(_Symbol,SYMBOL_BID);
        double sl=(signal==1) ? ask-current_atr*InpATRMultiplier : bid+current_atr*InpATRMultiplier;
        double lots=CalculateLotSize(signal==1?ask:bid, sl, signal);
        if(lots>0) {
            if(signal== 1) trade.Buy (lots,_Symbol,ask,sl,0.0,"Master4_Buy");
            if(signal==-1) trade.Sell(lots,_Symbol,bid,sl,0.0,"Master4_Sell");
        }
    }
    lastBarTime=currentBarTime;
}
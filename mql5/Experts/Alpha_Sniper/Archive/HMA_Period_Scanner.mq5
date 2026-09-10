//+------------------------------------------------------------------+
//|                                           HMA_Period_Scanner.mq5 |
//|                             Alpha Protocol - V16 Continuity Edge |
//+------------------------------------------------------------------+
#property copyright "Alpha Protocol"
#property link      ""
#property version   "1.00"
#property script_show_inputs

input int InpMinPeriod = 14;
input int InpMaxPeriod = 50;
input int InpStep = 2;
input int InpMinBuildupBars = 7;
input int InpBarsToAnalyze = 50000;

void OnStart() {
    Print("==================================================");
    Print("?? INICIANDO SCANNER VECTORIAL DE CONTINUIDAD HMA");
    Print("Simulando cruces y recorrido a favor en ", _Symbol, " ", EnumToString(_Period));
    
    MqlRates rates[];
    ArraySetAsSeries(rates, true);
    int copied = CopyRates(_Symbol, _Period, 0, InpBarsToAnalyze, rates);
    if(copied < 1000) { Print("Error al copiar datos."); return; }
    
    double atr[];
    ArraySetAsSeries(atr, true);
    int atr_handle = iATR(_Symbol, _Period, 14);
    CopyBuffer(atr_handle, 0, 0, copied, atr);
    
    int best_period = 0;
    double best_continuity = 0;
    
    for(int p = InpMinPeriod; p <= InpMaxPeriod; p += InpStep) {
        int hma_handle = iCustom(_Symbol, _Period, "HMA50", p);
        double hma_buf[];
        ArraySetAsSeries(hma_buf, true);
        if(CopyBuffer(hma_handle, 0, 0, copied, hma_buf) < copied) continue;
        
        double total_continuity = 0;
        int trades = 0;
        
        for(int i = copied - 60; i > 10; i--) { 
            bool build_up_buy = true;
            for(int j = i+1; j <= i + InpMinBuildupBars; j++) {
                if(rates[j].close >= hma_buf[j]) { build_up_buy = false; break; }
            }
            if(build_up_buy && rates[i].close > hma_buf[i] && rates[i+1].close < hma_buf[i+1]) { 
                double max_high = rates[i].close;
                for(int k = i-1; k >= 0; k--) {
                    if(rates[k].high > max_high) max_high = rates[k].high;
                    if(rates[k].close < hma_buf[k]) break; 
                }
                if(atr[i] > 0) {
                    total_continuity += (max_high - rates[i].close) / atr[i];
                    trades++;
                }
            }
            
            bool build_up_sell = true;
            for(int j = i+1; j <= i + InpMinBuildupBars; j++) {
                if(rates[j].close <= hma_buf[j]) { build_up_sell = false; break; }
            }
            if(build_up_sell && rates[i].close < hma_buf[i] && rates[i+1].close > hma_buf[i+1]) { 
                double min_low = rates[i].close;
                for(int k = i-1; k >= 0; k--) {
                    if(rates[k].low < min_low) min_low = rates[k].low;
                    if(rates[k].close > hma_buf[k]) break; 
                }
                if(atr[i] > 0) {
                    total_continuity += (rates[i].close - min_low) / atr[i];
                    trades++;
                }
            }
        }
        
        IndicatorRelease(hma_handle);
        double avg_cont = (trades > 0) ? total_continuity / trades : 0;
        PrintFormat("HMA %d | Operaciones: %d | Traccion Media: %.2f ATRs", p, trades, avg_cont);
        
        if(avg_cont > best_continuity) {
            best_continuity = avg_cont;
            best_period = p;
        }
    }
    
    IndicatorRelease(atr_handle);
    Print("==================================================");
    Print("?? EL MEJOR PERIODO ESTRUCTURAL ES: HMA ", best_period, " (Continuidad Media: ", DoubleToString(best_continuity, 2), " ATRs)");
    Print("Usa InpHMA_Entry_Period = ", best_period, " en V16 para extraccion.");
    Print("==================================================");
}

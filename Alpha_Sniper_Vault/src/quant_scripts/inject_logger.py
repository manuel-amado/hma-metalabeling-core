import os
import re

file_path = r"C:\Users\Manuel\AppData\Roaming\MetaQuotes\Terminal\D0E8209F77C8CF37AD8BF550E51FF075\MQL5\Experts\Alpha_Sniper\Alpha_Sniper_Master6.mq5"
with open(file_path, "r", encoding="utf-8") as f:
    text = f.read()

# 1. Add inputs
inputs = """input group "=== Meta-Labeling IA ==="
input bool   InpExportMetaLabeling = false;  // Activar volcado de Dataset CSV
input string InpCSVName            = "Master6_Dataset.csv";

input group "=== Ejecucion Institucional ==="""
text = text.replace('input group "=== Ejecucion Institucional ==="', inputs)

# 2. Add globals
globals_add = """datetime lastBarTime = 0;
int csv_handle = INVALID_HANDLE;"""
text = text.replace('datetime lastBarTime = 0;', globals_add)

# 3. Add OnInit
oninit_add = """    trade.SetExpertMagicNumber(28006);
    
    if(InpExportMetaLabeling && MQLInfoInteger(MQL_TESTER)) {
        csv_handle = FileOpen(InpCSVName, FILE_WRITE|FILE_CSV|FILE_ANSI, ",");
        if(csv_handle != INVALID_HANDLE) {
            FileWrite(csv_handle, "Time", "Signal", "RSI", "DistEMA_ATR", "Breakout_ATR", "Buildup", "Impulse_ATR", "LossStreak", "CandleSize_ATR", "DailyATR");
        }
    }"""
text = text.replace('    trade.SetExpertMagicNumber(28006);', oninit_add)

# 4. Add OnDeinit
ondeinit_add = """void OnDeinit(const int reason) {
    if(csv_handle != INVALID_HANDLE) FileClose(csv_handle);"""
text = text.replace('void OnDeinit(const int reason) {', ondeinit_add)

# 5. Fix impulse_atr calculation to be a separate variable for logging
impulse_old = """    bool valid_impulse = true;
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
    }"""
    
impulse_new = """    bool valid_impulse = true;
    double impulse_atr = 0.0;
    if(cross_up) {
        double lowest  = rates[1].low;
        for(int i=1; i<=20; i++) if(rates[i].low  < lowest)  lowest  = rates[i].low;
        impulse_atr = (current_close - lowest) / current_atr;
        if(InpMaxImpulseATR < 99.0 && impulse_atr > InpMaxImpulseATR) valid_impulse = false;
    }
    if(cross_dn) {
        double highest = rates[1].high;
        for(int i=1; i<=20; i++) if(rates[i].high > highest) highest = rates[i].high;
        impulse_atr = (highest - current_close) / current_atr;
        if(InpMaxImpulseATR < 99.0 && impulse_atr > InpMaxImpulseATR) valid_impulse = false;
    }"""
text = text.replace(impulse_old, impulse_new)

# 6. Add Logger inside signal execution
logger = """            if(signal == -1) trade.Sell(lots, _Symbol, bid, sl, 0.0, "Master6_Sell");
            
            // Meta-Labeling Export
            if(InpExportMetaLabeling && csv_handle != INVALID_HANDLE) {
                FileWrite(csv_handle, 
                    TimeToString(currentBarTime, TIME_DATE|TIME_MINUTES|TIME_SECONDS),
                    signal,
                    DoubleToString(current_rsi, 2),
                    DoubleToString(dist_ema_atr, 2),
                    DoubleToString(breakout_atr, 2),
                    IntegerToString(valid_buildup ? 1 : 0),
                    DoubleToString(impulse_atr, 2),
                    IntegerToString(loss_streak),
                    DoubleToString(candle_size / current_atr, 2),
                    DoubleToString(atr_d1[1], 2)
                );
            }
        }"""
text = text.replace('            if(signal == -1) trade.Sell(lots, _Symbol, bid, sl, 0.0, "Master5_Sell");\n        }', logger) # Notice it was Master5_Sell in original code, fixing it here
text = text.replace('"Master5_Buy"', '"Master6_Buy"')
text = text.replace('"Master5_Sell"', '"Master6_Sell"')

with open(file_path, "w", encoding="utf-8") as f:
    f.write(text)
print("Meta-Labeling logger injected.")
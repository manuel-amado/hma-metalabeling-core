//+------------------------------------------------------------------+
//|                                              Alpha_OHLC_Dump.mq5 |
//|                                   Script to dump raw OHLC + Inds |
//+------------------------------------------------------------------+
#property copyright "Alpha"
#property link      ""
#property version   "1.01"

void OnStart()
{
    int total_bars = iBars(_Symbol, _Period);
    int bars_to_copy = MathMin(total_bars, 350000); // ~10 years of M15
    
    MqlRates rates[];
    ArraySetAsSeries(rates, true);
    if(CopyRates(_Symbol, _Period, 0, bars_to_copy, rates) <= 0) {
        Print("Failed to copy rates");
        return;
    }
    
    int h_hma10 = iCustom(_Symbol, _Period, "HMA50", 10);
    int h_hma21 = iCustom(_Symbol, _Period, "HMA50", 21);
    int h_hma50 = iCustom(_Symbol, _Period, "HMA50", 50);
    int h_hma100 = iCustom(_Symbol, _Period, "HMA50", 100);
    int h_hma200 = iCustom(_Symbol, _Period, "HMA50", 200);
    int h_atr = iATR(_Symbol, _Period, 14);
    
    double h10[], h21[], h50[], h100[], h200[], atr[];
    ArraySetAsSeries(h10, true);
    ArraySetAsSeries(h21, true);
    ArraySetAsSeries(h50, true);
    ArraySetAsSeries(h100, true);
    ArraySetAsSeries(h200, true);
    ArraySetAsSeries(atr, true);
    
    CopyBuffer(h_hma10, 0, 0, bars_to_copy, h10);
    CopyBuffer(h_hma21, 0, 0, bars_to_copy, h21);
    CopyBuffer(h_hma50, 0, 0, bars_to_copy, h50);
    CopyBuffer(h_hma100, 0, 0, bars_to_copy, h100);
    CopyBuffer(h_hma200, 0, 0, bars_to_copy, h200);
    CopyBuffer(h_atr, 0, 0, bars_to_copy, atr);
    
    int h_ema_h4 = iMA(_Symbol, _Period, 50 * 16, 0, MODE_EMA, PRICE_CLOSE);
    int h_ema_d1 = iMA(_Symbol, _Period, 50 * 96, 0, MODE_EMA, PRICE_CLOSE);
    double emah4[], emad1[];
    ArraySetAsSeries(emah4, true);
    ArraySetAsSeries(emad1, true);
    CopyBuffer(h_ema_h4, 0, 0, bars_to_copy, emah4);
    CopyBuffer(h_ema_d1, 0, 0, bars_to_copy, emad1);
    
    int handle = FileOpen("Alpha_OHLC_Dump_XAUUSD.csv", FILE_WRITE|FILE_CSV|FILE_ANSI, ',');
    if(handle != INVALID_HANDLE) {
        FileWriteString(handle, "Time,Open,High,Low,Close,TickVolume,HMA10,HMA21,HMA50,HMA100,HMA200,ATR14,EMAH4,EMAD1\n");
        
        int written = 0;
        // Loop backwards so chronological order in CSV
        for(int i = bars_to_copy - 1; i >= 0; i--) {
            // Check for EMPTY_VALUE
            if(atr[i] > 100000 || h200[i] > 100000 || emad1[i] > 100000) continue;
            
            string line = TimeToString(rates[i].time) + "," +
                          DoubleToString(rates[i].open, 3) + "," +
                          DoubleToString(rates[i].high, 3) + "," +
                          DoubleToString(rates[i].low, 3) + "," +
                          DoubleToString(rates[i].close, 3) + "," +
                          IntegerToString(rates[i].tick_volume) + "," +
                          DoubleToString(h10[i], 3) + "," +
                          DoubleToString(h21[i], 3) + "," +
                          DoubleToString(h50[i], 3) + "," +
                          DoubleToString(h100[i], 3) + "," +
                          DoubleToString(h200[i], 3) + "," +
                          DoubleToString(atr[i], 3) + "," +
                          DoubleToString(emah4[i], 3) + "," +
                          DoubleToString(emad1[i], 3) + "\n";
            FileWriteString(handle, line);
            written++;
        }
        FileClose(handle);
        Print("Dump complete. Valid Bars written: ", written);
    } else {
        Print("Failed to open file for writing");
    }
}

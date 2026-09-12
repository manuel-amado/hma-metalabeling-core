//+------------------------------------------------------------------+
//|                                           Alpha_OHLC_Dump_EA.mq5 |
//|                     EA to dump raw OHLC + Inds in Tester         |
//+------------------------------------------------------------------+
#property copyright "Alpha"
#property link      ""
#property version   "1.00"

int h_hma10, h_hma21, h_hma50, h_hma100, h_hma200;
int h_atr, h_ema_h4, h_ema_d1;
int g_file_handle = INVALID_HANDLE;
int g_written_bars = 0;

int OnInit()
{
    if(!MQLInfoInteger(MQL_TESTER)) {
        Print("This EA must be run in the Strategy Tester.");
        return INIT_FAILED;
    }
    
    h_hma10 = iCustom(_Symbol, _Period, "HMA50", 10);
    h_hma21 = iCustom(_Symbol, _Period, "HMA50", 21);
    h_hma50 = iCustom(_Symbol, _Period, "HMA50", 50);
    h_hma100 = iCustom(_Symbol, _Period, "HMA50", 100);
    h_hma200 = iCustom(_Symbol, _Period, "HMA50", 200);
    
    h_atr = iATR(_Symbol, _Period, 14);
    h_ema_h4 = iMA(_Symbol, _Period, 50 * 16, 0, MODE_EMA, PRICE_CLOSE);
    h_ema_d1 = iMA(_Symbol, _Period, 50 * 96, 0, MODE_EMA, PRICE_CLOSE);
    
    string filename = "Alpha_OHLC_Dump_XAUUSD.csv";
    g_file_handle = FileOpen(filename, FILE_WRITE|FILE_CSV|FILE_ANSI, ',');
    if(g_file_handle != INVALID_HANDLE) {
        FileWriteString(g_file_handle, "Time,Open,High,Low,Close,TickVolume,HMA10,HMA21,HMA50,HMA100,HMA200,ATR14,EMAH4,EMAD1\n");
    } else {
        Print("Failed to open file!");
        return INIT_FAILED;
    }
    
    return INIT_SUCCEEDED;
}

void OnDeinit(const int reason)
{
    if(g_file_handle != INVALID_HANDLE) {
        FileClose(g_file_handle);
        Print("Dump complete. Valid Bars written: ", g_written_bars);
    }
}

void OnTick()
{
    static datetime last_bar;
    datetime current_bar = iTime(_Symbol, _Period, 0);
    if(current_bar == last_bar) return; // Only process once per closed bar
    last_bar = current_bar;
    
    // Skip the very first bar to avoid index out of range issues
    if(g_written_bars == 0) {
        g_written_bars++;
        return;
    }
    
    double h10[1], h21[1], h50[1], h100[1], h200[1];
    if(CopyBuffer(h_hma10, 0, 1, 1, h10) < 1) return;
    if(CopyBuffer(h_hma21, 0, 1, 1, h21) < 1) return;
    if(CopyBuffer(h_hma50, 0, 1, 1, h50) < 1) return;
    if(CopyBuffer(h_hma100, 0, 1, 1, h100) < 1) return;
    if(CopyBuffer(h_hma200, 0, 1, 1, h200) < 1) return;
    
    double atr[1], emah4[1], emad1[1];
    if(CopyBuffer(h_atr, 0, 1, 1, atr) < 1) return;
    if(CopyBuffer(h_ema_h4, 0, 1, 1, emah4) < 1) return;
    if(CopyBuffer(h_ema_d1, 0, 1, 1, emad1) < 1) return;
    
    // Check for EMPTY_VALUE
    if(atr[0] > 100000 || h200[0] > 100000 || emad1[0] > 100000) return;
    
    datetime time = iTime(_Symbol, _Period, 1);
    double open   = iOpen(_Symbol, _Period, 1);
    double high   = iHigh(_Symbol, _Period, 1);
    double low    = iLow(_Symbol, _Period, 1);
    double close  = iClose(_Symbol, _Period, 1);
    long   vol    = iTickVolume(_Symbol, _Period, 1);
    
    string line = TimeToString(time) + "," +
                  DoubleToString(open, 3) + "," +
                  DoubleToString(high, 3) + "," +
                  DoubleToString(low, 3) + "," +
                  DoubleToString(close, 3) + "," +
                  IntegerToString(vol) + "," +
                  DoubleToString(h10[0], 3) + "," +
                  DoubleToString(h21[0], 3) + "," +
                  DoubleToString(h50[0], 3) + "," +
                  DoubleToString(h100[0], 3) + "," +
                  DoubleToString(h200[0], 3) + "," +
                  DoubleToString(atr[0], 3) + "," +
                  DoubleToString(emah4[0], 3) + "," +
                  DoubleToString(emad1[0], 3) + "\n";
                  
    if(g_file_handle != INVALID_HANDLE) {
        FileWriteString(g_file_handle, line);
        g_written_bars++;
    }
}

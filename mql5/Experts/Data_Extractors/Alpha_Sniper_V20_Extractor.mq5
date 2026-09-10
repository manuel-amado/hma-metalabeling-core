//+------------------------------------------------------------------+
//|                                Alpha_Sniper_V20_Extractor.mq5    |
//|                                Event-Driven Triple Barrier AI    |
//+------------------------------------------------------------------+
#property copyright "Alpha Sniper V20"
#property link      ""
#property version   "20.00"

#include <Trade\Trade.mqh>
#include <Math\Stat\Math.mqh>
#include "HMA_FUNCTIONS.mqh"

input group "== V20 Extractor Settings =="
input int    InpRefHMA_Period    = 50;
input double InpTP_ATR           = 2.0;  // Triple Barrier TP
input double InpSL_ATR           = 1.0;  // Triple Barrier SL
input int    InpTime_Barrier     = 24;   // Triple Barrier Time Limit (Bars)
input int    InpATR_Period       = 14;
input int    InpRSI_Period       = 14;

int handle_hma;
int handle_atr;
int handle_rsi;
int g_file_handle = INVALID_HANDLE;

// Event Tracking
double max_distance_since_cross = 0;
int bars_since_cross = 0;
int last_trend_dir = 0;

struct PendingEvent {
    datetime time;
    int dir;
    double hma_slope;
    double hma_accel;
    double candle_vel;
    int time_in_trend;
    double snapback;
    double rsi;
    double time_sine;
    double time_cosine;
    double pain;
    
    double entry_price;
    double tp_price;
    double sl_price;
    int bars_elapsed;
};

PendingEvent queue[];

void OnInit() {
    handle_hma = iCustom(_Symbol, _Period, "HMA50", InpRefHMA_Period);
    handle_atr = iATR(_Symbol, _Period, InpATR_Period);
    handle_rsi = iRSI(_Symbol, _Period, InpRSI_Period, PRICE_CLOSE);
    
    if(MQLInfoInteger(MQL_TESTER)) {
        string filename = "Alpha_Sweep_Dataset_v20_" + _Symbol + ".csv";
        g_file_handle = FileOpen(filename, FILE_WRITE|FILE_CSV|FILE_ANSI, ',');
        if(g_file_handle != INVALID_HANDLE) {
            FileWriteString(g_file_handle, "Time,CrossDir,HMA_Slope,HMA_Accel,Candle_Vel,Time_in_Trend,Snapback_Dist,RSI,Time_Sine,Time_Cosine,PainIndex,Target_Label,Target_ReturnPct\n");
        }
    }
}

void OnDeinit(const int reason) {
    if(g_file_handle != INVALID_HANDLE) FileClose(g_file_handle);
}

void EvaluateQueue(double high, double low, double close) {
    if(g_file_handle == INVALID_HANDLE) return;
    
    for(int i = ArraySize(queue) - 1; i >= 0; i--) {
        queue[i].bars_elapsed++;
        
        bool closed = false;
        int label = 0;
        double return_pct = 0.0;
        
        if(queue[i].dir == 1) { // BUY
            if(low <= queue[i].sl_price) { closed = true; label = 0; return_pct = ((queue[i].sl_price - queue[i].entry_price) / queue[i].entry_price) * 100.0; }
            else if(high >= queue[i].tp_price) { closed = true; label = 1; return_pct = ((queue[i].tp_price - queue[i].entry_price) / queue[i].entry_price) * 100.0; }
        } else { // SELL
            if(high >= queue[i].sl_price) { closed = true; label = 0; return_pct = ((queue[i].entry_price - queue[i].sl_price) / queue[i].entry_price) * 100.0; }
            else if(low <= queue[i].tp_price) { closed = true; label = 1; return_pct = ((queue[i].entry_price - queue[i].tp_price) / queue[i].entry_price) * 100.0; }
        }
        
        if(!closed && queue[i].bars_elapsed >= InpTime_Barrier) {
            closed = true;
            label = 0; // Time barrier hit = failure to trend
            return_pct = ((close - queue[i].entry_price) / queue[i].entry_price) * 100.0;
            if(queue[i].dir == -1) return_pct = -return_pct;
            if(return_pct > 0) label = 1; // If it's still profitable after time expires, label as 1
        }
        
        if(closed) {
            string line = TimeToString(queue[i].time) + "," +
                          IntegerToString(queue[i].dir) + "," +
                          DoubleToString(queue[i].hma_slope, 4) + "," +
                          DoubleToString(queue[i].hma_accel, 4) + "," +
                          DoubleToString(queue[i].candle_vel, 4) + "," +
                          IntegerToString(queue[i].time_in_trend) + "," +
                          DoubleToString(queue[i].snapback, 4) + "," +
                          DoubleToString(queue[i].rsi, 4) + "," +
                          DoubleToString(queue[i].time_sine, 4) + "," +
                          DoubleToString(queue[i].time_cosine, 4) + "," +
                          DoubleToString(queue[i].pain, 4) + "," +
                          IntegerToString(label) + "," +
                          DoubleToString(return_pct, 4) + "\n";
            FileWriteString(g_file_handle, line);
            ArrayRemove(queue, i, 1);
        }
    }
}

void OnTick() {
    if(!MQLInfoInteger(MQL_TESTER)) return;
    
    static datetime last_bar;
    datetime current_bar = iTime(_Symbol, _Period, 0);
    if(current_bar == last_bar) return;
    last_bar = current_bar;
    
    double close1 = iClose(_Symbol, _Period, 1);
    double open1 = iOpen(_Symbol, _Period, 1);
    double high1 = iHigh(_Symbol, _Period, 1);
    double low1 = iLow(_Symbol, _Period, 1);
    
    EvaluateQueue(high1, low1, close1);
    
    double hma[5], atr[1], rsi[1];
    if(CopyBuffer(handle_hma, 0, 1, 5, hma) < 5) return;
    if(CopyBuffer(handle_atr, 0, 1, 1, atr) < 1) return;
    if(CopyBuffer(handle_rsi, 0, 1, 1, rsi) < 1) return;
    
    int current_dir = (close1 > hma[0]) ? 1 : -1;
    
    double dist = MathAbs(close1 - hma[0]) / atr[0];
    if(dist > max_distance_since_cross) max_distance_since_cross = dist;
    bars_since_cross++;
    
    if(current_dir != last_trend_dir && last_trend_dir != 0) {
        PendingEvent ev;
        ev.time = iTime(_Symbol, _Period, 1);
        ev.dir = current_dir;
        ev.hma_slope = (hma[0] - hma[3]) / atr[0];
        double prev_slope = (hma[1] - hma[4]) / atr[0];
        ev.hma_accel = ev.hma_slope - prev_slope;
        ev.candle_vel = (close1 - open1) / atr[0];
        ev.snapback = max_distance_since_cross;
        ev.time_in_trend = bars_since_cross;
        ev.rsi = rsi[0];
        
        MqlDateTime dt;
        TimeToStruct(ev.time, dt);
        double mins = dt.hour * 60 + dt.min;
        ev.time_sine = MathSin(2.0 * M_PI * mins / 1440.0);
        ev.time_cosine = MathCos(2.0 * M_PI * mins / 1440.0);
        
        double high10 = iHigh(_Symbol, _Period, iHighest(_Symbol, _Period, MODE_HIGH, 10, 1));
        double low10 = iLow(_Symbol, _Period, iLowest(_Symbol, _Period, MODE_LOW, 10, 1));
        ev.pain = (current_dir == 1) ? (close1 - high10)/atr[0] : (close1 - low10)/atr[0];
        
        ev.entry_price = close1;
        ev.tp_price = (current_dir == 1) ? close1 + (InpTP_ATR * atr[0]) : close1 - (InpTP_ATR * atr[0]);
        ev.sl_price = (current_dir == 1) ? close1 - (InpSL_ATR * atr[0]) : close1 + (InpSL_ATR * atr[0]);
        ev.bars_elapsed = 0;
        
        int sz = ArraySize(queue);
        ArrayResize(queue, sz + 1);
        queue[sz] = ev;
        
        max_distance_since_cross = 0;
        bars_since_cross = 0;
    }
    
    last_trend_dir = current_dir;
}

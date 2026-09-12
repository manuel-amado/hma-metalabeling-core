//+------------------------------------------------------------------+
//|                             Alpha_Sniper_Omni_Extractor.mq5      |
//|                 Dense Meta-Labeling & Excursion Tracking         |
//+------------------------------------------------------------------+
#property copyright "Alpha Omni v3"
#property link      ""
#property version   "23.00"

#include <Trade\Trade.mqh>
#include <Math\Stat\Math.mqh>

input group "== Omni Extractor Settings =="
input int    InpRefHMA_Period    = 50;
input int    InpATR_Period       = 14;
input int    InpRSI_Period       = 14;

int h_hma10, h_hma21, h_hma50, h_hma100, h_hma200;
int h_atr, h_atr_d1, h_rsi, h_sma20, h_std20;
int h_ema_h4, h_ema_d1;

int g_file_handle = INVALID_HANDLE;

double max_distance_since_cross = 0;
int bars_since_cross = 0;
int last_trend_dir = 0;

struct PendingEvent {
    datetime entry_time;
    int dir;
    double entry_price;
    double entry_atr;

    double f_slope_10;
    double f_slope_21;
    double f_slope_50;
    double f_slope_100;
    double f_slope_200;
    double f_ribbon_spread;
    int    f_ribbon_align;

    double f_dist_h4;
    double f_dist_d1;
    double f_mtf_atr;

    double f_candle_vel;
    double f_candle_dom;
    double f_zscore;
    double f_snapback;
    int    f_time_trend;
    double f_pain;
    double f_rsi;

    double f_swing_high_20;
    double f_swing_low_20;

    double max_favorable_excursion;
    double max_adverse_excursion;
};

PendingEvent queue[];

void OnInit() {
    h_hma10 = iCustom(_Symbol, _Period, "HMA50", 10);
    h_hma21 = iCustom(_Symbol, _Period, "HMA50", 21);
    h_hma50 = iCustom(_Symbol, _Period, "HMA50", 50);
    h_hma100 = iCustom(_Symbol, _Period, "HMA50", 100);
    h_hma200 = iCustom(_Symbol, _Period, "HMA50", 200);
    
    h_atr = iATR(_Symbol, _Period, InpATR_Period);
    h_atr_d1 = iATR(_Symbol, PERIOD_D1, InpATR_Period);
    h_rsi = iRSI(_Symbol, _Period, InpRSI_Period, PRICE_CLOSE);
    h_sma20 = iMA(_Symbol, _Period, 20, 0, MODE_SMA, PRICE_CLOSE);
    h_std20 = iStdDev(_Symbol, _Period, 20, 0, MODE_SMA, PRICE_CLOSE);
    
    h_ema_h4 = iMA(_Symbol, _Period, 50 * 16, 0, MODE_EMA, PRICE_CLOSE);
    h_ema_d1 = iMA(_Symbol, _Period, 50 * 96, 0, MODE_EMA, PRICE_CLOSE);
    
    if(MQLInfoInteger(MQL_TESTER)) {
        string filename = "Alpha_Omni_V3_Dataset_" + _Symbol + ".csv";
        g_file_handle = FileOpen(filename, FILE_WRITE|FILE_CSV|FILE_ANSI, ',');
        if(g_file_handle != INVALID_HANDLE) {
            string headers = "Time,Dir,Slope10,Slope21,Slope50,Slope100,Slope200,RibbonSpread,RibbonAlign,DistH4,DistD1,MTFATR,CandleVel,CandleDom,ZScore,Snapback,TimeInTrend,PainIndex,RSI,SwingHigh20,SwingLow20,MFE_ATR,MAE_ATR,Target_Cross_Ret\n";
            FileWriteString(g_file_handle, headers);
        }
    }
}

void OnDeinit(const int reason) {
    if(g_file_handle != INVALID_HANDLE) FileClose(g_file_handle);
}

void EvaluateQueue(double high, double low, double close, int current_dir) {
    if(g_file_handle == INVALID_HANDLE) return;
    
    for(int i = ArraySize(queue) - 1; i >= 0; i--) {
        if(queue[i].dir == 1) {
            double fav = high - queue[i].entry_price;
            double adv = low - queue[i].entry_price;
            if(fav > queue[i].max_favorable_excursion) queue[i].max_favorable_excursion = fav;
            if(adv < queue[i].max_adverse_excursion) queue[i].max_adverse_excursion = adv;
        } else {
            double fav = queue[i].entry_price - low;
            double adv = queue[i].entry_price - high;
            if(fav > queue[i].max_favorable_excursion) queue[i].max_favorable_excursion = fav;
            if(adv < queue[i].max_adverse_excursion) queue[i].max_adverse_excursion = adv;
        }

        if(current_dir != queue[i].dir) {
            double mfe_atr = queue[i].max_favorable_excursion / queue[i].entry_atr;
            double mae_atr = queue[i].max_adverse_excursion / queue[i].entry_atr;
            
            double cross_ret = 0;
            if(queue[i].dir == 1) cross_ret = (close - queue[i].entry_price) / queue[i].entry_price * 100.0;
            else cross_ret = (queue[i].entry_price - close) / queue[i].entry_price * 100.0;

            string line = TimeToString(queue[i].entry_time) + "," +
                          IntegerToString(queue[i].dir) + "," +
                          DoubleToString(queue[i].f_slope_10, 4) + "," +
                          DoubleToString(queue[i].f_slope_21, 4) + "," +
                          DoubleToString(queue[i].f_slope_50, 4) + "," +
                          DoubleToString(queue[i].f_slope_100, 4) + "," +
                          DoubleToString(queue[i].f_slope_200, 4) + "," +
                          DoubleToString(queue[i].f_ribbon_spread, 4) + "," +
                          IntegerToString(queue[i].f_ribbon_align) + "," +
                          DoubleToString(queue[i].f_dist_h4, 4) + "," +
                          DoubleToString(queue[i].f_dist_d1, 4) + "," +
                          DoubleToString(queue[i].f_mtf_atr, 4) + "," +
                          DoubleToString(queue[i].f_candle_vel, 4) + "," +
                          DoubleToString(queue[i].f_candle_dom, 4) + "," +
                          DoubleToString(queue[i].f_zscore, 4) + "," +
                          DoubleToString(queue[i].f_snapback, 4) + "," +
                          IntegerToString(queue[i].f_time_trend) + "," +
                          DoubleToString(queue[i].f_pain, 4) + "," +
                          DoubleToString(queue[i].f_rsi, 4) + "," +
                          DoubleToString(queue[i].f_swing_high_20, 4) + "," +
                          DoubleToString(queue[i].f_swing_low_20, 4) + "," +
                          DoubleToString(mfe_atr, 4) + "," +
                          DoubleToString(mae_atr, 4) + "," +
                          DoubleToString(cross_ret, 4) + "\n";
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
    double open1  = iOpen(_Symbol, _Period, 1);
    double high1  = iHigh(_Symbol, _Period, 1);
    double low1   = iLow(_Symbol, _Period, 1);
    
    double h10[2], h21[2], h50[2], h100[2], h200[2];
    if(CopyBuffer(h_hma10, 0, 1, 2, h10) < 2) return;
    if(CopyBuffer(h_hma21, 0, 1, 2, h21) < 2) return;
    if(CopyBuffer(h_hma50, 0, 1, 2, h50) < 2) return;
    if(CopyBuffer(h_hma100, 0, 1, 2, h100) < 2) return;
    if(CopyBuffer(h_hma200, 0, 1, 2, h200) < 2) return;
    
    double atr[1], atrd1[1], rsi[1], sma20[1], std20[1], emah4[1], emad1[1];
    if(CopyBuffer(h_atr, 0, 1, 1, atr) < 1) return;
    if(CopyBuffer(h_atr_d1, 0, 1, 1, atrd1) < 1) return;
    if(CopyBuffer(h_rsi, 0, 1, 1, rsi) < 1) return;
    if(CopyBuffer(h_sma20, 0, 1, 1, sma20) < 1) return;
    if(CopyBuffer(h_std20, 0, 1, 1, std20) < 1) return;
    if(CopyBuffer(h_ema_h4, 0, 1, 1, emah4) < 1) return;
    if(CopyBuffer(h_ema_d1, 0, 1, 1, emad1) < 1) return;
    
    int current_dir = (close1 > h50[1]) ? 1 : -1;
    
    EvaluateQueue(high1, low1, close1, current_dir);
    
    double dist = MathAbs(close1 - h50[1]) / atr[0];
    if(dist > max_distance_since_cross) max_distance_since_cross = dist;
    bars_since_cross++;
    
    if(current_dir != last_trend_dir && last_trend_dir != 0) {
        PendingEvent ev;
        ev.entry_time = iTime(_Symbol, _Period, 1);
        ev.dir = current_dir;
        ev.entry_price = close1;
        ev.entry_atr = atr[0];
        
        ev.f_slope_10 = (h10[1] - h10[0]) / atr[0];
        ev.f_slope_21 = (h21[1] - h21[0]) / atr[0];
        ev.f_slope_50 = (h50[1] - h50[0]) / atr[0];
        ev.f_slope_100 = (h100[1] - h100[0]) / atr[0];
        ev.f_slope_200 = (h200[1] - h200[0]) / atr[0];
        
        double vals[5] = {h10[1], h21[1], h50[1], h100[1], h200[1]};
        double mean = (h10[1]+h21[1]+h50[1]+h100[1]+h200[1])/5.0;
        double sum_sq = 0;
        for(int k=0; k<5; k++) sum_sq += MathPow(vals[k] - mean, 2);
        ev.f_ribbon_spread = MathSqrt(sum_sq / 5.0) / atr[0];
        
        if(h10[1] > h21[1] && h21[1] > h50[1] && h50[1] > h100[1] && h100[1] > h200[1]) ev.f_ribbon_align = 1;
        else if(h10[1] < h21[1] && h21[1] < h50[1] && h50[1] < h100[1] && h100[1] < h200[1]) ev.f_ribbon_align = -1;
        else ev.f_ribbon_align = 0;
        
        ev.f_dist_h4 = (close1 - emah4[0]) / atr[0];
        ev.f_dist_d1 = (close1 - emad1[0]) / atr[0];
        ev.f_mtf_atr = (atrd1[0] > 0) ? atr[0] / atrd1[0] : 0;
        
        ev.f_candle_vel = (close1 - open1) / atr[0];
        double cdl_range = high1 - low1;
        ev.f_candle_dom = (cdl_range > 0) ? (close1 - open1) / cdl_range : 0;
        ev.f_zscore = (std20[0] > 0) ? (close1 - sma20[0]) / std20[0] : 0;
        
        ev.f_snapback = max_distance_since_cross;
        ev.f_time_trend = bars_since_cross;
        
        double high10 = iHigh(_Symbol, _Period, iHighest(_Symbol, _Period, MODE_HIGH, 10, 1));
        double low10  = iLow(_Symbol, _Period, iLowest(_Symbol, _Period, MODE_LOW, 10, 1));
        ev.f_pain = (current_dir == 1) ? (close1 - high10)/atr[0] : (close1 - low10)/atr[0];
        ev.f_rsi = rsi[0];
        
        double high20 = iHigh(_Symbol, _Period, iHighest(_Symbol, _Period, MODE_HIGH, 20, 1));
        double low20  = iLow(_Symbol, _Period, iLowest(_Symbol, _Period, MODE_LOW, 20, 1));
        ev.f_swing_high_20 = (high20 - close1) / atr[0];
        ev.f_swing_low_20 = (close1 - low20) / atr[0];
        
        ev.max_favorable_excursion = 0;
        ev.max_adverse_excursion = 0;
        
        int sz = ArraySize(queue);
        ArrayResize(queue, sz + 1);
        queue[sz] = ev;
        
        max_distance_since_cross = 0;
        bars_since_cross = 0;
    }
    
    last_trend_dir = current_dir;
}

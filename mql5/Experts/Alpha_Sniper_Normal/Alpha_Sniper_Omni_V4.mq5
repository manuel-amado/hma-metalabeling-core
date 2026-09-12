//+------------------------------------------------------------------+
//|                             Alpha_Sniper_Omni_V4.mq5             |
//|                 The Final Edge (WFO AI + Dynamic Metalabeling)   |
//+------------------------------------------------------------------+
#property copyright "Alpha Omni v4.0 - True Edge"
#property link      ""
#property version   "4.00"

#include <Trade\Trade.mqh>
#include <Math\Stat\Math.mqh>
#include "Models\XGBoost_Model_WFO_OMNI_V2_XAUUSD.mqh"
#include "Models\XGBoost_Metalabel_V4.mqh"

input group "== Risk & AI =="
input double InpFixedLots        = 1.0;
input double InpAI_Threshold     = 0.45; // WFO Entry Threshold
input bool   InpUseMetalabeling  = true; // Usar salidas dinamicas
input bool   InpOneShotMode      = true;

int h_hma10, h_hma21, h_hma50, h_hma100, h_hma200;
int h_atr, h_atr_d1, h_rsi, h_sma20, h_std20;
int h_ema_h4, h_ema_d1;

double max_distance_since_cross = 0;
int bars_since_cross = 0;
int last_trend_dir = 0;

CTrade trade;

void OnInit() {
    h_hma10 = iCustom(_Symbol, _Period, "HMA50", 10);
    h_hma21 = iCustom(_Symbol, _Period, "HMA50", 21);
    h_hma50 = iCustom(_Symbol, _Period, "HMA50", 50);
    h_hma100 = iCustom(_Symbol, _Period, "HMA50", 100);
    h_hma200 = iCustom(_Symbol, _Period, "HMA50", 200);
    
    h_atr = iATR(_Symbol, _Period, 14);
    h_atr_d1 = iATR(_Symbol, PERIOD_D1, 14);
    h_rsi = iRSI(_Symbol, _Period, 14, PRICE_CLOSE);
    h_sma20 = iMA(_Symbol, _Period, 20, 0, MODE_SMA, PRICE_CLOSE);
    h_std20 = iStdDev(_Symbol, _Period, 20, 0, MODE_SMA, PRICE_CLOSE);
    
    h_ema_h4 = iMA(_Symbol, _Period, 50 * 16, 0, MODE_EMA, PRICE_CLOSE);
    h_ema_d1 = iMA(_Symbol, _Period, 50 * 96, 0, MODE_EMA, PRICE_CLOSE);
    
    trade.SetExpertMagicNumber(7779994);
}

void OnDeinit(const int reason) {}

void OnTick() {
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
    
    double vals[5] = {h10[1], h21[1], h50[1], h100[1], h200[1]};
    double mean = (h10[1]+h21[1]+h50[1]+h100[1]+h200[1])/5.0;
    double sum_sq = 0;
    for(int k=0; k<5; k++) sum_sq += MathPow(vals[k] - mean, 2);
    double current_ribbon_spread = MathSqrt(sum_sq / 5.0) / atr[0];
    
    bool has_open_trades = false;
    for(int i = PositionsTotal() - 1; i >= 0; i--) {
        if(PositionGetSymbol(i) == _Symbol && PositionGetInteger(POSITION_MAGIC) == 7779994) {
            has_open_trades = true;
        }
    }
    
    int current_dir = (close1 > h50[1]) ? 1 : -1;
    double dist = MathAbs(close1 - h50[1]) / atr[0];
    if(dist > max_distance_since_cross) max_distance_since_cross = dist;
    bars_since_cross++;
    
    if(current_dir != last_trend_dir && last_trend_dir != 0) {
        // --- 1. ENTRY AI (WFO) ---
        double entry_features[17];
        entry_features[0] = (h10[1] - h10[0]) / atr[0];
        entry_features[1] = (h21[1] - h21[0]) / atr[0];
        entry_features[2] = (h50[1] - h50[0]) / atr[0];
        entry_features[3] = (h100[1] - h100[0]) / atr[0];
        entry_features[4] = (h200[1] - h200[0]) / atr[0];
        entry_features[5] = current_ribbon_spread;
        
        int ribbon_align = 0;
        if(h10[1] > h21[1] && h21[1] > h50[1] && h50[1] > h100[1] && h100[1] > h200[1]) ribbon_align = 1;
        else if(h10[1] < h21[1] && h21[1] < h50[1] && h50[1] < h100[1] && h100[1] < h200[1]) ribbon_align = -1;
        entry_features[6] = ribbon_align;
        
        entry_features[7] = (close1 - emah4[0]) / atr[0];
        entry_features[8] = (close1 - emad1[0]) / atr[0];
        entry_features[9] = (atrd1[0] > 0) ? atr[0] / atrd1[0] : 0;
        entry_features[10] = (close1 - open1) / atr[0];
        double cdl_range = high1 - low1;
        entry_features[11] = (cdl_range > 0) ? (close1 - open1) / cdl_range : 0;
        entry_features[12] = (std20[0] > 0) ? (close1 - sma20[0]) / std20[0] : 0;
        entry_features[13] = max_distance_since_cross;
        entry_features[14] = bars_since_cross;
        
        double high10 = iHigh(_Symbol, _Period, iHighest(_Symbol, _Period, MODE_HIGH, 10, 1));
        double low10  = iLow(_Symbol, _Period, iLowest(_Symbol, _Period, MODE_LOW, 10, 1));
        entry_features[15] = (current_dir == 1) ? (close1 - high10)/atr[0] : (close1 - low10)/atr[0];
        entry_features[16] = rsi[0];
        
        MqlDateTime dt; TimeToStruct(iTime(_Symbol, _Period, 1), dt);
        double prob = XGBoost_Predict_WFO_OMNI_V2_XAUUSD(entry_features, dt.year, dt.mon);
        
        if(prob >= InpAI_Threshold) {
            if(!has_open_trades || !InpOneShotMode) {
                
                double target_sl_atr = 2.0;
                double target_tp_multi = 2.0;
                
                // --- 2. EXIT AI (METALABELING) ---
                if(InpUseMetalabeling) {
                    double meta_features[9];
                    meta_features[0] = entry_features[0];
                    meta_features[1] = entry_features[1];
                    meta_features[2] = entry_features[2];
                    meta_features[3] = entry_features[3];
                    meta_features[4] = entry_features[4];
                    meta_features[5] = entry_features[5]; // Spread
                    meta_features[6] = entry_features[6]; // Align
                    meta_features[7] = entry_features[7]; // DistH4
                    meta_features[8] = entry_features[8]; // DistD1
                    
                    int meta_class = Get_Optimal_Barrier_Class(meta_features);
                    
                    // Decode Class
                    if(meta_class == 4) {
                        Print("MetaLabeling abortó el trade. Clase 4 (Ruido Letal).");
                        return; // Skip trade completely!
                    }
                    if(meta_class == 0) { target_sl_atr = 1.0; target_tp_multi = 1.0; }
                    else if(meta_class == 1) { target_sl_atr = 1.0; target_tp_multi = 2.0; }
                    else if(meta_class == 2) { target_sl_atr = 2.0; target_tp_multi = 1.0; }
                    else if(meta_class == 3) { target_sl_atr = 2.0; target_tp_multi = 2.0; }
                    
                    Print("MetaLabeling asignó Clase: ", meta_class, " | SL ATR: ", target_sl_atr, " | TP Multi: ", target_tp_multi);
                }
                
                double ask = SymbolInfoDouble(_Symbol, SYMBOL_ASK);
                double bid = SymbolInfoDouble(_Symbol, SYMBOL_BID);
                double entry_price = (current_dir == 1) ? ask : bid;
                
                double sl_price = (current_dir == 1) ? entry_price - (target_sl_atr * atr[0]) : entry_price + (target_sl_atr * atr[0]);
                double tp_price = (current_dir == 1) ? entry_price + (target_sl_atr * target_tp_multi * atr[0]) : entry_price - (target_sl_atr * target_tp_multi * atr[0]);
                
                if(current_dir == 1) trade.Buy(InpFixedLots, _Symbol, ask, sl_price, tp_price, "V4 AI=" + DoubleToString(prob, 2));
                else trade.Sell(InpFixedLots, _Symbol, bid, sl_price, tp_price, "V4 AI=" + DoubleToString(prob, 2));
            }
        }
        
        max_distance_since_cross = 0;
        bars_since_cross = 0;
    }
    
    last_trend_dir = current_dir;
}

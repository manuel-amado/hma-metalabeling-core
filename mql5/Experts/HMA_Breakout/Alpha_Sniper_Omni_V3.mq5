//+------------------------------------------------------------------+
//|                             Alpha_Sniper_Omni_V3.mq5             |
//|                 The Original Edge (1:2 RR + Ribbon Compression)  |
//+------------------------------------------------------------------+
#property copyright "Alpha Omni v3.1"
#property link      ""
#property version   "24.01"

#include <Trade\Trade.mqh>
#include <Math\Stat\Math.mqh>
#include "Models\XGBoost_Model_WFO_OMNI_V2_XAUUSD.mqh"

input group "== Strategy Settings =="
input int    InpATR_Period       = 14;
input int    InpRSI_Period       = 14;

input group "== Risk & AI =="
input double InpFixedLots        = 1.0;
input double InpAI_Threshold     = 0.45; // Filtrado fuerte
input double InpRR_Multiplier    = 2.0;
input double InpMinSL_ATR        = 2.0;  // Minimizar impacto de spread
input double InpMaxSL_ATR        = 5.0;
input bool   InpOneShotMode      = true;

input group "== Smart Exits =="
input bool   InpUseRibbonExit    = false;
input double InpRibbonCompressPct= 0.30;

int h_hma10, h_hma21, h_hma50, h_hma100, h_hma200;
int h_atr, h_atr_d1, h_rsi, h_sma20, h_std20;
int h_ema_h4, h_ema_d1;

double max_distance_since_cross = 0;
int bars_since_cross = 0;
int last_trend_dir = 0;
double max_ribbon_spread_trade = 0;

CTrade trade;

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
    
    trade.SetExpertMagicNumber(777999);
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
        if(PositionGetSymbol(i) == _Symbol && PositionGetInteger(POSITION_MAGIC) == 777999) {
            has_open_trades = true;
            ulong ticket = PositionGetTicket(i);
            
            if(InpUseRibbonExit) {
                if(current_ribbon_spread > max_ribbon_spread_trade) {
                    max_ribbon_spread_trade = current_ribbon_spread;
                } else if(current_ribbon_spread < max_ribbon_spread_trade * (1.0 - InpRibbonCompressPct)) {
                    double floating_profit = PositionGetDouble(POSITION_PROFIT);
                    if(floating_profit > 0) {
                        trade.PositionClose(ticket);
                        Print("Salida Inteligente: Compresión del Ribbon detectada.");
                        max_ribbon_spread_trade = 0;
                        has_open_trades = false;
                    }
                }
            }
        }
    }
    
    if(!has_open_trades) max_ribbon_spread_trade = 0;
    
    int current_dir = (close1 > h50[1]) ? 1 : -1;
    double dist = MathAbs(close1 - h50[1]) / atr[0];
    if(dist > max_distance_since_cross) max_distance_since_cross = dist;
    bars_since_cross++;
    
    if(current_dir != last_trend_dir && last_trend_dir != 0) {
        double features[17];
        features[0] = (h10[1] - h10[0]) / atr[0];
        features[1] = (h21[1] - h21[0]) / atr[0];
        features[2] = (h50[1] - h50[0]) / atr[0];
        features[3] = (h100[1] - h100[0]) / atr[0];
        features[4] = (h200[1] - h200[0]) / atr[0];
        features[5] = current_ribbon_spread;
        
        if(h10[1] > h21[1] && h21[1] > h50[1] && h50[1] > h100[1] && h100[1] > h200[1]) features[6] = 1;
        else if(h10[1] < h21[1] && h21[1] < h50[1] && h50[1] < h100[1] && h100[1] < h200[1]) features[6] = -1;
        else features[6] = 0;
        
        features[7] = (close1 - emah4[0]) / atr[0];
        features[8] = (close1 - emad1[0]) / atr[0];
        features[9] = (atrd1[0] > 0) ? atr[0] / atrd1[0] : 0;
        features[10] = (close1 - open1) / atr[0];
        double cdl_range = high1 - low1;
        features[11] = (cdl_range > 0) ? (close1 - open1) / cdl_range : 0;
        features[12] = (std20[0] > 0) ? (close1 - sma20[0]) / std20[0] : 0;
        features[13] = max_distance_since_cross;
        features[14] = bars_since_cross;
        
        double high10 = iHigh(_Symbol, _Period, iHighest(_Symbol, _Period, MODE_HIGH, 10, 1));
        double low10  = iLow(_Symbol, _Period, iLowest(_Symbol, _Period, MODE_LOW, 10, 1));
        features[15] = (current_dir == 1) ? (close1 - high10)/atr[0] : (close1 - low10)/atr[0];
        features[16] = rsi[0];
        
        MqlDateTime dt; TimeToStruct(iTime(_Symbol, _Period, 1), dt);
        double prob = XGBoost_Predict_WFO_OMNI_V2_XAUUSD(features, dt.year, dt.mon);
        
        if(prob >= InpAI_Threshold) {
            if(!has_open_trades || !InpOneShotMode) {
                double high20 = iHigh(_Symbol, _Period, iHighest(_Symbol, _Period, MODE_HIGH, 20, 1));
                double low20  = iLow(_Symbol, _Period, iLowest(_Symbol, _Period, MODE_LOW, 20, 1));
                
                double swing_dist_atr = (current_dir == 1) ? (close1 - low20) / atr[0] : (high20 - close1) / atr[0];
                if(swing_dist_atr < InpMinSL_ATR) swing_dist_atr = InpMinSL_ATR;
                if(swing_dist_atr > InpMaxSL_ATR) swing_dist_atr = InpMaxSL_ATR;
                
                double ask = SymbolInfoDouble(_Symbol, SYMBOL_ASK);
                double bid = SymbolInfoDouble(_Symbol, SYMBOL_BID);
                double entry_price = (current_dir == 1) ? ask : bid;
                
                // Anclar TP y SL al precio real de entrada, no al cierre pasado
                double sl_price = (current_dir == 1) ? entry_price - (swing_dist_atr * atr[0]) : entry_price + (swing_dist_atr * atr[0]);
                double tp_price = (current_dir == 1) ? entry_price + (swing_dist_atr * InpRR_Multiplier * atr[0]) : entry_price - (swing_dist_atr * InpRR_Multiplier * atr[0]);
                
                if(current_dir == 1) trade.Buy(InpFixedLots, _Symbol, ask, sl_price, tp_price, "V3 AI=" + DoubleToString(prob, 2));
                else trade.Sell(InpFixedLots, _Symbol, bid, sl_price, tp_price, "V3 AI=" + DoubleToString(prob, 2));
                
                max_ribbon_spread_trade = current_ribbon_spread;
            }
        }
        
        max_distance_since_cross = 0;
        bars_since_cross = 0;
    }
    
    last_trend_dir = current_dir;
}

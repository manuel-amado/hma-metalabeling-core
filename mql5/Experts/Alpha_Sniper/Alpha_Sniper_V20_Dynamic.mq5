//+------------------------------------------------------------------+
//|                                Alpha_Sniper_V20_Dynamic.mq5      |
//|                                LIVE Event-Driven AI Trading      |
//+------------------------------------------------------------------+
#property copyright "Alpha Sniper V20"
#property link      ""
#property version   "20.00"

#include <Trade\Trade.mqh>
#include <Math\Stat\Math.mqh>
#include "Models\\XGBoost_Model_WFO_v20_XAUUSD.mqh"
#include "HMA_FUNCTIONS.mqh"

input group "== V20 AI Settings =="
input int    InpRefHMA_Period    = 50;
input double InpAI_Threshold     = 0.65; // Sniper Threshold
input double InpRiskPerTrade     = 2.0;  // Riesgo % 
input double InpTP_ATR           = 10.0;  
input double InpSL_ATR           = 5.0;  
input int    InpATR_Period       = 14;
input int    InpRSI_Period       = 14;

CTrade trade;
int handle_hma, handle_atr, handle_rsi;

double max_distance_since_cross = 0;
int bars_since_cross = 0;
int last_trend_dir = 0;

void OnInit() {
    handle_hma = iCustom(_Symbol, _Period, "HMA50", InpRefHMA_Period);
    handle_atr = iATR(_Symbol, _Period, InpATR_Period);
    handle_rsi = iRSI(_Symbol, _Period, InpRSI_Period, PRICE_CLOSE);
}

void OnDeinit(const int reason) {}

void OnTick() {

    
    static datetime last_bar;
    datetime current_bar = iTime(_Symbol, _Period, 0);
    if(current_bar == last_bar) return;
    last_bar = current_bar;
    
    double close1 = iClose(_Symbol, _Period, 1);
    double open1 = iOpen(_Symbol, _Period, 1);
    
    double hma[5], atr[1], rsi[1];
    if(CopyBuffer(handle_hma, 0, 1, 5, hma) < 5) return;
    if(CopyBuffer(handle_atr, 0, 1, 1, atr) < 1) return;
    if(CopyBuffer(handle_rsi, 0, 1, 1, rsi) < 1) return;
    
    int current_dir = (close1 > hma[0]) ? 1 : -1;
    
    double dist = MathAbs(close1 - hma[0]) / atr[0];
    if(dist > max_distance_since_cross) max_distance_since_cross = dist;
    bars_since_cross++;
    
    if(current_dir != last_trend_dir && last_trend_dir != 0) {
        // Event!
        double features[10];
        features[0] = current_dir;
        features[1] = (hma[0] - hma[3]) / atr[0]; // HMA_Slope
        double prev_slope = (hma[1] - hma[4]) / atr[0];
        features[2] = features[1] - prev_slope; // HMA_Accel
        features[3] = (close1 - open1) / atr[0]; // Candle_Vel
        features[4] = bars_since_cross; // Time_in_Trend
        features[5] = max_distance_since_cross; // Snapback_Dist
        features[6] = rsi[0]; // RSI
        
        MqlDateTime dt;
        TimeToStruct(current_bar, dt);
        double mins = dt.hour * 60 + dt.min;
        features[7] = MathSin(2.0 * M_PI * mins / 1440.0);
        features[8] = MathCos(2.0 * M_PI * mins / 1440.0);
        
        double high10 = iHigh(_Symbol, _Period, iHighest(_Symbol, _Period, MODE_HIGH, 10, 1));
        double low10 = iLow(_Symbol, _Period, iLowest(_Symbol, _Period, MODE_LOW, 10, 1));
        features[9] = (current_dir == 1) ? (close1 - high10)/atr[0] : (close1 - low10)/atr[0];
        
        // Ask AI
        double prob = XGBoost_Predict_WFO_v20_XAUUSD(features, dt.year, dt.mon);
        
        if(prob >= InpAI_Threshold && PositionsTotal() == 0) {
            double sl_price = (current_dir == 1) ? close1 - (InpSL_ATR * atr[0]) : close1 + (InpSL_ATR * atr[0]);
            double tp_price = (current_dir == 1) ? close1 + (InpTP_ATR * atr[0]) : close1 - (InpTP_ATR * atr[0]);
            
            // Calculate risk-based lot size
            double risk_money = AccountInfoDouble(ACCOUNT_BALANCE) * (InpRiskPerTrade / 100.0);
            double sl_points = MathAbs(tp_price - sl_price) / 2.0; // Approximation for 2:1 RR
            sl_points = MathAbs(close1 - sl_price) / SymbolInfoDouble(_Symbol, SYMBOL_POINT);
            double tick_value = SymbolInfoDouble(_Symbol, SYMBOL_TRADE_TICK_VALUE);
            double lots = NormalizeDouble(risk_money / (sl_points * tick_value), 2);
            double min_lot = SymbolInfoDouble(_Symbol, SYMBOL_VOLUME_MIN);
            double max_lot = SymbolInfoDouble(_Symbol, SYMBOL_VOLUME_MAX);
            if(lots < min_lot) lots = min_lot;
            if(lots > max_lot) lots = max_lot;
            
            bool success = false;
            
            if(current_dir == 1) {
                double ask = SymbolInfoDouble(_Symbol, SYMBOL_ASK);
                success = trade.Buy(lots, _Symbol, ask, sl_price, tp_price, "Alpha V20 AI=" + DoubleToString(prob, 2));
            } else {
                double bid = SymbolInfoDouble(_Symbol, SYMBOL_BID);
                success = trade.Sell(lots, _Symbol, bid, sl_price, tp_price, "Alpha V20 AI=" + DoubleToString(prob, 2));
            }
            
            if(!success) {
                Print("Order Failed. Error: ", GetLastError(), " | Prob: ", prob, " | SL: ", sl_price, " | TP: ", tp_price);
            }
        }
        
        max_distance_since_cross = 0;
        bars_since_cross = 0;
    }
    
    last_trend_dir = current_dir;
}

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
#include <HMA_FUNCTIONS.mqh>

input group "== V20 AI Settings =="
input int    InpRefHMA_Period    = 50;
input double InpAI_Threshold     = 0.54; // Sniper Threshold (Baja para +volumen)
input double InpFixedLots        = 1.0;  // Lotaje Fijo para aislar el Edge 
input double InpTP_ATR           = 10.0;  
input double InpSL_ATR           = 5.0;  
input int    InpATR_Period       = 14;
input int    InpRSI_Period       = 14;

input group "== V20 Dynamic Exits =="
input bool   InpUseHMA_Exit      = false; // Salir si cruza HMA en contra
input bool   InpUseTrailingATR   = false; // Usar Trailing Stop
input double InpTrailingATR_Mult = 3.0;  // Multiplicador del Trailing Stop

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

void ManageOpenTrades(double current_close, double hma_val, double atr_val, int current_dir) {
    for(int i = PositionsTotal() - 1; i >= 0; i--) {
        string symbol = PositionGetSymbol(i);
        if(symbol == _Symbol) {
            ulong ticket = PositionGetInteger(POSITION_TICKET);
            long type = PositionGetInteger(POSITION_TYPE);
            double open_price = PositionGetDouble(POSITION_PRICE_OPEN);
            double current_sl = PositionGetDouble(POSITION_SL);
            
            // 1. Salida Dinamica HMA
            if(InpUseHMA_Exit) {
                if(type == POSITION_TYPE_BUY && current_dir == -1) {
                    trade.PositionClose(ticket);
                    Print("Exit BUY: HMA Cross");
                    continue; // Position closed, go to next
                }
                if(type == POSITION_TYPE_SELL && current_dir == 1) {
                    trade.PositionClose(ticket);
                    Print("Exit SELL: HMA Cross");
                    continue; // Position closed, go to next
                }
            }
            
            // 2. Trailing ATR (Solo si esta en profit)
            if(InpUseTrailingATR) {
                double current_price = PositionGetDouble(POSITION_PRICE_CURRENT);
                if(type == POSITION_TYPE_BUY) {
                    double new_sl = current_price - (atr_val * InpTrailingATR_Mult);
                    if(new_sl > current_sl && new_sl > open_price) { 
                        trade.PositionModify(ticket, new_sl, PositionGetDouble(POSITION_TP));
                    }
                } else if(type == POSITION_TYPE_SELL) {
                    double new_sl = current_price + (atr_val * InpTrailingATR_Mult);
                    if((current_sl == 0 || new_sl < current_sl) && new_sl < open_price) {
                        trade.PositionModify(ticket, new_sl, PositionGetDouble(POSITION_TP));
                    }
                }
            }
        }
    }
}

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
    
    // Manage open trades dynamically BEFORE evaluating new crosses
    ManageOpenTrades(close1, hma[0], atr[0], current_dir);
    
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
        
        if(prob >= InpAI_Threshold) {
            double sl_price = (current_dir == 1) ? close1 - (InpSL_ATR * atr[0]) : close1 + (InpSL_ATR * atr[0]);
            double tp_price = (current_dir == 1) ? close1 + (InpTP_ATR * atr[0]) : close1 - (InpTP_ATR * atr[0]);
            
            double lots = InpFixedLots;
            
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


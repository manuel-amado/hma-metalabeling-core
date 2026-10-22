import os
filepath = r'C:\Users\Manuel\Desktop\HMA_MetaLabeling\Alpha_Sniper_Vault\mql5\Alpha_Sniper_V20_Dynamic.mq5'
with open(filepath, 'r') as f:
    content = f.read()

old_str = '''        if(prob >= InpAI_Threshold) {
            double sl_price = (current_dir == 1) ? close1 - (InpSL_ATR * atr[0]) : close1 + (InpSL_ATR * atr[0]);
            double tp_price = (current_dir == 1) ? close1 + (InpTP_ATR * atr[0]) : close1 - (InpTP_ATR * atr[0]);
            
            // Fixed simplified lots for V20 MVP
            double lots = 0.10; 
            
            if(current_dir == 1) {
                trade.Buy(lots, _Symbol, 0, sl_price, tp_price, "Alpha V20 AI=" + DoubleToString(prob, 2));
            } else {
                trade.Sell(lots, _Symbol, 0, sl_price, tp_price, "Alpha V20 AI=" + DoubleToString(prob, 2));
            }
        }'''

new_str = '''        if(prob >= InpAI_Threshold) {
            double sl_price = (current_dir == 1) ? close1 - (InpSL_ATR * atr[0]) : close1 + (InpSL_ATR * atr[0]);
            double tp_price = (current_dir == 1) ? close1 + (InpTP_ATR * atr[0]) : close1 - (InpTP_ATR * atr[0]);
            
            double lots = 0.10; 
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
        }'''

content = content.replace(old_str, new_str)
with open(filepath, 'w') as f:
    f.write(content)

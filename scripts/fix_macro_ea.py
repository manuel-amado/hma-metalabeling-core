import os
filepath = r'C:\Users\Manuel\Desktop\HMA_MetaLabeling\Alpha_Sniper_Vault\mql5\Alpha_Sniper_V20_Dynamic.mq5'
with open(filepath, 'r') as f:
    content = f.read()

# Update default TP/SL inputs
content = content.replace('input double InpTP_ATR           = 2.0;', 'input double InpTP_ATR           = 10.0;')
content = content.replace('input double InpSL_ATR           = 1.0;', 'input double InpSL_ATR           = 5.0;')

# Update lot calculation
old_lots = '''            double lots = 0.10; 
            bool success = false;'''

new_lots = '''            // Calculate risk-based lot size
            double risk_money = AccountInfoDouble(ACCOUNT_BALANCE) * (InpRiskPerTrade / 100.0);
            double sl_points = MathAbs(tp_price - sl_price) / 2.0; // Approximation for 2:1 RR
            sl_points = MathAbs(close1 - sl_price) / SymbolInfoDouble(_Symbol, SYMBOL_POINT);
            double tick_value = SymbolInfoDouble(_Symbol, SYMBOL_TRADE_TICK_VALUE);
            double lots = NormalizeDouble(risk_money / (sl_points * tick_value), 2);
            double min_lot = SymbolInfoDouble(_Symbol, SYMBOL_VOLUME_MIN);
            double max_lot = SymbolInfoDouble(_Symbol, SYMBOL_VOLUME_MAX);
            if(lots < min_lot) lots = min_lot;
            if(lots > max_lot) lots = max_lot;
            
            bool success = false;'''

content = content.replace(old_lots, new_lots)

with open(filepath, 'w') as f:
    f.write(content)

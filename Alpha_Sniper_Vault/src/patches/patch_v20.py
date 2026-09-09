import os
import shutil
import re

source = r'C:\Users\Manuel\Desktop\HMA_MetaLabeling\Alpha_Sniper_Vault\mql5\Alpha_Sniper_v19.mq5'
target = r'C:\Users\Manuel\Desktop\HMA_MetaLabeling\Alpha_Sniper_Vault\mql5\Alpha_Sniper_v20.mq5'

shutil.copy(source, target)

with open(target, 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Update Inputs for Exit
content = re.sub(r'input double InpMaxSLATR\s*=\s*5\.0;', 'input double InpMaxSLATR         = 3.0;', content)
# Remove InpTPATR completely
content = re.sub(r'input double InpTPATR\s*=\s*4\.5;.*?\n', '', content)

# 2. Fix the GetInitialRiskDist function if it references InpTPATR (it usually doesn't, but let's check)
# It uses InpMaxSLATR.

# 3. Fix trade.Buy / trade.Sell to remove TP calculation
tp_block = """                    double tp = 0.0;
                    if(InpTPATR > 0) {
                        if(signalType == 0) tp = ask + (current_atr * InpTPATR);
                        else tp = bid - (current_atr * InpTPATR);
                    }"""
content = content.replace(tp_block, "                    double tp = 0.0; // V20: No static TP. Dynamic Exhaustion only.")

# 4. Modify CheckTrailingStop/ManageOpenTrades
# Let's replace the entire EXIT modes logic in ManageOpenTrades with the Exhaustion logic
target_exit_logic = """                bool hard_close = false;
                if(InpExitMode == EXIT_IMMEDIATE) {
                    if(type == POSITION_TYPE_BUY && hma_exit[0] < hma_exit[1]) hard_close = true;
                    if(type == POSITION_TYPE_SELL && hma_exit[0] > hma_exit[1]) hard_close = true;
                } else if(InpExitMode == EXIT_DELAYED) {
                    if(type == POSITION_TYPE_BUY && hma_exit[0] < hma_exit[1] && hma_exit[1] < hma_exit[2]) hard_close = true;
                    if(type == POSITION_TYPE_SELL && hma_exit[0] > hma_exit[1] && hma_exit[1] > hma_exit[2]) hard_close = true;
                } else if(InpExitMode == EXIT_TRAILING_ATR) {"""

new_exit_logic = """                bool hard_close = false;
                // V20: EXHAUSTION EXIT LOGIC
                // Condicion 1: La media HMA rapida (InpHMA_Exit_Period) se gira en contra del trade
                if(type == POSITION_TYPE_BUY && hma_exit[0] < hma_exit[1]) hard_close = true;
                if(type == POSITION_TYPE_SELL && hma_exit[0] > hma_exit[1]) hard_close = true;
                
                // Condicion 2: Contracción extrema tras expansión (Precio vuelve dentro de bandas Bollinger)
                double upper_band_1 = sma20[1] + (2.0 * stddev[1]);
                double lower_band_1 = sma20[1] - (2.0 * stddev[1]);
                double upper_band_0 = sma20[0] + (2.0 * stddev[0]);
                double lower_band_0 = sma20[0] - (2.0 * stddev[0]);
                
                if(type == POSITION_TYPE_BUY && rates[1].close > upper_band_1 && rates[0].close < upper_band_0) hard_close = true;
                if(type == POSITION_TYPE_SELL && rates[1].close < lower_band_1 && rates[0].close > lower_band_0) hard_close = true;

                // Mantenemos el trailing stop de ATR como red de seguridad adicional
                if(true) {"""

content = content.replace(target_exit_logic, new_exit_logic)

with open(target, 'w', encoding='utf-8') as f:
    f.write(content)
print("Alpha_Sniper_v20.mq5 generated and patched.")
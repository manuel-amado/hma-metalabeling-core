import os
import re
import shutil

source = r'C:\Users\Manuel\Desktop\HMA_MetaLabeling\Alpha_Sniper_Vault\mql5\Alpha_Sniper_v19.mq5'
target = r'C:\Users\Manuel\Desktop\HMA_MetaLabeling\Alpha_Sniper_Vault\mql5\Alpha_Sniper_v21.mq5'
shutil.copy(source, target)

with open(target, 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Update SL inputs
content = re.sub(r'input double InpMaxSLATR\s*=\s*5\.0;', 'input double InpMaxSLATR         = 3.0;', content)
content = re.sub(r'input double InpTPATR\s*=\s*4\.5;.*?\n', '', content)

# 2. Fix trade.Buy / trade.Sell to remove TP calculation
tp_block = """                    double tp = 0.0;
                    if(InpTPATR > 0) {
                        if(signalType == 0) tp = ask + (current_atr * InpTPATR);
                        else tp = bid - (current_atr * InpTPATR);
                    }"""
content = content.replace(tp_block, "                    double tp = 0.0; // V21: No static TP. HMA Baseline Exit.")

# 3. Replace the EXIT modes logic with V21 Baseline Exit
target_manage = """        double hma_exit[2], rsi_buf[1], stddev[1], sma20[1], atr_d1_buf[1];
        MqlRates rates[];
        ArraySetAsSeries(rates, true);
        
        if(CopyBuffer(hma_exit_handle, 0, 0, 2, hma_exit) < 2) return;
        if(CopyBuffer(rsi_handle, 0, 0, 1, rsi_buf) < 1) return;
        if(CopyRates(m_symbol, _Period, 0, 2, rates) < 2) return;
        
        CopyBuffer(std_dev_handle, 0, 0, 1, stddev);
        CopyBuffer(sma20_handle, 0, 0, 1, sma20);
        CopyBuffer(atr_d1_handle, 0, 0, 1, atr_d1_buf);"""

new_manage = """        double hma_entry_chk[2], rsi_buf[1], stddev[1], sma20[1], atr_d1_buf[1];
        MqlRates rates[];
        ArraySetAsSeries(rates, true);
        
        // V21: Obtenemos el HMA 50 (hma_entry) en lugar de hma_exit para la Baseline
        if(CopyBuffer(hma_entry_handle, 0, 1, 2, hma_entry_chk) < 2) return;
        if(CopyBuffer(rsi_handle, 0, 1, 1, rsi_buf) < 1) return;
        if(CopyRates(m_symbol, _Period, 0, 3, rates) < 3) return; // 0=abierta, 1=cerrada, 2=anterior a cerrada
        
        CopyBuffer(std_dev_handle, 0, 1, 1, stddev);
        CopyBuffer(sma20_handle, 0, 1, 1, sma20);
        CopyBuffer(atr_d1_handle, 0, 1, 1, atr_d1_buf);
        
        ArraySetAsSeries(hma_entry_chk, true);"""

content = content.replace(target_manage, new_manage)

target_exit_logic = """                bool hard_close = false;
                if(InpExitMode == EXIT_IMMEDIATE) {
                    if(type == POSITION_TYPE_BUY && hma_exit[0] < hma_exit[1]) hard_close = true;
                    if(type == POSITION_TYPE_SELL && hma_exit[0] > hma_exit[1]) hard_close = true;
                } else if(InpExitMode == EXIT_DELAYED) {
                    if(type == POSITION_TYPE_BUY && hma_exit[0] < hma_exit[1] && hma_exit[1] < hma_exit[2]) hard_close = true;
                    if(type == POSITION_TYPE_SELL && hma_exit[0] > hma_exit[1] && hma_exit[1] > hma_exit[2]) hard_close = true;
                } else if(InpExitMode == EXIT_TRAILING_ATR) {"""

new_exit_logic = """                bool hard_close = false;
                
                // V21: EXHAUSTION EXIT LOGIC (BASELINE CROSS)
                // Usamos la HMA de entrada (HMA 50) como Baseline de tendencia.
                // Si el precio CERRADO (rates[1]) cruza en contra del HMA 50 (hma_entry_chk[0]), salimos inmediatamente.
                if(type == POSITION_TYPE_BUY && rates[1].close < hma_entry_chk[0]) hard_close = true;
                if(type == POSITION_TYPE_SELL && rates[1].close > hma_entry_chk[0]) hard_close = true;
                
                // Mantenemos el trailing stop de ATR como red de seguridad adicional (Cisnes negros)
                if(true) {"""

content = content.replace(target_exit_logic, new_exit_logic)

with open(target, 'w', encoding='utf-8') as f:
    f.write(content)
print("Alpha_Sniper_v21.mq5 generated and patched.")
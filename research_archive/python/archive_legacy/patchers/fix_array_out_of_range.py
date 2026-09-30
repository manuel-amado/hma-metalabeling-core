import os
import re

filepath = r'C:\Users\Manuel\Desktop\HMA_MetaLabeling\Alpha_Sniper_Vault\mql5\Alpha_Sniper_v20.mq5'
with open(filepath, 'r', encoding='utf-8') as f:
    content = f.read()

# Buscamos el inicio de ManageOpenTrades
target_manage = """        double hma_exit[2], rsi_buf[1], stddev[1], sma20[1], atr_d1_buf[1];
        MqlRates rates[];
        ArraySetAsSeries(rates, true);
        
        if(CopyBuffer(hma_exit_handle, 0, 0, 2, hma_exit) < 2) return;
        if(CopyBuffer(rsi_handle, 0, 0, 1, rsi_buf) < 1) return;
        if(CopyRates(m_symbol, _Period, 0, 2, rates) < 2) return;
        
        CopyBuffer(std_dev_handle, 0, 0, 1, stddev);
        CopyBuffer(sma20_handle, 0, 0, 1, sma20);
        CopyBuffer(atr_d1_handle, 0, 0, 1, atr_d1_buf);"""

new_manage = """        double hma_exit[2], rsi_buf[1], stddev[2], sma20[2], atr_d1_buf[1];
        MqlRates rates[];
        ArraySetAsSeries(rates, true);
        
        // Copiamos datos desde el índice 1 (vela ya cerrada) para mayor precisión
        if(CopyBuffer(hma_exit_handle, 0, 1, 2, hma_exit) < 2) return;
        if(CopyBuffer(rsi_handle, 0, 1, 1, rsi_buf) < 1) return;
        if(CopyRates(m_symbol, _Period, 0, 3, rates) < 3) return; // 0=abierta, 1=cerrada, 2=anterior a cerrada
        
        if(CopyBuffer(std_dev_handle, 0, 1, 2, stddev) < 2) return;
        if(CopyBuffer(sma20_handle, 0, 1, 2, sma20) < 2) return;
        CopyBuffer(atr_d1_handle, 0, 1, 1, atr_d1_buf);
        
        ArraySetAsSeries(hma_exit, true);
        ArraySetAsSeries(stddev, true);
        ArraySetAsSeries(sma20, true);"""

content = content.replace(target_manage, new_manage)

# Ahora corregimos la condición de agotamiento, ya que ArraySetAsSeries es true
# Index 0 = vela recién cerrada, Index 1 = vela anterior
target_exit = """                // V20: EXHAUSTION EXIT LOGIC
                // Condicion 1: La media HMA rapida (InpHMA_Exit_Period) se gira en contra del trade
                if(type == POSITION_TYPE_BUY && hma_exit[0] < hma_exit[1]) hard_close = true;
                if(type == POSITION_TYPE_SELL && hma_exit[0] > hma_exit[1]) hard_close = true;
                
                // Condicion 2: Contracción extrema tras expansión (Precio vuelve dentro de bandas Bollinger)
                double upper_band_1 = sma20[1] + (2.0 * stddev[1]);
                double lower_band_1 = sma20[1] - (2.0 * stddev[1]);
                double upper_band_0 = sma20[0] + (2.0 * stddev[0]);
                double lower_band_0 = sma20[0] - (2.0 * stddev[0]);
                
                if(type == POSITION_TYPE_BUY && rates[1].close > upper_band_1 && rates[0].close < upper_band_0) hard_close = true;
                if(type == POSITION_TYPE_SELL && rates[1].close < lower_band_1 && rates[0].close > lower_band_0) hard_close = true;"""

new_exit = """                // V20: EXHAUSTION EXIT LOGIC
                // Condicion 1: La media HMA rápida se gira en contra del trade
                // Como hma_exit tiene ArraySetAsSeries(true), el indice 0 es la vela recién cerrada, y el 1 es la anterior.
                if(type == POSITION_TYPE_BUY && hma_exit[0] < hma_exit[1]) hard_close = true;
                if(type == POSITION_TYPE_SELL && hma_exit[0] > hma_exit[1]) hard_close = true;
                
                // Condicion 2: Contracción extrema tras expansión (Precio vuelve dentro de bandas Bollinger)
                // rates[2] = vela anterior a la cerrada, rates[1] = vela recién cerrada
                double upper_band_1 = sma20[1] + (2.0 * stddev[1]);
                double lower_band_1 = sma20[1] - (2.0 * stddev[1]);
                double upper_band_0 = sma20[0] + (2.0 * stddev[0]);
                double lower_band_0 = sma20[0] - (2.0 * stddev[0]);
                
                if(type == POSITION_TYPE_BUY && rates[2].close > upper_band_1 && rates[1].close < upper_band_0) hard_close = true;
                if(type == POSITION_TYPE_SELL && rates[2].close < lower_band_1 && rates[1].close > lower_band_0) hard_close = true;"""

content = content.replace(target_exit, new_exit)

with open(filepath, 'w', encoding='utf-8') as f:
    f.write(content)
print("Parche aplicado con exito a Alpha_Sniper_v20.mq5")
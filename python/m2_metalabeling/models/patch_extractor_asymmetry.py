import re
import os

f_path = r'C:\Users\Manuel\Desktop\HMA_MetaLabeling\mql5\Experts\HMA_SQX_Discovery\Pipeline_Extractor_M1.mq5'
with open(f_path, 'r', encoding='utf-8') as f:
    code = f.read()

# 1. Eliminar Profit Target (Take Profit = 0)
code = re.sub(
    r'pt\s*=\s*sqFixMarketPrice\(sqGetPTLevel\("Current",\s*ORDER_TYPE_BUY,\s*openPrice,\s*2,\s*ProfitTargetCoef1\s*\*\s*sqGetIndicatorValue\(ATR_1,\s*1\)\),\s*"Current"\);',
    'pt = 0; // TAKE PROFIT DESACTIVADO (Asimetria Liberada)',
    code
)

code = re.sub(
    r'pt\s*=\s*sqFixMarketPrice\(sqGetPTLevel\("Current",\s*ORDER_TYPE_SELL,\s*openPrice,\s*2,\s*ProfitTargetCoef2\s*\*\s*sqGetIndicatorValue\(ATR_2,\s*1\)\),\s*"Current"\);',
    'pt = 0; // TAKE PROFIT DESACTIVADO (Asimetria Liberada)',
    code
)

# 2. Implementar Trailing Stop Dinamico basado en ATR (x3)
trailing_stop_logic = """
        // --- CUSTOM TRAILING STOP LOGIC (ATR DYNAMIC) ---
        for (int i = PositionsTotal() - 1; i >= 0; i--) {
            ulong posTicket = PositionGetTicket(i);
            if (PositionGetString(POSITION_SYMBOL) == _Symbol) {
                double current_sl = PositionGetDouble(POSITION_SL);
                double current_price = PositionGetDouble(POSITION_PRICE_CURRENT);
                double open_price = PositionGetDouble(POSITION_PRICE_OPEN);
                long pos_type = PositionGetInteger(POSITION_TYPE);
                
                double atrH1[];
                int atrHandle = iATR(_Symbol, PERIOD_H1, 14);
                CopyBuffer(atrHandle, 0, 1, 1, atrH1);
                double ts_distance = atrH1[0] * 3.0; // Trailing Stop a 3 ATR
                
                if (pos_type == POSITION_TYPE_BUY) {
                    double new_sl = current_price - ts_distance;
                    if (new_sl > open_price && (current_sl == 0 || new_sl > current_sl)) {
                        trade.PositionModify(posTicket, new_sl, 0); // Modificamos solo SL, PT=0
                    }
                }
            }
        }
        // ------------------------------------------------
"""

# Insertar el Trailing Stop en la funcion OnTick, justo antes de EvaluateXGBoost o al final
if "// --- CUSTOM TRAILING STOP LOGIC (ATR DYNAMIC) ---" not in code:
    code = code.replace('void OnTick() {', 'void OnTick() {\n' + trailing_stop_logic)

with open(f_path, 'w', encoding='utf-8') as f:
    f.write(code)

print("Extractor parcheado: RR Estatico desactivado. Trailing Stop Dinamico (3 ATR) inyectado.")

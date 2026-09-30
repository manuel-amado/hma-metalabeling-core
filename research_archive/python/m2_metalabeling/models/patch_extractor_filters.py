import re
import os

f_path = r'C:\Users\Manuel\Desktop\HMA_MetaLabeling\mql5\Experts\HMA_SQX_Discovery\Pipeline_Extractor_M1.mq5'
with open(f_path, 'r', encoding='utf-8') as f: code = f.read()

# 1. Forzar TradeShorts = false y MaxSpreadPoints = 50 (por defecto)
code = re.sub(r'input\s+bool\s+TradeShorts\s*=\s*(?:true|false);\s*//.*', 'input bool TradeShorts = false; // LONG-ONLY INSTITUCIONAL', code)
code = re.sub(r'input\s+int\s+MaxSpreadPoints\s*=\s*\d+;\s*//.*', 'input int MaxSpreadPoints = 50; // Spread Max estatico', code)
code = re.sub(r'input\s+double\s+RegimeADX_MinTrend\s*=\s*\d+\.\d+;\s*//.*', 'input double RegimeADX_MinTrend = 25.0;  // ADX Diario minimo', code)

# 2. Modificar IsSpreadSafe para que sea dinamico (25% del ATR H1)
dynamic_spread_logic = '''bool IsSpreadSafe(int max_spread_points = 50) {
    int current_spread = (int)SymbolInfoInteger(_Symbol, SYMBOL_SPREAD);
    
    // Filtro Dinamico ATR (25%)
    double atrH1[];
    int atrHandle = iATR(_Symbol, PERIOD_H1, 14);
    CopyBuffer(atrHandle, 0, 1, 1, atrH1);
    
    if (atrH1[0] > 0) {
        double spread_price = current_spread * _Point;
        if (spread_price > (0.25 * atrH1[0])) {
            return false;
        }
    }
    
    // Filtro Estatico de Respaldo
    if(current_spread > max_spread_points) {
        return false;
    }
    return true;
}'''

code = re.sub(r'bool\s+IsSpreadSafe\s*\(\s*int\s+max_spread_points[^}]+\}\s*return\s+(?:true|false);\s*\}', dynamic_spread_logic, code, flags=re.MULTILINE|re.DOTALL)

with open(f_path, 'w', encoding='utf-8') as f: f.write(code)
print('Extractor parcheado exitosamente con filtros institucionales.')

import re

file_path = r'C:\Users\Manuel\Desktop\HMA_MetaLabeling\mql5\Experts\HMA_SQX_Discovery\Strategy 2.91.69.mq5'
with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
    code = f.read()

# 1. Añadir input para el ADX threshold
new_input = """input int RegimeADX_Period = 14;         // Periodo ADX del Filtro de Regimen
input double RegimeADX_MinTrend = 25.0;  // ADX Diario minimo para operar (0=desactivado)
"""
code = code.replace(
    'input bool TradeLongs = true;',
    new_input + 'input bool TradeLongs = true;'
)

# 2. Añadir la función IsRegimeTrending() antes de las demás funciones de riesgo
regime_function = """
//+------------------------------------------------------------------+
//| FASE 1: Filtro de Regimen de Mercado (ADX Diario)               |
//| Aborta cualquier señal si el mercado está en rango lateral       |
//| Previene operar en regimenes destructivos (ej. 2026 Q1)         |
//+------------------------------------------------------------------+
bool IsRegimeTrending() {
    if (RegimeADX_MinTrend <= 0) return true; // Filtro desactivado
    
    int adx_handle = iADX(_Symbol, PERIOD_D1, RegimeADX_Period);
    if (adx_handle == INVALID_HANDLE) return true; // Si falla, no bloqueamos
    
    double adx_val[1];
    if (CopyBuffer(adx_handle, 0, 1, 1, adx_val) <= 0) {
        IndicatorRelease(adx_handle);
        return true;
    }
    IndicatorRelease(adx_handle);
    
    bool trending = adx_val[0] > RegimeADX_MinTrend;
    if (!trending) {
        Print("REGIMEN: ADX Diario = ", DoubleToString(adx_val[0], 2),
              " <= ", RegimeADX_MinTrend, ". Mercado lateral. Señal abortada.");
    }
    return trending;
}
"""
# Inyectar antes del bloque de IsDailyDrawdownSafe
code = code.replace(
    '//| FASE 2A: FTMO Daily Drawdown Kill-Switch',
    regime_function + '\n  //| FASE 2A: FTMO Daily Drawdown Kill-Switch'
)

# 3. Inyectar el check en la entrada Long (inmediatamente después del check de TradeLongs)
code = code.replace(
    'if (_sqIsBarOpen == true && LongEntrySignal && TradeLongs) {\n        if(!IsDailyDrawdownSafe(MaxDailyDrawdown)) return;',
    'if (_sqIsBarOpen == true && LongEntrySignal && TradeLongs) {\n        if(!IsRegimeTrending()) return;\n        if(!IsDailyDrawdownSafe(MaxDailyDrawdown)) return;'
)

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(code)

print('Filtro de Regimen ADX Diario inyectado correctamente.')
print('Input: RegimeADX_Period = 14, RegimeADX_MinTrend = 25.0')
print('Funcion: IsRegimeTrending() -> iADX(PERIOD_D1, 14, vela anterior)')

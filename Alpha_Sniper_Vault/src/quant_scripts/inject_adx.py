import re

file_path = r"C:\Users\Manuel\AppData\Roaming\MetaQuotes\Terminal\D0E8209F77C8CF37AD8BF550E51FF075\MQL5\Experts\Alpha_Sniper\Alpha_Sniper_Master6.mq5"
with open(file_path, "r", encoding="utf-8") as f:
    text = f.read()

# 1. Add Inputs
inputs_str = """input group "=== Filtro de Regimen Macro ==="
input bool   InpUseADXFilter     = true;   // Activar filtro ADX Diario
input int    InpADXPeriod        = 14;     // Periodo del ADX
input double InpMinDailyADX      = 25.0;   // Valor minimo ADX para operar (Tendencia)

input group "=== Filtro Macro Inter-Mercado (DXY) ==="""
text = text.replace('input group "=== Filtro Macro Inter-Mercado (DXY) ==="', inputs_str)

# 2. Add Globals
globals_str = """int dxy_hma_handle = INVALID_HANDLE;
int adx_handle = INVALID_HANDLE;"""
text = text.replace('int dxy_hma_handle = INVALID_HANDLE;', globals_str)

# 3. OnInit
oninit_str = """    if(InpUseDXYFilter) {
        dxy_hma_handle = iCustom(InpDXYSymbol, _Period, "HMA50", InpHMA_Period);
        if(dxy_hma_handle == INVALID_HANDLE) Print("ERROR: No se pudo cargar HMA para ", InpDXYSymbol);
    }
    
    if(InpUseADXFilter) {
        adx_handle = iADX(_Symbol, PERIOD_D1, InpADXPeriod);
        if(adx_handle == INVALID_HANDLE) Print("ERROR: No se pudo cargar ADX para ", _Symbol);
    }"""
text = text.replace("""    if(InpUseDXYFilter) {
        dxy_hma_handle = iCustom(InpDXYSymbol, _Period, "HMA50", InpHMA_Period);
        if(dxy_hma_handle == INVALID_HANDLE) Print("ERROR: No se pudo cargar HMA para ", InpDXYSymbol);
    }""", oninit_str)

# 4. OnDeinit
ondeinit_str = """    if(dxy_hma_handle != INVALID_HANDLE) IndicatorRelease(dxy_hma_handle);
    if(adx_handle != INVALID_HANDLE) IndicatorRelease(adx_handle);"""
text = text.replace("""    if(dxy_hma_handle != INVALID_HANDLE) IndicatorRelease(dxy_hma_handle);""", ondeinit_str)

# 5. OnTick
ontick_str = """    if(atr_d1[1] < InpMinDailyATR) { lastBarTime = currentBarTime; return; }
    
    // ---- FILTRO ADX DIARIO (Régimen de Tendencia) ----
    if(InpUseADXFilter && adx_handle != INVALID_HANDLE) {
        double adx_buffer[]; ArraySetAsSeries(adx_buffer, true);
        if(CopyBuffer(adx_handle, 0, 1, 1, adx_buffer) == 1) { // Shift 1 (vela diaria cerrada)
            if(adx_buffer[0] < InpMinDailyADX) {
                lastBarTime = currentBarTime; 
                return; // Mercado en rango lateral, abortar.
            }
        }
    }"""
text = text.replace("""    if(atr_d1[1] < InpMinDailyATR) { lastBarTime = currentBarTime; return; }""", ontick_str)


with open(file_path, "w", encoding="utf-8") as f:
    f.write(text)
print("ADX Filter injected.")
import re

file_path = r"C:\Users\Manuel\AppData\Roaming\MetaQuotes\Terminal\D0E8209F77C8CF37AD8BF550E51FF075\MQL5\Experts\Alpha_Sniper\Alpha_Sniper_Master6.mq5"
with open(file_path, "r", encoding="utf-8") as f:
    text = f.read()

# 1. Inputs
dxy_inputs = """input group "=== Filtro Macro Inter-Mercado (DXY) ==="
input bool   InpUseDXYFilter     = false;
input string InpDXYSymbol        = "DXY";

input group "=== Ejecucion Institucional ==="""
text = text.replace('input group "=== Ejecucion Institucional ==="', dxy_inputs)

# 2. Globals
globals_str = """datetime lastBarTime = 0;
int csv_handle = INVALID_HANDLE;
int dxy_hma_handle = INVALID_HANDLE;"""
text = text.replace("""datetime lastBarTime = 0;
int csv_handle = INVALID_HANDLE;""", globals_str)

# 3. OnInit
oninit_str = """    trade.SetExpertMagicNumber(28006);
    
    if(InpUseDXYFilter) {
        dxy_hma_handle = iCustom(InpDXYSymbol, _Period, "HMA50", InpHMA_Period);
        if(dxy_hma_handle == INVALID_HANDLE) Print("ERROR: No se pudo cargar HMA para ", InpDXYSymbol);
    }
    
    if(InpExportMetaLabeling"""
text = text.replace("""    trade.SetExpertMagicNumber(28006);
    
    if(InpExportMetaLabeling""", oninit_str)

# 4. OnDeinit
ondeinit_str = """void OnDeinit(const int reason) {
    if(csv_handle != INVALID_HANDLE) FileClose(csv_handle);
    if(dxy_hma_handle != INVALID_HANDLE) IndicatorRelease(dxy_hma_handle);"""
text = text.replace("""void OnDeinit(const int reason) {
    if(csv_handle != INVALID_HANDLE) FileClose(csv_handle);""", ondeinit_str)

# 5. OnTick logic
dxy_logic = """    if(valid_buildup && valid_rsi_long && cross_up)   signal = 1;
    if(valid_buildup && valid_rsi_short && cross_dn)  signal = -1;
    if(!valid_impulse) signal = 0;

    // ---- FILTRO DXY INTER-MERCADO ----
    if(signal != 0 && InpUseDXYFilter && dxy_hma_handle != INVALID_HANDLE) {
        double dxy_hma[]; ArraySetAsSeries(dxy_hma, true);
        if(CopyBuffer(dxy_hma_handle, 0, 0, 2, dxy_hma) == 2) {
            double current_dxy_close = iClose(InpDXYSymbol, _Period, 1);
            if(current_dxy_close > 0) {
                bool dxy_is_bullish = (current_dxy_close > dxy_hma[1]);
                bool dxy_is_bearish = (current_dxy_close < dxy_hma[1]);
                
                // Si el Oro compra (alcista) pero el Dolar (DXY) tambien es alcista -> Divergencia (Bull Trap)
                if(signal == 1 && dxy_is_bullish) {
                    Print("DXY Filter: Abortando Compra en Oro porque DXY es Alcista.");
                    signal = 0;
                }
                // Si el Oro vende (bajista) pero el Dolar (DXY) tambien es bajista -> Divergencia (Bear Trap)
                if(signal == -1 && dxy_is_bearish) {
                    Print("DXY Filter: Abortando Venta en Oro porque DXY es Bajista.");
                    signal = 0;
                }
            }
        }
    }"""
    
text = text.replace("""    if(valid_buildup && valid_rsi_long && cross_up)   signal = 1;
    if(valid_buildup && valid_rsi_short && cross_dn)  signal = -1;
    if(!valid_impulse) signal = 0;""", dxy_logic)

with open(file_path, "w", encoding="utf-8") as f:
    f.write(text)
print("DXY Filter injected.")
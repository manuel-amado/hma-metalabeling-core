import os
import re

file_in = r"C:\Users\Manuel\AppData\Roaming\MetaQuotes\Terminal\D0E8209F77C8CF37AD8BF550E51FF075\MQL5\Experts\Alpha_Sniper\Alpha_Sniper_Master5.mq5"
file_out = r"C:\Users\Manuel\AppData\Roaming\MetaQuotes\Terminal\D0E8209F77C8CF37AD8BF550E51FF075\MQL5\Experts\Alpha_Sniper\Alpha_Sniper_Master6.mq5"

with open(file_in, "r", encoding="utf-8") as f:
    text = f.read()

# 1. Update Names
text = text.replace("Alpha_Sniper_Master5", "Alpha_Sniper_Master6")
text = text.replace('version   "5.0"', 'version   "6.0"')

# 2. Add New Inputs
inputs_to_add = """
input group "=== Ejecucion Institucional ==="
input int    InpMaxSpreadPoints  = 40;     // Spread maximo permitido (puntos)
input ulong  InpMaxSlippage      = 20;     // Slippage maximo (puntos)
input double InpMaxMarginPct     = 80.0;   // % Maximo de Margen Libre a usar

input group "=== Escudos de Curva de Capital (ECT) ==="""
text = text.replace('input group "=== Escudos de Curva de Capital (ECT) ==="', inputs_to_add)

# 3. Modify CalculateLotSize
margin_logic = """    if(rounded_lots > max_lot) rounded_lots = max_lot;
    
    // --- MARGIN CHECK (Anti 'Invalid Volume'/'No Money') ---
    double margin_required = 0.0;
    if(OrderCalcMargin(order_type, _Symbol, rounded_lots, open_price, margin_required)) {
        double free_margin = AccountInfoDouble(ACCOUNT_MARGIN_FREE);
        double max_allowed_margin = free_margin * (InpMaxMarginPct / 100.0);
        
        if(margin_required > max_allowed_margin) {
            Print("WARNING: Lotaje reducido por falta de margen. Requerido: ", margin_required, " Permitido: ", max_allowed_margin);
            rounded_lots = rounded_lots * (max_allowed_margin / margin_required);
            rounded_lots = MathFloor(rounded_lots / lot_step) * lot_step;
        }
    }
    
    if(rounded_lots < min_lot) return 0.0;
    return rounded_lots;"""
text = re.sub(r'if\(rounded_lots > max_lot\) rounded_lots = max_lot;\s*return rounded_lots;', margin_logic, text)

# 4. Modify OnInit
init_logic = """    trade.SetExpertMagicNumber(28006);
    trade.SetDeviationInPoints(InpMaxSlippage);"""
text = re.sub(r'trade\.SetExpertMagicNumber\(\d+\);', init_logic, text)

# 5. Modify OnTick Spread Check
spread_logic = """    // ---- ESCUDOS MACRO Y HORARIO ----
    long current_spread = SymbolInfoInteger(_Symbol, SYMBOL_SPREAD);
    if(current_spread > InpMaxSpreadPoints) { lastBarTime = currentBarTime; return; }
"""
text = text.replace('    // ---- ESCUDOS MACRO Y HORARIO ----\n', spread_logic)

with open(file_out, "w", encoding="utf-8") as f:
    f.write(text)
print(f"Master6 generated successfully at {file_out}")
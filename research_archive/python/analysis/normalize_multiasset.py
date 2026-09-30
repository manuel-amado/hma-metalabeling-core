import re

file_path = r"C:\Users\Manuel\AppData\Roaming\MetaQuotes\Terminal\D0E8209F77C8CF37AD8BF550E51FF075\MQL5\Experts\Alpha_Sniper\Alpha_Sniper_Master6.mq5"
with open(file_path, "r", encoding="utf-8") as f:
    text = f.read()

# 1. Extract Magic Number to Input
magic_input = """input group "=== Configuracion Base Python ==="
input int    InpMagicNumber      = 28006;  // Magic Number (DNI del Bot)
input int    InpHMA_Period       = 200;"""
text = text.replace("""input group "=== Configuracion Base Python ==="
input int    InpHMA_Period       = 200;""", magic_input)

# 2. Update OnInit to use InpMagicNumber
text = text.replace("trade.SetExpertMagicNumber(28006);", "trade.SetExpertMagicNumber(InpMagicNumber);")

# 3. Update ECT History Filtering
ect_old = """    for(int i = total - 1; i >= 0; i--) {
        ulong ticket = HistoryDealGetTicket(i);
        long entry = HistoryDealGetInteger(ticket, DEAL_ENTRY);
        if(entry == DEAL_ENTRY_OUT || entry == DEAL_ENTRY_INOUT) {"""

ect_new = """    for(int i = total - 1; i >= 0; i--) {
        ulong ticket = HistoryDealGetTicket(i);
        long entry = HistoryDealGetInteger(ticket, DEAL_ENTRY);
        long magic = HistoryDealGetInteger(ticket, DEAL_MAGIC);
        string sym = HistoryDealGetString(ticket, DEAL_SYMBOL);
        
        // Filtro estricto Multi-Activo: Solo leer deals de este grafico y este bot
        if(magic != InpMagicNumber || sym != _Symbol) continue;
        
        if(entry == DEAL_ENTRY_OUT || entry == DEAL_ENTRY_INOUT) {"""
text = text.replace(ect_old, ect_new)

with open(file_path, "w", encoding="utf-8") as f:
    f.write(text)
print("Multi-Asset normalization injected.")
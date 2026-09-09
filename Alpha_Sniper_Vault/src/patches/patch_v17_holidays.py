import os
import re

filepath = r'C:\Users\Manuel\Desktop\HMA_MetaLabeling\Alpha_Sniper_Vault\mql5\Alpha_Sniper_v17.mq5'
with open(filepath, 'r', encoding='utf-8') as f:
    content = f.read()

# Buscamos donde inyectar el filtro de vacaciones y rollover
# En la funcion CanOpenNewTrade:
target = "double current_global_risk = 0.0;"
injection = """
      // [ALINEACION CON PYTHON TRAINING] Bloqueo de Rollover y Navidades
      MqlDateTime dt_curr;
      TimeToStruct(cur_time, dt_curr);
      
      // 1. Bloqueo de Rollover (23:00 a 00:00)
      if(dt_curr.hour == 23 || dt_curr.hour == 0) {
          blockReason = "Rollover";
          Print("[ANTI-NEWS SHIELD] Orden bloqueada en ", candidate_symbol, ". Razon: ", blockReason);
          return false;
      }
      
      // 2. Bloqueo de Navidades / Fin de anio (24 Dic a 2 Ene)
      if((dt_curr.mon == 12 && dt_curr.day >= 24) || (dt_curr.mon == 1 && dt_curr.day <= 2)) {
          blockReason = "Bank Holiday (Navidad)";
          Print("[ANTI-NEWS SHIELD] Orden bloqueada en ", candidate_symbol, ". Razon: ", blockReason);
          return false;
      }
      
"""

if "Bloqueo de Rollover y Navidades" not in content:
    content = content.replace(target, injection + target)
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    print("Filtros hardcodeados en Alpha_Sniper_v17.mq5 con exito.")
else:
    print("El filtro ya estaba inyectado.")
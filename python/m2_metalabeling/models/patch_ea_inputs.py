import re
file_path = r'C:\Users\Manuel\Desktop\HMA_MetaLabeling\mql5\Experts\HMA_SQX_Discovery\Strategy 2.91.69.mq5'
with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
    code = f.read()

# 1. Inject Input Parameters
inputs_block = """input string srmm = "----------- Institutional Risk Engine (AGY) -----------";
input bool UseCompounding = false; // Interes Compuesto (False = Fijo al Balance Inicial)
input double KellyFraction = 0.0358; // Fraccion Kelly base
input double MaxRiskPerTrade = 0.02; // Limite Riesgo por Trade (Ej. 0.02 = 2%)
input double MaxDailyDrawdown = 0.045; // Max Daily Drawdown (Ej. 0.045 = 4.5%)
input int MaxSpreadPoints = 50; // Max Spread en Puntos (Pon 9999 para Backtest)
input double XGBoostThreshold = 0.36; // XGBoost M2 Prob Threshold
"""
if 'Institutional Risk Engine (AGY)' not in code:
    code = code.replace('//+------------------------------------------------------------------+\n// Money Management variables', 
                        inputs_block + '\n//+------------------------------------------------------------------+\n// Money Management variables')

# 2. Update GetKellyLotSize function signature and logic
old_kelly_sig = 'double GetKellyLotSize(double atr_sl_points, double kelly_pct = 0.0358, double max_risk_pct = 0.02) {'
new_kelly_sig = """double GetKellyLotSize(double atr_sl_points, double kelly_pct, double max_risk_pct) {
      double current_equity;
      if (UseCompounding) {
          current_equity = AccountInfoDouble(ACCOUNT_EQUITY); // Interes compuesto dinamico
      } else {
          static double initial_equity = AccountInfoDouble(ACCOUNT_BALANCE); // Fijo al inicio
          current_equity = initial_equity; // Desactiva el interes compuesto
      }"""
code = code.replace(old_kelly_sig, new_kelly_sig)

# Clean up any leftover 'double current_equity = AccountInfoDouble(ACCOUNT_EQUITY);' right after the signature
code = re.sub(r'(double current_equity;\s+if \(UseCompounding\) \{[\s\S]*?current_equity = initial_equity; // Desactiva el interes compuesto\s+\})\s+double current_equity = AccountInfoDouble\(ACCOUNT_EQUITY\); // VPS Live: Interés compuesto dinámico', r'\1', code)
code = re.sub(r'(double current_equity;\s+if \(UseCompounding\) \{[\s\S]*?current_equity = initial_equity; // Desactiva el interes compuesto\s+\})\s+double current_equity = AccountInfoDouble\(ACCOUNT_EQUITY\);', r'\1', code)

# 3. Update calls to GetKellyLotSize
code = re.sub(r'GetKellyLotSize\([^,]+,\s*0\.0358,\s*0\.02\)', lambda m: m.group(0).replace('0.0358, 0.02', 'KellyFraction, MaxRiskPerTrade'), code)

# 4. Update IsSpreadSafe calls
code = re.sub(r'if\(!IsSpreadSafe\(\d+\)\)', 'if(!IsSpreadSafe(MaxSpreadPoints))', code)
code = re.sub(r'if\(!IsSpreadSafe\(\)\)', 'if(!IsSpreadSafe(MaxSpreadPoints))', code)

# 5. Update IsDailyDrawdownSafe calls
code = re.sub(r'if\(!IsDailyDrawdownSafe\([\d\.]+\)\)', 'if(!IsDailyDrawdownSafe(MaxDailyDrawdown))', code)

# 6. Update XGBoost Threshold checks
code = re.sub(r'if\s*\(\s*prob\s*>=\s*0\.36\s*\)', 'if (prob >= XGBoostThreshold)', code)
code = re.sub(r'if\s*\(\s*prob\s*>=\s*0\.34\s*\)', 'if (prob >= XGBoostThreshold)', code)

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(code)

print('Nuevos parametros (Inputs) inyectados con exito y funciones adaptadas.')

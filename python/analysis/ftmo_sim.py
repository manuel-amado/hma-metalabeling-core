import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
from bs4 import BeautifulSoup
import pandas as pd
import numpy as np
from datetime import timedelta

# --- Leer reporte ---
found = r"C:\Users\Manuel\Documents\BACKTESTS\[Alpha_Sniper_Master][XAUUSD][M15 (2022.01.01 - 2026.08.29)]\ReportTester-5102370101.html"
with open(found, "r", encoding="utf-16", errors="replace") as fh:
    content = fh.read()
soup = BeautifulSoup(content, "html.parser")
trades = []
for row in soup.find_all("tr"):
    cols = row.find_all("td")
    if len(cols) >= 10:
        t = [c.get_text(strip=True) for c in cols]
        if "out" in t:
            try:
                trades.append((t[0], float(t[-3].replace(" ","")), float(t[-4].replace(" ",""))))
            except: pass

df = pd.DataFrame(trades, columns=["Date","Profit","Swap"])
df["PnL"] = df["Profit"] + df["Swap"]
df["Date"] = pd.to_datetime(df["Date"], format="%Y.%m.%d %H:%M:%S")
df = df.sort_values("Date").reset_index(drop=True)
df["Day"] = df["Date"].dt.date

# --- Aplicar limite diario 4% sobre balance inicial de la cuenta ---
BALANCE_INICIAL = 100_000.0
DAILY_LOSS_LIMIT_PCT = 4.0     # paramos si perdemos 4% en el dia
DAILY_HARD_STOP_PCT  = 5.0     # FTMO nunca debe superar 5%
MAX_TOTAL_DD_PCT     = 10.0    # FTMO limite total
FASE1_TARGET_PCT     = 10.0    # Fase 1: 10% profit
FASE2_TARGET_PCT     = 5.0     # Fase 2: 5% profit
WITHDRAWAL_SPLIT     = 0.80    # 80% para el trader

def simulate_ftmo(df_trades, balance_inicial, label=""):
    balance     = balance_inicial
    peak        = balance_inicial
    day_start_eq= balance_inicial
    prev_day    = None
    blocked_today = False
    
    log = []  # (date, pnl_applied, balance, dd_pct, daily_loss_pct, blocked)
    
    for _, row in df_trades.iterrows():
        day = row["Day"]
        
        # Reset diario
        if day != prev_day:
            day_start_eq  = balance
            blocked_today = False
            prev_day      = day
        
        # Calcular DD diario actual ANTES de este trade
        daily_loss_pct = (day_start_eq - balance) / balance_inicial * 100
        
        # Si ya perdimos >= 4% hoy, bloqueamos el resto del dia
        if daily_loss_pct >= DAILY_LOSS_LIMIT_PCT:
            blocked_today = True
        
        if blocked_today:
            log.append((row["Date"], 0.0, balance, (peak-balance)/balance_inicial*100, daily_loss_pct, True))
            continue
        
        # Aplicar trade
        balance += row["PnL"]
        if balance > peak:
            peak = balance
        
        dd_total_pct  = (peak - balance) / balance_inicial * 100
        daily_loss_now = (day_start_eq - balance) / balance_inicial * 100
        
        log.append((row["Date"], row["PnL"], balance, dd_total_pct, max(daily_loss_now,0), False))
    
    return pd.DataFrame(log, columns=["Date","PnL","Balance","DD_total_pct","Daily_loss_pct","Blocked"])

df_sim = simulate_ftmo(df, BALANCE_INICIAL)
df_sim["Day"] = df_sim["Date"].dt.date

# --- Estadisticas del filtro 4% ---
total_original = df["PnL"].sum()
total_filtered = df_sim["PnL"].sum()
blocked_trades = df_sim["Blocked"].sum()
print("=== IMPACTO DEL LIMITE DIARIO 4% ===")
print(f"Trades originales: {len(df)} | Trades bloqueados: {blocked_trades} ({blocked_trades/len(df)*100:.1f}%)")
print(f"Profit original: ${total_original:,.0f} | Profit filtrado: ${total_filtered:,.0f}")
print(f"MaxDD original: {df['PnL'].cumsum().cummax().sub(df['PnL'].cumsum()).div(BALANCE_INICIAL).mul(100).max():.1f}%")
print(f"MaxDD filtrado: {df_sim['DD_total_pct'].max():.1f}%")
print()

# --- Simulacion de cuentas FTMO consecutivas ---
print("=== SIMULACION FTMO CONSECUTIVA (2022-2026) ===")
print("Reglas: Fase1=10%, Fase2=5%, MaxDD=10%, DailyDD=4%, Retiro 80%")
print()

# Construir equity diaria con filtro
daily_eq = df_sim.groupby("Day")["PnL"].sum().reset_index()
daily_eq.columns = ["Day","Daily_PnL"]
daily_eq["Day"] = pd.to_datetime(daily_eq["Day"])
daily_eq = daily_eq.sort_values("Day").reset_index(drop=True)

# Calcular DD diario maximo por dia (usando el log detallado)
daily_max_dd = df_sim.groupby("Day")["Daily_loss_pct"].max().reset_index()
daily_max_dd.columns = ["Day","Max_Daily_Loss_pct"]
daily_max_dd["Day"] = pd.to_datetime(daily_max_dd["Day"])

cuentas = []
total_retirado = 0.0
total_gastado_en_fees = 0.0  # FTMO Challenge fee ~$540 por cuenta 100k
FTMO_FEE = 540.0

# Estado
state      = "FASE1"     # FASE1, FASE2, FUNDED
bal        = BALANCE_INICIAL
peak_acc   = BALANCE_INICIAL
fase_start = daily_eq["Day"].iloc[0]
fase_start_bal = bal
cuenta_num = 0
retiros_mes= {}
monthly_peak = bal

cuenta_log = []  # Para el resumen

i = 0
while i < len(daily_eq):
    row   = daily_eq.iloc[i]
    day   = row["Day"]
    pnl   = row["Daily_PnL"]
    
    # DD diario maximo
    max_dl = daily_max_dd[daily_max_dd["Day"]==day]["Max_Daily_Loss_pct"].values
    max_daily_loss = max_dl[0] if len(max_dl)>0 else 0.0
    
    bal   += pnl
    if bal > peak_acc: peak_acc = bal
    
    dd_total_pct  = (peak_acc - bal) / BALANCE_INICIAL * 100
    profit_pct    = (bal - fase_start_bal) / BALANCE_INICIAL * 100
    
    busted_daily  = max_daily_loss >= DAILY_HARD_STOP_PCT
    busted_total  = dd_total_pct >= MAX_TOTAL_DD_PCT
    busted        = busted_daily or busted_total
    
    # Retiro mensual en FUNDED
    month_key = (day.year, day.month)
    if state == "FUNDED":
        if month_key not in retiros_mes:
            # Fin de mes anterior: retirar beneficio acumulado
            # Calcular ganancia desde inicio de este mes
            if len(retiros_mes) > 0:
                mes_profit = bal - monthly_peak
                if mes_profit > 0:
                    retiro = mes_profit * WITHDRAWAL_SPLIT
                    total_retirado += retiro
                    bal -= retiro  # El broker se queda el 20%
                    retiros_mes[month_key] = retiro
                    cuenta_log.append(f"  [RETIRO {day.strftime('%Y-%m')}] ${retiro:,.0f} (80% de ${mes_profit:,.0f})")
            retiros_mes[month_key] = 0
            monthly_peak = bal
    
    if busted:
        motivo = "DD_DIARIO>=5%" if busted_daily else "DD_TOTAL>=10%"
        cuenta_num += 1
        total_gastado_en_fees += FTMO_FEE
        cuentas.append({
            "Cuenta": cuenta_num,
            "Fase": state,
            "Inicio": fase_start.strftime("%Y-%m-%d"),
            "Fin": day.strftime("%Y-%m-%d"),
            "Dias": (day - fase_start).days,
            "Resultado": f"PERDIDA ({motivo})",
            "Profit_pct": round(profit_pct,1),
            "MaxDD_pct": round(dd_total_pct,1),
            "Retirado": 0
        })
        for msg in cuenta_log: print(msg)
        cuenta_log = []
        print(f"  Cuenta #{cuenta_num} [{state}] PERDIDA por {motivo} el {day.strftime('%Y-%m-%d')} | Profit: {profit_pct:.1f}% | DD: {dd_total_pct:.1f}%")
        
        # Reiniciar
        state        = "FASE1"
        bal          = BALANCE_INICIAL
        peak_acc     = BALANCE_INICIAL
        fase_start   = day + timedelta(days=1)
        fase_start_bal = bal
        retiros_mes  = {}
        monthly_peak = bal
        i += 1
        continue
    
    # Avance de fases
    if state == "FASE1" and profit_pct >= FASE1_TARGET_PCT:
        cuenta_num += 1
        total_gastado_en_fees += FTMO_FEE
        cuentas.append({
            "Cuenta": cuenta_num, "Fase": "FASE1",
            "Inicio": fase_start.strftime("%Y-%m-%d"),
            "Fin": day.strftime("%Y-%m-%d"),
            "Dias": (day - fase_start).days,
            "Resultado": "PASADA",
            "Profit_pct": round(profit_pct,1),
            "MaxDD_pct": round(dd_total_pct,1),
            "Retirado": 0
        })
        print(f"  Cuenta #{cuenta_num} [FASE1] PASADA el {day.strftime('%Y-%m-%d')} | Profit: {profit_pct:.1f}% en {(day-fase_start).days} dias")
        state        = "FASE2"
        fase_start   = day + timedelta(days=1)
        fase_start_bal = bal
        i += 1
        continue
    
    if state == "FASE2" and profit_pct >= FASE2_TARGET_PCT:
        cuentas.append({
            "Cuenta": cuenta_num, "Fase": "FASE2",
            "Inicio": fase_start.strftime("%Y-%m-%d"),
            "Fin": day.strftime("%Y-%m-%d"),
            "Dias": (day - fase_start).days,
            "Resultado": "PASADA",
            "Profit_pct": round(profit_pct,1),
            "MaxDD_pct": round(dd_total_pct,1),
            "Retirado": 0
        })
        print(f"  Cuenta #{cuenta_num} [FASE2] PASADA el {day.strftime('%Y-%m-%d')} | Profit: {profit_pct:.1f}% en {(day-fase_start).days} dias")
        state        = "FUNDED"
        fase_start   = day + timedelta(days=1)
        fase_start_bal = bal
        retiros_mes  = {}
        monthly_peak = bal
        i += 1
        continue
    
    i += 1

# Retiro final si quedamos en FUNDED
if state == "FUNDED":
    profit_final = bal - fase_start_bal
    if profit_final > 0:
        retiro_final = profit_final * WITHDRAWAL_SPLIT
        total_retirado += retiro_final
        print(f"  [RETIRO FINAL] ${retiro_final:,.0f}")

print()
print("="*65)
print("RESUMEN FINAL")
print("="*65)
df_c = pd.DataFrame(cuentas)
if len(df_c) > 0:
    fase1_pass  = len(df_c[(df_c["Fase"]=="FASE1") & (df_c["Resultado"]=="PASADA")])
    fase1_fail  = len(df_c[(df_c["Fase"]=="FASE1") & (df_c["Resultado"].str.contains("PERDIDA"))])
    fase2_fail  = len(df_c[(df_c["Fase"]=="FASE2") & (df_c["Resultado"].str.contains("PERDIDA"))])
    funded_fail = len(df_c[(df_c["Fase"]=="FUNDED") & (df_c["Resultado"].str.contains("PERDIDA"))])
    print(f"Fase 1 pasadas:     {fase1_pass}")
    print(f"Fase 1 fallidas:    {fase1_fail}")
    print(f"Fase 2 fallidas:    {fase2_fail}")
    print(f"Funded perdidas:    {funded_fail}")
print(f"Total fees pagados: ${total_gastado_en_fees:,.0f} ({int(total_gastado_en_fees/FTMO_FEE)} challenges)")
print(f"Total retirado:     ${total_retirado:,.0f}")
print(f"Balance neto:       ${total_retirado - total_gastado_en_fees:,.0f}")
print(f"Estado actual:      {state} | Balance: ${bal:,.0f}")
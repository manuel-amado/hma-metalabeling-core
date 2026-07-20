import os
import sys
import io
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
else:
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from pipeline_global_optimizer import (
    cargar_entry_dataset, cargar_exit_dataset,
    entrenar_entry_model, entrenar_exit_model,
    entrenar_regime_model,
    fusionar_datasets, SYMBOL, OUTPUT_DIR
)

ENTRY_THRESH = 0.36
EXIT_THRESH = 0.80
INITIAL_BALANCE = 10000.0
RISK_PER_TRADE = 0.0025  # 0.25% Riesgo Institucional Compuesto

def run():
    print("Ejecutando Pipeline para obtener OOF probabilities...")
    df_entry_raw, df_entry_clean = cargar_entry_dataset()
    df_exit_raw, df_exit_clean   = cargar_exit_dataset()

    df_entry_clean, toxic_id = entrenar_regime_model(df_entry_clean)
    _, df_entry_proba, _ = entrenar_entry_model(df_entry_clean, toxic_id)
    _, df_exit_proba, _ = entrenar_exit_model(df_exit_clean)

    df_merged, exit_map = fusionar_datasets(df_entry_raw, df_entry_proba, df_exit_proba)

    print(f"\nCalculando RR Efectivos para {ENTRY_THRESH} / {EXIT_THRESH}...")
    df_sel = df_merged[
        df_merged["entry_proba"].notna() &
        (df_merged["entry_proba"] >= ENTRY_THRESH)
    ].copy()

    def get_rr(row):
        ticket = row["Ticket"]
        base_rr = float(row["Realized_RR"])
        # 1. Resolver el Exit Model Trigger
        exit_model_rr = base_rr
        if ticket in exit_map:
            em = exit_map[ticket]
            mask = em["exit_proba"] >= EXIT_THRESH
            if mask.any():
                first_idx = np.argmax(mask)
                exit_model_rr = float(em["float_rr"][first_idx])
        
        # 2. Determinar si hubo Scale-Out (1.5R)
        hit_scale_out = False
        if exit_model_rr >= 1.5 or base_rr >= 1.5:
            hit_scale_out = True
        elif ticket in exit_map:
            if (em["float_rr"] >= 1.5).any():
                hit_scale_out = True
                
        # 3. Calcular RR Final aplicando física (Scale-Out 50% + Breakeven)
        if hit_scale_out:
            rr_mitad_1 = 1.5 
            rr_mitad_2 = exit_model_rr
            if rr_mitad_2 < 0:
                rr_mitad_2 = 0.0 # Stop Loss a Breakeven
            return (rr_mitad_1 * 0.5) + (rr_mitad_2 * 0.5)
        else:
            return exit_model_rr

    df_sel["effective_rr"] = df_sel.apply(get_rr, axis=1)
    
    # === FASE 10.9: CONCURRENCY LOCK SÍNCRONO ===
    print("Aplicando Bloqueo de Concurrencia (Max 1 Trade Simultáneo)...")
    
    # Asegurarnos de que el tiempo es datetime y ordenar cronológicamente
    df_sel["Time_dt"] = pd.to_datetime(df_sel["Time"], format="%Y.%m.%d %H:%M:%S")
    df_sel = df_sel.sort_values("Time_dt")
    
    # Asumimos timeframe H1 para el espacio temporal de las velas
    # (Si cambia el TF a M15 o H4, habría que parametrizarlo)
    TIMEFRAME_DELTA = pd.Timedelta(hours=1) 
    
    blocked_until_time = None
    purged_rrs = []
    purged_times = []
    
    for idx, row in df_sel.iterrows():
        current_time = row["Time_dt"]
        
        # Filtro restrictivo con if/else puros (sin escapes)
        is_trade_allowed = False
        
        if pd.isna(blocked_until_time):
            is_trade_allowed = True
        else:
            if current_time > blocked_until_time:
                is_trade_allowed = True
            else:
                is_trade_allowed = False
                
        if is_trade_allowed:
            purged_rrs.append(row["effective_rr"])
            purged_times.append(current_time)
            # Calcular tiempo de liberación
            bars_in_trade = row["Bars_In_Trade"]
            # En caso extremo de que el dataset no tenga Bars_In_Trade válido, asumimos 1 vela de vida útil
            if pd.isna(bars_in_trade) or bars_in_trade <= 0:
                bars_in_trade = 1
            blocked_until_time = current_time + (bars_in_trade * TIMEFRAME_DELTA)
    
    rr_array = np.array(purged_rrs)
    trades_totales = len(df_sel)
    trades_reales = len(rr_array)
    trades_fantasma = trades_totales - trades_reales
    print(f"Purga completa: {trades_totales} señales iniciales -> {trades_reales} trades reales ejecutados ({trades_fantasma} fantasmas purgados).")
    
    if len(rr_array) == 0:
        print("Cero trades aprobados tras la purga.")
        return

    # Cálculo de Equidad
    balance = INITIAL_BALANCE
    equity_curve = [balance]
    for rr in rr_array:
        risk_amount = balance * RISK_PER_TRADE
        trade_profit = risk_amount * rr
        balance += trade_profit
        equity_curve.append(balance)
        
    equity_curve = np.array(equity_curve)
    final_balance = equity_curve[-1]
    net_profit = final_balance - INITIAL_BALANCE
    roi = (net_profit / INITIAL_BALANCE) * 100

    print("Ejecutando Simulacion Monte Carlo (1,000 caminos) con Interes Compuesto...")
    N_MC = 1000
    mc_drawdowns_pct = []
    mc_drawdowns_usd = []
    
    mc_paths = []
    
    for _ in range(N_MC):
        mc_rr_path = np.random.choice(rr_array, size=len(rr_array), replace=True)
        mc_bal = INITIAL_BALANCE
        mc_eq_curve = [mc_bal]
        for rr in mc_rr_path:
            mc_bal += (mc_bal * RISK_PER_TRADE) * rr
            mc_eq_curve.append(mc_bal)
            
        mc_eq_curve = np.array(mc_eq_curve)
        mc_paths.append(mc_eq_curve)
        
        peaks = np.maximum.accumulate(mc_eq_curve)
        drawdowns_usd = peaks - mc_eq_curve
        drawdowns_pct = drawdowns_usd / peaks
        
        mc_drawdowns_pct.append(np.max(drawdowns_pct))
        mc_drawdowns_usd.append(np.max(drawdowns_usd))
        
    mc_dd_95_pct = np.percentile(mc_drawdowns_pct, 95)
    mc_dd_95_usd = np.percentile(mc_drawdowns_usd, 95)

    plt.style.use('dark_background')
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(18, 7))
    
    ax1.plot(equity_curve, color='#00ffcc', linewidth=2.5, label='Historical Equity ($)')
    ax1.fill_between(range(len(equity_curve)), equity_curve, INITIAL_BALANCE, where=(equity_curve > INITIAL_BALANCE), alpha=0.1, color='#00ffcc')
    ax1.fill_between(range(len(equity_curve)), equity_curve, INITIAL_BALANCE, where=(equity_curve <= INITIAL_BALANCE), alpha=0.1, color='#ff3366')
    ax1.axhline(INITIAL_BALANCE, color='white', linestyle='--', alpha=0.5)
    ax1.set_title(f'Real Historical Equity | {RISK_PER_TRADE*100}% Risk | {SYMBOL}', fontsize=14, pad=15)
    ax1.set_xlabel('Trade Number (Purged)', fontsize=12)
    ax1.set_ylabel('Account Balance ($)', fontsize=12)
    ax1.grid(True, alpha=0.2)
    ax1.legend()

    for path in mc_paths:
        ax2.plot(path, color='gray', alpha=0.03)
    ax2.plot(equity_curve, color='#00ffcc', linewidth=2, label='Actual Historical Path')
    ax2.axhline(INITIAL_BALANCE, color='white', linestyle='--', alpha=0.5)
    ax2.set_title(f'Monte Carlo Simulation (1,000 Paths)', fontsize=14, pad=15)
    ax2.set_xlabel('Trade Number (Purged)', fontsize=12)
    ax2.set_ylabel('Account Balance ($)', fontsize=12)
    ax2.grid(True, alpha=0.2)
    
    textstr = '\n'.join((
        f'Initial: ${INITIAL_BALANCE:,.2f}',
        f'Final: ${final_balance:,.2f}',
        f'ROI: {roi:.2f}%',
        f'MC 95% Max DD: ${mc_dd_95_usd:,.2f} ({mc_dd_95_pct*100:.2f}%)',
        f'Trades Fantasma: {trades_fantasma}'
    ))
    props = dict(boxstyle='round', facecolor='black', alpha=0.5)
    ax2.text(0.05, 0.95, textstr, transform=ax2.transAxes, fontsize=12,
            verticalalignment='top', bbox=props, color='white')

    ax2.legend()

    plt.tight_layout()
    chart_path = os.path.join(OUTPUT_DIR, f"equity_curve_{SYMBOL.lower()}_purged.png")
    plt.savefig(chart_path, dpi=150)
    plt.close()

    print("\n=================================================================")
    print(f"  VALIDACION INSTITUCIONAL (CONCURRENCY PURGED) | {SYMBOL}")
    print("=================================================================")
    print(f"  Riesgo          : {RISK_PER_TRADE*100}% Compuesto")
    print(f"  Señales Totales : {trades_totales}")
    print(f"  Trades Reales   : {trades_reales}")
    print(f"  Balance Inicial : ${INITIAL_BALANCE:,.2f}")
    print(f"  Balance Final   : ${final_balance:,.2f}")
    print(f"  Net Profit      : ${net_profit:,.2f} ({roi:.2f}%)")
    print("-----------------------------------------------------------------")
    print(f"  MC 95% Max DD   : ${mc_dd_95_usd:,.2f} ({mc_dd_95_pct*100:.2f}%)")
    print("=================================================================")
    print(f"  Grafico guardado en: {chart_path}")

if __name__ == "__main__":
    run()

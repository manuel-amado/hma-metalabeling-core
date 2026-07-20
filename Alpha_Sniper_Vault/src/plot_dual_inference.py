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
    fusionar_datasets, SYMBOL, OUTPUT_DIR
)

ENTRY_THRESH = 0.55
EXIT_THRESH = 0.75

def run():
    print("Ejecutando Pipeline para obtener OOF probabilities...")
    df_entry_raw, df_entry_clean = cargar_entry_dataset()
    df_exit_raw, df_exit_clean   = cargar_exit_dataset()

    _, df_entry_proba, _ = entrenar_entry_model(df_entry_clean)
    _, df_exit_proba, _ = entrenar_exit_model(df_exit_clean)

    df_merged, exit_map = fusionar_datasets(df_entry_raw, df_entry_proba, df_exit_proba)

    print(f"\nGenerando Equidad para {ENTRY_THRESH} / {EXIT_THRESH}...")
    
    # Filter entries
    df_sel = df_merged[
        df_merged["entry_proba"].notna() &
        (df_merged["entry_proba"] >= ENTRY_THRESH)
    ].copy()

    def get_rr(row):
        ticket = row["Ticket"]
        base_rr = row["Realized_RR"]
        if ticket not in exit_map: return base_rr
        em = exit_map[ticket]
        mask = em["exit_proba"] >= EXIT_THRESH
        if not mask.any(): return base_rr
        first_idx = np.argmax(mask)
        return float(em["float_rr"][first_idx])

    df_sel["effective_rr"] = df_sel.apply(get_rr, axis=1)

    rr = df_sel["effective_rr"].values
    if len(rr) == 0:
        print("Cero trades aprobados.")
        return

    cum_rr = np.cumsum(rr)
    total_r = np.sum(rr)
    winners = np.sum(rr > 0)
    losers = np.sum(rr <= 0)
    win_rate = winners / len(rr)
    pf = np.sum(rr[rr>0]) / abs(np.sum(rr[rr<=0])) if np.sum(rr<=0) != 0 else float('inf')

    # Monte Carlo (10,000 caminos para alta resolucion)
    print("Ejecutando Simulacion Monte Carlo (10,000 caminos)...")
    N_MC = 10000
    mc_drawdowns = []
    for _ in range(N_MC):
        mc_path = np.random.choice(rr, size=len(rr), replace=True)
        mc_cum = np.cumsum(mc_path)
        peaks = np.maximum.accumulate(mc_cum)
        drawdowns = peaks - mc_cum
        mc_drawdowns.append(np.max(drawdowns))
    
    mc_dd_95 = np.percentile(mc_drawdowns, 95)
    mc_dd_max = np.max(mc_drawdowns)

    # Plot
    plt.style.use('dark_background')
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))
    
    # Curva de Equidad
    ax1.plot(cum_rr, color='#00ffcc', linewidth=2, label='Equity (R)')
    ax1.fill_between(range(len(cum_rr)), cum_rr, alpha=0.1, color='#00ffcc')
    ax1.set_title(f'Dual-Inference Equity Curve | {SYMBOL}', fontsize=14, pad=15)
    ax1.set_xlabel('Trade Number')
    ax1.set_ylabel('Cumulative Return (R)')
    ax1.grid(True, alpha=0.2)
    ax1.legend()

    # Histograma Drawdowns MC
    ax2.hist(mc_drawdowns, bins=50, color='#ff3366', alpha=0.7)
    ax2.axvline(mc_dd_95, color='white', linestyle='dashed', linewidth=2, label=f'95th Pct: {mc_dd_95:.2f}R')
    ax2.set_title('Monte Carlo Max Drawdown Distribution', fontsize=14, pad=15)
    ax2.set_xlabel('Max Drawdown (R)')
    ax2.set_ylabel('Frequency')
    ax2.grid(True, alpha=0.2)
    ax2.legend()

    plt.tight_layout()
    chart_path = os.path.join(OUTPUT_DIR, f"dual_inference_validation_{SYMBOL}.png")
    plt.savefig(chart_path, dpi=150)
    plt.close()

    print("\n=================================================================")
    print(f"  VALIDACION INSTITUCIONAL DUAL-INFERENCE | {SYMBOL}")
    print("=================================================================")
    print(f"  Entry Threshold : {ENTRY_THRESH}")
    print(f"  Exit Threshold  : {EXIT_THRESH}")
    print(f"  Total Trades    : {len(rr)}")
    print(f"  Win Rate        : {win_rate:.2%}")
    print(f"  Profit Factor   : {pf:.2f}")
    print(f"  Retorno Total   : +{total_r:.2f} R")
    print(f"  Avg RR/Trade    : +{total_r/len(rr):.4f} R")
    print("-----------------------------------------------------------------")
    print(f"  MC 95% Max DD   : {mc_dd_95:.2f} R")
    print(f"  MC Absolute Max : {mc_dd_max:.2f} R")
    print(f"  Rentabilidad / Riesgo (Return / 95% DD): {(total_r / mc_dd_95) if mc_dd_95 > 0 else 0:.2f}")
    print("=================================================================")
    print(f"  Grafico guardado en: {chart_path}")

if __name__ == "__main__":
    run()

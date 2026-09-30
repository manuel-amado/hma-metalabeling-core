import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import pipeline_global_optimizer as pgo
import warnings

warnings.filterwarnings("ignore")

print("Iniciando Monte Carlo...")

# Cargar
df_entry_raw, df_entry_clean = pgo.cargar_entry_dataset()
df_exit_raw, df_exit_clean   = pgo.cargar_exit_dataset()

# OOF predict
df_entry_clean, toxic_id = pgo.entrenar_regime_model(df_entry_clean)
entry_model, df_entry_proba, entry_feats = pgo.entrenar_entry_model(df_entry_clean, toxic_id)
exit_model, df_exit_proba, exit_feats = pgo.entrenar_exit_model(df_exit_clean)

# Merge
df_merged, exit_map = pgo.fusionar_datasets(df_entry_raw, df_entry_proba, df_exit_proba)

# Filter by threshold
entry_thresh = 0.36
exit_thresh = 0.80

df_selected = df_merged[
    df_merged["entry_proba"].notna() &
    (df_merged["entry_proba"] >= entry_thresh)
].copy()

def get_effective_rr(row):
    ticket = row["Ticket"]
    base_rr = row["Realized_RR"]
    if ticket not in exit_map:
        return base_rr
    em = exit_map[ticket]
    mask = em["exit_proba"] >= exit_thresh
    if not mask.any():
        return base_rr
    first_idx = np.argmax(mask)
    return float(em["float_rr"][first_idx])

df_selected["effective_rr"] = df_selected.apply(get_effective_rr, axis=1)

rr_series = df_selected["effective_rr"].values.astype(float)
equity_pct = rr_series * 0.01  # 1% risk per trade

original_equity = np.cumprod(1 + equity_pct)

# Montecarlo
n_simulations = 500
n_trades = len(rr_series)

plt.figure(figsize=(12, 6))

for _ in range(n_simulations):
    # Resample with replacement
    mc_series = np.random.choice(equity_pct, size=n_trades, replace=True)
    mc_equity = np.cumprod(1 + mc_series)
    plt.plot(mc_equity, color='gray', alpha=0.05)

plt.plot(original_equity, color='blue', linewidth=2, label='Curva Original (Orden Cronológico)')
plt.title(f'Simulación Montecarlo (500 runs) - {pgo.SYMBOL}\nEntry: {entry_thresh} | Exit: {exit_thresh} | Riesgo Fijo: 1%')
plt.xlabel('Número de Trades')
plt.ylabel('Crecimiento del Capital (Múltiplo)')
plt.legend()
plt.grid(alpha=0.3)

out_path = f'output/montecarlo_simulation_{pgo.SYMBOL}.png'
plt.savefig(out_path, dpi=150, bbox_inches='tight')
print(f"\\nPlot saved to {out_path}")

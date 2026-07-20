import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

log_file = 'models/portfolio_trades_log.csv'
if not os.path.exists(log_file):
    print('No trades log found.')
    exit()

df = pd.read_csv(log_file)
trades = df['Profit_USD'].values.copy()
initial_balance = 100000.0
n_simulations = 100

plt.style.use('dark_background')
fig, ax = plt.subplots(figsize=(12, 6))

for i in range(n_simulations):
    shuffled_trades = np.random.permutation(trades)
    simulated_equity = initial_balance + np.cumsum(shuffled_trades)
    ax.plot(simulated_equity, color='white', alpha=0.1, linewidth=0.8)

# Original sequence
original_equity = initial_balance + np.cumsum(trades)
ax.plot(original_equity, color='#00ff88', alpha=1.0, linewidth=2, label='Original Trade Sequence')

ax.set_title('Portfolio Monte Carlo Analysis (100 Scenarios)', color='#00ff88', fontsize=14, pad=15)
ax.set_xlabel('Number of Trades')
ax.set_ylabel('Account Balance ($)')
ax.legend(loc='upper left')
ax.grid(True, linestyle='--', alpha=0.2)

out_path = 'models/portfolio_montecarlo.png'
plt.tight_layout()
plt.savefig(out_path, dpi=300, bbox_inches='tight')
print('Saved', out_path)

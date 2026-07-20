import pandas as pd
import matplotlib.pyplot as plt
import os

df = pd.read_csv("C:/Users/Manuel/Desktop/HMA_MetaLabeling/Alpha_Sniper_Vault/models/portfolio_trades_log.csv")
df['Time'] = pd.to_datetime(df['Time'])

# Filter 2015 to 2023
df_filtered = df[(df['Time'] >= '2015-01-01') & (df['Time'] <= '2023-12-31')].copy()

# Recalculate balance starting from 100000
balance = 100000.0
balances = []
for profit in df_filtered['Profit_USD']:
    balance += profit
    balances.append(balance)
    
df_filtered['Balance'] = balances

plt.figure(figsize=(12, 6))
plt.plot(df_filtered['Time'], df_filtered['Balance'], color='cyan', linewidth=2)
plt.title("Expected Portfolio Equity Curve (2015-2023) - In Sample", fontsize=16, color='white')
plt.xlabel("Date", fontsize=12, color='white')
plt.ylabel("Balance (USD)", fontsize=12, color='white')
plt.grid(True, linestyle='--', alpha=0.3)
plt.gca().set_facecolor('#1e1e1e')
plt.gcf().patch.set_facecolor('#1e1e1e')
plt.tick_params(colors='white')
plt.tight_layout()

out_path = "C:/Users/Manuel/.gemini/antigravity/brain/cb6503f8-f051-41b7-ac20-8fa79020986e/expected_equity_2015_2023.png"
plt.savefig(out_path, dpi=300, facecolor='#1e1e1e')
print(f"Chart saved to {out_path}")

total_return = (balances[-1] - 100000) / 100000 * 100
running_max = df_filtered['Balance'].cummax()
drawdown = (df_filtered['Balance'] - running_max) / running_max * 100
max_dd = abs(drawdown.min())

print(f"Return: {total_return:.2f}%")
print(f"Max DD: {max_dd:.2f}%")

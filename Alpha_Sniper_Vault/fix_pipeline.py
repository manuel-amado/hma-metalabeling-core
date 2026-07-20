import os
file_path = r"C:\Users\Manuel\Desktop\HMA_MetaLabeling\Alpha_Sniper_Vault\src\pipeline_global_optimizer.py"
with open(file_path, "r") as f:
    lines = f.readlines()

new_lines = lines[:1051]

new_lines.extend([
    "        # FINAL: Guardar la simulacion de todos los activos combinados\n",
    "        if len(all_portfolio_trades) > 0:\n",
    "            df_port = pd.concat(all_portfolio_trades, ignore_index=True)\n",
    "            df_port.to_csv(os.path.join(DATA_DIR, 'portfolio_trades_log.csv'), index=False)\n",
    "            print(f'\\n[PORTFOLIO] {len(df_port)} trades exportados a portfolio_trades_log.csv')\n",
    "\n",
    "    print('\\n' + '='*70)\n",
    "    print('  Pipeline global completado')\n",
    "    print('='*70)\n",
    "\n",
    "if __name__ == '__main__':\n",
    "    main()\n"
])

with open(file_path, "w") as f:
    f.writelines(new_lines)

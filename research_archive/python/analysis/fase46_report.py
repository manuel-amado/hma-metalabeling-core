import os
import sys
import pandas as pd
import numpy as np
import joblib
from glob import glob

BASE_DIR = r'C:\Users\Manuel\Desktop\HMA_MetaLabeling\Alpha_Sniper_Vault'
DATA_DIR = os.path.join(BASE_DIR, 'data')
MODELS_DIR = os.path.join(BASE_DIR, 'models')

sys.path.append(os.path.join(BASE_DIR, 'src'))
from pipeline_global_optimizer import ENTRY_FEATURES, EXIT_FEATURES

config = {
    'USDJPY': {'entry': 0.10, 'exit': 0.55},
    'EURJPY': {'entry': 0.48, 'exit': 0.55}
}

results = []

for symbol, thresh in config.items():
    print(f"Processing {symbol}...")
    
    # Get latest entry/exit models and scalers (June 16 T4 ones)
    entry_models = sorted(glob(os.path.join(MODELS_DIR, f'modelo_universal_{symbol}_entry_*.pkl')))
    exit_models = sorted(glob(os.path.join(MODELS_DIR, f'modelo_universal_{symbol}_exit_*.pkl')))
    
    if not entry_models or not exit_models:
        print(f"Models missing for {symbol}")
        continue
        
    m_entry = joblib.load(entry_models[-1])
    m_exit = joblib.load(exit_models[-1])
    
    entry_scaler_path = os.path.join(MODELS_DIR, f'scaler_universal_{symbol}_entry.pkl')
    exit_scaler_path = os.path.join(MODELS_DIR, f'scaler_universal_{symbol}_exit.pkl')
    
    entry_scaler = joblib.load(entry_scaler_path) if os.path.exists(entry_scaler_path) else None
    exit_scaler = joblib.load(exit_scaler_path) if os.path.exists(exit_scaler_path) else None
    
    df_in = pd.read_csv(os.path.join(DATA_DIR, f'Struct_Dataset_{symbol}_T4.csv'))
    df_in['Time'] = pd.to_datetime(df_in['Time'])
    
    df_ex_path = os.path.join(DATA_DIR, f'Struct_Exit_Dataset_{symbol}_T4.csv')
    df_ex = pd.read_csv(df_ex_path) if os.path.exists(df_ex_path) else pd.DataFrame()
    
    # Predict Entry
    av_ent = [c for c in ENTRY_FEATURES if c in df_in.columns]
    X_ent = df_in[av_ent].fillna(0).values
    if entry_scaler:
        X_ent = entry_scaler.transform(X_ent)
    df_in['entry_proba'] = m_entry.predict_proba(X_ent)[:, 1]
    
    # Predict Exit
    if not df_ex.empty:
        av_ex = [c for c in EXIT_FEATURES if c in df_ex.columns]
        X_ex = df_ex[av_ex].fillna(0).values
        if exit_scaler:
            X_ex = exit_scaler.transform(X_ex)
        
        feature_names = m_exit.get_booster().feature_names
        if feature_names:
            indices = [av_ex.index(f) for f in feature_names]
            X_ex_model = X_ex[:, indices]
        else:
            X_ex_model = X_ex
            
        df_ex['exit_proba'] = m_exit.predict_proba(X_ex_model)[:, 1]
    
    df_sel = df_in[df_in['entry_proba'] >= thresh['entry']].copy()
    if df_sel.empty:
        print(f"No trades triggered for {symbol}")
        continue
    
    exit_map = {}
    if not df_ex.empty:
        df_ex = df_ex.sort_values(['Ticket', 'Bars_In_Trade'])
        for t, g in df_ex.groupby('Ticket'):
            rr_col = 'Floating_RR' if 'Floating_RR' in g.columns else 'Open_Profit_R'
            exit_map[t] = {
                'float_rr': g[rr_col].values if rr_col in g.columns else np.zeros(len(g)),
                'exit_proba': g['exit_proba'].values
            }
    
    def get_trade_return(row):
        t = row['Ticket']
        base_rr = float(row.get('Realized_RR', 0.0))
        if pd.isna(base_rr): base_rr = 0.0
        
        exit_rr = base_rr
        if t in exit_map:
            em = exit_map[t]
            mask = em['exit_proba'] >= thresh['exit']
            if mask.any():
                exit_rr = float(em['float_rr'][np.argmax(mask)])
                
        # Pure ML exit. No 1.5R Scale-Out, no Breakeven.
        return exit_rr
            
    df_sel['trade_return_pct'] = df_sel.apply(get_trade_return, axis=1)
    
    df_sel['Year'] = df_sel['Time'].dt.year
    for year, g in df_sel.groupby('Year'):
        total_r = g['trade_return_pct'].sum()
        compounded = (np.prod(1 + (g['trade_return_pct'] / 100.0)) - 1.0) * 100.0
        win_rate = (g['trade_return_pct'] > 0).mean() * 100
        
        results.append({
            'Asset': symbol,
            'Year': year,
            'Trades': len(g),
            'Total_R': round(total_r, 2),
            'Compounded_%': round(compounded, 2),
            'WinRate_%': round(win_rate, 2)
        })

df_res = pd.DataFrame(results)

output_md = "# 📊 Reporte de Rentabilidad del Portfolio (Fase 47: AI-Driven Exits)\n\n"
output_md += "**Condiciones de Simulación:**\n"
output_md += "- Riesgo por Operación: 1%\n"
output_md += "- Gestión de Salida: 100% controlada por la Inteligencia Artificial (Exit Model).\n"
output_md += "- Scale-Out: DESACTIVADO. Posición al 100% hasta la señal de salida.\n"
output_md += "- Break-Even: DESACTIVADO. Se permite el desarrollo íntegro del trade (Fat Tails).\n"
output_md += "- Umbrales de Entrada: USDJPY (0.10), EURJPY (0.48)\n"
output_md += "- Umbral de Salida ML: 0.55\n"
output_md += "- Modelos y Datasets: Tanda 4 OOS (`modelo_universal_*.pkl`)\n\n"

output_md += "## 📈 Desglose por Activo y Año\n\n"
output_md += df_res.to_markdown(index=False)
output_md += "\n\n"

output_md += "## 🌐 Rentabilidad Agregada del Portfolio (Anual)\n\n"
agg_res = []
df_res['Year'] = df_res['Year'].astype(int)
for year in sorted(df_res['Year'].unique()):
    y_df = df_res[df_res['Year'] == year]
    trades = y_df['Trades'].sum()
    total_r = y_df['Total_R'].sum()
    comp = (np.prod(1 + (y_df['Compounded_%'] / 100.0)) - 1.0) * 100.0
    agg_res.append({'Year': year, 'Total_Trades': trades, 'Total_R': round(total_r, 2), 'Compounded_%': round(comp, 2)})

df_agg = pd.DataFrame(agg_res)
output_md += df_agg.to_markdown(index=False)

# Add Total Portfolio Accumulation
total_trades = df_agg['Total_Trades'].sum()
total_r_all = df_agg['Total_R'].sum()
total_comp = (np.prod(1 + (df_res['Compounded_%'] / 100.0)) - 1.0) * 100.0

output_md += f"\n\n**Total Trades (2015-2023):** {total_trades}\n"
output_md += f"**Total R Ganadas:** +{total_r_all:.2f}R\n"
output_md += f"**Rentabilidad Total Compuesta (Global):** +{total_comp:.2f}%\n"

with open(r'C:\Users\Manuel\Desktop\HMA_MetaLabeling\Alpha_Sniper_Vault\src\report_output.md', 'w', encoding='utf-8') as f:
    f.write(output_md)

print("Report saved to report_output.md")

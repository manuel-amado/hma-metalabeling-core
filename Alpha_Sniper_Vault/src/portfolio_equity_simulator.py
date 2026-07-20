import os
import glob
import json
import joblib
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import seaborn as sns
from datetime import timedelta

# =============================================================================
# CONFIGURACIÓN INSTITUCIONAL DE PROP FIRM Y PIPELINE
# =============================================================================
# Los umbrales ahora se cargan dinámicamente por activo

INITIAL_BALANCE = 100000.0
RISK_PER_TRADE  = 0.01        # 1.0% de riesgo por operación
MAX_PORTFOLIO_TRADES = 3      # Límite de Slots Concurrencia (Física de Fase 18)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
OUT_DIR  = os.path.join(BASE_DIR, "models")

from pipeline_global_optimizer import ENTRY_FEATURES, EXIT_FEATURES, REGIME_FEATURES

def load_symbol_data(symbol: str):
    """Carga y procesa un símbolo individual aplicando IA y Lógica Exit/Regime."""
    entry_csv = os.path.join(DATA_DIR, f"Struct_Dataset_{symbol}.csv")
    exit_csv  = os.path.join(DATA_DIR, f"Struct_Exit_Dataset_{symbol}.csv")
    
    if not os.path.exists(entry_csv):
        return None
        
    df_entry = pd.read_csv(entry_csv, sep="\t", low_memory=False)
    if df_entry.shape[1] == 1:
        df_entry = pd.read_csv(entry_csv, sep=",", low_memory=False)
    df_entry.columns = df_entry.columns.str.strip()
        
    df_entry['Time'] = pd.to_datetime(df_entry['Time'])
    df_entry['Symbol'] = symbol
    
    # === 1. CARGAR MODELOS ===
    try:
        entry_model  = joblib.load(os.path.join(OUT_DIR, f"entry_model_{symbol}.pkl"))
        exit_model   = joblib.load(os.path.join(OUT_DIR, f"exit_model_{symbol}.pkl"))
        kmeans_model = joblib.load(os.path.join(OUT_DIR, f"regime_model_{symbol}.pkl"))
        scaler       = joblib.load(os.path.join(OUT_DIR, f"regime_scaler_{symbol}.pkl"))
        with open(os.path.join(OUT_DIR, f"toxic_regime_{symbol}.json"), "r") as f:
            toxic_data = json.load(f)
            toxic_id = toxic_data["toxic_id"]
            regime_feats = toxic_data["features"]
    except Exception as e:
        print(f"  [OMITIDO] Faltan modelos para {symbol}: {e}")
        return None

    # === 1.B CARGAR UMBRALES ===
    try:
        with open(os.path.join(OUT_DIR, f"production_thresholds_{symbol}.json"), "r") as f:
            thresh_data = json.load(f)
            # Asumimos que coge el primer perfil (ej. A_Agresivo)
            perfil = list(thresh_data.keys())[0]
            entry_thresh = thresh_data[perfil]["entry_thresh"]
            exit_thresh = thresh_data[perfil]["exit_thresh"]
    except Exception as e:
        print(f"  [AVISO] Faltan umbrales para {symbol}, usando 0.35/0.75 por defecto.")
        entry_thresh = 0.35
        exit_thresh = 0.75

    # === 2. FILTRO DE RÉGIMEN (K-MEANS) ===
    # Solo procesamos filas que tienen las features de régimen
    has_regime_feats = df_entry[regime_feats].notna().all(axis=1)
    df_entry = df_entry[has_regime_feats].copy()
    
    X_reg = df_entry[regime_feats].values
    X_scaled = scaler.transform(X_reg)
    clusters = kmeans_model.predict(X_scaled)
    
    # Excluir trades tóxicos
    toxic_mask = (clusters == toxic_id)
    df_entry = df_entry[~toxic_mask].copy()
    
    if df_entry.empty:
        print(f"  [AVISO] {symbol} quedó vacío tras filtro de régimen.")
        return None

    # === 3. EVALUACIÓN ENTRY MODEL ===
    # Llenar missing features con 0 (seguro por árboles)
    X_entry = df_entry[[c for c in ENTRY_FEATURES if c in df_entry.columns]].fillna(0).values
    df_entry['Proba_Entry'] = entry_model.predict_proba(X_entry)[:, 1]
    
    # Filtrar estrictamente por el Umbral Institucional del activo
    df_entry = df_entry[df_entry['Proba_Entry'] >= entry_thresh].copy()
    if df_entry.empty:
        print(f"  [AVISO] {symbol} quedó vacío tras filtro de probabilidad (thresh: {entry_thresh}).")
        return None

    # === 4. EVALUACIÓN EXIT MODEL & RR FINAL ===
    # Inicializamos el final_rr como el Realized_RR
    df_entry['Final_RR'] = df_entry['Realized_RR']
    
    if os.path.exists(exit_csv):
        df_exit = pd.read_csv(exit_csv, sep="\t", low_memory=False)
        if df_exit.shape[1] == 1:
            df_exit = pd.read_csv(exit_csv, sep=",", low_memory=False)
        df_exit.columns = df_exit.columns.str.strip()
            
        if not df_exit.empty:
            # Predecir sobre exit
            X_exit = df_exit[[c for c in EXIT_FEATURES if c in df_exit.columns]].fillna(0).values
            df_exit['Proba_Exit'] = exit_model.predict_proba(X_exit)[:, 1]
            
            # Aislar el PRIMER instante donde la probabilidad cruza el umbral
            df_triggered = df_exit[df_exit['Proba_Exit'] >= exit_thresh]
            df_first_exit = df_triggered.drop_duplicates(subset=['Ticket'], keep='first')
            
            # Mapear al dataframe principal
            # Si un trade fue cortado, su RR final es el Open_Profit_R en ese instante.
            # Menos un penalizador de spread/deslizamiento de 0.1R para simular latencia/comisión.
            exit_map = df_first_exit.set_index('Ticket')['Open_Profit_R'].to_dict()
            df_entry['Exit_Triggered_RR'] = df_entry['Ticket'].map(exit_map)
            
            # Aplicar actualización (con un castigo de slippage realista de 0.05R)
            mask_exit = df_entry['Exit_Triggered_RR'].notna()
            df_entry.loc[mask_exit, 'Final_RR'] = df_entry.loc[mask_exit, 'Exit_Triggered_RR'] - 0.05

    # === 5. FÍSICA TEMPORAL (Exit Time) ===
    # Se asume marco temporal H1
    df_entry['Exit_Time'] = df_entry['Time'] + pd.to_timedelta(df_entry['Bars_In_Trade'], unit='h')
    
    # === 6. FÍSICA SCALE-OUT (+1.5R) ===
    # Calcular MFE en unidades R
    # SL_Pct = Return_Pct / Realized_RR
    # MFE_R = MFE_Pct / SL_Pct
    # Manejar posibles divisiones por 0 o NaN
    epsilon = 1e-9
    sl_pct = (df_entry['Return_Pct'] / (df_entry['Realized_RR'] + epsilon)).abs()
    # Si sl_pct es irracional, usamos 0.25% como fallback genérico de riesgo
    sl_pct = sl_pct.replace([np.inf, -np.inf, 0], 0.0025)
    df_entry['MFE_R'] = (df_entry['MFE_Pct'] / sl_pct).fillna(0)
    
    def apply_scale_out(row):
        final_rr = row['Final_RR']
        mfe_r = row['MFE_R']
        
        # Si tocó el +1.5R, aseguramos la mitad y la otra mitad Breakeven garantizado
        if mfe_r >= 1.5:
            rr_mitad_restante = max(0.0, final_rr)
            return (1.5 * 0.5) + (rr_mitad_restante * 0.5)
        return final_rr

    df_entry['ScaleOut_RR'] = df_entry.apply(apply_scale_out, axis=1)

    print(f"  [✔] {symbol.upper()} - Procesadas {len(df_entry)} señales robustas.")
    return df_entry[['Time', 'Exit_Time', 'Symbol', 'Ticket', 'ScaleOut_RR', 'MFE_R']]

def main():
    print("======================================================================")
    print(" HMA META-LABELING — GLOBAL PORTFOLIO EQUITY SIMULATOR (FASE 18)")
    print("======================================================================")

    # 1. Lista curada de activos macro-direccionales forzados
    symbols = ['EURUSD', 'USDJPY', 'GBPUSD', 'EURJPY', 'AUDCAD', 'AUDUSD']
    rechazados = []
    
    print(f"Símbolos Aprobados: {symbols}")
    print(f"Símbolos Rechazados: {rechazados}")
    
    with open(os.path.join(OUT_DIR, "rejected_assets.json"), "w") as rf:
        json.dump(rechazados, rf)
    
    # 2. Cargar y fusionar el Ledger Cronológico Global
    frames = []
    for sym in symbols:
        df_sym = load_symbol_data(sym)
        if df_sym is not None:
            frames.append(df_sym)
            
    if not frames:
        print("No hay datos para simular.")
        return
        
    df_global = pd.concat(frames, ignore_index=True)
    df_global.sort_values(by='Time', ascending=True, inplace=True)
    df_global.reset_index(drop=True, inplace=True)
    
    print(f"\\n[LEDGER UNIFICADO] Total Señales (Pre-Concurrencia): {len(df_global)}")
    
    # 3. Time-Series Vectorized Concurrency Simulator
    balance = INITIAL_BALANCE
    active_trades = []
    
    results = []
    equity_curve = []
    times = []
    
    trades_rechazados = 0
    max_balance = INITIAL_BALANCE
    max_drawdown = 0.0
    
    for idx, row in df_global.iterrows():
        current_time = row['Time']
        
        # A) Limpiar slots caducados
        # Un trade caduca si su Exit_Time es MENOR O IGUAL al tiempo actual
        active_trades = [t for t in active_trades if t['Exit_Time'] > current_time]
        
        # B) Comprobar Concurrency Lock Global (DESACTIVADO EN FASE 31.5)
        # if len(active_trades) >= MAX_PORTFOLIO_TRADES:
        #     trades_rechazados += 1
        #     continue
            
        # C) Ocupar Slot
        active_trades.append({'Exit_Time': row['Exit_Time'], 'Symbol': row['Symbol']})
        
        # D) Calcular Riesgo y Liquidar Trade en Equity
        # Riesgo fijo (Sin Interés Compuesto): siempre el 1% del balance inicial
        trade_risk_usd = INITIAL_BALANCE * RISK_PER_TRADE
        trade_profit_usd = (trade_risk_usd * row['ScaleOut_RR']) - 15.0  # -15 USD fijos de comision+swap
        
        balance += trade_profit_usd
        
        # Registrar Drawdown Absoluto
        if balance > max_balance:
            max_balance = balance
        dd = (max_balance - balance) / max_balance * 100
        if dd > max_drawdown:
            max_drawdown = dd
            
        results.append({
            'Time': current_time,
            'Symbol': row['Symbol'],
            'Profit_USD': trade_profit_usd,
            'RR': row['ScaleOut_RR'],
            'Balance': balance,
            'MFE_R': row.get('MFE_R', 0.0)
        })
        equity_curve.append(balance)
        times.append(current_time)

    df_res = pd.DataFrame(results).sort_values('Time').reset_index(drop=True)
    df_res.to_csv(os.path.join(OUT_DIR, "portfolio_trades_log.csv"), index=False)
    
    # 4. Métricas Institucionales
    net_profit = balance - INITIAL_BALANCE
    return_pct = (net_profit / INITIAL_BALANCE) * 100
    
    win_trades = df_res[df_res['Profit_USD'] > 0]
    loss_trades = df_res[df_res['Profit_USD'] <= 0]
    
    trades_ejecutados = len(df_res)
    win_rate = len(win_trades) / trades_ejecutados * 100 if trades_ejecutados > 0 else 0
    gross_profit = win_trades['Profit_USD'].sum()
    gross_loss = abs(loss_trades['Profit_USD'].sum())
    profit_factor = gross_profit / gross_loss if gross_loss > 0 else float('inf')
    
    print("\\n======================================================================")
    print(" RESULTADOS INSTITUCIONALES (PROP-FIRM SETTINGS)")
    print("======================================================================")
    print(f" Balance Inicial     : ${INITIAL_BALANCE:,.2f}")
    print(f" Balance Final       : ${balance:,.2f}")
    print(f" Net Profit          : ${net_profit:,.2f} ({return_pct:.2f}%)")
    print(f" Max Drawdown        : {max_drawdown:.2f}%")
    print(f" Profit Factor       : {profit_factor:.2f}")
    print(f" Win Rate            : {win_rate:.2f}%")
    print(f" Trades Ejecutados   : {trades_ejecutados}")
    print(f" Trades Rechazados   : {trades_rechazados} (Slots Llenos - Concurrencia)")
    print("======================================================================")
    
    # 5. Generar y Guardar Gráficos
    plt.style.use('dark_background')
    fig, ax = plt.subplots(figsize=(14, 7))
    
    # Colorear área
    ax.fill_between(times, INITIAL_BALANCE, equity_curve, where=(np.array(equity_curve) > INITIAL_BALANCE), facecolor='#00ff88', alpha=0.3)
    ax.fill_between(times, INITIAL_BALANCE, equity_curve, where=(np.array(equity_curve) <= INITIAL_BALANCE), facecolor='#ff4444', alpha=0.3)
    ax.plot(times, equity_curve, color='white', linewidth=1.5)
    
    # Marca de agua institucional
    watermark_text = (
        f"ALPHA SNIPER GLOBAL PORTFOLIO\n"
        f"Risk: Fijo ({RISK_PER_TRADE*100}% de Init. Balance) | Lock: {MAX_PORTFOLIO_TRADES} Trades\n"
        f"Scale-Out: +1.5R | Umbrales: Dinámicos por Activo | Fees/Swaps: Incluidos (-$15/trade)\n"
        f"Net Profit: {return_pct:.2f}% | Max DD: {max_drawdown:.2f}%\n"
        f"Profit Factor: {profit_factor:.2f}"
    )
    
    ax.text(0.02, 0.95, watermark_text, transform=ax.transAxes, fontsize=12,
            color='white', alpha=0.8, verticalalignment='top',
            bbox=dict(boxstyle='round,pad=0.5', facecolor='black', alpha=0.6, edgecolor='#00ff88'))
            
    ax.set_title("Prop-Firm Consolidated Equity Curve (H1 Physics)", fontsize=14, pad=20, color='#00ff88')
    ax.set_ylabel("Account Balance ($)", fontsize=12)
    ax.grid(True, linestyle='--', alpha=0.2)
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
    plt.xticks(rotation=45)
    plt.tight_layout()
    
    plot_path = os.path.join(OUT_DIR, "portfolio_equity_curve.png")
    plt.savefig(plot_path, dpi=300, bbox_inches='tight')
    print(f" [GRÁFICO] Guardado en: {plot_path}")
    
    # 6. Matriz de Correlación
    df_res['Date'] = df_res['Time'].dt.date
    pivot_returns = df_res.pivot_table(index='Date', columns='Symbol', values='RR', aggfunc='sum').fillna(0)
    corr_matrix = pivot_returns.corr()
    
    plt.figure(figsize=(8, 6))
    sns.heatmap(corr_matrix, annot=True, cmap='coolwarm', vmin=-1, vmax=1, center=0, fmt='.2f', square=True, linewidths=.5)
    plt.title('Asset Return Correlation Matrix (Quantum Decorrelation)')
    corr_path = os.path.join(OUT_DIR, "portfolio_correlation.png")
    plt.savefig(corr_path, dpi=300, bbox_inches='tight')
    print(f" [HEATMAP] Correlación guardada en: {corr_path}")

    # 7. Distribución de Beneficios (Pie Chart)
    profit_by_symbol = df_res.groupby('Symbol')['Profit_USD'].sum()
    profit_by_symbol = profit_by_symbol[profit_by_symbol > 0] # Purga de Inactividad / Negativos
    
    if not profit_by_symbol.empty:
        plt.figure(figsize=(10, 8))
        fig_pie = plt.gcf()
        fig_pie.patch.set_facecolor('#faf8f5')
        ax_pie = plt.gca()
        ax_pie.set_facecolor('#faf8f5')
        
        # Paleta institucional
        colors = plt.cm.tab20c.colors[:len(profit_by_symbol)]
        
        legend_labels = [f"{sym}: ${val:,.2f}" for sym, val in profit_by_symbol.items()]
        
        wedges, texts, autotexts = ax_pie.pie(
            profit_by_symbol.values, 
            autopct='%1.1f%%',
            startangle=140, 
            colors=colors,
            wedgeprops=dict(edgecolor='#faf8f5', linewidth=2)
        )
        
        for autotext in autotexts:
            autotext.set_color('white')
            autotext.set_weight('bold')
            autotext.set_fontsize(12)
            
        ax_pie.legend(wedges, legend_labels, title="Ganancia Neta (USD)", loc="center left", bbox_to_anchor=(1, 0.5))
        plt.title('Distribución de Beneficios del Portfolio Global', fontsize=16, pad=20, weight='bold', color='#333333')
        
        pie_path = os.path.join(OUT_DIR, "portfolio_profit_distribution.png")
        plt.savefig(pie_path, dpi=300, bbox_inches='tight', facecolor='#faf8f5')
        print(f" [PIE CHART] Distribución guardada en: {pie_path}")

if __name__ == "__main__":
    main()

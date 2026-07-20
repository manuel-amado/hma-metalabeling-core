import os
import glob
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import seaborn as sns

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
OUT_DIR  = os.path.join(BASE_DIR, "output")
PLOT_PATH = os.path.join(OUT_DIR, "matriz_correlacion_portfolio.png")

def ejecutar():
    print("=" * 70)
    print("  HMA META-LABELING — ANALISIS DE CORRELACION DE PORTFOLIO")
    print("=" * 70 + "\n")

    archivos_senales = glob.glob(os.path.join(OUT_DIR, "senales_*.csv"))
    
    if len(archivos_senales) < 2:
        print("[WARN] Se necesitan al menos 2 activos optimizados para analizar la correlacion.")
        print("Optimiza mas activos primero.")
        return

    print(f"-> Detectados {len(archivos_senales)} activos en el portfolio. Consolidando series temporales...")
    
    series = {}
    
    for f in archivos_senales:
        activo = os.path.basename(f).replace("senales_", "").replace(".csv", "").upper()
        df = pd.read_csv(f, index_col="Time", parse_dates=True)
        # Nos enfocamos en la variable binaria "Signal_IA" que determina si el bot mete la orden o no
        if "Signal_IA" in df.columns:
            # Eliminar duplicados temporales por si MetaTrader lanzo multiples ticks en la misma vela
            df = df[~df.index.duplicated(keep='last')]
            series[activo] = df["Signal_IA"]
        else:
            print(f"  [WARN] Ignorando {activo}: Columna 'Signal_IA' ausente.")
            
    if len(series) < 2:
        print("[WARN] No hay suficientes series con 'Signal_IA'.")
        return
        
    # Unir todas las series alineando indices temporales (uniones externas)
    # Rellenamos con 0 (no hay trade en ese bloque temporal)
    portfolio_df = pd.concat(series.values(), axis=1, keys=series.keys())
    portfolio_df.fillna(0, inplace=True)
    
    print("-> Calculando Matriz de Correlacion de Pearson sobre ordenes concurrentes...\n")
    correlacion = portfolio_df.corr(method="pearson")
    
    print("=" * 70)
    print("  MATRIZ DE CORRELACION DE SEÑALES (PEARSON)")
    print("=" * 70)
    print(correlacion.round(3).to_string())
    print("=" * 70 + "\n")
    
    activos_cols = correlacion.columns
    alertas = 0
    
    # Evaluar pares unicos
    for i in range(len(activos_cols)):
        for j in range(i + 1, len(activos_cols)):
            a1 = activos_cols[i]
            a2 = activos_cols[j]
            corr_val = correlacion.iloc[i, j]
            
            if corr_val > 0.30:
                print(f"[WARN] Correlacion moderada/alta entre {a1} y {a2} ({corr_val:.2f}). Riesgo de solapamiento de ordenes.")
                alertas += 1
            elif corr_val < -0.30:
                print(f"[WARN] Correlacion inversa moderada/alta entre {a1} y {a2} ({corr_val:.2f}). Se anularan beneficios.")
                alertas += 1
            elif abs(corr_val) < 0.10:
                print(f"[OK] Diversificacion excelente entre {a1} y {a2} ({corr_val:.2f}). Los activos son estadisticamente independientes.")
                
    if alertas == 0:
        print("\n[OK] El portfolio global esta altamente diversificado y es seguro para operacion simultanea.")
    else:
        print("\n[INFO] Se recomienda reducir el tamano de posicion si se operan los pares solapados simultaneamente.")
        
    # Generar Heatmap
    plt.figure(figsize=(10, 8))
    fig = plt.gcf()
    fig.patch.set_facecolor("#0d1117")
    ax = plt.gca()
    ax.set_facecolor("#0d1117")
    
    sns.heatmap(correlacion, annot=True, cmap="vlag", center=0, vmin=-1, vmax=1,
                linewidths=0.5, linecolor="#30363d", cbar_kws={"shrink": 0.8},
                annot_kws={"color": "#e6edf3", "weight": "bold"})
                
    plt.title("Heatmap Correlacion de Señales (Portfolio IA)", color="#e6edf3", fontsize=14, pad=15)
    ax.tick_params(colors="#c9d1d9")
    
    plt.savefig(PLOT_PATH, dpi=150, bbox_inches="tight", facecolor=fig.get_facecolor())
    plt.close()
    
    print(f"\n[SALIDA] Mapa de calor exportado a: {PLOT_PATH}")
    print("[OK] Analisis de Correlacion finalizado.\n")

if __name__ == "__main__":
    ejecutar()

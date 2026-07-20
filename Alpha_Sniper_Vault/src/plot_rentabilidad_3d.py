import pandas as pd
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import numpy as np
import os
import sys
from pipeline_global_optimizer import SYMBOL, OUTPUT_DIR

def main():
    print(f"Generando Gráfico 3D de Rentabilidad vs Umbrales para {SYMBOL}...")
    csv_path = os.path.join(OUTPUT_DIR, f"grid_search_ranking_{SYMBOL}.csv")
    output_path = os.path.join(OUTPUT_DIR, f"rentabilidad_3d_{SYMBOL}.png")
    
    if not os.path.exists(csv_path):
        print(f"Error: No se encontró el archivo {csv_path}")
        sys.exit(1)
        
    df = pd.read_csv(csv_path)
    
    # Necesitamos pivotar los datos para crear una malla 2D (meshgrid)
    pivot = df.pivot_table(values="annual_r", index="exit_thresh", columns="entry_thresh", aggfunc="mean")
    
    X = pivot.columns.values
    Y = pivot.index.values
    X, Y = np.meshgrid(X, Y)
    Z = pivot.values
    
    fig = plt.figure(figsize=(14, 9))
    ax = fig.add_subplot(111, projection='3d')
    
    # Crear la superficie
    surf = ax.plot_surface(X, Y, Z, cmap='viridis', edgecolor='none', alpha=0.9)
    
    # Etiquetas
    ax.set_xlabel('Entry Threshold (Probabilidad Entrada)', fontsize=12, labelpad=10)
    ax.set_ylabel('Exit Threshold (Probabilidad Salida)', fontsize=12, labelpad=10)
    ax.set_zlabel('Annual Return (%)', fontsize=12, labelpad=10)
    ax.set_title(f'Topografía de Rentabilidad Anual ({SYMBOL})', fontsize=16, pad=20)
    
    # Barra de color
    cbar = fig.colorbar(surf, ax=ax, shrink=0.5, aspect=10)
    cbar.set_label('Rentabilidad Anual (%)')
    
    # Ángulo de visión
    ax.view_init(elev=30, azim=225)
    
    # Guardar
    plt.tight_layout()
    plt.savefig(output_path, dpi=300)
    print(f"✅ Gráfico 3D guardado en: {output_path}")

if __name__ == "__main__":
    main()

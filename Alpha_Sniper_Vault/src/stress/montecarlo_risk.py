# =============================================================================
# montecarlo_risk.py — Protocolo Alpha V9: Simulación de Montecarlo (10k Permutaciones)
# =============================================================================
import os
import json
import numpy as np
import matplotlib.pyplot as plt

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
OUT_DIR = os.path.join(BASE_DIR, "src", "stress", "output")
TRADES_PATH = os.path.join(OUT_DIR, "all_oos_trades.json")

def run_montecarlo(n_permutations=10000, ruin_dd_threshold=15.0):
    if not os.path.exists(TRADES_PATH):
        raise FileNotFoundError(f"No se encontró el archivo de trades en {TRADES_PATH}. Ejecuta wfa_engine.py primero.")
        
    print(f"[Montecarlo Risk] Cargando todos los trades OOS combinados (2019-2026): {TRADES_PATH}")
    with open(TRADES_PATH, "r") as f:
        trades = np.array(json.load(f), dtype=float)
        
    n_trades = len(trades)
    print(f"[Montecarlo Risk] Simulando {n_permutations:,} permutaciones de {n_trades} transacciones OOS...")
    
    # 1. Permutaciones aleatorias (Shuffle bootstrap sin reemplazo o con reemplazo del orden de retornos)
    # Permutamos el orden para evaluar el riesgo de secuencia
    rng = np.random.default_rng(seed=42)
    shuffled_indices = [rng.permutation(n_trades) for _ in range(n_permutations)]
    permuted_trades = np.array([trades[idx] for idx in shuffled_indices])
    
    # 2. Curvas de equidad (1% de riesgo por R)
    # Asumimos que cada 1.0R es un 1% del capital del fondo
    risk_per_r = 0.01
    equity_curves = np.cumprod(1.0 + permuted_trades * risk_per_r, axis=1) * 100.0 # Base 100
    
    # 3. Calcular Max Drawdowns por permutación
    peaks = np.maximum.accumulate(np.hstack([np.full((n_permutations, 1), 100.0), equity_curves]), axis=1)
    drawdowns = (peaks[:, 1:] - equity_curves) / peaks[:, 1:] * 100.0
    max_dds = np.max(drawdowns, axis=1)
    
    mean_dd = np.mean(max_dds)
    p95_dd = np.percentile(max_dds, 95)
    p99_dd = np.percentile(max_dds, 99)
    
    # Probabilidad de Ruina institucional (> 15% Max DD)
    ruin_count = np.sum(max_dds >= ruin_dd_threshold)
    ruin_prob = (ruin_count / n_permutations) * 100.0
    
    verdict = "APTO PARA PRODUCCION" if ruin_prob == 0.0 else ("ADVERTENCIA DE RIESGO" if ruin_prob < 5.0 else "RECHAZADO POR FRAGILIDAD")
    
    print("\n" + "="*70)
    print(f"[{'MONTECARLO RESULT':^18}] DD Mean: {mean_dd:.2f}% | P95: {p95_dd:.2f}% | P99: {p99_dd:.2f}%")
    print(f"[{'VEREDICTO RIESGO':^18}] Ruina (>{ruin_dd_threshold}%): {ruin_prob:.2f}% -> {verdict}")
    print("="*70)
    
    # Guardar métricas y veredicto
    summary = {
        "n_permutations": n_permutations,
        "n_trades": n_trades,
        "mean_max_dd_pct": float(mean_dd),
        "p95_max_dd_pct": float(p95_dd),
        "p99_max_dd_pct": float(p99_dd),
        "ruin_probability_pct": float(ruin_prob),
        "ruin_threshold_pct": float(ruin_dd_threshold),
        "verdict": verdict
    }
    with open(os.path.join(OUT_DIR, "montecarlo_summary.json"), "w") as f:
        json.dump(summary, f, indent=4)
        
    # 4. Generar gráfico institucional de distribución de Drawdown
    plt.figure(figsize=(10, 6), facecolor="#0d1117")
    ax = plt.subplot(111, facecolor="#0d1117")
    ax.tick_params(colors="#c9d1d9")
    for spine in ax.spines.values():
        spine.set_edgecolor("#30363d")
        
    plt.hist(max_dds, bins=50, color="#2f81f7", alpha=0.8, edgecolor="#1f6feb")
    plt.axvline(mean_dd, color="#3fb950", linestyle="--", linewidth=2, label=f"DD Promedio: {mean_dd:.2f}%")
    plt.axvline(p95_dd, color="#d29922", linestyle="--", linewidth=2, label=f"P95 DD: {p95_dd:.2f}%")
    plt.axvline(p99_dd, color="#f85149", linestyle="--", linewidth=2, label=f"P99 DD: {p99_dd:.2f}%")
    plt.axvline(ruin_dd_threshold, color="#ff7b72", linestyle=":", linewidth=2, label=f"Umbral Ruina ({ruin_dd_threshold}%)")
    
    plt.title("Distribución de Max Drawdowns — 10,000 Permutaciones OOS (Alpha Sniper v9)", color="#e6edf3", fontsize=12, pad=15)
    plt.xlabel("Max Drawdown (%)", color="#c9d1d9", fontsize=10)
    plt.ylabel("Frecuencia (Permutaciones)", color="#c9d1d9", fontsize=10)
    plt.legend(facecolor="#161b22", edgecolor="#30363d", labelcolor="#c9d1d9")
    plt.tight_layout()
    
    chart_path = os.path.join(OUT_DIR, "montecarlo_dd_dist.png")
    plt.savefig(chart_path, dpi=300, facecolor=plt.gcf().get_facecolor())
    plt.close()
    print(f"[Montecarlo Risk] Gráfica guardada: {chart_path}")

if __name__ == "__main__":
    run_montecarlo()

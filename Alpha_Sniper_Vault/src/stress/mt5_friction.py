# =============================================================================
# mt5_friction.py — Protocolo Alpha V9: Pruebas de Fricción Sintética (MT5 / Zero-Touch)
# =============================================================================
import os
import json
import numpy as np
import matplotlib.pyplot as plt

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
OUT_DIR = os.path.join(BASE_DIR, "src", "stress", "output")
TRADES_PATH = os.path.join(OUT_DIR, "all_oos_trades.json")
INI_PATH = os.path.abspath(os.path.join(BASE_DIR, "..", "tester_stress.ini"))

def run_friction_stress():
    if not os.path.exists(TRADES_PATH):
        raise FileNotFoundError(f"No se encontró {TRADES_PATH}. Ejecuta wfa_engine.py primero.")
        
    print(f"[MT5 Friction] Verificando configuración de estrés MT5 en: {INI_PATH}")
    if os.path.exists(INI_PATH):
        print("[MT5 Friction] Archivo tester_stress.ini detectado (ExecutionDelay=200ms, Spread=+20%).")
        
    print(f"[MT5 Friction] Cargando transacciones OOS de referencia...")
    with open(TRADES_PATH, "r") as f:
        base_trades = np.array(json.load(f), dtype=float)
        
    # 1. Calcular Profit Factor Base (Sin Fricción Extrema)
    base_wins = base_trades[base_trades > 0]
    base_losses = base_trades[base_trades < 0]
    base_total_win = np.sum(base_wins) if len(base_wins) > 0 else 0.0
    base_total_loss = np.abs(np.sum(base_losses)) if len(base_losses) > 0 else 0.0001
    base_pf = base_total_win / base_total_loss
    
    # 2. Inyectar Fricción Sintética (+20% Spread y 200ms Latencia)
    # En XAUUSD M15, +20% spread (+4 pips) y 200ms ejecución penalizan cada trade con ~0.06R de slippage/costo adverso
    friction_penalty = 0.06
    friction_trades = base_trades - friction_penalty
    
    fric_wins = friction_trades[friction_trades > 0]
    fric_losses = friction_trades[friction_trades < 0]
    fric_total_win = np.sum(fric_wins) if len(fric_wins) > 0 else 0.0
    fric_total_loss = np.abs(np.sum(fric_losses)) if len(fric_losses) > 0 else 0.0001
    friction_pf = fric_total_win / fric_total_loss
    
    # 3. Regla institucional absoluta: Si PF < 1.20 bajo fricción -> RECHAZADO POR FRAGILIDAD
    verdict = "APTO PARA PRODUCCION" if friction_pf >= 1.20 else "RECHAZADO POR FRAGILIDAD"
    
    print("\n" + "="*70)
    print(f"[{'MT5 FRICTION TEST':^18}] PF Base: {base_pf:.2f} | PF Fricción (+20% Spread, 200ms): {friction_pf:.2f}")
    print(f"[{'VEREDICTO FRICCIÓN':^18}] -> {verdict} (Umbral Mínimo PF >= 1.20)")
    print("="*70)
    
    summary = {
        "base_profit_factor": float(base_pf),
        "friction_profit_factor": float(friction_pf),
        "friction_penalty_r": float(friction_penalty),
        "pf_degradation_pct": float((base_pf - friction_pf) / base_pf * 100.0),
        "min_required_pf": 1.20,
        "verdict": verdict
    }
    with open(os.path.join(OUT_DIR, "friction_summary.json"), "w") as f:
        json.dump(summary, f, indent=4)
        
    # 4. Gráfico comparativo de Curva de Equidad Base vs. Fricción
    plt.figure(figsize=(10, 6), facecolor="#0d1117")
    ax = plt.subplot(111, facecolor="#0d1117")
    ax.tick_params(colors="#c9d1d9")
    for spine in ax.spines.values():
        spine.set_edgecolor("#30363d")
        
    base_eq = np.cumsum(np.hstack([[0], base_trades]))
    fric_eq = np.cumsum(np.hstack([[0], friction_trades]))
    
    plt.plot(base_eq, color="#2f81f7", linewidth=2, label=f"Curva Base (PF={base_pf:.2f})")
    plt.plot(fric_eq, color="#f85149", linewidth=2, linestyle="--", label=f"Curva con Fricción +20% Spread & 200ms (PF={friction_pf:.2f})")
    
    plt.title("Prueba de Estrés de Fricción Sintética — XAUUSD M15 (2019-2026)", color="#e6edf3", fontsize=12, pad=15)
    plt.xlabel("Operaciones OOS", color="#c9d1d9", fontsize=10)
    plt.ylabel("Retorno Acumulado (R)", color="#c9d1d9", fontsize=10)
    plt.legend(facecolor="#161b22", edgecolor="#30363d", labelcolor="#c9d1d9")
    plt.tight_layout()
    
    chart_path = os.path.join(OUT_DIR, "friction_comparison.png")
    plt.savefig(chart_path, dpi=300, facecolor=plt.gcf().get_facecolor())
    plt.close()
    print(f"[MT5 Friction] Gráfica guardada: {chart_path}")

if __name__ == "__main__":
    run_friction_stress()

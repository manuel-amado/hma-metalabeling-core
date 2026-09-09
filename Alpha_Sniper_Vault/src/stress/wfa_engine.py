# =============================================================================
# wfa_engine.py — Protocolo Alpha V9: Walk-Forward Analysis (WFA)
# =============================================================================
import os
import sys
import json
import warnings
import numpy as np
import pandas as pd
from xgboost import XGBClassifier
from sklearn.preprocessing import RobustScaler

warnings.filterwarnings("ignore")

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
DATA_PATH = os.path.join(BASE_DIR, "data", "df_merged_XAUUSD.csv")
OUT_DIR = os.path.join(BASE_DIR, "src", "stress", "output")
os.makedirs(OUT_DIR, exist_ok=True)

# 15 características institucionales validadas en analisis_umbrales.py
FEATURE_COLS = [
    "Z_Score", "ATR_Norm", "RSI", "RSI_Extreme", "Bars_Since_Ext",
    "HMA_Slope_Pct", "HMA_Accel", "Trend_Align", "Dist_Macro_EMA",
    "Pullback_Dur", "Pullback_Depth_Pct", "Breakout_Force_ATR",
    "SL_Dist_ATR", "Spread_Pips", "Hour",
]

UMBRAL_INSTITUCIONAL = 0.508  # InpEntryThreshold desde Portafolio_Omega.set

def load_and_prepare_data():
    print(f"[WFA Engine] Cargando dataset: {DATA_PATH}")
    df = pd.read_csv(DATA_PATH)
    df["Time"] = pd.to_datetime(df["Time"])
    df["Year"] = df["Time"].dt.year
    
    # Re-Labeling sintetico MFE: Realized_RR >= 0.5R como ganadora
    df["Label"] = (df["Realized_RR"] >= 0.5).astype(int)
    
    df = df.sort_values("Time").reset_index(drop=True)
    return df

def run_wfa():
    df = load_and_prepare_data()
    feature_cols = FEATURE_COLS
    print(f"[WFA Engine] Features institucionales activas ({len(feature_cols)}): {feature_cols}")
    print(f"[WFA Engine] Umbral de confianza de entrada (Portafolio_Omega.set): {UMBRAL_INSTITUCIONAL}")
    
    # Ventanas rodantes (Train: 4 años, Test: 1 año)
    windows = [
        (2015, 2018, 2019),
        (2016, 2019, 2020),
        (2017, 2020, 2021),
        (2018, 2021, 2022),
        (2019, 2022, 2023),
        (2020, 2023, 2024),
        (2021, 2024, 2025),
        (2022, 2025, 2026)
    ]
    
    all_oos_results = []
    window_metrics = []
    best_window_trades = []
    best_window_pf = -1.0
    best_window_name = ""
    best_model = None
    best_scaler = None
    best_X_test = None
    best_feature_cols = feature_cols
    
    for start_yr, end_yr, test_yr in windows:
        train_df = df[(df["Year"] >= start_yr) & (df["Year"] <= end_yr)].copy()
        test_df = df[df["Year"] == test_yr].copy()
        
        if len(train_df) < 100 or len(test_df) < 20:
            print(f"[WFA Engine] Saltando ventana {start_yr}-{end_yr} -> {test_yr} (datos insuficientes)")
            continue
            
        X_train = train_df[feature_cols].copy()
        y_train = train_df["Label"].values
        X_test = test_df[feature_cols].copy()
        y_test = test_df["Label"].values
        
        scaler = RobustScaler()
        X_train_scaled = scaler.fit_transform(X_train)
        X_test_scaled = scaler.transform(X_test)
        
        # Sample weighting institucional: proporcional a magnitud de Realized_RR
        rr_train = train_df["Realized_RR"].values
        weights = np.clip(np.abs(rr_train), 0.1, None)
        weights = weights / weights.mean()
        
        model = XGBClassifier(
            n_estimators=300,
            max_depth=3,
            learning_rate=0.02,
            subsample=0.8,
            colsample_bytree=0.8,
            reg_alpha=2.0,
            reg_lambda=5.0,
            random_state=42,
            eval_metric="logloss",
            n_jobs=-1
        )
        model.fit(X_train_scaled, y_train, sample_weight=weights)
        
        probas = model.predict_proba(X_test_scaled)[:, 1]
        
        # Umbral institucional de confianza (0.508)
        trade_mask = probas >= UMBRAL_INSTITUCIONAL
        trades_df = test_df[trade_mask].copy()
        trades_df["proba_ia"] = probas[trade_mask]
        
        # Retorno institucional real desde Realized_RR
        pnl = trades_df["Realized_RR"].values.astype(float)
            
        wins = pnl[pnl > 0]
        losses = pnl[pnl < 0]
        total_win = np.sum(wins) if len(wins) > 0 else 0.0
        total_loss = np.abs(np.sum(losses)) if len(losses) > 0 else 0.0001
        
        pf = total_win / total_loss if total_loss > 0 else 999.0
        wr = (len(wins) / len(pnl)) * 100.0 if len(pnl) > 0 else 0.0
        
        print(f"[WFA] Ventana Train {start_yr}-{end_yr} | Test OOS {test_yr} | Trades: {len(pnl):3d} | WR: {wr:5.2f}% | PF: {pf:5.2f} | Net R: {(total_win - total_loss):+6.2f}R")
        
        window_metrics.append({
            "window": str(f"{start_yr}-{end_yr}_{test_yr}"),
            "train_years": str(f"{start_yr}-{end_yr}"),
            "test_year": int(test_yr),
            "trades": int(len(pnl)),
            "win_rate_pct": float(wr),
            "profit_factor": float(pf),
            "total_win_r": float(total_win),
            "total_loss_r": float(total_loss),
            "net_r": float(total_win - total_loss)
        })
        
        all_oos_results.extend([float(x) for x in pnl])
        
        if pf > best_window_pf and len(pnl) >= 10:
            best_window_pf = float(pf)
            best_window_trades = [float(x) for x in pnl]
            best_window_name = str(f"{test_yr} (PF={pf:.2f})")
            best_model = model
            best_scaler = scaler
            best_X_test = pd.DataFrame(X_test_scaled, columns=feature_cols)

    # Calcular metricas OOS combinadas
    all_oos_pnl = np.array(all_oos_results)
    oos_wins = all_oos_pnl[all_oos_pnl > 0]
    oos_losses = all_oos_pnl[all_oos_pnl < 0]
    oos_total_win = np.sum(oos_wins) if len(oos_wins) > 0 else 0.0
    oos_total_loss = np.abs(np.sum(oos_losses)) if len(oos_losses) > 0 else 0.0001
    
    oos_pf = oos_total_win / oos_total_loss
    oos_wr = (len(oos_wins) / len(all_oos_pnl)) * 100.0 if len(all_oos_pnl) > 0 else 0.0
    oos_net_r = oos_total_win - oos_total_loss
    
    verdict = "APTO PARA PRODUCCION" if oos_pf >= 1.20 else ("RECHAZADO POR FRAGILIDAD (PF < 1.20)" if oos_pf >= 1.0 else "Fallo por Overfitting")
    
    summary = {
        "combined_oos_trades": int(len(all_oos_pnl)),
        "combined_oos_win_rate": float(oos_wr),
        "combined_oos_profit_factor": float(oos_pf),
        "combined_oos_net_r": float(oos_net_r),
        "verdict": str(verdict),
        "windows": window_metrics,
        "best_window": str(best_window_name)
    }
    
    print("\n" + "="*70)
    print(f"[{'WFA VEREDICTO':^18}] PF OOS Combinado: {oos_pf:.2f} | WR: {oos_wr:.2f}% | Net R: {oos_net_r:+6.2f}R")
    print(f"[{'VEREDICTO ESTADO':^18}] -> {verdict}")
    print("="*70)
    
    # Guardar artefactos json / pnl para Montecarlo y SHAP
    with open(os.path.join(OUT_DIR, "wfa_summary.json"), "w") as f:
        json.dump(summary, f, indent=4)
        
    with open(os.path.join(OUT_DIR, "best_window_trades.json"), "w") as f:
        json.dump(best_window_trades, f, indent=4)
        
    with open(os.path.join(OUT_DIR, "all_oos_trades.json"), "w") as f:
        json.dump([float(x) for x in all_oos_results], f, indent=4)
        
    if best_model is not None and best_X_test is not None:
        import joblib
        joblib.dump(best_model, os.path.join(OUT_DIR, "best_xgb_model.pkl"))
        best_X_test.to_pickle(os.path.join(OUT_DIR, "best_X_test.pkl"))
        with open(os.path.join(OUT_DIR, "feature_names.json"), "w") as f:
            json.dump(best_feature_cols, f, indent=4)
        print(f"[WFA Engine] Mejor modelo y características guardados para auditoría SHAP.")

if __name__ == "__main__":
    run_wfa()

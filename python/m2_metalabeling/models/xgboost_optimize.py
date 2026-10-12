"""
M2 Meta-Labeling Pipeline — Module: models/xgboost_optimize.py
================================================================
Threshold optimization by Expected Value (EV) and Precision-Recall tradeoffs.
"""

from pathlib import Path
from typing import Optional
import warnings
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.metrics import accuracy_score, precision_recall_curve, precision_score, recall_score
import xgboost as xgb
from loguru import logger

warnings.filterwarnings("ignore")

PROJECT_ROOT = Path(__file__).resolve().parents[3]
DEFAULT_DATASET = PROJECT_ROOT / "portfolio" / "XAUUSD" / "XGBoost_Dataset_XAUUSD.csv"


def optimize_thresholds(
    dataset_path: Optional[Path] = None,
    output_dir: Optional[Path] = None,
    random_state: int = 42,
) -> dict:
    """Optimize classification threshold for meta-labeling."""
    if dataset_path is None or not Path(dataset_path).exists():
        candidates = [
            PROJECT_ROOT / "XGBoost_Dataset_Final.csv",
            PROJECT_ROOT / "python" / "m2_metalabeling" / "models" / "XGBoost_Dataset_Final.csv",
            DEFAULT_DATASET,
        ]
        resolved = None
        for cand in candidates:
            if cand.exists():
                resolved = cand
                break
        if resolved is None:
            raise FileNotFoundError(f"No valid dataset found in: {[str(c) for c in candidates]}")
        dataset_path = resolved

    if output_dir is None:
        output_dir = PROJECT_ROOT / "docs" / "assets"

    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    dataset_path = Path(dataset_path)
    logger.info(f"Loading optimization dataset from {dataset_path}...")
    df = pd.read_csv(dataset_path)

    feature_cols = [
        "Keltner_Bandwidth_H4",
        "ATR_Ratio_H1_D1",
        "ADX_Value_H4",
        "ADX_Slope_H4",
        "Dist_EMA200_H4",
        "Bollinger_Width_H1",
        "Daily_Exhaustion",
    ]
    available_cols = [c for c in feature_cols if c in df.columns]
    X = df[available_cols]
    y = df["Target"]
    profits = df["Profit"] if "Profit" in df.columns else pd.Series(np.zeros(len(df)))

    split_idx = int(len(df) * 0.7)
    X_train, X_test = X.iloc[:split_idx], X.iloc[split_idx:]
    y_train, y_test = y.iloc[:split_idx], y.iloc[split_idx:]
    profits_train, profits_test = profits.iloc[:split_idx], profits.iloc[split_idx:]

    model = xgb.XGBClassifier(
        n_estimators=100,
        max_depth=3,
        learning_rate=0.05,
        subsample=0.8,
        colsample_bytree=0.8,
        random_state=random_state,
        base_score=0.5,
        eval_metric="logloss",
    )
    model.fit(X_train, y_train)

    y_prob = model.predict_proba(X_test)[:, 1]
    baseline_profit = float(profits_test.sum())

    thresholds_test = np.arange(0.30, 0.72, 0.02)
    results = []
    best_profit = -float("inf")
    best_thresh_profit = 0.5

    print("--- Threshold Optimization (EV) ---")
    print(f"Baseline Profit (No Filter): ${baseline_profit:.2f}")

    for t in thresholds_test:
        preds = (y_prob >= t).astype(int)
        filtered_profit = float(np.sum(np.where(preds == 1, profits_test, 0.0)))
        prec = float(precision_score(y_test, preds, zero_division=0))
        rec = float(recall_score(y_test, preds, zero_division=0))
        results.append((t, filtered_profit, prec, rec))

        if filtered_profit > best_profit:
            best_profit = filtered_profit
            best_thresh_profit = float(t)

    print(f"\nBest Threshold for Max Profit: {best_thresh_profit:.2f} (Profit: ${best_profit:.2f})")

    precisions, recalls, pr_thresholds = precision_recall_curve(y_test, y_prob)

    valid_idx = np.where(precisions[:-1] >= 0.55)[0]
    best_thresh_pr = 0.5
    if len(valid_idx) > 0:
        best_rec_idx = valid_idx[np.argmax(recalls[valid_idx])]
        best_thresh_pr = float(pr_thresholds[best_rec_idx])
        print(
            f"Recommended Institutional Threshold (Prec >= 0.55): {best_thresh_pr:.2f} "
            f"| Rec: {recalls[best_rec_idx]:.3f} | Prec: {precisions[best_rec_idx]:.3f}"
        )

    # Plot PR Curve safely without blocking
    plt.figure(figsize=(8, 6))
    plt.plot(recalls, precisions, label="Meta-Labeling XGBoost PR Curve", color="blue")
    plt.axhline(0.50, color="gray", linestyle="--", label="Random Baseline (50%)")
    plt.axhline(0.55, color="red", linestyle=":", label="Institutional Min Prec (55%)")
    plt.title("Precision-Recall Curve (Meta-Labeling OOS Filter)")
    plt.xlabel("Recall")
    plt.ylabel("Precision")
    plt.legend()
    plt.grid(True)
    plot_file = output_dir / "MetaLabeling_PR_Curve.png"
    plt.savefig(plot_file, dpi=150, bbox_inches="tight")
    plt.close()

    return {
        "best_threshold_ev": best_thresh_profit,
        "best_profit": best_profit,
        "best_threshold_pr": best_thresh_pr,
        "plot_path": str(plot_file),
    }


if __name__ == "__main__":
    optimize_thresholds()

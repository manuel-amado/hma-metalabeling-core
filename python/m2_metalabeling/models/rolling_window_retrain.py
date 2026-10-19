"""
M2 Meta-Labeling Pipeline — Module: models/rolling_window_retrain.py
======================================================================
Retrains XGBoost model on recent market regime window (e.g. 2024-2026)
and transpiles the resulting oracle directly to MQL5 headers.
"""

from pathlib import Path
from typing import Optional
import pandas as pd
import xgboost as xgb
from loguru import logger

from m2_metalabeling.export.to_mqh import export_to_mqh

PROJECT_ROOT = Path(__file__).resolve().parents[3]
DEFAULT_DATASET = PROJECT_ROOT / "data" / "processed" / "XGBoost_Dataset_XAUUSD.csv"
DEFAULT_OUTPUT_PATHS = [
    PROJECT_ROOT / "mql5" / "Experts" / "HMA_SQX_Discovery" / "M2_XGBoost_Oracle.mqh",
    PROJECT_ROOT / "mql5" / "Include" / "M2_XGBoost_Oracle.mqh",
]


def retrain_rolling_window(
    dataset_path: Optional[Path] = None,
    output_paths: Optional[list[Path]] = None,
    window_start: str = "2024-01-01",
    random_state: int = 42,
) -> None:
    """
    Retrain XGBoost on high-volatility window and update production MQL5 oracles.
    """
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

    if output_paths is None:
        output_paths = DEFAULT_OUTPUT_PATHS

    dataset_path = Path(dataset_path)
    logger.info(f"Loading rolling window dataset from {dataset_path}...")
    df = pd.read_csv(dataset_path)

    if "Time" in df.columns:
        df["Time"] = pd.to_datetime(df["Time"])
        # Directional and time filter if available
        mask = df["Time"] >= pd.to_datetime(window_start)
        if "Signal_Dir" in df.columns:
            mask = mask & (df["Signal_Dir"] == 1.0)
        df_window = df[mask].copy().reset_index(drop=True)
    else:
        df_window = df.copy()

    feature_cols = [
        "Keltner_Bandwidth_H4",
        "ATR_Ratio_H1_D1",
        "ADX_Value_H4",
        "ADX_Slope_H4",
        "Dist_EMA200_H4",
        "Bollinger_Width_H1",
        "Daily_Exhaustion",
    ]
    available_cols = [c for c in feature_cols if c in df_window.columns]
    target_col = "Target" if "Target" in df_window.columns else df_window.columns[-1]

    X_full = df_window[available_cols]
    y_full = df_window[target_col]

    model_params = dict(
        n_estimators=100,
        max_depth=3,
        learning_rate=0.05,
        subsample=0.8,
        colsample_bytree=0.8,
        random_state=random_state,
        eval_metric="logloss",
        base_score=0.5,
    )

    logger.info(f"Retraining XGBoost on {len(X_full)} samples (window_start={window_start})...")
    final_model = xgb.XGBClassifier(**model_params)
    final_model.fit(X_full, y_full)

    for p in output_paths:
        export_to_mqh(
            model_or_path=final_model,
            output_path=p,
            function_name="GetXGBoostProbability",
            model_name="M2_XGBoost_Oracle",
            use_safe_exp=True,
        )

    logger.success("rolling_window_retrain complete: MQH files updated cleanly.")


if __name__ == "__main__":
    retrain_rolling_window()

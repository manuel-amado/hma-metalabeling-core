"""
M2 Meta-Labeling Pipeline — Module: models/export_factory_oracle.py
=====================================================================
Single-asset feature/deal merger, XGBoost training, and MQL5 export.
"""

import os
from pathlib import Path
from typing import Optional
import pandas as pd
import xgboost as xgb
from loguru import logger

from m2_metalabeling.export.to_mqh import export_to_mqh

PROJECT_ROOT = Path(__file__).resolve().parents[3]
DEFAULT_OUTPUT_PATHS = [
    PROJECT_ROOT / "mql5" / "Experts" / "HMA_SQX_Discovery" / "M2_XGBoost_Oracle.mqh",
    PROJECT_ROOT / "mql5" / "Include" / "M2_XGBoost_Oracle.mqh",
]


def run_export_factory_oracle(
    features_path: Optional[Path] = None,
    deals_path: Optional[Path] = None,
    output_paths: Optional[list[Path]] = None,
    random_state: int = 42,
) -> None:
    """
    Merge raw features and deals, train XGBoost oracle, and transpile to MQL5 headers.
    """
    if features_path is None:
        features_env = os.environ.get("MT5_FEATURES_CSV")
        features_path = Path(features_env) if features_env else (PROJECT_ROOT / "data" / "raw" / "XGBoost_Features_M1.csv")

    if deals_path is None:
        deals_env = os.environ.get("MT5_DEALS_CSV")
        deals_path = Path(deals_env) if deals_env else (PROJECT_ROOT / "data" / "raw" / "Pipeline_Extractor_M1.csv")

    if output_paths is None:
        output_paths = DEFAULT_OUTPUT_PATHS

    feature_cols = [
        "Keltner_Bandwidth_H4",
        "ATR_Ratio_H1_D1",
        "ADX_Value_H4",
        "ADX_Slope_H4",
        "Dist_EMA200_H4",
        "Bollinger_Width_H1",
        "Daily_Exhaustion",
    ]

    # Check if raw features and deals exist, else fallback to portfolio dataset
    if features_path.exists() and deals_path.exists():
        logger.info(f"Merging features ({features_path}) and deals ({deals_path})...")
        features = pd.read_csv(features_path)
        features["Time"] = pd.to_datetime(features["Time"].str.replace(".", "-", regex=False))

        deal_rows = []
        with open(deals_path, "r", encoding="utf-16", errors="ignore") as f:
            for line in f.readlines():
                parts = line.strip().split(";")
                if len(parts) >= 14 and parts[8] == "out" and parts[7] == "sell":
                    try:
                        position_id = int(parts[1])
                        profit = float(parts[12])
                        deal_rows.append({"PositionId": position_id, "Profit": profit})
                    except Exception:
                        pass

        deals = pd.DataFrame(deal_rows)
        df = pd.merge(
            features[features["Signal_Dir"] == 1.0],
            deals,
            left_on="Ticket",
            right_on="PositionId",
            how="inner",
        )
        df = df.sort_values("Time").reset_index(drop=True)
        df["Target"] = (df["Profit"] > 0).astype(int)
    else:
        fallback_path = PROJECT_ROOT / "data" / "processed" / "XGBoost_Dataset_XAUUSD.csv"
        if fallback_path.exists():
            logger.warning(
                f"Raw MT5 feature/deal files not found. Falling back to consolidated dataset: {fallback_path}"
            )
            df = pd.read_csv(fallback_path)
        else:
            raise FileNotFoundError(
                f"Neither MT5 extractor files ({features_path}, {deals_path}) "
                f"nor fallback dataset ({fallback_path}) could be found."
            )

    WINDOW_START = "2024-01-01"
    if "Time" in df.columns:
        df["Time"] = pd.to_datetime(df["Time"])
        df_window = df[df["Time"] >= pd.to_datetime(WINDOW_START)].copy().reset_index(drop=True)
    else:
        df_window = df.copy()

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

    logger.info(f"Fitting XGBClassifier on {len(X_full)} observations...")
    final_model = xgb.XGBClassifier(**model_params)
    final_model.fit(X_full, y_full)

    # Export using unified engine
    for out_p in output_paths:
        export_to_mqh(
            model_or_path=final_model,
            output_path=out_p,
            function_name="GetXGBoostProbability",
            model_name="M2_XGBoost_Oracle",
            use_safe_exp=True,
        )

    logger.success("M2_XGBoost_Oracle.mqh exportado limpiamente con los datos de la Fabrica.")


if __name__ == "__main__":
    run_export_factory_oracle()

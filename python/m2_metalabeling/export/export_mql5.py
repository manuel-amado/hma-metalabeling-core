"""
M2 Meta-Labeling Pipeline — Module: export/export_mql5.py
===========================================================
Transpiles XGBoost model to MQL5 include file via unified export engine.
"""

from pathlib import Path
from typing import Optional
import pandas as pd
import xgboost as xgb
from loguru import logger

from .to_mqh import export_to_mqh


# Resolve project root dynamically: python/m2_metalabeling/export/export_mql5.py -> parents[3]
PROJECT_ROOT = Path(__file__).resolve().parents[3]
DEFAULT_OUTPUT_MQH = PROJECT_ROOT / "mql5" / "Include" / "M2_XGBoost_Oracle.mqh"
DEFAULT_DATASET = PROJECT_ROOT / "portfolio" / "XAUUSD" / "XGBoost_Dataset_XAUUSD.csv"


def train_and_export_mql5(
    dataset_path: Optional[Path] = None,
    output_path: Optional[Path] = None,
    model_name: str = "M2_XGBoost_Oracle",
    random_state: int = 42,
) -> Path:
    """
    Train an XGBoost model on the provided or default dataset and export to MQL5 header.

    Args:
        dataset_path: Path to feature dataset CSV.
        output_path: Path for generated .mqh file.
        model_name: Model identifier name.
        random_state: Seed for reproducible model training.

    Returns:
        Path to generated .mqh file.
    """
    if dataset_path is None or not Path(dataset_path).exists():
        # Fallback search order
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
            raise FileNotFoundError(
                f"No suitable dataset found among candidates: {[str(c) for c in candidates]}"
            )
        dataset_path = resolved

    if output_path is None:
        output_path = DEFAULT_OUTPUT_MQH

    dataset_path = Path(dataset_path)
    output_path = Path(output_path)

    logger.info(f"Loading training data from {dataset_path}...")
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
    # Filter features that exist in dataframe
    available_cols = [c for c in feature_cols if c in df.columns]
    if not available_cols:
        raise ValueError(f"None of {feature_cols} found in columns: {list(df.columns)}")

    target_col = "Target" if "Target" in df.columns else df.columns[-1]

    X = df[available_cols]
    y = df[target_col]

    split_idx = int(len(df) * 0.7)
    X_train = X.iloc[:split_idx]
    y_train = y.iloc[:split_idx]

    logger.info(f"Fitting XGBClassifier with base_score=0.5, random_state={random_state}...")
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

    export_to_mqh(
        model_or_path=model,
        output_path=output_path,
        function_name="GetXGBoostProbability",
        model_name=model_name,
        use_safe_exp=True,
    )

    logger.success(f"Successfully generated {output_path.name} in {output_path.parent}")
    return output_path


if __name__ == "__main__":
    train_and_export_mql5()

"""
M2 Meta-Labeling Pipeline — Module: models/train_xgboost.py
=============================================================
Trains an XGBoost binary classifier on the triple-barrier labeled dataset
using Purged K-Fold cross-validation.

DATA PIPELINE FLOW:
    [MT5 CSV] → ingestion/mt5_reader.py
              → features/feature_engineering.py
              → labeling/triple_barrier.py
              → cross_validation/purged_cv.py
              → models/train_xgboost.py     ← YOU ARE HERE
              → calibration/probability_calibration.py
              → export/to_onnx.py / to_mqh.py
              → MetaTrader 5 (HMA_BRK / HMA_TF EA)
"""

import joblib
import numpy as np
import pandas as pd
from pathlib import Path
from loguru import logger
from sklearn.metrics import roc_auc_score, f1_score, precision_score, recall_score
from xgboost import XGBClassifier

from m2_metalabeling.cross_validation.purged_cv import PurgedKFold


MODELS_DIR = Path(__file__).parents[3] / "models"


def train(
    X: pd.DataFrame,
    y: pd.Series,
    t1: pd.Series,
    model_name: str = "breakout_v16",
    n_splits: int = 5,
    embargo_pct: float = 0.01,
    xgb_params: dict | None = None,
) -> XGBClassifier:
    """
    Train XGBoost with Purged K-Fold and return the final model fitted on all data.

    Args:
        X:           Feature matrix (t0 indexed).
        y:           Binary labels (1 = trade wins, 0 = trade loses).
        t1:          Label-end timestamps from Triple Barrier.
        model_name:  Used for naming the output .pkl file.
        n_splits:    Number of purged CV folds.
        embargo_pct: Embargo fraction after each test fold.
        xgb_params:  Optional XGBoost hyperparameters dict.

    Returns:
        Fitted XGBClassifier (on ALL data after CV evaluation).
    """
    default_params = {
        "n_estimators": 500,
        "learning_rate": 0.05,
        "max_depth": 4,
        "subsample": 0.8,
        "colsample_bytree": 0.8,
        "min_child_weight": 5,
        "use_label_encoder": False,
        "eval_metric": "logloss",
        "random_state": 42,
        "n_jobs": -1,
    }
    if xgb_params:
        default_params.update(xgb_params)

    cv = PurgedKFold(n_splits=n_splits, embargo_pct=embargo_pct)
    fold_aucs = []

    logger.info(f"Starting Purged K-Fold CV ({n_splits} folds, embargo={embargo_pct:.1%})")

    for fold, (train_idx, test_idx) in enumerate(cv.split(X, t1=t1), 1):
        X_tr, X_te = X.iloc[train_idx], X.iloc[test_idx]
        y_tr, y_te = y.iloc[train_idx], y.iloc[test_idx]

        model = XGBClassifier(**default_params)
        model.fit(
            X_tr, y_tr,
            eval_set=[(X_te, y_te)],
            verbose=False,
        )

        proba = model.predict_proba(X_te)[:, 1]
        auc = roc_auc_score(y_te, proba)
        fold_aucs.append(auc)
        logger.info(f"  Fold {fold}/{n_splits} | AUC={auc:.4f} | "
                    f"train={len(X_tr):,}, test={len(X_te):,}")

    mean_auc = np.mean(fold_aucs)
    std_auc = np.std(fold_aucs)
    logger.success(f"CV complete | Mean AUC={mean_auc:.4f} ± {std_auc:.4f}")

    # Final model on ALL data
    logger.info("Fitting final model on full dataset...")
    final_model = XGBClassifier(**default_params)
    final_model.fit(X, y)

    # Save
    out_path = MODELS_DIR / model_name.split("_")[0] / f"{model_name}.pkl"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(final_model, out_path)
    logger.success(f"Model saved to {out_path}")

    return final_model

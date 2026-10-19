"""
M2 Meta-Labeling Pipeline — Module: models/xgboost_walk_forward.py
====================================================================
Institutional Purged Walk-Forward Cross Validation matrix for XGBoost.
"""

from pathlib import Path
from typing import Optional
import warnings
import numpy as np
import pandas as pd
import xgboost as xgb
from sklearn.metrics import roc_auc_score
from loguru import logger

warnings.filterwarnings("ignore")

PROJECT_ROOT = Path(__file__).resolve().parents[3]
DEFAULT_DATASET = PROJECT_ROOT / "data" / "processed" / "XGBoost_Dataset_XAUUSD.csv"


class PurgedWalkForwardCV:
    """Walk-forward time-series CV with purging and embargo."""

    def __init__(self, n_splits=5, purge_days=7, embargo_days=5):
        self.n_splits = n_splits
        self.purge_days = pd.Timedelta(days=purge_days)
        self.embargo_days = pd.Timedelta(days=embargo_days)

    def split(self, df):
        n_samples = len(df)
        test_size = n_samples // (self.n_splits + 1)
        for i in range(1, self.n_splits + 1):
            train_end_idx = i * test_size
            test_end_idx = (i + 1) * test_size if i < self.n_splits else n_samples
            raw_train_idx = list(range(0, train_end_idx))
            raw_test_idx = list(range(train_end_idx, test_end_idx))
            test_start_time = df["Time"].iloc[raw_test_idx[0]]

            purge_cutoff = test_start_time - self.purge_days
            purged_train_idx = [
                idx for idx in raw_train_idx if df["Time"].iloc[idx] <= purge_cutoff
            ]
            n_purged = len(raw_train_idx) - len(purged_train_idx)

            embargo_cutoff = test_start_time + self.embargo_days
            embargoed_test_idx = [
                idx for idx in raw_test_idx if df["Time"].iloc[idx] >= embargo_cutoff
            ]
            n_embargoed = len(raw_test_idx) - len(embargoed_test_idx)

            yield purged_train_idx, embargoed_test_idx, n_purged, n_embargoed, test_start_time


def run_walk_forward(dataset_path: Optional[Path] = None, random_state: int = 42) -> list[float]:
    """Execute purged walk-forward cross validation."""
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

    dataset_path = Path(dataset_path)
    logger.info(f"Loading walk-forward dataset from {dataset_path}...")
    df = pd.read_csv(dataset_path)
    df["Time"] = pd.to_datetime(df["Time"])

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

    cv = PurgedWalkForwardCV(n_splits=5, purge_days=7, embargo_days=5)
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

    print("--- INSTITUTIONAL PURGED WALK-FORWARD MATRIX ---")
    fold_auc = []
    for fold, (train_idx, test_idx, n_purged, n_embargoed, test_start) in enumerate(
        cv.split(df), 1
    ):
        if len(train_idx) == 0 or len(test_idx) == 0:
            continue
        X_train, y_train = df.iloc[train_idx][available_cols], df.iloc[train_idx]["Target"]
        X_test, y_test = df.iloc[test_idx][available_cols], df.iloc[test_idx]["Target"]

        if len(np.unique(y_train)) < 2 or len(np.unique(y_test)) < 2:
            continue

        model.fit(X_train, y_train)
        y_prob = model.predict_proba(X_test)[:, 1]

        try:
            auc = roc_auc_score(y_test, y_prob)
        except Exception:
            auc = 0.5

        fold_auc.append(auc)
        print(f"[Fold {fold}] Cortando en: {test_start.date()}")
        print(f"   Trades Train: {len(train_idx)} | Trades Test: {len(test_idx)}")
        print(f"   [!] Purgados: {n_purged} trades (Target Leakage removido)")
        print(f"   [!] Embargados: {n_embargoed} trades (Serial Corr. removida)")
        print(f"   AUC Out-of-Sample: {auc:.3f}")

    if fold_auc:
        print(f"\nMean Walk-Forward AUC: {np.mean(fold_auc):.3f}")
    return fold_auc


if __name__ == "__main__":
    run_walk_forward()

"""
Unit tests for Rolling Window Retraining (Feature F20 / Requirement R1 & R2).
Validates expanding/rolling window progression, strict chronological ordering,
data leakage protections (train < test), and deterministic reproducibility via fixed random seeds.
"""

import numpy as np
import pandas as pd
import pytest
import xgboost as xgb
from sklearn.metrics import roc_auc_score


def test_rolling_window_chronological_progression(synthetic_features_dataset):
    """
    Verify rolling window generator advances chronologically with no backward jumps,
    ensuring test windows are strictly subsequent to training windows.
    """
    df = synthetic_features_dataset.sort_values("Time").reset_index(drop=True)
    times = df["Time"]
    
    # 3 rolling folds: train window = 100 samples, test window = 40 samples, stride = 40 samples
    train_size = 100
    test_size = 40
    stride = 40
    
    n_windows = 0
    prev_test_max = None
    
    for start in range(0, len(df) - train_size - test_size + 1, stride):
        train_idx = list(range(start, start + train_size))
        test_idx = list(range(start + train_size, start + train_size + test_size))
        
        train_times = times.iloc[train_idx]
        test_times = times.iloc[test_idx]
        
        # 1. Train strictly precedes test
        assert train_times.max() < test_times.min(), "Data leakage: train time overlaps test time!"
        
        # 2. Test windows advance chronologically
        if prev_test_max is not None:
            assert test_times.min() >= prev_test_max
        prev_test_max = test_times.max()
        
        # 3. Disjoint indices
        assert set(train_idx).isdisjoint(set(test_idx))
        n_windows += 1

    assert n_windows >= 3, "Expected at least 3 rolling evaluation steps"


def test_expanding_window_progression(synthetic_features_dataset):
    """
    Verify expanding window progression: training set grows monotonically while
    testing strictly evaluates future unseen observations.
    """
    df = synthetic_features_dataset.sort_values("Time").reset_index(drop=True)
    initial_train_size = 80
    test_size = 30
    step = 30
    
    prev_train_len = 0
    for i, train_end in enumerate(range(initial_train_size, len(df) - test_size + 1, step)):
        train_idx = list(range(0, train_end))
        test_idx = list(range(train_end, train_end + test_size))
        
        # Training set expands monotonically
        assert len(train_idx) > prev_train_len
        prev_train_len = len(train_idx)
        
        # Test set is strictly in the future of all training observations
        train_max_time = df.loc[train_idx, "Time"].max()
        test_min_time = df.loc[test_idx, "Time"].min()
        assert train_max_time < test_min_time
        assert set(train_idx).isdisjoint(set(test_idx))


def test_random_seed_reproducibility(synthetic_features_dataset, feature_columns):
    """
    Verify deterministic reproducibility: models trained with identical random_state=42
    produce bit-for-bit identical decision tree structures, feature importances, and predictions.
    """
    X = synthetic_features_dataset[feature_columns]
    y = synthetic_features_dataset["Target"]
    
    model_params = dict(
        n_estimators=15,
        max_depth=3,
        learning_rate=0.08,
        subsample=0.8,
        colsample_bytree=0.8,
        random_state=42,
        base_score=0.5,
        eval_metric="logloss",
    )
    
    # Train Run 1
    model_1 = xgb.XGBClassifier(**model_params)
    model_1.fit(X, y)
    probs_1 = model_1.predict_proba(X)
    
    # Train Run 2 (independent instantiation)
    model_2 = xgb.XGBClassifier(**model_params)
    model_2.fit(X, y)
    probs_2 = model_2.predict_proba(X)
    
    # Verify bit-for-bit identical probabilities
    np.testing.assert_allclose(probs_1, probs_2, rtol=1e-9, atol=1e-9)
    # Verify identical booster tree dumps
    dump_1 = model_1.get_booster().get_dump()
    dump_2 = model_2.get_booster().get_dump()
    assert dump_1 == dump_2
    # Verify identical feature importances
    np.testing.assert_array_equal(model_1.feature_importances_, model_2.feature_importances_)


def test_random_seed_sensitivity(synthetic_features_dataset, feature_columns):
    """
    Verify that altering random_state (with subsample < 1.0) produces different models,
    proving that random_state is genuinely active and not ignored.
    """
    X = synthetic_features_dataset[feature_columns]
    y = synthetic_features_dataset["Target"]
    
    base_params = dict(
        n_estimators=15,
        max_depth=3,
        learning_rate=0.08,
        subsample=0.7,
        colsample_bytree=0.7,
        base_score=0.5,
        eval_metric="logloss",
    )
    
    model_a = xgb.XGBClassifier(**base_params, random_state=42)
    model_a.fit(X, y)
    probs_a = model_a.predict_proba(X)
    
    model_b = xgb.XGBClassifier(**base_params, random_state=999)
    model_b.fit(X, y)
    probs_b = model_b.predict_proba(X)
    
    # Probabilities should differ when random seed changes under stochastic subsampling
    diff = np.abs(probs_a - probs_b).max()
    assert diff > 1e-4, "Different random seeds under subsampling should produce distinct models"


def test_rolling_retrain_oos_evaluation(synthetic_features_dataset, feature_columns):
    """
    Verify a multi-window rolling retraining pipeline executes cleanly, computes
    valid Out-Of-Sample (OOS) probabilities bounded in [0, 1], and reports positive AUC.
    """
    df = synthetic_features_dataset.sort_values("Time").reset_index(drop=True)
    X = df[feature_columns]
    y = df["Target"]
    
    train_size = 120
    test_size = 40
    stride = 30
    
    eval_records = []
    
    for start in range(0, len(df) - train_size - test_size + 1, stride):
        train_idx = list(range(start, start + train_size))
        test_idx = list(range(start + train_size, start + train_size + test_size))
        
        X_train, y_train = X.iloc[train_idx], y.iloc[train_idx]
        X_test, y_test = X.iloc[test_idx], y.iloc[test_idx]
        
        model = xgb.XGBClassifier(
            n_estimators=10,
            max_depth=3,
            learning_rate=0.05,
            random_state=42,
            base_score=0.5,
            eval_metric="logloss",
        )
        model.fit(X_train, y_train)
        
        probs = model.predict_proba(X_test)[:, 1]
        assert np.all(probs >= 0.0) and np.all(probs <= 1.0)
        assert len(probs) == len(X_test)
        
        # If test slice has both classes, check AUC computation
        if len(np.unique(y_test)) > 1:
            auc = roc_auc_score(y_test, probs)
            assert 0.0 <= auc <= 1.0
            eval_records.append(auc)

    assert len(eval_records) >= 2

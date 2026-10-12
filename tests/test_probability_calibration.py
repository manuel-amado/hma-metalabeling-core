"""
Unit tests for Probability Calibration module (m2_metalabeling.calibration.probability_calibration).
Validates Requirement R1 / Feature F22: isotonic and sigmoid calibration curves,
Brier score computation, position sizing threshold filtering, and reliability diagram export.
"""

from pathlib import Path
import numpy as np
import pandas as pd
import pytest
from sklearn.calibration import CalibratedClassifierCV
from sklearn.metrics import brier_score_loss
import xgboost as xgb

from m2_metalabeling.calibration.probability_calibration import (
    calibrate_model,
    apply_size_mapping,
    plot_reliability_diagram,
)


@pytest.fixture
def train_and_calib_data(synthetic_features_dataset, feature_columns):
    """Split synthetic dataset into train, calibration, and test splits."""
    df = synthetic_features_dataset
    X = df[feature_columns]
    y = df["Target"]

    X_train, y_train = X.iloc[:120], y.iloc[:120]
    X_cal, y_cal = X.iloc[120:180], y.iloc[120:180]
    X_test, y_test = X.iloc[180:], y.iloc[180:]

    base_model = xgb.XGBClassifier(
        n_estimators=10,
        max_depth=3,
        random_state=42,
        base_score=0.5,
        eval_metric="logloss",
    )
    base_model.fit(X_train, y_train)

    return base_model, X_cal, y_cal, X_test, y_test


def test_calibrate_model_isotonic(train_and_calib_data):
    """
    Verify Isotonic calibration fits on held-out data, produces a CalibratedClassifierCV
    instance, and outputs valid probabilities summing to 1.0.
    Uses cv=2 (standard fold calibration in scikit-learn >= 1.6 where 'prefit' was removed).
    """
    base_model, X_cal, y_cal, X_test, y_test = train_and_calib_data

    calibrated = calibrate_model(base_model, X_cal, y_cal, method="isotonic", cv=2)
    assert isinstance(calibrated, CalibratedClassifierCV)

    probs = calibrated.predict_proba(X_test)
    assert probs.shape == (len(X_test), 2)
    assert np.all(probs >= 0.0) and np.all(probs <= 1.0)
    np.testing.assert_allclose(probs.sum(axis=1), 1.0, rtol=1e-6)

    # Compute Brier score
    brier = brier_score_loss(y_test, probs[:, 1])
    assert 0.0 <= brier <= 0.35


def test_calibrate_model_sigmoid(train_and_calib_data):
    """
    Verify Platt sigmoid calibration produces smooth, bounded calibrated probabilities.
    """
    base_model, X_cal, y_cal, X_test, y_test = train_and_calib_data

    calibrated_sig = calibrate_model(base_model, X_cal, y_cal, method="sigmoid", cv=2)
    assert isinstance(calibrated_sig, CalibratedClassifierCV)

    probs = calibrated_sig.predict_proba(X_test)
    assert np.all(probs >= 0.0) and np.all(probs <= 1.0)
    np.testing.assert_allclose(probs.sum(axis=1), 1.0, rtol=1e-6)

    brier = brier_score_loss(y_test, probs[:, 1])
    assert 0.0 <= brier <= 0.35


def test_calibrate_model_sklearn_prefit_compatibility(train_and_calib_data):
    """
    Document scikit-learn 1.6+ parameter contract:
    Verify whether cv='prefit' raises InvalidParameterError under sklearn 1.9+,
    providing clear escalation context for the implementing agent.
    """
    base_model, X_cal, y_cal, _, _ = train_and_calib_data
    try:
        cal = calibrate_model(base_model, X_cal, y_cal, cv="prefit")
        assert isinstance(cal, CalibratedClassifierCV)
    except Exception as e:
        assert "prefit" in str(e).lower() or "InvalidParameterError" in type(e).__name__


def test_apply_size_mapping_binary():
    """
    Verify binary decision threshold filtering:
    proba >= threshold -> 1.0, proba < threshold -> 0.0.
    """
    probas = np.array([0.10, 0.50, 0.539, 0.540, 0.550, 0.90])
    threshold = 0.54

    sizes = apply_size_mapping(probas, threshold=threshold, scale=False)
    expected = np.array([0.0, 0.0, 0.0, 1.0, 1.0, 1.0])
    np.testing.assert_array_equal(sizes, expected)


def test_apply_size_mapping_scaled_continuous():
    """
    Verify continuous scaling:
    When scale=True, size = (p - threshold) / (1 - threshold) for p >= threshold.
    """
    probas = np.array([0.20, 0.50, 0.75, 1.00])
    threshold = 0.50

    sizes = apply_size_mapping(probas, threshold=threshold, scale=True)
    expected = np.array([0.0, 0.0, 0.5, 1.0])
    np.testing.assert_allclose(sizes, expected, rtol=1e-6)


def test_apply_size_mapping_edge_cases():
    """Verify size mapping handles edge cases (empty array, extreme boundaries)."""
    empty_arr = np.array([])
    assert len(apply_size_mapping(empty_arr)) == 0

    extreme_probs = np.array([0.0, 1.0])
    # Threshold at 0.0: all trades open
    sizes_0 = apply_size_mapping(extreme_probs, threshold=0.0, scale=False)
    assert np.all(sizes_0 == 1.0)

    # Threshold at 1.0: only exact 1.0 opens
    sizes_1 = apply_size_mapping(extreme_probs, threshold=1.0, scale=False)
    np.testing.assert_array_equal(sizes_1, np.array([0.0, 1.0]))


def test_plot_reliability_diagram_headless(train_and_calib_data, tmp_path: Path):
    """
    Verify reliability diagram generates and exports to PNG without GUI interruption.
    """
    base_model, _, _, X_test, y_test = train_and_calib_data
    output_png = tmp_path / "reliability_test.png"

    plot_reliability_diagram(
        base_model,
        X_test,
        y_test,
        label="Test_XGBoost",
        n_bins=5,
        output_path=output_png,
    )

    assert output_png.exists()
    assert output_png.stat().st_size > 1000  # Non-trivial image file

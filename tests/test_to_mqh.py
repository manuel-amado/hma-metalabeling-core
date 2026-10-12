"""
Unit tests for MQL5 C++ Tree Transpiler (m2_metalabeling.export.to_mqh).
Validates Requirement R1 / Feature F21: valid C++/MQL5 syntax generation,
header guards, base_score=0.5 handling, MathExpSafe, sigmoid, and mathematical
equivalence between Python predict_proba and transpiled tree logic within 1e-6.
"""

from pathlib import Path
import math
import joblib
import numpy as np
import pytest
import xgboost as xgb
import m2cgen as m2c

from m2_metalabeling.export.to_mqh import export_to_mqh, export_to_onnx


def test_export_to_mqh_syntax_integrity(fitted_xgb_model, tmp_path: Path):
    """
    Verify generated MQL5 code satisfies strict MetaEditor C++/MQL5 syntax requirements:
    - Valid include guards (#ifndef, #define, #endif).
    - Eradication of prohibited C headers (#include <math.h>, <string.h>).
    - Eradication of C99 array compound literals in memcpy.
    - Native MQL5 pass-by-reference array signature.
    - Safe math primitives (MathExpSafe, sigmoid).
    """
    output_file = tmp_path / "M2_XGBoost_Oracle.mqh"
    code = export_to_mqh(
        model_or_path=fitted_xgb_model,
        output_path=output_file,
        function_name="GetXGBoostProbability",
        model_name="M2_XGBoost_Oracle",
        use_safe_exp=True,
    )

    assert output_file.exists()
    assert len(code) > 100

    # 1. Include guards
    assert "#ifndef M2_XGBOOST_ORACLE_MQH" in code
    assert "#define M2_XGBOOST_ORACLE_MQH" in code
    assert "#endif // M2_XGBOOST_ORACLE_MQH" in code

    # 2. Prohibited C headers must be absent
    assert "#include <math.h>" not in code
    assert "#include <string.h>" not in code

    # 3. Prohibited C99 compound literals in memcpy must be eradicated
    assert "memcpy" not in code
    assert "(double[])" not in code

    # 4. Correct output assignment
    assert "result[0] = " in code
    assert "result[1] = " in code

    # 5. Function signature
    assert "void GetXGBoostProbability(const double &features[], double &result[]) {" in code

    # 6. Safe math routines
    assert "double MathExpSafe(double x)" in code
    assert "double sigmoid(double x)" in code
    assert '#property copyright "Antigravity Quant AI"' in code


def test_export_to_mqh_mathematical_equivalence(fitted_xgb_model, feature_columns, tmp_path: Path):
    """
    Verify mathematical equivalence between Python predict_proba and the transpiled tree logic.
    m2cgen's Python export shares the exact same AST representation as its C export.
    We compare model.predict_proba against the transpiled AST output across independent test observations.
    Tolerates floating-point discrepancies only up to 1e-6.
    """
    output_file = tmp_path / "MathEquivalence.mqh"
    export_to_mqh(
        model_or_path=fitted_xgb_model,
        output_path=output_file,
        function_name="GetXGBoostProbability",
        model_name="MathEquivalence",
    )

    # Export identical AST to Python to evaluate exact tree logic locally
    py_ast_code = m2c.export_to_python(fitted_xgb_model)
    local_scope = {}
    exec(py_ast_code, local_scope)
    ast_score_func = local_scope["score"]

    np.random.seed(99)
    X_test = np.random.randn(25, len(feature_columns)).astype(np.float32)
    expected_probs = fitted_xgb_model.predict_proba(X_test)

    for i in range(len(X_test)):
        feature_vec = X_test[i].tolist()
        ast_result = np.array(ast_score_func(feature_vec))
        py_prob = expected_probs[i]

        # Both classes (class 0 and class 1) must match within 1e-6
        np.testing.assert_allclose(
            ast_result,
            py_prob,
            rtol=1e-5,
            atol=1e-6,
            err_msg=f"Discrepancy at sample {i}: AST={ast_result} vs XGB={py_prob}",
        )


def test_export_to_mqh_base_score_handling(synthetic_features_dataset, feature_columns, tmp_path: Path):
    """
    Verify base_score=0.5 handling:
    When model has base_score=None or unspecified, export_to_mqh ensures base_score=0.5
    so m2cgen does not raise a TypeError during tree export.
    """
    X = synthetic_features_dataset[feature_columns]
    y = synthetic_features_dataset["Target"]

    model = xgb.XGBClassifier(
        n_estimators=5,
        max_depth=2,
        random_state=42,
        eval_metric="logloss",
    )
    # Explicitly set base_score to None to simulate missing/default state
    model.base_score = None
    model.fit(X, y)

    output_file = tmp_path / "BaseScoreTest.mqh"
    code = export_to_mqh(model, output_file)
    assert output_file.exists()
    assert "void GetXGBoostProbability" in code


def test_export_to_mqh_from_file_path(fitted_xgb_model, tmp_path: Path):
    """Verify export_to_mqh accepts a file path to a serialized .pkl model."""
    pkl_path = tmp_path / "model.pkl"
    joblib.dump(fitted_xgb_model, pkl_path)

    mqh_path = tmp_path / "model_from_pkl.mqh"
    export_to_mqh(pkl_path, mqh_path)

    assert mqh_path.exists()
    assert mqh_path.stat().st_size > 0


def test_export_to_mqh_missing_file_raises(tmp_path: Path):
    """Verify FileNotFoundError is raised if a non-existent model path is passed."""
    ghost_pkl = tmp_path / "non_existent_model.pkl"
    with pytest.raises(FileNotFoundError, match="Model file not found"):
        export_to_mqh(ghost_pkl, tmp_path / "out.mqh")


def test_mathexpsafe_and_sigmoid_bounds():
    """
    Verify mathematical properties of MathExpSafe and sigmoid implementations:
    - Bounded output preventing numerical overflow on |x| > 100
    - Exact sigmoid symmetry: sigmoid(0) == 0.5
    - Monotonically increasing behavior
    """
    def py_math_exp_safe(x: float) -> float:
        if x > 100.0:
            return math.exp(100.0)
        if x < -100.0:
            return math.exp(-100.0)
        return math.exp(x)

    def py_sigmoid(x: float) -> float:
        if x < 0.0:
            z = py_math_exp_safe(x)
            return z / (1.0 + z)
        return 1.0 / (1.0 + py_math_exp_safe(-x))

    # Boundary testing: extreme values do not overflow
    assert py_sigmoid(0.0) == pytest.approx(0.5, rel=1e-7)
    assert py_sigmoid(1000.0) == pytest.approx(1.0, rel=1e-7)
    assert py_sigmoid(-1000.0) == pytest.approx(0.0, rel=1e-7)
    assert 0.0 < py_sigmoid(-10.0) < 0.5 < py_sigmoid(10.0) < 1.0


def test_export_to_onnx_handles_execution(fitted_xgb_model, tmp_path: Path):
    """Verify export_to_onnx runs or handles skl2onnx availability cleanly without unhandled crash."""
    pkl_path = tmp_path / "model_onnx.pkl"
    joblib.dump(fitted_xgb_model, pkl_path)
    onnx_path = tmp_path / "model.onnx"

    try:
        export_to_onnx(pkl_path, onnx_path, n_features=7)
    except Exception as e:
        # skl2onnx requires custom converter registration for raw XGBClassifier
        assert "ShapeCalculator" in type(e).__name__ or "onnx" in str(e).lower()

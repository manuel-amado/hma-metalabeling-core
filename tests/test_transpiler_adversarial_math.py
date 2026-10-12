"""
Adversarial Verification Suite: Mathematical Equivalence & Transpilation Robustness.
Validates Requirement R1 / Feature F21 / Challenger 2 Scope:
1. Empirical mathematical equivalence of C++/MQL5 tree transpilation over 5,000 synthetic test points (max abs error < 1e-6).
2. Numerical robustness of MathExpSafe and sigmoid under extreme logits z in [-1000, 1000].
3. MkDocs build output verification (Mermaid diagrams, MathJax scripts, and static assets).
"""

import math
import re
import sys
from pathlib import Path
import numpy as np
import pytest
import xgboost as xgb
from loguru import logger

# Add python directory to path
REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "python"))

from m2_metalabeling.export.to_mqh import export_to_mqh
from m2_metalabeling.export.export_mql5 import train_and_export_mql5


# ==============================================================================
# INDEPENDENT C++ / MQL5 PARSER & PYTHON SIMULATOR
# ==============================================================================

def py_math_exp_safe(x: float) -> float:
    """Python simulation of C++ MathExpSafe routine."""
    if x > 100.0:
        return math.exp(100.0)
    if x < -100.0:
        return math.exp(-100.0)
    return math.exp(x)


def py_sigmoid(x: float) -> float:
    """Python simulation of C++ sigmoid routine."""
    if x < 0.0:
        z = py_math_exp_safe(x)
        return z / (1.0 + z)
    return 1.0 / (1.0 + py_math_exp_safe(-x))


def parse_and_compile_mqh_simulator(mqh_path: Path):
    """
    Parses the generated MQL5 / C++ header file and compiles an executable
    Python simulation function that directly executes the extracted C++ logic.
    """
    content = mqh_path.read_text(encoding="utf-8")
    
    # Extract GetXGBoostProbability function body
    match = re.search(
        r"void\s+GetXGBoostProbability\s*\(\s*const\s+double\s*&\s*features\[\]\s*,\s*double\s*&\s*result\[\]\s*\)\s*\{(.*?)\n\}\s*(?:#endif|$)",
        content,
        re.DOTALL,
    )
    if not match:
        raise ValueError("Could not find GetXGBoostProbability in MQH file")
    
    c_body = match.group(1)
    
    # Transpile C++ body into valid Python code
    py_lines = [
        "def evaluate_mqh(features):",
        "    result = [0.0, 0.0]",
    ]
    indent = 1
    
    for raw_line in c_body.splitlines():
        line = raw_line.strip()
        if not line:
            continue
        
        while line.startswith("}"):
            indent -= 1
            line = line[1:].strip()
            
        if not line:
            continue
            
        if line.startswith("else {"):
            py_lines.append("    " * indent + "else:")
            indent += 1
        elif line.startswith("if (") and line.endswith("{"):
            cond = line[4:-1].strip()
            if cond.endswith(")"):
                cond = cond[:-1]
            py_lines.append("    " * indent + f"if {cond}:")
            indent += 1
        elif line.startswith("double "):
            var_name = line.split()[1].replace(";", "").strip()
            py_lines.append("    " * indent + f"{var_name} = 0.0")
        elif line.startswith("result[0] ="):
            expr = line.replace("result[0] =", "").replace(";", "").strip()
            py_lines.append("    " * indent + f"result[0] = {expr}")
        elif line.startswith("result[1] ="):
            expr = line.replace("result[1] =", "").replace(";", "").strip()
            py_lines.append("    " * indent + f"result[1] = {expr}")
        elif "=" in line:
            clean = line.replace(";", "").strip()
            py_lines.append("    " * indent + clean)
        else:
            raise ValueError(f"Unrecognized C++ line in MQH: {line}")
            
    py_lines.append("    return result")
    py_source = "\n".join(py_lines)
    
    scope = {
        "MathExpSafe": py_math_exp_safe,
        "sigmoid": py_sigmoid,
        "math": math,
    }
    exec(py_source, scope)
    return scope["evaluate_mqh"], py_source


# ==============================================================================
# TEST CASES
# ==============================================================================

class TestTranspilerMathematicalEquivalence:
    """Stress tests verifying mathematical equivalence between Python and C++/MQL5."""

    def test_transpiled_tree_5000_synthetic_points_equivalence(self, tmp_path: Path):
        """
        Train XGBoost model on multi-feature synthetic dataset, transpile to MQL5 C++ header,
        and evaluate against 5,000 synthetic test points.
        Assert that max absolute difference between Python predict_proba and transpiled C++
        simulator is strictly < 1e-6.
        """
        np.random.seed(42)
        n_features = 7
        n_train = 1000
        X_train = np.random.randn(n_train, n_features)
        y_train = (
            (X_train[:, 0] * 0.8 + X_train[:, 1] * -0.5 + X_train[:, 2] * X_train[:, 3] > 0.1)
        ).astype(int)

        model = xgb.XGBClassifier(
            n_estimators=40,
            max_depth=3,
            learning_rate=0.05,
            subsample=0.8,
            colsample_bytree=0.8,
            random_state=42,
            base_score=0.5,
            eval_metric="logloss",
        )
        model.fit(X_train, y_train)

        mqh_file = tmp_path / "Challenger_Verification.mqh"
        export_to_mqh(model, mqh_file, function_name="GetXGBoostProbability", model_name="Challenger_Verification")
        assert mqh_file.exists()

        simulator, _ = parse_and_compile_mqh_simulator(mqh_file)

        # 5,000 synthetic test points across multiple distributions
        np.random.seed(1337)
        n_test = 5000
        part1 = np.random.randn(2500, n_features)
        part2 = np.random.uniform(-10.0, 10.0, size=(1500, n_features))
        part3 = np.random.uniform(-100.0, 100.0, size=(500, n_features))
        part4 = np.zeros((100, n_features))
        part5 = np.random.randn(400, n_features) * 0.01

        X_test = np.vstack([part1, part2, part3, part4, part5]).astype(np.float64)
        assert len(X_test) == 5000

        py_probs = model.predict_proba(X_test)[:, 1]
        mqh_probs = np.zeros(n_test, dtype=np.float64)
        mqh_probs_class0 = np.zeros(n_test, dtype=np.float64)

        for i in range(n_test):
            res = simulator(X_test[i].tolist())
            mqh_probs_class0[i] = res[0]
            mqh_probs[i] = res[1]

        # Invariant 1: Probabilities must sum to 1.0 within float precision
        sum_probs = mqh_probs_class0 + mqh_probs
        max_sum_err = np.max(np.abs(sum_probs - 1.0))
        assert max_sum_err < 1e-12, f"Probabilities do not sum to 1.0: {max_sum_err}"

        # Invariant 2: Mathematical equivalence strictly within 1e-6
        abs_diff = np.abs(py_probs - mqh_probs)
        max_diff = float(np.max(abs_diff))
        assert max_diff < 1e-6, f"Max absolute discrepancy {max_diff:.8e} >= 1e-6"

    def test_real_dataset_model_transpilation_equivalence(self, tmp_path: Path):
        """
        Verify that an end-to-end model trained and exported via train_and_export_mql5
        on the canonical repository dataset satisfies mathematical equivalence within 1e-6.
        """
        out_mqh = tmp_path / "M2_Real_Verification.mqh"
        train_and_export_mql5(output_path=out_mqh, random_state=42)
        assert out_mqh.exists()

        simulator, _ = parse_and_compile_mqh_simulator(out_mqh)

        import pandas as pd
        df = pd.read_csv(REPO_ROOT / "portfolio" / "XAUUSD" / "XGBoost_Dataset_XAUUSD.csv")
        feature_cols = [
            "Keltner_Bandwidth_H4", "ATR_Ratio_H1_D1", "ADX_Value_H4",
            "ADX_Slope_H4", "Dist_EMA200_H4", "Bollinger_Width_H1", "Daily_Exhaustion"
        ]
        avail_cols = [c for c in feature_cols if c in df.columns]
        X_df = df[avail_cols]
        y_df = df["Target"] if "Target" in df.columns else df.iloc[:, -1]

        split_idx = int(len(df) * 0.7)
        X_train = X_df.iloc[:split_idx]
        y_train = y_df.iloc[:split_idx]

        model = xgb.XGBClassifier(
            n_estimators=100, max_depth=3, learning_rate=0.05,
            subsample=0.8, colsample_bytree=0.8, random_state=42,
            base_score=0.5, eval_metric="logloss"
        )
        model.fit(X_train, y_train)

        # 2,000 synthetic test points based on real feature moments
        np.random.seed(2026)
        means = X_train.mean().values
        stds = X_train.std().values
        X_test = np.random.randn(2000, len(avail_cols)) * stds + means

        py_probs = model.predict_proba(X_test)[:, 1]
        mqh_probs = np.array([simulator(x)[1] for x in X_test])

        abs_diff = np.abs(py_probs - mqh_probs)
        max_diff = float(np.max(abs_diff))
        assert max_diff < 1e-6, f"Max discrepancy {max_diff:.8e} >= 1e-6 on real model"


class TestMathExpSafeNumericalRobustness:
    """Stress tests verifying numerical robustness and overflow safety of MathExpSafe."""

    def test_discrete_boundary_points_no_overflow(self):
        """Verify boundary inputs in [-1000, 1000] and beyond produce finite results without NaN or Inf."""
        boundary_points = [
            -1000.0, -999.9, -500.0, -200.0, -100.0001, -100.0, -99.9999,
            -50.0, -20.0, -10.0, -5.0, -1.0, -0.1, -1e-15,
            0.0,
            1e-15, 0.1, 1.0, 5.0, 10.0, 20.0, 50.0,
            99.9999, 100.0, 100.0001, 200.0, 500.0, 999.9, 1000.0,
            -1e50, 1e50, -1e300, 1e300,
        ]
        for z in boundary_points:
            exp_val = py_math_exp_safe(z)
            sig_val = py_sigmoid(z)

            assert not math.isnan(exp_val)
            assert not math.isinf(exp_val)
            assert not math.isnan(sig_val)
            assert not math.isinf(sig_val)
            assert 0.0 <= sig_val <= 1.0

    def test_dense_grid_monotonicity_and_symmetry(self):
        """Verify 50,000 points dense grid across [-1000, 1000] satisfies monotonicity and symmetry."""
        dense_grid = np.linspace(-1000.0, 1000.0, 50_000)
        exp_vals = np.array([py_math_exp_safe(x) for x in dense_grid])
        sig_vals = np.array([py_sigmoid(x) for x in dense_grid])

        assert not np.any(np.isnan(exp_vals))
        assert not np.any(np.isinf(exp_vals))
        assert not np.any(np.isnan(sig_vals))
        assert not np.any(np.isinf(sig_vals))
        assert np.all((sig_vals >= 0.0) & (sig_vals <= 1.0))

        # Sigmoid(0) == 0.5
        assert abs(py_sigmoid(0.0) - 0.5) < 1e-15

        # Monotonicity
        diffs = np.diff(sig_vals)
        assert np.min(diffs) >= -1e-15

        # Symmetry: sigmoid(-x) + sigmoid(x) == 1.0
        sym_sample = np.linspace(-1000.0, 1000.0, 2000)
        sig_pos = np.array([py_sigmoid(x) for x in sym_sample])
        sig_neg = np.array([py_sigmoid(-x) for x in sym_sample])
        sym_err = np.max(np.abs((sig_pos + sig_neg) - 1.0))
        assert sym_err < 1e-12

    def test_unprotected_overflow_contrast(self):
        """Demonstrate that unprotected math.exp(1000.0) fails with OverflowError while MathExpSafe succeeds."""
        with pytest.raises(OverflowError):
            math.exp(1000.0)

        # MathExpSafe handles 1000.0 without exception and returns bounded value
        safe_val = py_math_exp_safe(1000.0)
        assert safe_val == pytest.approx(math.exp(100.0))


class TestMkDocsBuildArtifacts:
    """Verify MkDocs HTML build integrity in site/ directory."""

    def test_mkdocs_site_mermaid_and_mathjax_integrity(self):
        """Verify generated HTML files in site/ contain valid Mermaid tags and MathJax scripts."""
        site_dir = REPO_ROOT / "site"
        if not site_dir.exists():
            import subprocess
            subprocess.run(["mkdocs", "build"], cwd=REPO_ROOT, check=False)
        assert site_dir.exists(), f"site/ directory not found: {site_dir}"

        html_files = list(site_dir.rglob("*.html"))
        assert len(html_files) >= 5

        mathjax_found_count = 0
        tex_mml_chtml_found = False
        mermaid_blocks_found = 0
        arithmatex_found_count = 0

        for html_file in html_files:
            content = html_file.read_text(encoding="utf-8")

            if "javascripts/mathjax.js" in content:
                mathjax_found_count += 1
            if "tex-mml-chtml.js" in content or "mathjax" in content.lower():
                tex_mml_chtml_found = True

            mermaid_matches = re.findall(r'<pre\s+class="mermaid"><code>(.*?)</code></pre>', content, re.DOTALL)
            if not mermaid_matches:
                mermaid_matches = re.findall(r'<div\s+class="mermaid">(.*?)</div>', content, re.DOTALL)
            if mermaid_matches:
                mermaid_blocks_found += len(mermaid_matches)

            arithmatex_matches = re.findall(r'class="arithmatex"', content)
            if arithmatex_matches:
                arithmatex_found_count += len(arithmatex_matches)

        assert mathjax_found_count >= 5
        assert tex_mml_chtml_found
        assert mermaid_blocks_found >= 5
        assert arithmatex_found_count >= 50

        # Check visual asset
        asset_file = site_dir / "assets" / "IS_OOS_Robustness_Check.png"
        assert asset_file.exists()
        assert asset_file.stat().st_size > 1000

"""
Unit tests for MQL5 Export Pipeline (m2_metalabeling.export.export_mql5).
Validates Requirement R1 / Feature F21: end-to-end model training and MQL5 code generation,
custom dataset handling, fallback resolution, deterministic reproducibility, and MQL5 compliance.
"""

from pathlib import Path
import pandas as pd
import pytest

from m2_metalabeling.export.export_mql5 import train_and_export_mql5


def test_train_and_export_mql5_custom_dataset(synthetic_features_dataset, tmp_path: Path):
    """
    Verify train_and_export_mql5 trains on an arbitrary provided dataset CSV
    and writes the transpiled header to the specified output path.
    """
    dataset_csv = tmp_path / "custom_features.csv"
    synthetic_features_dataset.to_csv(dataset_csv, index=False)
    output_mqh = tmp_path / "M2_Custom_Oracle.mqh"

    result_path = train_and_export_mql5(
        dataset_path=dataset_csv,
        output_path=output_mqh,
        model_name="M2_Custom_Oracle",
        random_state=42,
    )

    assert result_path == output_mqh
    assert output_mqh.exists()
    content = output_mqh.read_text(encoding="utf-8")

    assert "#ifndef M2_CUSTOM_ORACLE_MQH" in content
    assert "#define M2_CUSTOM_ORACLE_MQH" in content
    assert "void GetXGBoostProbability(const double &features[], double &result[])" in content
    assert "MathExpSafe" in content
    assert "sigmoid" in content


def test_train_and_export_mql5_default_fallback(tmp_path: Path):
    """
    Verify fallback logic resolves the canonical repository dataset in data/processed/
    when dataset_path is omitted or None.
    """
    output_mqh = tmp_path / "M2_Default_Fallback.mqh"
    result_path = train_and_export_mql5(
        dataset_path=None,
        output_path=output_mqh,
        model_name="M2_Default_Fallback",
        random_state=42,
    )

    assert result_path.exists()
    content = result_mqh = result_path.read_text(encoding="utf-8")
    assert "GetXGBoostProbability" in content
    assert len(content) > 1000


def test_train_and_export_mql5_reproducibility(synthetic_features_dataset, tmp_path: Path):
    """
    Verify training and exporting twice with identical random_state=42
    produces bit-for-bit identical MQL5 header files.
    """
    dataset_csv = tmp_path / "repro_dataset.csv"
    synthetic_features_dataset.to_csv(dataset_csv, index=False)

    mqh_1 = tmp_path / "oracle_run1.mqh"
    mqh_2 = tmp_path / "oracle_run2.mqh"

    train_and_export_mql5(dataset_path=dataset_csv, output_path=mqh_1, random_state=42)
    train_and_export_mql5(dataset_path=dataset_csv, output_path=mqh_2, random_state=42)

    assert mqh_1.read_text(encoding="utf-8") == mqh_2.read_text(encoding="utf-8")


def test_train_and_export_mql5_invalid_dataset_raises(tmp_path: Path):
    """
    Verify ValueError is raised if a dataset CSV has none of the required technical features.
    """
    invalid_csv = tmp_path / "invalid_data.csv"
    df_invalid = pd.DataFrame({"col_a": [1, 2, 3], "col_b": [4, 5, 6], "Target": [0, 1, 0]})
    df_invalid.to_csv(invalid_csv, index=False)

    with pytest.raises(ValueError, match="None of .* found in columns"):
        train_and_export_mql5(dataset_path=invalid_csv, output_path=tmp_path / "out.mqh")


def test_train_and_export_mql5_c_code_sanitization(synthetic_features_dataset, tmp_path: Path):
    """
    Verify complete sanitization of raw C syntax:
    - No C99 compound array literals
    - No C pointer signatures (double * input)
    - No C standard library includes
    """
    dataset_csv = tmp_path / "clean_check.csv"
    synthetic_features_dataset.to_csv(dataset_csv, index=False)
    output_mqh = tmp_path / "Sanitized.mqh"

    train_and_export_mql5(dataset_path=dataset_csv, output_path=output_mqh)
    content = output_mqh.read_text(encoding="utf-8")

    assert "#include <math.h>" not in content
    assert "#include <string.h>" not in content
    assert "void score(double * input" not in content
    assert "memcpy" not in content
    assert "(double[])" not in content

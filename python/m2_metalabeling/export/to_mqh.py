"""
M2 Meta-Labeling Pipeline — Module: export/to_mqh.py
======================================================
Transpiles trained XGBClassifier models to zero-latency native C++/MQL5 headers
for sub-microsecond execution inside MetaTrader 5 Expert Advisors.
"""

import os
import re
from pathlib import Path
from typing import Union
import joblib
from loguru import logger
import m2cgen as m2c
from xgboost import XGBClassifier


def export_to_mqh(
    model_or_path: Union[XGBClassifier, str, Path],
    output_path: Union[str, Path],
    function_name: str = "GetXGBoostProbability",
    model_name: str = "M2_XGBoost_Oracle",
    use_safe_exp: bool = True,
) -> str:
    """
    Transpile a fitted XGBClassifier to a valid, zero-latency MQL5 include header (.mqh).

    Ensures:
      - base_score=0.5 compatibility with m2cgen.
      - Eradication of forbidden C headers (#include <math.h>, <string.h>).
      - Eradication of C99 compound literals (memcpy array literals rejected by MetaEditor).
      - Injection of MathExpSafe and sigmoid to protect against float overflow.
      - Native MQL5 const array pass-by-reference signature.

    Args:
        model_or_path: Fitted XGBClassifier instance or Path to a saved .pkl file.
        output_path: Destination path for the .mqh file.
        function_name: Name of the exported C++/MQL5 scoring function.
        model_name: Model identifier used for header guards and comments.
        use_safe_exp: Whether to use bounded MathExpSafe preventing overflow for |x| > 100.

    Returns:
        The generated MQL5 code as a string.
    """
    # 1. Resolve model
    if isinstance(model_or_path, (str, Path)):
        model_path = Path(model_or_path)
        if not model_path.exists():
            raise FileNotFoundError(f"Model file not found: {model_path}")
        model = joblib.load(model_path)
    else:
        model = model_or_path

    # Ensure base_score is set to 0.5 to avoid m2cgen TypeError
    if hasattr(model, "base_score") and (model.base_score is None):
        model.base_score = 0.5

    logger.info(f"Transpiling XGBoost model via m2cgen -> {output_path}")

    # 2. Export raw C code via m2cgen
    c_code = m2c.export_to_c(model)

    # 3. Post-process C code to valid native MQL5 syntax
    # Remove prohibited ANSI C headers
    c_code = re.sub(r"#include <math\.h>\s*", "", c_code)
    c_code = re.sub(r"#include <string\.h>\s*", "", c_code)

    # Replace m2cgen's signature and strip any pre-existing sigmoid from m2cgen
    c_code = re.sub(r"^.*?void score", f"void {function_name}", c_code, flags=re.DOTALL)

    # Convert parameter signatures to MQL5 array references
    mql5_code = c_code.replace(
        "(double * input, double * output) {",
        "(const double &features[], double &result[]) {"
    )
    mql5_code = mql5_code.replace("input[", "features[")
    mql5_code = mql5_code.replace("output[", "result[")
    mql5_code = mql5_code.replace(" exp(", " MathExp(")

    # Eradicate C99 compound literals from memcpy (rejected by MetaEditor)
    mql5_code = re.sub(
        r"memcpy\s*\(\s*(?:output|result)\s*,\s*\(\s*double\s*\[\s*\]\s*\)\s*\{\s*([^,]+)\s*,\s*([^}]+)\s*\}\s*,\s*2\s*\*\s*sizeof\s*\(\s*double\s*\)\s*\)\s*;",
        r"result[0] = \1;\n    result[1] = \2;",
        mql5_code
    )

    # 4. Construct complete header with guards and safe math
    clean_model_identifier = re.sub(r"[^A-Za-z0-9_]", "_", model_name.upper())
    guard_macro = f"{clean_model_identifier}_MQH"

    if use_safe_exp:
        math_routines = (
            "double MathExpSafe(double x) {\n"
            "    if (x > 100.0) return MathExp(100.0);\n"
            "    if (x < -100.0) return MathExp(-100.0);\n"
            "    return MathExp(x);\n"
            "}\n\n"
            "double sigmoid(double x) {\n"
            "    if (x < 0.0) {\n"
            "        double z = MathExpSafe(x);\n"
            "        return z / (1.0 + z);\n"
            "    }\n"
            "    return 1.0 / (1.0 + MathExpSafe(-x));\n"
            "}\n"
        )
    else:
        math_routines = (
            "double sigmoid(double x) {\n"
            "    if (x < 0.0) {\n"
            "        double z = MathExp(x);\n"
            "        return z / (1.0 + z);\n"
            "    }\n"
            "    return 1.0 / (1.0 + MathExp(-x));\n"
            "}\n"
        )

    final_mql5 = (
        f"//+------------------------------------------------------------------+\n"
        f"//| {model_name}.mqh\n"
        f"//| Auto-generated zero-latency C++/MQL5 tree header                 |\n"
        f"//+------------------------------------------------------------------+\n"
        f"#ifndef {guard_macro}\n"
        f"#define {guard_macro}\n\n"
        f'#property copyright "Antigravity Quant AI"\n\n'
        f"{math_routines}\n"
        f"{mql5_code.strip()}\n\n"
        f"#endif // {guard_macro}\n"
    )

    # 5. Write to output file
    out_file = Path(output_path)
    out_file.parent.mkdir(parents=True, exist_ok=True)
    with open(out_file, "w", encoding="utf-8") as f:
        f.write(final_mql5)

    logger.success(f"Successfully generated MQL5 include: {out_file}")
    return final_mql5


# Alias for backward compatibility
export_xgboost_to_mqh = export_to_mqh


def export_to_onnx(
    model_path: Union[str, Path],
    output_path: Union[str, Path],
    n_features: int,
) -> None:
    """
    Export a fitted XGBClassifier to ONNX format for use with
    OnnxCreate() / OnnxRun() in MT5 Expert Advisors.
    """
    try:
        from skl2onnx import convert_sklearn
        from skl2onnx.common.data_types import FloatTensorType
    except ImportError:
        logger.error("skl2onnx/onnx not installed. Run: pip install skl2onnx onnx")
        return

    model = joblib.load(model_path)
    initial_type = [("float_input", FloatTensorType([None, n_features]))]
    onnx_model = convert_sklearn(model, initial_types=initial_type)

    out_file = Path(output_path)
    out_file.parent.mkdir(parents=True, exist_ok=True)
    with open(out_file, "wb") as f:
        f.write(onnx_model.SerializeToString())

    logger.success(f"ONNX export complete -> {out_file}")

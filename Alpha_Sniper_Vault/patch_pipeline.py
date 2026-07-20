import re

path = r"C:\Users\Manuel\Desktop\HMA_MetaLabeling\Alpha_Sniper_Vault\src\pipeline_global_optimizer.py"
with open(path, "r", encoding="utf-8") as f:
    content = f.read()

# 1. Imports
if "from sklearn.calibration import CalibratedClassifierCV" not in content:
    content = content.replace("from xgboost import XGBClassifier", 
                              "from xgboost import XGBClassifier\nfrom sklearn.calibration import CalibratedClassifierCV")

# 2. ACTIVOS
content = re.sub(r'assets\s*=\s*\[.*?\]', 'assets = ["EURUSD", "GBPUSD", "USDJPY", "EURJPY", "XAUUSD"]', content)

# 3. XGB_PARAMS
content = re.sub(r'max_depth\s*=\s*3', 'max_depth         = 4', content)
content = re.sub(r'min_child_weight\s*=\s*50', 'min_child_weight  = 20', content)
content = re.sub(r'reg_alpha\s*=\s*0\.1', 'reg_alpha         = 1.0', content)
content = re.sub(r'reg_lambda\s*=\s*1\.5', 'reg_lambda        = 5.0', content)

# Also fix EXIT_XGB_PARAMS if it uses the same values or different ones
# Let's just do a generic replace for reg_alpha and reg_lambda, and max_depth=3 to max_depth=4
# Actually, the user wants max_depth 3 or 4. We set it to 4.

# 4. Calibration Wrapper for WFO models
content = content.replace(
    "model = XGBClassifier(**XGB_PARAMS, scale_pos_weight=scale_weight)\n        model.fit(pd.DataFrame(X_tr, columns=available_features), y_tr, sample_weight=w_tr, verbose=False)",
    """model_base = XGBClassifier(**XGB_PARAMS, scale_pos_weight=scale_weight)
        model = CalibratedClassifierCV(estimator=model_base, method='isotonic', cv=5)
        model.fit(pd.DataFrame(X_tr, columns=available_features), y_tr, sample_weight=w_tr)"""
)

# Calibration Wrapper for EXIT WFO models
content = content.replace(
    "model = XGBClassifier(**EXIT_XGB_PARAMS, scale_pos_weight=scale_weight)\n        model.fit(X_tr, y_tr, sample_weight=w_tr, eval_set=[(X_val, y_val)], sample_weight_eval_set=[w_val], verbose=False)",
    """model_base = XGBClassifier(**EXIT_XGB_PARAMS, scale_pos_weight=scale_weight)
        model = CalibratedClassifierCV(estimator=model_base, method='isotonic', cv=5)
        model.fit(pd.DataFrame(X_tr, columns=available_features), y_tr, sample_weight=w_tr)"""
)

# Calibration Wrapper for Final Entry Model
content = content.replace(
    "final_model = XGBClassifier(**final_params, scale_pos_weight=scale_weight)\n    final_model.fit(pd.DataFrame(X, columns=available_features), y, sample_weight=weights, verbose=False)",
    """final_model_base = XGBClassifier(**final_params, scale_pos_weight=scale_weight)
    final_model = CalibratedClassifierCV(estimator=final_model_base, method='isotonic', cv=5)
    final_model.fit(pd.DataFrame(X, columns=available_features), y, sample_weight=weights)"""
)

# Calibration Wrapper for Final Exit Model
content = content.replace(
    "final_model = XGBClassifier(**final_params, scale_pos_weight=scale_weight)\n    final_model.fit(X, y, sample_weight=weights, verbose=False)",
    """final_model_base = XGBClassifier(**final_params, scale_pos_weight=scale_weight)
    final_model = CalibratedClassifierCV(estimator=final_model_base, method='isotonic', cv=5)
    final_model.fit(pd.DataFrame(X, columns=available_features), y, sample_weight=weights)"""
)

# Add feature names injection to CalibratedClassifierCV since joblib dump needs them later
content = content.replace(
    "joblib.dump(final_model, model_path)",
    "final_model.feature_names_in_ = np.array(available_features)\n    joblib.dump(final_model, model_path)"
)

# Also in WFO
content = content.replace(
    "joblib.dump(model, wfo_model_path)",
    "model.feature_names_in_ = np.array(available_features)\n        joblib.dump(model, wfo_model_path)"
)

# Handle feature_names_in_ correctly for pipeline optimizer if it complains.
# Actually CalibratedClassifierCV exposes feature_names_in_ naturally if fitted with DataFrame!
# Let's ensure X is DataFrame for exit model as well:
content = content.replace(
    "final_model.fit(X, y, sample_weight=weights, verbose=False)",
    "final_model.fit(pd.DataFrame(X, columns=available_features), y, sample_weight=weights, verbose=False)"
)

with open(path, "w", encoding="utf-8") as f:
    f.write(content)
print("Pipeline optimizado con xito.")

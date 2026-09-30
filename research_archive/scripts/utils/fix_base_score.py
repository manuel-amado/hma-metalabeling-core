import xgboost as xgb
import numpy as np
X = np.array([[1], [2]])
y = np.array([-0.3, -0.4])
model = xgb.XGBRegressor(objective='reg:squarederror')
model.fit(X, y)
import json
bs = json.loads(model.get_booster().save_config())['learner']['learner_model_param']['base_score']
print(f"Base score: {bs}")

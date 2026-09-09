import xgboost as xgb
import numpy as np
import json
model = xgb.XGBClassifier(objective='binary:logistic')
model.fit(np.array([[1], [2]]), np.array([0, 1]))
bs = json.loads(model.get_booster().save_config())['learner']['learner_model_param']['base_score']
print(f"Base score: {bs}")

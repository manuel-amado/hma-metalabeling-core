import sys
import joblib
import pandas as pd
sys.path.append('src')
from pipeline_global_optimizer import ENTRY_FEATURES

scaler = joblib.load('api/models/scaler_entry_eurjpy.pkl')
print('Scaler features:', getattr(scaler, 'feature_names_in_', 'NOT AVAILABLE'))
print('ENTRY_FEATURES length:', len(ENTRY_FEATURES))


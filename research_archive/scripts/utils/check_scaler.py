import pandas as pd
from sklearn.preprocessing import RobustScaler
df = pd.read_csv('C:/Users/Manuel/Desktop/HMA_MetaLabeling/Alpha_Sweep_Dataset_XAUUSD.csv', header=None)
X = df.iloc[:, :18]
scaler = RobustScaler().fit(X)
print('Medians:', scaler.center_)
print('Scales:', scaler.scale_)

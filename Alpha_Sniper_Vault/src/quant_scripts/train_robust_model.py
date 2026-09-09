import pandas as pd
import numpy as np
from sklearn.tree import DecisionTreeClassifier
from sklearn.model_selection import GridSearchCV, StratifiedKFold
from sklearn.metrics import classification_report

csv_path = r"C:\Users\Manuel\AppData\Roaming\MetaQuotes\Tester\D0E8209F77C8CF37AD8BF550E51FF075\Agent-127.0.0.1-3000\MQL5\Files\ML_Alpha_Trades.csv"
df = pd.read_csv(csv_path)

# Drop Time, Hour, Day. Only purely physical/structural features
features = ['RSI', 'ATR', 'DistEMA']
X = df[features]
y = df['Label']

# Queremos Maxima Precision (calidad de trades).
cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)

param_grid = {
    'max_depth': [2, 3], # Shallow trees
    'min_samples_leaf': [40, 60, 80], 
    'class_weight': ['balanced', None],
    'ccp_alpha': [0.005, 0.01, 0.015, 0.02] # Cost complexity pruning
}

clf = GridSearchCV(
    DecisionTreeClassifier(random_state=42), 
    param_grid, 
    cv=cv, 
    scoring='precision' # Optimizar precision
)
clf.fit(X, y)

best_clf = clf.best_estimator_
print(f"Mejores Hiperparametros: {clf.best_params_}")

print("\n--- RENDIMIENTO ROBUSTO (IN-SAMPLE) ---")
y_pred = best_clf.predict(X)
print(classification_report(y, y_pred))

def tree_to_cpp(tree, feature_names):
    tree_ = tree.tree_
    feature_name = [feature_names[i] if i != -2 else "undefined!" for i in tree_.feature]
    
    code = "bool IsTradeAllowedByAI(double RSI, double ATR, double Dist_EMA, int Hour, int DayOfWeek, int Signal) {\n"
    
    def recurse(node, depth):
        indent = "    " * depth
        if tree_.feature[node] != -2:
            name = feature_name[node]
            if name == 'DistEMA': name = 'Dist_EMA'
            threshold = tree_.threshold[node]
            c = f"{indent}if ({name} <= {threshold:.4f}) {{\n"
            c += recurse(tree_.children_left[node], depth + 1)
            c += f"{indent}}} else {{\n"
            c += recurse(tree_.children_right[node], depth + 1)
            c += f"{indent}}}\n"
            return c
        else:
            value = tree_.value[node][0]
            pred_class = 1 if value[1] > value[0] else 0
            ret_val = "true" if pred_class == 1 else "false"
            return f"{indent}return {ret_val};\n"

    code += recurse(0, 1)
    code += "}\n"
    return code

cpp_code = tree_to_cpp(best_clf, features)
print("\n--- NUEVO CODIGO C++ ROBUSTO ---")
print(cpp_code)
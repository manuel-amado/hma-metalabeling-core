import pandas as pd
import numpy as np
from sklearn.tree import DecisionTreeClassifier, export_text
from sklearn.metrics import accuracy_score, classification_report
from sklearn.model_selection import GridSearchCV

csv_path = r"C:\Users\Manuel\AppData\Roaming\MetaQuotes\Tester\D0E8209F77C8CF37AD8BF550E51FF075\Agent-127.0.0.1-3000\MQL5\Files\ML_Alpha_Trades.csv"
df = pd.read_csv(csv_path)

print(f"Total trades for ML: {len(df)}")
features = ['RSI', 'ATR', 'DistEMA', 'Hour', 'Day', 'Signal']
X = df[features]
y = df['Label']

# Queremos prevenir sobreajuste, probaremos max_depth 3 y 4, min_samples_leaf
param_grid = {
    'max_depth': [3, 4],
    'min_samples_leaf': [15, 30, 50],
    'class_weight': ['balanced']
}
clf = GridSearchCV(DecisionTreeClassifier(random_state=42), param_grid, cv=5, scoring='accuracy')
clf.fit(X, y)

best_clf = clf.best_estimator_
print(f"Mejor Modelo: {clf.best_params_}")

y_pred = best_clf.predict(X)
print("Accuracy global:", accuracy_score(y, y_pred))
print(classification_report(y, y_pred))

def tree_to_cpp(tree, feature_names):
    tree_ = tree.tree_
    feature_name = [
        feature_names[i] if i != -2 else "undefined!"
        for i in tree_.feature
    ]
    
    code = "bool IsTradeAllowedByAI(double RSI, double ATR, double Dist_EMA, int Hour, int DayOfWeek, int Signal) {\n"
    
    def recurse(node, depth):
        indent = "    " * depth
        if tree_.feature[node] != -2:
            name = feature_name[node]
            if name == 'DistEMA': name = 'Dist_EMA'
            if name == 'Day': name = 'DayOfWeek'
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
print("\n--- NUEVO CODIGO C++ (IS_TRADE_ALLOWED_BY_AI) ---")
print(cpp_code)
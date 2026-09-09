import pandas as pd
import numpy as np
from sklearn.tree import DecisionTreeClassifier, export_text
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report

csv_path = r"C:\Users\Manuel\AppData\Roaming\MetaQuotes\Terminal\D0E8209F77C8CF37AD8BF550E51FF075\MQL5\Files\XAUUSD_M15_2015_2026.csv"
df = pd.read_csv(csv_path)
df['time'] = pd.to_datetime(df['time'], format='%Y.%m.%d %H:%M')

def wma(s, period):
    weights = np.arange(1, period + 1)
    return s.rolling(period).apply(lambda x: np.dot(x, weights) / weights.sum(), raw=True)

def hma(s, period):
    return wma((2 * wma(s, int(period / 2))) - wma(s, period), int(np.sqrt(period)))

df['hma200'] = hma(df['close'], 200)
df['ema400'] = df['close'].ewm(span=400, adjust=False).mean()

delta = df['close'].diff()
gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
df['rsi14'] = 100 - (100 / (1 + (gain/loss)))

df['tr'] = np.maximum(df['high'] - df['low'], np.maximum(abs(df['high'] - df['close'].shift(1)), abs(df['low'] - df['close'].shift(1))))
df['atr14'] = df['tr'].rolling(14).mean()

df['hour'] = df['time'].dt.hour
df['day_of_week'] = df['time'].dt.dayofweek

df.dropna(inplace=True)

# Generate Trades and Features
features = []
targets = []

in_trade = False
trade_dir = 0
entry_price = 0.0
sl = 0.0
friction = 0.35
risk_dist = 0.0

c = df['close'].values
h = df['high'].values
l = df['low'].values
hma_arr = df['hma200'].values
ema_arr = df['ema400'].values
rsi_arr = df['rsi14'].values
atr_arr = df['atr14'].values
hour_arr = df['hour'].values
dow_arr = df['day_of_week'].values

for i in range(1, len(df)):
    if in_trade:
        if trade_dir == 1 and l[i] <= sl:
            targets.append(0)
            in_trade = False
        elif trade_dir == -1 and h[i] >= sl:
            targets.append(0)
            in_trade = False
        elif trade_dir == 1 and c[i] < hma_arr[i]:
            profit = (c[i] - entry_price - friction)
            targets.append(1 if profit > 0 else 0)
            in_trade = False
        elif trade_dir == -1 and c[i] > hma_arr[i]:
            profit = (entry_price - c[i] - friction)
            targets.append(1 if profit > 0 else 0)
            in_trade = False
    else:
        hr = hour_arr[i]
        if hr < 12 or hr > 21: continue
            
        c_curr, c_prev = c[i], c[i-1]
        hma_curr, hma_prev = hma_arr[i], hma_arr[i-1]
        ema_curr = ema_arr[i]
        rsi_curr = rsi_arr[i]
        atr_curr = atr_arr[i]
        
        signal = 0
        if c_prev < hma_prev and c_curr > hma_curr and c_curr > ema_curr and rsi_curr < 70: signal = 1
        elif c_prev > hma_prev and c_curr < hma_curr and c_curr < ema_curr and rsi_curr > 30: signal = -1
            
        if signal != 0:
            # Capture Features
            dist_ema = (c_curr - ema_curr) / atr_curr
            feat = [rsi_curr, atr_curr, dist_ema, hr, dow_arr[i], signal]
            features.append(feat)
            
            in_trade = True; trade_dir = signal; entry_price = c_curr
            risk_dist = 1.5 * atr_curr
            sl = c_curr - risk_dist if signal == 1 else c_curr + risk_dist

X = pd.DataFrame(features, columns=['RSI', 'ATR', 'Dist_EMA', 'Hour', 'DayOfWeek', 'Signal'])
y = np.array(targets)

print(f"Total Trades: {len(X)}")
print(f"Base Win Rate: {np.mean(y)*100:.2f}%")

# Train Decision Tree
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42, shuffle=False)

# We want a shallow tree so it doesn't overfit and can be exported as simple MQL5 if/else
clf = DecisionTreeClassifier(max_depth=4, class_weight='balanced', min_samples_leaf=20, random_state=42)
clf.fit(X_train, y_train)

# Evaluate
y_pred_train = clf.predict(X_train)
y_pred_test = clf.predict(X_test)

print("\n--- TEST SET EVALUATION ---")
test_trades = len(y_test)
test_taken = np.sum(y_pred_test)
test_wins = np.sum((y_pred_test == 1) & (y_test == 1))
print(f"Original Test Trades: {test_trades}, Original WinRate: {np.mean(y_test)*100:.2f}%")
if test_taken > 0:
    print(f"Filtered Test Trades: {test_taken}, New WinRate: {test_wins/test_taken*100:.2f}%")
else:
    print("Model rejected all trades in test set.")

# Export to C++ (MQL5) function
def export_tree_to_mql5(tree, feature_names):
    tree_ = tree.tree_
    feature_name = [
        feature_names[i] if i != -2 else "undefined!"
        for i in tree_.feature
    ]
    
    mql5_code = "bool IsTradeAllowedByAI(double RSI, double ATR, double Dist_EMA, int Hour, int DayOfWeek, int Signal) {\n"
    
    def recurse(node, depth):
        indent = "    " * depth
        nonlocal mql5_code
        if tree_.feature[node] != -2:
            name = feature_name[node]
            threshold = tree_.threshold[node]
            mql5_code += f"{indent}if ({name} <= {threshold:.4f}) {{\n"
            recurse(tree_.children_left[node], depth + 1)
            mql5_code += f"{indent}}} else {{\n"
            recurse(tree_.children_right[node], depth + 1)
            mql5_code += f"{indent}}}\n"
        else:
            value = tree_.value[node][0]
            # Prob of class 1
            prob = value[1] / (value[0] + value[1])
            prediction = "true" if prob >= 0.5 else "false"
            mql5_code += f"{indent}return {prediction}; // Prob Win: {prob*100:.1f}%\n"
            
    recurse(0, 1)
    mql5_code += "}\n"
    return mql5_code

mql5_logic = export_tree_to_mql5(clf, X.columns)
with open(r"C:\Users\Manuel\Desktop\HMA_MetaLabeling\Alpha_Sniper_Vault\src\quant_scripts\08_ai_logic.mqh", "w") as f:
    f.write(mql5_logic)

print("\nMQL5 AI Logic Generated.")
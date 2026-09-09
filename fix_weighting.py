filepath = r'C:\Users\Manuel\Desktop\HMA_MetaLabeling\Alpha_Sniper_Vault\src\training\train_wfo_v19.py'
with open(filepath, 'r') as f:
    content = f.read()

# We need to extract ReturnPct to use as sample weights.
# In train_wfo_v19.py, we only extract Label:
# y_train = df_train[TARGET_CLASS].values
# We need:
# y_train = df_train[TARGET_CLASS].values
# w_train = np.abs(df_train['ReturnPct'].values)

old_extract = '''        X_train = df_train[FEATURES].values
        y_train = df_train[TARGET_CLASS].values
        scaler = RobustScaler()'''

new_extract = '''        X_train = df_train[FEATURES].values
        y_train = df_train[TARGET_CLASS].values
        w_train = np.abs(df_train['ReturnPct'].values)
        scaler = RobustScaler()'''

content = content.replace(old_extract, new_extract)

# Update optimize_hyperparams signature and fit
old_opt = '''def optimize_hyperparams(X_train, y_train):
    def objective(trial):
        params = {
            'max_depth': trial.suggest_int('max_depth', 2, 5),
            'learning_rate': trial.suggest_float('learning_rate', 0.01, 0.1, log=True),
            'n_estimators': trial.suggest_int('n_estimators', 30, 80),
            'subsample': trial.suggest_float('subsample', 0.5, 0.9),
            'colsample_bytree': trial.suggest_float('colsample_bytree', 0.5, 0.9),
            'objective': 'binary:logistic',
            'random_state': 42
        }
        model = xgb.XGBClassifier(**params)
        model.fit(X_train, y_train)'''

new_opt = '''def optimize_hyperparams(X_train, y_train, w_train):
    def objective(trial):
        params = {
            'max_depth': trial.suggest_int('max_depth', 2, 5),
            'learning_rate': trial.suggest_float('learning_rate', 0.01, 0.1, log=True),
            'n_estimators': trial.suggest_int('n_estimators', 30, 80),
            'subsample': trial.suggest_float('subsample', 0.5, 0.9),
            'colsample_bytree': trial.suggest_float('colsample_bytree', 0.5, 0.9),
            'objective': 'binary:logistic',
            'random_state': 42
        }
        model = xgb.XGBClassifier(**params)
        model.fit(X_train, y_train, sample_weight=w_train)'''

content = content.replace(old_opt, new_opt)

# Update the call to optimize_hyperparams
content = content.replace('best_params = optimize_hyperparams(X_tr_sc, y_train)', 'best_params = optimize_hyperparams(X_tr_sc, y_train, w_train)')

# Update the final model fit
content = content.replace('model.fit(X_tr_sc, y_train)\n        test_year = current_train_end.year', 'model.fit(X_tr_sc, y_train, sample_weight=w_train)\n        test_year = current_train_end.year')

with open(filepath, 'w') as f:
    f.write(content)
print("Weighted Training Implemented")

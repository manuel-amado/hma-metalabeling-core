import os
import glob
import pandas as pd
import xgboost as xgb
import matplotlib.pyplot as plt
import numpy as np

def find_latest_dataset():
    base_path = r"C:\Users\Manuel\AppData\Roaming\MetaQuotes\Tester"
    # Find all Alpha_Sweep_Dataset_XAUUSD.csv files recursively in Tester directory
    search_pattern = os.path.join(base_path, "**", "Alpha_Sweep_Dataset_XAUUSD.csv")
    files = glob.glob(search_pattern, recursive=True)
    
    if not files:
        print("ERROR: Could not find Alpha_Sweep_Dataset_XAUUSD.csv in Tester folder.")
        return None
        
    # Get the most recently modified file
    latest_file = max(files, key=os.path.getmtime)
    print(f"[*] Found dataset: {latest_file}")
    return latest_file

def main():
    dataset_path = find_latest_dataset()
    if not dataset_path:
        return
        
    print("[*] Loading dataset...")
    try:
        df = pd.read_csv(dataset_path)
    except Exception as e:
        print(f"Error reading CSV: {e}")
        return
        
    print(f"[*] Original shape: {df.shape}")
    
    # Drop rows with NaN
    df = df.dropna()
    print(f"[*] Shape after dropping NaNs: {df.shape}")
    
    if df.empty:
        print("Dataset is empty. Exiting.")
        return
        
    # Define features (X) and target (y)
    # Exclude non-feature columns
    cols_to_exclude = ['ReturnPct', 'Label']
    feature_cols = [c for c in df.columns if c not in cols_to_exclude]
    
    X = df[feature_cols]
    y = df['Label']
    
    print(f"[*] Positive class ratio (Win Rate): {y.mean():.2%}")
    print("[*] Training XGBoost Classifier to extract feature importance...")
    
    # Initialize XGBoost model
    # We use tree_method='hist' for speed, and slightly deep trees to capture interactions
    model = xgb.XGBClassifier(
        n_estimators=100,
        max_depth=5,
        learning_rate=0.05,
        tree_method='hist',
        random_state=42
    )
    
    model.fit(X, y)
    
    # Get Feature Importance (Gain is usually better for identifying the most predictive features)
    importance_gain = model.get_booster().get_score(importance_type='gain')
    importance_weight = model.get_booster().get_score(importance_type='weight')
    
    # Convert to DataFrames
    df_gain = pd.DataFrame([{'Feature': k, 'Gain': v} for k, v in importance_gain.items()])
    df_weight = pd.DataFrame([{'Feature': k, 'Weight': v} for k, v in importance_weight.items()])
    
    # Merge and sort by Gain
    if not df_gain.empty:
        df_importance = pd.merge(df_gain, df_weight, on='Feature', how='outer').fillna(0)
        df_importance = df_importance.sort_values(by='Gain', ascending=False).reset_index(drop=True)
        
        print("\n" + "="*50)
        print("TOP 20 FEATURES BY INFORMATION GAIN")
        print("="*50)
        print(df_importance.head(20).to_string(index=False))
        
        # Save plot
        plt.figure(figsize=(12, 8))
        top_plot = df_importance.head(20)
        plt.barh(top_plot['Feature'][::-1], top_plot['Gain'][::-1], color='#1f77b4')
        plt.title('Top 20 Features by Information Gain (XGBoost)')
        plt.xlabel('Information Gain (Average purity increase)')
        plt.tight_layout()
        plot_path = r"C:\Users\Manuel\Desktop\HMA_MetaLabeling\Alpha_Sniper_Vault\src\feature_importance_m15.png"
        plt.savefig(plot_path)
        print(f"\n[*] Plot saved to: {plot_path}")
    else:
        print("No features used by the model.")

if __name__ == '__main__':
    main()

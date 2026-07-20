import pandas as pd
import joblib
import xgboost as xgb
import matplotlib.pyplot as plt
import os

from pipeline_global_optimizer import ENTRY_FEATURES, EXIT_FEATURES, SYMBOL, OUTPUT_DIR

def plot_importance(model_path, feature_names, output_filename, title):
    print(f'Procesando {model_path}...')
    if not os.path.exists(model_path):
        print(f'Error: No se encontro el modelo {model_path}')
        return
        
    model = joblib.load(model_path)
    
    # XGBoost classifier
    booster = model.get_booster()
    booster.feature_names = feature_names
    
    # Get feature importance (gain)
    importance = booster.get_score(importance_type='gain')
    
    # Convert to DataFrame
    df_imp = pd.DataFrame(list(importance.items()), columns=['Feature', 'Importance'])
    df_imp = df_imp.sort_values(by='Importance', ascending=True).tail(15)
    
    # Plot
    plt.figure(figsize=(10, 8))
    plt.barh(df_imp['Feature'], df_imp['Importance'], color='skyblue', edgecolor='black')
    plt.title(title, fontsize=14, pad=15)
    plt.xlabel('F-Score (Gain)', fontsize=12)
    plt.grid(axis='x', linestyle='--', alpha=0.7)
    plt.tight_layout()
    plt.savefig(output_filename, dpi=300)
    plt.close()
    print(f'Guardado: {output_filename}')

if __name__ == '__main__':
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    plot_importance(
        os.path.join(OUTPUT_DIR, f'entry_model_{SYMBOL}.pkl'), 
        ENTRY_FEATURES, 
        f'entry_importance_{SYMBOL}.png', 
        f'Top 15 Features - Entry Model ({SYMBOL})'
    )
    plot_importance(
        os.path.join(OUTPUT_DIR, f'exit_model_{SYMBOL}.pkl'), 
        EXIT_FEATURES, 
        f'exit_importance_{SYMBOL}.png', 
        f'Top 15 Features - Exit Model ({SYMBOL})'
    )

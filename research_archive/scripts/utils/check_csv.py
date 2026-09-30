import pandas as pd
df = pd.read_csv('C:/Users/Manuel/Desktop/HMA_MetaLabeling/Alpha_Sniper_Vault/data/Alpha_Sweep_Dataset_XAUUSD.csv')
print(f'Total rows: {len(df)}')
# In the CSV we don't have timestamps. But we know the first few rows are from early 2015.
# Let's see the proportion of labels
print(df['Label'].value_counts(normalize=True))
# Let's evaluate the Python model's predictions on the first 100 rows!
# We don't have the model object readily available, but we can check the 'Gross_PnL_Pips'
print(df['Gross_PnL_Pips'].head(20))

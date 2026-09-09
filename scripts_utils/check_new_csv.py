import pandas as pd
df = pd.read_csv('C:/Users/Manuel/Desktop/HMA_MetaLabeling/Alpha_Sweep_Dataset_XAUUSD.csv')
print(f'Total rows: {len(df)}')
print('Label distribution:')
print(df['Label'].value_counts(normalize=True))
print('\nProfitPips description:')
print(df['ProfitPips'].describe())

y = (df['ProfitPips'] - 2.5 > 0).astype(int)
print('\nActual ML targets (ProfitPips > 2.5):')
print(y.value_counts(normalize=True))

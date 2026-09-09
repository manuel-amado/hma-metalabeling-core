from bs4 import BeautifulSoup
import pandas as pd

file_path = r"C:\Users\Manuel\Documents\BACKTESTS\ReportOptimizer-510237087.xml"
with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
    content = f.read()

soup = BeautifulSoup(content, 'xml')
rows = soup.find_all('Row')

data = []
headers = []
for i, row in enumerate(rows):
    cells = row.find_all('Cell')
    row_data = [cell.get_text(strip=True) for cell in cells]
    if i == 0:
        headers = row_data
    else:
        if len(row_data) == len(headers):
            data.append(row_data)

df = pd.DataFrame(data, columns=headers)
numeric_cols = ['Result', 'Profit', 'Trades', 'Profit Factor', 'Expected Payoff', 'Drawdown %']
for col in df.columns:
    if col in numeric_cols or 'Inp' in col or 'Trigger' in col or 'Partial' in col or 'Trail' in col:
        try:
            df[col] = pd.to_numeric(df[col].str.replace(' ', '').str.replace(',', '.'))
        except:
            pass

df_true = df[(df['InpUseTradeManagement'] == 'true') | (df['InpUseTradeManagement'] == True)].copy()

# Remove the (0,0,0) baseline to see actual management combinations
df_mgmt = df_true[~((df_true['InpBE_Trigger_R'] == 0.0) & (df_true['InpPartialTP_R'] == 0) & (df_true['InpTrail_Activation_R'] == 0))].copy()

if len(df_mgmt) > 0:
    df_sorted = df_mgmt.sort_values('Profit Factor', ascending=False)
    cols_to_show = ['Pass', 'Profit', 'Trades', 'Profit Factor', 'InpBE_Trigger_R', 'InpPartialTP_R', 'InpTrail_Activation_R', 'InpTrail_Distance_ATR']
    print("--- TOP 10 COMBINACIONES (GESTION ACTIVADA) POR PROFIT FACTOR ---")
    print(df_sorted[cols_to_show].head(10).to_string(index=False))
else:
    print("No hay pases con gestion activada.")
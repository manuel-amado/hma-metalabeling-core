import pandas as pd
import datetime

html_path = r'C:\Users\Manuel\Documents\BACKTESTS\ReportTester-1513981370.html'

try:
    tables = pd.read_html(html_path)
    deals_table = sorted(tables, key=lambda t: len(t))[-1]
    
    # Check the columns
    print("Columns:", deals_table.columns)
    
    # We want to find the Profit column. Often it's named 'Beneficio' or 'Profit'
    col_idx = -1
    for i, col in enumerate(deals_table.columns):
        if 'Beneficio' in str(col) or 'Profit' in str(col):
            col_idx = i
            break
            
    if col_idx == -1:
        # Usually it is the second to last column, index -2
        col_idx = len(deals_table.columns) - 2

    parsed_deals = []
    for idx, row in deals_table.iterrows():
        try:
            date_str = str(row.iloc[0])
            if '.' in date_str and ':' in date_str:
                dt = datetime.datetime.strptime(date_str, '%Y.%m.%d %H:%M:%S')
                
                row_str = ' '.join([str(x) for x in row.values])
                symbol = None
                for sym in ['XAUUSD', 'GBPJPY', 'XAGUSD', 'USDJPY', 'EURUSD', 'AUDUSD']:
                    if sym in row_str:
                        symbol = sym
                        break
                if not symbol: continue
                
                profit_str = str(row.iloc[col_idx]).replace(' ', '')
                profit = float(profit_str)
                
                if profit != 0 and ('sell' in row_str.lower() or 'buy' in row_str.lower() or 'tp' in row_str.lower() or 'sl' in row_str.lower()):
                    parsed_deals.append({
                        'Date': dt,
                        'Year': dt.year,
                        'Symbol': symbol,
                        'Profit': profit
                    })
        except:
            pass

    df = pd.DataFrame(parsed_deals)
    print(f'Extracted {len(df)} profit trades.')
    
    start_date = datetime.datetime(2015, 1, 1)
    end_date = datetime.datetime(2026, 7, 1)
    total_days = (end_date - start_date).days
    block_days = total_days / 10.0
    
    def get_zone(dt):
        days_passed = (dt - start_date).days
        block = int(days_passed / block_days)
        if block in [2, 5, 8]:
            return 'OOS'
        return 'IS'
        
    df['Zone'] = df['Date'].apply(get_zone)
    
    agg = df.groupby(['Year', 'Symbol', 'Zone'])['Profit'].agg(['sum', 'count']).reset_index()
    agg = agg.sort_values(by=['Year', 'Symbol'])
    
    totals = df.groupby(['Symbol', 'Zone'])['Profit'].agg(['sum', 'count']).reset_index()
    
    print('\n--- ANNUAL REPORT ---')
    print(agg.to_string())
    
    print('\n--- TOTALS BY SYMBOL ---')
    print(totals.to_string())
    
except Exception as e:
    print('Failed:', str(e))
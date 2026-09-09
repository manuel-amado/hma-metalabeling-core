import pandas as pd
import datetime

html_path = r'C:\Users\Manuel\Documents\BACKTESTS\ReportTester-1513981370.html'

try:
    tables = pd.read_html(html_path)
    deals_table = sorted(tables, key=lambda t: len(t))[-1]
    
    start_idx = -1
    for idx, row in deals_table.iterrows():
        if 'Transacciones' in str(row.values):
            start_idx = idx
            break
            
    parsed_deals = []
    
    # We slice the dataframe from start_idx + 2 to avoid headers
    for idx, row in deals_table.iloc[start_idx+2:].iterrows():
        try:
            date_str = str(row.iloc[0])
            if '.' in date_str and ':' in date_str:
                dt = datetime.datetime.strptime(date_str, '%Y.%m.%d %H:%M:%S')
                symbol = str(row.iloc[2]).strip()
                profit_str = str(row.iloc[10]).replace(' ', '')
                
                if symbol in ['XAUUSD', 'GBPJPY', 'XAGUSD', 'USDJPY', 'EURUSD', 'AUDUSD'] and profit_str != 'nan':
                    profit = float(profit_str)
                    if profit != 0.0:
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
    
    # Aggregation
    agg = df.groupby(['Year', 'Symbol', 'Zone'])['Profit'].agg(['sum', 'count']).reset_index()
    agg = agg.sort_values(by=['Year', 'Symbol'])
    
    totals = df.groupby(['Symbol', 'Zone'])['Profit'].agg(['sum', 'count']).reset_index()
    
    print('\n--- ANNUAL REPORT ---')
    print(agg.to_string())
    
    print('\n--- TOTALS BY SYMBOL ---')
    print(totals.to_string())
    
    print(f"\nTOTAL NET PROFIT SUM: {df['Profit'].sum()}")
    
except Exception as e:
    print('Failed:', str(e))
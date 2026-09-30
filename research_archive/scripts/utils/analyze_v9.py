import pandas as pd
import datetime
import warnings
warnings.filterwarnings('ignore')

html_path = r'C:\Users\Manuel\Documents\BACKTESTS\ReportTester-1513981370.html'

try:
    tables = pd.read_html(html_path)
    deals_table = sorted(tables, key=lambda t: len(t))[-1]
    
    # We need to extract Date, Symbol, and Profit
    # Typical columns for deals: Date, Ticket, Symbol, Type, Vol, Price, S/L, T/P, Date_Exit, State, Comment, Profit, Balance
    # Since columns can vary, let's just inspect the rows.
    
    parsed_deals = []
    
    for idx, row in deals_table.iterrows():
        try:
            date_str = str(row.iloc[0])
            if '.' in date_str and ':' in date_str:
                dt = datetime.datetime.strptime(date_str, '%Y.%m.%d %H:%M:%S')
                
                # Check for symbol in row
                row_str = ' '.join([str(x) for x in row.values])
                
                symbol = None
                for sym in ['XAUUSD', 'GBPJPY', 'XAGUSD', 'USDJPY', 'EURUSD', 'AUDUSD']:
                    if sym in row_str:
                        symbol = sym
                        break
                        
                if not symbol:
                    continue
                    
                # Find profit (usually 2nd to last number, or last number if balance is empty)
                # Let's extract all numbers
                row_vals = row.values
                val = None
                
                # In MT5 deals, closed deals have profit. Let's find the profit.
                # It's usually the last number smaller than 50k
                nums = []
                for v in reversed(row_vals):
                    try:
                        v_str = str(v).replace(' ', '')
                        num = float(v_str)
                        nums.append(num)
                    except:
                        continue
                
                # The first number from the right is usually balance (if it exists and > 50k).
                # The next number from the right is profit.
                profit = None
                for n in nums:
                    if abs(n) < 50000 and abs(n) > 0: # Profit shouldn't exceed 50k per trade usually
                        profit = n
                        break
                        
                if profit is not None and ('sell' in row_str.lower() or 'buy' in row_str.lower() or 'tp' in row_str.lower() or 'sl' in row_str.lower()):
                    # Avoid duplicate counting (MT5 has an "in" and "out" deal for a trade, "in" deal has 0 profit)
                    # We only care about deals that closed and had profit/loss
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
    
    # Calculate IS / OOS mapping
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
    
    # Group by Year, Symbol, Zone
    agg = df.groupby(['Year', 'Symbol', 'Zone'])['Profit'].agg(['sum', 'count']).reset_index()
    agg = agg.sort_values(by=['Year', 'Symbol'])
    
    # Also total per symbol
    totals = df.groupby(['Symbol', 'Zone'])['Profit'].agg(['sum', 'count']).reset_index()
    
    print('\n--- ANNUAL REPORT ---')
    print(agg.to_string())
    
    print('\n--- TOTALS BY SYMBOL ---')
    print(totals.to_string())
    
    # Save to a CSV for easier reading by AI
    agg.to_csv(r'C:\Users\Manuel\.gemini\antigravity\brain\5fbebb0b-cbfe-47dc-9d97-f804c2687de4\scratch\report_v9.csv', index=False)
    
except Exception as e:
    print('Failed:', str(e))
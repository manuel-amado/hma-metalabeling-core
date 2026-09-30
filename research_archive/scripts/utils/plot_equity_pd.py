import pandas as pd
import datetime
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

html_path = r'C:\Users\Manuel\Documents\BACKTESTS\ReportTester-1513981369.html'
print('Reading HTML with pandas...')

try:
    tables = pd.read_html(html_path)
    print(f'Found {len(tables)} tables.')
    
    # The deals table is usually the largest table (index -1 or -2)
    deals_table = sorted(tables, key=lambda t: len(t))[-1]
    
    print(f'Deals table shape: {deals_table.shape}')
    
    # Typically MT5 Deals table columns are something like: [Time, Order, Symbol, Type, Vol, Price, S/L, T/P, Time, State, Comment, Profit, Balance]
    # We just need to find the column with Date and the column with Balance.
    # To be safe, if we dropna on the column and try parsing as date
    
    date_col = None
    balance_col = None
    
    # Usually first column is Date.
    dates = []
    balances = []
    
    # Iterate through rows
    for idx, row in deals_table.iterrows():
        try:
            date_str = str(row.iloc[0])
            if '.' in date_str and ':' in date_str:
                dt = datetime.datetime.strptime(date_str, '%Y.%m.%d %H:%M:%S')
                
                # Balance is usually the last column that is numeric and increasing (or profit is second to last)
                # Let's take the last numeric value in the row
                row_vals = row.values
                val = None
                for v in reversed(row_vals):
                    try:
                        v_str = str(v).replace(' ', '')
                        num = float(v_str)
                        if num > 50000: # We started at 100k
                            val = num
                            break
                    except:
                        continue
                        
                if val is not None:
                    dates.append(dt)
                    balances.append(val)
        except Exception as e:
            pass

    print(f'Extracted {len(balances)} valid balance points.')
    
    if len(balances) > 50000:
        dates = dates[::5]
        balances = balances[::5]

    start_date = datetime.datetime(2015, 1, 1)
    end_date = datetime.datetime(2026, 7, 1)
    total_days = (end_date - start_date).days
    block_days = total_days / 10.0

    plt.figure(figsize=(14, 7))
    plt.plot(dates, balances, color='#00aaff', linewidth=1.5, label='Equity Curve')

    for i in range(10):
        b_start = start_date + datetime.timedelta(days=i*block_days)
        b_end = start_date + datetime.timedelta(days=(i+1)*block_days)
        if i in [2, 5, 8]:
            plt.axvspan(b_start, b_end, color='red', alpha=0.15, label='OOS (Out of Sample)' if i==2 else "")
        else:
            plt.axvspan(b_start, b_end, color='green', alpha=0.1, label='IS (In Sample)' if i==0 else "")

    plt.title('Alpha_Sniper_v8: IS vs OOS Interleaved Robustness Validation', fontsize=16, fontweight='bold', color='#333333')
    plt.xlabel('Date', fontsize=12)
    plt.ylabel('Balance (USD)', fontsize=12)
    plt.grid(True, linestyle='--', alpha=0.5)
    plt.legend(loc='upper left')

    plt.tight_layout()
    out_path = r'C:\Users\Manuel\.gemini\antigravity\brain\5fbebb0b-cbfe-47dc-9d97-f804c2687de4\equity_oos_shading.png'
    plt.savefig(out_path, dpi=150)
    print(f'Plot saved successfully to {out_path}')
    
except Exception as e:
    print('Failed with Pandas:', str(e))
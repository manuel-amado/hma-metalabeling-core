import pandas as pd
import numpy as np

filepath = r'C:\Users\Manuel\Documents\BACKTESTS\ReportTester-1514246756.html'
with open(filepath, 'r', encoding='utf-16', errors='ignore') as f:
    html = f.read()

active_positions = {}
weekend_trades = []
weekday_trades = []

for line in html.split('\n'):
    if 'bgcolor' in line and '<td' in line:
        tds = [td.split('>')[1].split('<')[0].strip() for td in line.split('<td')[1:]]
        if len(tds) >= 12:
            time_str = tds[0].replace('.', '-')
            sym = tds[2]
            action = tds[4]
            try:
                dt = pd.to_datetime(time_str)
            except:
                continue
            if action == 'in':
                active_positions[sym] = {'open_time': dt, 'open_day': dt.weekday()}
            elif action == 'out' or action == 'in/out':
                if sym in active_positions:
                    open_info = active_positions[sym]
                    profit = float(tds[10].replace(' ', ''))
                    
                    is_weekend = False
                    days_held = (dt.date() - open_info['open_time'].date()).days
                    if days_held >= 2 and (open_info['open_time'].weekday() >= 3 or dt.weekday() <= 2):
                        if (dt - open_info['open_time']).total_seconds() > 48*3600:
                            is_weekend = True
                    
                    trade = {'Sym': sym, 'Profit': profit, 'Days': days_held}
                    if is_weekend:
                        weekend_trades.append(trade)
                    else:
                        weekday_trades.append(trade)
                    if action == 'out':
                        del active_positions[sym]

wd = pd.DataFrame(weekday_trades)
we = pd.DataFrame(weekend_trades)

print("INTRA-WEEK MAX LOSS:", wd['Profit'].min())
print("INTRA-WEEK MAX WIN:", wd['Profit'].max())
print("WEEKEND MAX LOSS:", we['Profit'].min())
print("WEEKEND MAX WIN:", we['Profit'].max())
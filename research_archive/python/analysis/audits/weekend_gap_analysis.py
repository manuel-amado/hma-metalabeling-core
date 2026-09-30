import pandas as pd
import numpy as np

filepath = r'C:\Users\Manuel\Documents\BACKTESTS\ReportTester-1514246756.html'
with open(filepath, 'r', encoding='utf-16', errors='ignore') as f:
    html = f.read()

active_positions = {} # symbol -> { 'open_time': dt, 'open_day': int }
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
                    # Weekend check: if open day is before Friday (or Friday), and close day is next week.
                    # Or simply: if the timedelta spans over a weekend
                    days_held = (dt.date() - open_info['open_time'].date()).days
                    # If open on Friday (4) and close on Monday (0), days_held is 3
                    
                    # Alternatively, checking if weekday of close < weekday of open AND days_held > 0
                    if days_held >= 2 and (open_info['open_time'].weekday() >= 3 or dt.weekday() <= 2):
                        # roughly spans weekend
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

def analyze(df, name):
    if len(df) == 0:
        return f"{name}: No data"
    wins = df[df['Profit'] > 0]
    wr = len(wins) / len(df) * 100
    net = df['Profit'].sum()
    avg = df['Profit'].mean()
    return f"{name:15} | Trades: {len(df):4} | Win Rate: {wr:5.1f}% | Net Profit: ${net:10,.2f} | Avg: ${avg:6,.2f}"

print("=== Análisis de Operaciones de Fin de Semana (V16.1) ===")
print(analyze(wd, "Intrasemanal"))
print(analyze(we, "Fin de Semana"))

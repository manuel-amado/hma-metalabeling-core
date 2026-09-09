import pandas as pd

filepath = r'C:\Users\Manuel\Documents\BACKTESTS\ReportTester-1514246756.html'
with open(filepath, 'r', encoding='utf-16', errors='ignore') as f:
    html = f.read()

parsed_out = []
parsed_in = {}

for line in html.split('\n'):
    if '>in<' in line or '>in/out<' in line or '>out<' in line:
        tds = line.split('<td')
        if len(tds) >= 12:
            try:
                time_str = tds[1].split('>')[1].split('<')[0].replace('.', '-')
                ticket = tds[2].split('>')[1].split('<')[0]
                action = tds[5].split('>')[1].split('<')[0]
                
                if action == 'in':
                    parsed_in[ticket] = pd.to_datetime(time_str)
                elif action == 'out':
                    profit = float(tds[11].split('>')[1].split('<')[0].replace(' ', ''))
                    parsed_out.append({
                        'CloseTime': pd.to_datetime(time_str),
                        'Ticket': ticket,
                        'Profit': profit
                    })
            except: pass

# Unfortunately, the Deals table tickets don't easily map IN to OUT tickets in MT5 unless we use Position ID.
# Let's use the Orders/Positions table instead for exact Open and Close time of the same position.
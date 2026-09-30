import re
import datetime
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

html_path = r'C:\Users\Manuel\Documents\BACKTESTS\ReportTester-1513981369.html'

dates = []
balance_curve = []
current_balance = 100000.0

with open(html_path, 'r', encoding='utf-8', errors='ignore') as f:
    for line in f:
        # MT5 html rows are usually single lines per <tr>
        if '<tr' in line and '</tr>' in line:
            # check if it has a date
            m_date = re.search(r'<td>(\d{4}\.\d{2}\.\d{2} \d{2}:\d{2}:\d{2})</td>', line)
            if m_date:
                # Find all td values
                tds = re.findall(r'<td[^>]*>(.*?)</td>', line)
                if len(tds) >= 8:
                    # The second to last or last might be the profit. Let's look for closed trades:
                    # Deals that close a trade have a non-zero profit/loss.
                    # Usually MT5 deal table: date | deal | symbol | type | dir | vol | price | order | comm | swap | profit | balance
                    # If we just extract all numbers from the end of the row
                    nums = []
                    for t in reversed(tds):
                        val = t.replace(' ', '')
                        if re.match(r'^-?\d+(\.\d+)?$', val):
                            nums.append(float(val))
                    
                    if len(nums) >= 2:
                        # nums[0] is usually balance, nums[1] is profit
                        # Or if balance is omitted, nums[0] is profit.
                        # Let's just track cumulative profit!
                        # The profit column is usually before the balance column.
                        profit = nums[1] if len(nums) > 1 and nums[0] > 50000 else nums[0]
                        
                        # Only add if it's a real closed deal (profit != 0 or it's a trade close)
                        if 'sell' in line or 'buy' in line or 'tp' in line or 'sl' in line:
                            # To be safe and just get the curve, if nums[0] is a large number > 50k, it's the balance
                            if nums[0] > 50000:
                                balance_curve.append(nums[0])
                                dt = datetime.datetime.strptime(m_date.group(1), '%Y.%m.%d %H:%M:%S')
                                dates.append(dt)

if len(balance_curve) == 0:
    print('Still 0. Trying pure profit summation logic...')
    current_balance = 100000.0
    with open(html_path, 'r', encoding='utf-8', errors='ignore') as f:
        for line in f:
            if '<tr' in line and ('sell' in line.lower() or 'buy' in line.lower() or 'tp' in line.lower() or 'sl' in line.lower()):
                m_date = re.search(r'>(\d{4}\.\d{2}\.\d{2} \d{2}:\d{2}:\d{2})<', line)
                if m_date:
                    tds = re.findall(r'>([^<]+)<', line)
                    nums = []
                    for t in reversed(tds):
                        val = t.replace(' ', '')
                        if re.match(r'^-?\d+(\.\d+)?$', val):
                            nums.append(float(val))
                    if len(nums) >= 1:
                        # Usually profit is the last small number before balance
                        profit_candidates = [n for n in nums if abs(n) < 10000 and abs(n) > 0]
                        if len(profit_candidates) > 0:
                            current_balance += profit_candidates[0] # assuming the last small number is profit
                            dt = datetime.datetime.strptime(m_date.group(1), '%Y.%m.%d %H:%M:%S')
                            dates.append(dt)
                            balance_curve.append(current_balance)
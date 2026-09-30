import re
import datetime
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

html_path = r'C:\Users\Manuel\Documents\BACKTESTS\ReportTester-1513981369.html'

with open(html_path, 'r', encoding='utf-8', errors='ignore') as f:
    content = f.read()

# Instead of bs4, let's just do a highly robust regex for the balance updates
# We know the date pattern "YYYY.MM.DD HH:MM:SS"
# We know balance is typically the largest number at the end of the row
# But wait, deals in MT5: the balance is only updated on closing trades (sell/buy in out).
# MT5 report "Transacciones" has "balance" row or standard close deal row.
# A simpler approach: Just parse the file for all matches of:
# >YYYY.MM.DD HH:MM:SS</td>.....<td>123456.78</td></tr>
# We can use a regex that captures the date, and the LAST number before </td></tr>

pattern = re.compile(r'>(\d{4}\.\d{2}\.\d{2} \d{2}:\d{2}:\d{2})</td>.*?<td[^>]*>(-?\d+(\.\d+)?)</td></tr>', re.DOTALL)
matches = pattern.findall(content)

dates = []
balance_curve = []

for m in matches:
    date_str = m[0]
    val_str = m[1]
    
    try:
        val = float(val_str)
        if val > 50000: # It's a balance since we start at 100k
            dt = datetime.datetime.strptime(date_str, '%Y.%m.%d %H:%M:%S')
            dates.append(dt)
            balance_curve.append(val)
    except:
        pass

# Ensure chronological order
if len(dates) > 0:
    combined = sorted(zip(dates, balance_curve), key=lambda x: x[0])
    dates, balance_curve = zip(*combined)

print(f'Extracted {len(balance_curve)} points.')

if len(balance_curve) == 0:
    # Let's try profit sum if balance column is missing
    current_balance = 100000.0
    profit_pattern = re.compile(r'>(\d{4}\.\d{2}\.\d{2} \d{2}:\d{2}:\d{2})</td>.*?<td[^>]*>(-?\d+(\.\d+)?)</td>(?:<td[^>]*>.*?</td>)?</tr>', re.DOTALL)
    print("Trying alternative extraction...")
    exit()

if len(balance_curve) > 50000:
    dates = dates[::5]
    balance_curve = balance_curve[::5]

start_date = datetime.datetime(2015, 1, 1)
end_date = datetime.datetime(2026, 7, 1)
total_days = (end_date - start_date).days
block_days = total_days / 10.0

plt.figure(figsize=(14, 7))
plt.plot(dates, balance_curve, color='#00aaff', linewidth=1.5, label='Equity Curve')

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
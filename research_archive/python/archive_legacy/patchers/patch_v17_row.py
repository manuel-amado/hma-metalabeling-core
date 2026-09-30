import os

filepath = r'C:\Users\Manuel\Desktop\HMA_MetaLabeling\Alpha_Sniper_Vault\mql5\Alpha_Sniper_v17.mq5'
with open(filepath, 'r', encoding='utf-8') as f:
    content = f.read()

# We need to prepend the TimeToString to the row
old_code = """
                        if(m_csv_handle != INVALID_HANDLE) {
                            string row = "";
                            for(int f = 0; f < 26; f++) row += StringFormat("%f,", m_saved_features[f]);
                            row += StringFormat("%f,%d\\n", return_pct, label);
                            FileWriteString(m_csv_handle, row);
                            FileFlush(m_csv_handle);
                        }
"""

new_code = """
                        if(m_csv_handle != INVALID_HANDLE) {
                            string row = TimeToString(m_saved_open_time, TIME_DATE|TIME_MINUTES) + ",";
                            for(int f = 0; f < 26; f++) row += StringFormat("%f,", m_saved_features[f]);
                            row += StringFormat("%f,%d\\n", return_pct, label);
                            FileWriteString(m_csv_handle, row);
                            FileFlush(m_csv_handle);
                        }
"""

content = content.replace(old_code.strip(), new_code.strip())

with open(filepath, 'w', encoding='utf-8') as f:
    f.write(content)
print("Row writing fixed")
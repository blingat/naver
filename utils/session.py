import os
import datetime

def clean_old_comments(file_path, days=7):
    if not os.path.exists(file_path):
        return
    lines = []
    now = datetime.datetime.now()
    with open(file_path, 'r', encoding='utf-8') as f:
        for line in f:
            if line.startswith('#') or not line.strip():
                lines.append(line)
                continue
            try:
                url, date_str = line.strip().split(',')
                date = datetime.datetime.strptime(date_str, '%Y-%m-%d')
                if (now - date).days <= days:
                    lines.append(line)
            except:
                continue
    with open(file_path, 'w', encoding='utf-8') as f:
        f.writelines(lines) 
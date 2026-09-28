import glob, os, sys
sys.path.insert(0, '.')
from scripts.parser_engine import read_tabular_file, get_exact_val, clean_key

files = glob.glob('raw_data/data (*).xlsx')
latest_file = sorted(files, key=os.path.getmtime)[-1]
datasets = read_tabular_file(latest_file)
leads_rows = datasets[0][1] if datasets else []

lines = []
lines.append(f'Latest leads file: {latest_file}, rows: {len(leads_rows)}')
if leads_rows:
    lines.append('Keys: ' + ', '.join(leads_rows[0].keys()))

sber_leads = []
for r in leads_rows:
    p = str(get_exact_val(r, 'BI', 'ПАРТНЕР') or '')
    if 'сбер' in p.lower():
        sber_leads.append(r)

lines.append(f'Total sber leads: {len(sber_leads)}')

contact_counts = {}
for r in sber_leads:
    c = str(get_exact_val(r, 'НАЗВАНИЕКОНТАКТА', 'КОНТАКТ') or 'ПУСТО')
    contact_counts[c] = contact_counts.get(c, 0) + 1

lines.append('Contacts count:')
for c, cnt in sorted(contact_counts.items(), key=lambda x: -x[1])[:60]:
    lines.append(f'  {cnt}: {c}')

with open('temp_sber_leads_utf8.txt', 'w', encoding='utf-8') as f:
    f.write('\n'.join(lines))
print('Done writing temp_sber_leads_utf8.txt')

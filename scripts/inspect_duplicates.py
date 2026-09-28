import json
from collections import defaultdict

with open('partners_registry.json', 'r', encoding='utf-8') as f:
    reg = json.load(f)

partners = reg.get('partners', [])
print(f'Total partners: {len(partners)}')

print('=== SPECIFIC SEARCH (Автопрестиж, Прагматика) ===')
for p in partners:
    cname = p.get('canonical_name', '')
    pid = p.get('id')
    if any(k in cname.lower() for k in ['автопрестиж', 'прагматик']):
        print(f"ID {pid}: '{cname}' | KAM: {p.get('kam')}")
        print(f"  bitrix: {p.get('bitrix_names', [])}")
        print(f"  bi: {p.get('bi_names', [])}")
        print(f"  pochta: {p.get('pochta_names', [])}")

print('\n=== CHECKING FOR DUPLICATE CANONICAL NAMES OR OBVIOUS DUPLICATES ===')
by_name = defaultdict(list)
for p in partners:
    name_clean = p.get('canonical_name', '').strip().lower()
    by_name[name_clean].append(p)

for name, p_list in by_name.items():
    if len(p_list) > 1:
        ids = [p.get('id') for p in p_list]
        kams = [p.get('kam') for p in p_list]
        print(f"Exact duplicate canonical_name '{name}': IDs={ids}, KAMs={kams}")

print('\n=== CHECKING ALL ACTIVE PARTNERS IN DATA.JSON ===')
with open('data.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

sys_db_partners = data.get('sys_db_partners', [])
active_partners = defaultdict(lambda: {'leads': 0, 'deals': 0, 'prepays': 0, 'kam': '', 'names': set()})
for r in sys_db_partners:
    pid = r.get('PartnerId')
    pname = r.get('Partner')
    t = r.get('Type')
    active_partners[pid]['names'].add(pname)
    active_partners[pid]['kam'] = r.get('KAM')
    if t == 'Лид':
        active_partners[pid]['leads'] += 1
    elif t == 'Сделка':
        active_partners[pid]['deals'] += 1
    elif t == 'Предоплата':
        active_partners[pid]['prepays'] += 1

print(f"Total active partner IDs in sys_db_partners: {len(active_partners)}")
# Group active partners by normalized root names to find split companies
import re

def get_root_name(s):
    s = s.lower()
    s = re.sub(r'^(ооо|зао|пао|ао|гк|тц|фдц|дц|онлайн|online|приоритет_|приоритет)\s+', '', s)
    s = re.sub(r'\s+(пилот|новые|бу|б/у|online|онлайн|спб|мск|екб|крд).*', '', s)
    s = re.sub(r'[^a-zа-я0-9]', '', s)
    return s

roots = defaultdict(list)
for pid, info in active_partners.items():
    for n in info['names']:
        if not n: continue
        r = get_root_name(n)
        if len(r) >= 4:
            roots[r].append((pid, n, info['kam'], info['deals'], info['leads'], info['prepays']))

print('\n=== POTENTIAL SPLIT PARTNERS IN ACTIVE DATA ===')
for r, plist in sorted(roots.items()):
    # deduplicate by pid
    unique_pids = {item[0] for item in plist}
    if len(unique_pids) > 1:
        print(f"Root '{r}':")
        seen = set()
        for item in plist:
            if item[0] not in seen:
                seen.add(item[0])
                print(f"  ID {item[0]}: '{item[1]}' | KAM: {item[2]} | Deals: {item[3]}, Leads: {item[4]}, Prepays: {item[5]}")

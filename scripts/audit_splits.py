import json
from collections import defaultdict
import re

with open('partners_registry.json', 'r', encoding='utf-8') as f:
    reg = json.load(f)

partners = reg.get('partners', [])

with open('data.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

sys_db_partners = data.get('sys_db_partners', [])

# Map active usage: for each partner ID, collect total deals, leads, prepays, names, and raw partners
active_by_id = defaultdict(lambda: {
    'canonical_names': set(),
    'raw_partners': set(),
    'kam': '',
    'deals': 0,
    'leads': 0,
    'prepays': 0
})

for r in sys_db_partners:
    pid = r.get('PartnerId')
    pname = r.get('Partner')
    rp = r.get('RawPartner')
    t = r.get('Type')
    kam = r.get('KAM')
    
    active_by_id[pid]['canonical_names'].add(pname)
    if rp: active_by_id[pid]['raw_partners'].add(rp)
    if kam and not active_by_id[pid]['kam']: active_by_id[pid]['kam'] = kam
    
    if t == 'Лид':
        active_by_id[pid]['leads'] += 1
    elif t == 'Сделка':
        active_by_id[pid]['deals'] += 1
    elif t == 'Предоплата':
        active_by_id[pid]['prepays'] += 1

# Normalize text for matching
def clean_norm(s):
    if not s: return ''
    s = s.lower()
    # remove legal forms
    s = re.sub(r'\b(ооо|зао|пао|ао|гк|тц|фдц|дц|ип|онлайн|online|пилот|новые|used|new|б/у|бу)\b', '', s)
    s = re.sub(r'^(приоритет_|приоритет)\s*', '', s)
    s = re.sub(r'[^a-zа-я0-9]', '', s)
    return s

# Group by normalized root
partner_dict_by_id = {}
for p in partners:
    pid = p.get('partner_id') or p.get('id')
    partner_dict_by_id[pid] = p

print("=== ANALYSIS OF ACTIVE SPLITS ===")
# Check active IDs
active_ids = [pid for pid in active_by_id if pid is not None]

# Group active IDs by normalized name
root_groups = defaultdict(list)
for pid in active_ids:
    names = active_by_id[pid]['canonical_names']
    for n in names:
        rn = clean_norm(n)
        if len(rn) >= 4:
            root_groups[rn].append(pid)

split_candidates = {}
for rn, pids in root_groups.items():
    uniq = sorted(list(set(pids)), key=str)
    if len(uniq) > 1:
        split_candidates[rn] = uniq

with open('active_splits.txt', 'w', encoding='utf-8') as out:
    for rn, pids in sorted(split_candidates.items()):
        out.write(f"\n==================== ROOT: '{rn}' ====================\n")
        for pid in pids:
            info = active_by_id[pid]
            p_obj = partner_dict_by_id.get(pid, {})
            out.write(f"  ID {pid}: Canonical in registry: '{p_obj.get('canonical_name')}'\n")
            out.write(f"      Names in data: {list(info['canonical_names'])}\n")
            out.write(f"      KAM: {info['kam']}\n")
            out.write(f"      Stats -> Deals: {info['deals']}, Leads: {info['leads']}, Prepays: {info['prepays']}\n")
            out.write(f"      Raw sample: {list(info['raw_partners'])[:3]}\n")

print(f"Found {len(split_candidates)} potential split groups written to active_splits.txt")

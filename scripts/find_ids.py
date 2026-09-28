import json

with open('partners_registry.json', 'r', encoding='utf-8') as f:
    reg = json.load(f)

target_ids = [1076, 1045, 1198, 1205, 1193, 1022]

for p in reg.get('partners', []):
    pid = p.get('id')
    if pid in target_ids:
        print(f"ID {pid}: canonical='{p.get('canonical_name')}', kam='{p.get('kam')}'")
        print(f"   bitrix: {p.get('bitrix_names')}")
        print(f"   bi: {p.get('bi_names')}")
        print(f"   pochta: {p.get('pochta_names')}")

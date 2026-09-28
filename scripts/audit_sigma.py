import json

with open('partners_registry.json', encoding='utf-8') as f:
    reg = json.load(f)

lines = []
for p in reg['partners']:
    raw = json.dumps(p, ensure_ascii=False)
    if any(k in raw.lower() for k in ['сигма', '1011', '1012', '1013', '1024']):
        lines.append(f"PID: {p['partner_id']} | NAME: {p['canonical_name']} | KAM: {p.get('kam')}")
        lines.append(f"  bitrix: {p.get('bitrix_aliases')}")
        lines.append(f"  bi: {p.get('bi_aliases')}")
        lines.append(f"  pochta: {p.get('pochta_aliases')}")

with open('temp_sigma_audit.txt', 'w', encoding='utf-8') as f:
    f.write('\n'.join(lines))

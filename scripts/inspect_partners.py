import json

with open('partners_registry.json', encoding='utf-8') as f:
    reg = json.load(f)

lines = []
for p in reg['partners']:
    cname = p['canonical_name']
    pid = p['partner_id']
    kam = p.get('kam')
    if any(w in cname.lower() for w in ['авторитет', 'сигма', 'премиум', 'сберавто', 'автодель', 'тверь', 'союз']):
        lines.append(f"{pid}: {cname} | KAM: {kam} | bitrix: {p.get('bitrix_aliases')} | bi: {p.get('bi_aliases')} | pochta: {p.get('pochta_aliases')}")

with open('temp_partners_out.txt', 'w', encoding='utf-8') as f:
    f.write('\n'.join(lines))
print(f"Wrote {len(lines)} partners")

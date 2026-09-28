import json

with open('partners_registry.json', encoding='utf-8') as f:
    reg = json.load(f)

lines = []
for p in reg['partners']:
    if 'авторитет' in p['canonical_name'].lower() or p['partner_id'] == 1138:
        lines.append(f"REGISTRY PARTNER {p['partner_id']}: {p['canonical_name']} | kam={p.get('kam')}")
        lines.append(f"  bitrix_aliases: {p.get('bitrix_aliases')}")
        lines.append(f"  bi_aliases: {p.get('bi_aliases')}")
        lines.append(f"  pochta_aliases: {p.get('pochta_aliases')}")
        lines.append(f"  oem_data: {p.get('oem_data')}")

with open('data.json', encoding='utf-8') as f:
    d = json.load(f)

lines.append("\n=== DEALS FOR АВТОРИТЕТ ===")
for deal in d.get('deals', []):
    pname = str(deal.get('PartnerName', ''))
    pid = str(deal.get('PartnerId', ''))
    if 'авторитет' in pname.lower() or pid == '1138':
        lines.append(f"DEAL #{deal.get('DealId')}: pid={pid} | name={pname} | brand={deal.get('Brand')} | city={deal.get('City')} | kam={deal.get('KAM')} | month={deal.get('SaleMonth')}")

lines.append("\n=== SYS_DB_PARTNERS FOR АВТОРИТЕТ ===")
for r in d.get('sys_db_partners', []):
    pname = str(r.get('Partner', ''))
    pid = str(r.get('PartnerId', ''))
    if 'авторитет' in pname.lower() or pid == '1138':
        lines.append(f"DB: pid={pid} | name={pname} | kam={r.get('KAM')} | brand={r.get('Brand')} | month={r.get('Month')} | type={r.get('Type')} | count={r.get('Qty', r.get('Count', 1))}")

with open('temp_avtoritet_audit.txt', 'w', encoding='utf-8') as f:
    f.write('\n'.join(lines))

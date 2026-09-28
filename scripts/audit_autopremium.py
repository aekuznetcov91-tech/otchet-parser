import json

with open('data.json', encoding='utf-8') as f:
    d = json.load(f)

lines = []
lines.append("=== DEALS FOR АВТОПРЕМИУМ / ПРЕМИУМ АВТО / СОЮЗ-Т ===")
for deal in d.get('deals', []):
    pname = str(deal.get('PartnerName', ''))
    pid = str(deal.get('PartnerId', ''))
    city = str(deal.get('City', ''))
    if any(k in pname.lower() for k in ['автопремиум', 'авто премиум', 'премиум авто', 'союз-т']) or pid in ['1012', '1040', '632032']:
        lines.append(f"DEAL #{deal.get('DealId')}: pid={pid} | name={pname} | brand={deal.get('Brand')} | city={city} | kam={deal.get('KAM')} | month={deal.get('SaleMonth')}")

lines.append("\n=== SYS_DB_PARTNERS ===")
for r in d.get('sys_db_partners', []):
    pname = str(r.get('Partner', ''))
    pid = str(r.get('PartnerId', ''))
    if any(k in pname.lower() for k in ['автопремиум', 'авто премиум', 'премиум авто', 'союз-т']) or pid in ['1012', '1040', '632032']:
        lines.append(f"DB: pid={pid} | name={pname} | kam={r.get('KAM')} | month={r.get('Month')} | type={r.get('Type')} | count={r.get('Qty', r.get('Count', 1))}")

with open('temp_autopremium_audit.txt', 'w', encoding='utf-8') as f:
    f.write('\n'.join(lines))

import json

with open('data.json', encoding='utf-8') as f:
    d = json.load(f)

lines = []
lines.append("=== 1. ALL DEALS FOR СИГМА ===")
deals = d.get('deals', [])
for deal in deals:
    pname = str(deal.get('PartnerName', ''))
    pid = str(deal.get('PartnerId', ''))
    if any(k in pname.lower() for k in ['сигма', 'автопремиум', 'премиум авто', 'авторитет', 'союз-т', 'сберавто']):
        lines.append(f"DEAL: id={deal.get('DealId')} | p_id={pid} | p_name={pname} | brand={deal.get('Brand')} | city={deal.get('City')} | month={deal.get('SaleMonth')} | kam={deal.get('KAM')}")

lines.append("\n=== 2. SYS_DB_PARTNERS FOR RELEVANT PARTNERS ===")
for p in d.get('sys_db_partners', []):
    name = str(p.get('Dealer', ''))
    pid = str(p.get('PartnerId', ''))
    kam = str(p.get('KAM', ''))
    if any(k in name.lower() for k in ['сигма', 'автопремиум', 'премиум авто', 'авторитет', 'союз-т', 'сберавто']):
        lines.append(f"DB_PARTNER: id={pid} | name={name} | kam={kam} | month={p.get('Month')} | type={p.get('Type')} | count={p.get('Count', 1)}")

lines.append("\n=== 3. LEAD_GEO_DEALERS FOR RELEVANT PARTNERS ===")
for p in d.get('lead_geo_dealers', []):
    name = str(p.get('partner_name', ''))
    dname = str(p.get('dealer_name', ''))
    kam = str(p.get('kam', ''))
    if any(k in (name + ' ' + dname).lower() for k in ['сигма', 'автопремиум', 'премиум авто', 'авторитет', 'союз-т', 'сберавто']):
        lines.append(f"GEO_DEALER: p_name={name} | d_name={dname} | brand={p.get('brand')} | city={p.get('city')} | kam={kam} | month={p.get('month')} | trans={p.get('trans_clients')}")

with open('temp_audit_4_issues.txt', 'w', encoding='utf-8') as f:
    f.write('\n'.join(lines))
print(f"Audit wrote {len(lines)} lines")

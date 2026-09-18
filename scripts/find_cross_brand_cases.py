import sys
import os
import re
import datetime
from collections import defaultdict

sys.path.append('.')
from scripts.parser_engine import read_tabular_file, parse_custom_date, normalize_brand, clean_key, get_exact_val

print("Loading completed deals from June to September...")

# 1. Deals from reestr_work (covers June - August)
reestr_fpath = 'raw_data/reestr_work_июнь _авг_filled(итог)_v2.xlsx'
reestr_datasets = read_tabular_file(reestr_fpath)

all_deals = []
seen_deal_keys = set()

for sname, rows in reestr_datasets:
    for r in rows:
        stage = str(get_exact_val(r, 'СТАДИЯСДЕЛКИ', 'СТАДИЯ') or '').upper()
        tovar = str(get_exact_val(r, 'ТОВАР') or '').strip()
        is_prepay = "ВНЕСЕНИЕ АВАНСА" in tovar.upper()
        is_sale = ("ЗАКРЫТО И РЕАЛИЗОВАН" in stage) and not is_prepay
        if not is_sale:
            continue
        
        cid = str(get_exact_val(r, 'CLIENTID', 'CLIENT_ID', 'IDКЛИЕНТА') or '').strip()
        if not cid:
            continue
        
        did = str(get_exact_val(r, 'ID', 'IDСДЕЛКИ') or '').strip()
        vin = str(get_exact_val(r, 'VIN', 'VINНОМЕР') or '').strip()
        if not vin:
            words = tovar.split()
            if words and len(words[-1]) > 10 and bool(re.search(r'[A-Z0-9]', words[-1])):
                vin = words[-1]
            else:
                vin = did
        
        dt_val = get_exact_val(r, 'ПРЕДПОЛАГАЕМАЯДАТАЗАКРЫТИЯ', 'ДАТАЗАКРЫТИЯ')
        d_dt = parse_custom_date(dt_val)
        
        try:
            price = float(str(get_exact_val(r, 'ФИНАЛЬНАЯЦЕНАB2C', 'ЦЕНА') or 0).replace(' ', '').replace('\xa0', '').replace(',', '.'))
        except ValueError:
            price = 0.0
            
        try:
            comm = float(str(get_exact_val(r, 'КОМИССИЯСДЕЛКИРУБ', 'КОМИССИЯСДЕЛКИ') or 0).replace(' ', '').replace('\xa0', '').replace(',', '.'))
        except ValueError:
            comm = 0.0

        b2c = str(get_exact_val(r, 'ТИПСДЕЛКИB2C', 'ТИПСДЕЛКИ') or '').strip()
        mgr = str(get_exact_val(r, 'МЕНЕДЖЕРСДЕЛКИ', 'МЕНЕДЖЕР') or '').strip()
        comp = str(get_exact_val(r, 'КОМПАНИЯНАЗВАНИЕКОМПАНИИ', 'КОМПАНИЯ') or '').strip()

        brand = normalize_brand(tovar)
        
        deal_key = f"{did}::{vin}" if (did and vin) else f"{cid}::{tovar}::{d_dt}"
        if deal_key in seen_deal_keys:
            continue
        seen_deal_keys.add(deal_key)
        
        all_deals.append({
            'client_id': cid,
            'deal_id': did,
            'vin': vin,
            'date': d_dt,
            'date_str': d_dt.strftime('%d.%m.%Y') if d_dt else '',
            'month': d_dt.strftime('%Y-%m') if d_dt else '',
            'brand': brand,
            'tovar': tovar,
            'price': price,
            'comm': comm,
            'b2c': b2c,
            'manager': mgr,
            'company': comp,
            'source_file': 'reestr_work'
        })

print(f"Loaded {len(all_deals)} sales from reestr_work.")

# 2. Deals from latest Bitrix export (covers fresh September deals)
latest_bitrix_fpath = 'raw_data/DEAL_20260917_49024c28_6aab926388945.xls'
bitrix_datasets = read_tabular_file(latest_bitrix_fpath)
bitrix_added = 0

for sname, rows in bitrix_datasets:
    for r in rows:
        stream = str(get_exact_val(r, 'СТРИМ') or '').strip()
        if stream and stream != 'Импортеры':
            continue
        stage = str(get_exact_val(r, 'СТАДИЯСДЕЛКИ', 'СТАДИЯ') or '').upper()
        tovar = str(get_exact_val(r, 'ТОВАР') or '').strip()
        is_prepay = "ВНЕСЕНИЕ АВАНСА" in tovar.upper()
        is_sale = ("ЗАКРЫТО И РЕАЛИЗОВАН" in stage) and not is_prepay
        if not is_sale:
            continue
        
        cid = str(get_exact_val(r, 'CLIENTID', 'CLIENT_ID', 'IDКЛИЕНТА') or '').strip()
        if not cid:
            continue
        
        did = str(get_exact_val(r, 'ID', 'IDСДЕЛКИ') or '').strip()
        vin = str(get_exact_val(r, 'VIN', 'VINНОМЕР') or '').strip()
        if not vin:
            words = tovar.split()
            if words and len(words[-1]) > 10 and bool(re.search(r'[A-Z0-9]', words[-1])):
                vin = words[-1]
            else:
                vin = did

        deal_key = f"{did}::{vin}" if (did and vin) else f"{cid}::{tovar}"
        if deal_key in seen_deal_keys:
            continue
        seen_deal_keys.add(deal_key)
        
        dt_val = get_exact_val(r, 'ПРЕДПОЛАГАЕМАЯДАТАЗАКРЫТИЯ', 'ДАТАЗАКРЫТИЯ')
        d_dt = parse_custom_date(dt_val)
        
        try:
            price = float(str(get_exact_val(r, 'ФИНАЛЬНАЯЦЕНАB2C', 'ЦЕНА') or 0).replace(' ', '').replace('\xa0', '').replace(',', '.'))
        except ValueError:
            price = 0.0
            
        try:
            comm = float(str(get_exact_val(r, 'КОМИССИЯСДЕЛКИРУБ', 'КОМИССИЯСДЕЛКИ') or 0).replace(' ', '').replace('\xa0', '').replace(',', '.'))
        except ValueError:
            comm = 0.0

        b2c = str(get_exact_val(r, 'ТИПСДЕЛКИB2C', 'ТИПСДЕЛКИ') or '').strip()
        mgr = str(get_exact_val(r, 'МЕНЕДЖЕРСДЕЛКИ', 'МЕНЕДЖЕР') or '').strip()
        comp = str(get_exact_val(r, 'КОМПАНИЯНАЗВАНИЕКОМПАНИИ', 'КОМПАНИЯ') or '').strip()
        brand = normalize_brand(tovar)
        
        all_deals.append({
            'client_id': cid,
            'deal_id': did,
            'vin': vin,
            'date': d_dt,
            'date_str': d_dt.strftime('%d.%m.%Y') if d_dt else '',
            'month': d_dt.strftime('%Y-%m') if d_dt else '',
            'brand': brand,
            'tovar': tovar,
            'price': price,
            'comm': comm,
            'b2c': b2c,
            'manager': mgr,
            'company': comp,
            'source_file': 'DEAL_20260917'
        })
        bitrix_added += 1

print(f"Added {bitrix_added} new deals from DEAL_20260917. Total combined deals: {len(all_deals)}")

# Group deals by client_id
deals_by_client = defaultdict(list)
for d in all_deals:
    deals_by_client[d['client_id']].append(d)

print(f"Total unique buying clients: {len(deals_by_client)}")

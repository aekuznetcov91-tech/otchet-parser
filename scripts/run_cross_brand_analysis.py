import sys
import os
import re
import datetime
from collections import defaultdict
import pandas as pd

sys.path.append('.')
from scripts.parser_engine import read_tabular_file, parse_custom_date, normalize_brand, clean_key, get_exact_val

print("=== 1. Loading all completed deals (June - Sept 2026) ===")
# 1. Deals from reestr_work
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

# 2. Deals from latest Bitrix export
latest_bitrix_fpath = 'raw_data/DEAL_20260917_49024c28_6aab926388945.xls'
bitrix_datasets = read_tabular_file(latest_bitrix_fpath)
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

print(f"Total deals: {len(all_deals)}")
deals_by_client = defaultdict(list)
for d in all_deals:
    deals_by_client[d['client_id']].append(d)

print(f"Total clients with deals: {len(deals_by_client)}")

print("\n=== 2. Loading Partner Leads (Transfers / Переданные лиды) ===")
# Partner files: data (22).xlsx, data (49).xlsx, data (38).xlsx, data (40).xlsx
partner_files = ['raw_data/archive/data (22).xlsx', 'raw_data/data (49).xlsx', 'raw_data/data (40).xlsx', 'raw_data/data (38).xlsx']

partner_leads_by_client = defaultdict(list)
seen_partner_rows = set()

for pf in partner_files:
    if not os.path.exists(pf):
        continue
    ds = read_tabular_file(pf)
    loaded_pf = 0
    for sname, rows in ds:
        for r in rows:
            cid = str(get_exact_val(r, 'CLIENTID', 'CLIENT_ID', 'IDКЛИЕНТА') or '').strip()
            if not cid:
                continue
            b_raw = str(get_exact_val(r, 'БРЕНД') or '').strip()
            m_raw = str(get_exact_val(r, 'МОДЕЛЬ') or '').strip()
            partner = str(get_exact_val(r, 'ПАРТНЕР', 'КОМПАНИЯ') or '').strip()
            dt_val = get_exact_val(r, 'ДАТА', 'ДАТАСОБЫТИЯ')
            d_dt = parse_custom_date(dt_val)
            ev = str(get_exact_val(r, 'EVENT_NAME', 'СОБЫТИЕ') or 'Передача лида').strip()
            vin = str(get_exact_val(r, 'VIN') or '').strip()
            
            b_norm = normalize_brand(f"{b_raw} {m_raw}") or b_raw.upper()
            
            row_key = f"{cid}::{b_raw}::{m_raw}::{partner}::{d_dt}"
            if row_key in seen_partner_rows:
                continue
            seen_partner_rows.add(row_key)
            
            partner_leads_by_client[cid].append({
                'client_id': cid,
                'brand_raw': b_raw,
                'brand_norm': b_norm,
                'model': m_raw,
                'partner': partner,
                'date': d_dt,
                'date_str': d_dt.strftime('%d.%m.%Y') if d_dt else '',
                'event': ev,
                'vin': vin,
                'source': pf
            })
            loaded_pf += 1
    print(f"Loaded {loaded_pf} unique partner lead transfers from {pf}")

print(f"Total clients in partner transfers: {len(partner_leads_by_client)}")

print("\n=== 3. Loading General CRM Leads ===")
crm_files = ['raw_data/archive/data (23).xlsx', 'raw_data/data (48).xlsx']
crm_leads_by_client = defaultdict(list)
seen_crm_rows = set()

for cf in crm_files:
    if not os.path.exists(cf):
        continue
    ds = read_tabular_file(cf)
    loaded_cf = 0
    for sname, rows in ds:
        for r in rows:
            cid = str(get_exact_val(r, 'CLIENT_ID', 'CLIENTID', 'IDКЛИЕНТА') or '').strip()
            if not cid:
                continue
            b_raw = str(get_exact_val(r, 'БРЕНД') or '').strip()
            m_raw = str(get_exact_val(r, 'МОДЕЛЬ') or '').strip()
            det_raw = str(get_exact_val(r, 'ДЕТАЛИ') or '').strip()
            ev = str(get_exact_val(r, 'СОБЫТИЕ', 'EVENT_NAME') or '').strip()
            val = str(get_exact_val(r, 'ЗНАЧЕНИЕ') or '').strip()
            to_dealer = str(get_exact_val(r, 'ОТПРАВЛЕНДИЛЕРУ') or '').strip()
            dt_val = get_exact_val(r, 'ДАТАСОБЫТИЯ', 'ДАТАПЕРВОГОСОБЫТИЯ', 'ДАТА')
            d_dt = parse_custom_date(dt_val)
            mgr = str(get_exact_val(r, 'МЕНЕДЖЕР', 'ОТВЕТСТВЕННЫЙ') or '').strip()

            b_norm = normalize_brand(f"{b_raw} {m_raw} {det_raw}") or b_raw.upper()
            
            row_key = f"{cid}::{b_raw}::{m_raw}::{ev}::{val}::{d_dt}"
            if row_key in seen_crm_rows:
                continue
            seen_crm_rows.add(row_key)

            is_transferred = to_dealer in ('1', 'Да', 'да', 'true', 'True') or 'дилер' in ev.lower() or 'отправка' in ev.lower()
            
            crm_leads_by_client[cid].append({
                'client_id': cid,
                'brand_raw': b_raw,
                'brand_norm': b_norm,
                'model': m_raw,
                'details': det_raw,
                'event': ev,
                'val': val,
                'is_transferred': is_transferred,
                'date': d_dt,
                'date_str': d_dt.strftime('%d.%m.%Y') if d_dt else '',
                'manager': mgr,
                'source': cf
            })
            loaded_cf += 1
    print(f"Loaded {loaded_cf} unique CRM lead events from {cf}")

print(f"Total clients in CRM leads: {len(crm_leads_by_client)}")

print("\nSaving compiled data to disk for fast querying...")
import pickle
with open('scratch/cross_brand_data.pkl', 'wb') as f:
    pickle.dump({
        'deals_by_client': dict(deals_by_client),
        'partner_leads_by_client': dict(partner_leads_by_client),
        'crm_leads_by_client': dict(crm_leads_by_client)
    }, f)
print("Data saved successfully!")

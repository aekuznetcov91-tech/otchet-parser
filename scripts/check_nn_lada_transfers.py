# -*- coding: utf-8 -*-
import sys
import os
import json
from collections import Counter, defaultdict

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(PROJECT_ROOT, 'scripts'))
from parser_engine import read_tabular_file, get_exact_val, parse_custom_date, normalize_brand

with open(os.path.join(PROJECT_ROOT, 'data.json'), 'r', encoding='utf-8') as f:
    data_json = json.load(f)

# 1. Partners in registry with LADA in NN
print("=== LADA Partners in Registry for Nizhny Novgorod Region ===")
preg = data_json.get('partners_registry', [])
for p in preg:
    cname = p.get('canonical_name', '')
    oem = p.get('oem_data', [])
    for o in oem:
        sheet = str(o.get('sheet', '')).upper()
        city = str(o.get('city', '')).lower()
        if 'LADA' in sheet and ('нижн' in city or 'дзержин' in city or 'кстов' in city or 'бор' in city or 'арзамас' in city or '52' in str(o.get('inn', ''))):
            print(f"Partner: {cname} | Holding: {p.get('holding')} | City: {o.get('city')} | Legal: {o.get('legal_entity')} | INN: {o.get('inn')}")

# 2. Check all transfers from data (47).xlsx (Sep 2026) and data (39).xlsx (Aug 2026)
files = [
    ('2026-09', os.path.join(PROJECT_ROOT, 'raw_data', 'data (47).xlsx')),
    ('2026-08', os.path.join(PROJECT_ROOT, 'raw_data', 'data (39).xlsx'))
]

for m_label, fpath in files:
    print(f"\n==================== FULL ANALYSIS: {m_label} ({fpath}) ====================")
    datasets = read_tabular_file(fpath)
    sname, rows = datasets[0]
    
    # 1. All rows where event == 'Отправка лида' and brand == 'LADA'
    lada_transfers = []
    for r in rows:
        b = normalize_brand(str(get_exact_val(r, 'БРЕНД', 'МАРКА') or ''))
        ev = str(get_exact_val(r, 'EVENTNAME', 'СОБЫТИЕ') or '').strip()
        if b == 'LADA' and ev == 'Отправка лида':
            lada_transfers.append(r)
            
    print(f"Total raw 'Отправка лида' rows for LADA: {len(lada_transfers)}")
    
    # 2. Group by SumID to get unique transfers
    unique_transfers = {}
    for r in lada_transfers:
        sid = str(get_exact_val(r, 'СУММАID', 'ID') or '').strip()
        if sid and sid not in unique_transfers:
            unique_transfers[sid] = r
            
    print(f"Total UNIQUE transfers (Сумма ID) for LADA: {len(unique_transfers)}")
    
    # Analyze who got clients from Nizhny Novgorod or situated in NN
    nn_client_transfers = []
    nn_dealer_transfers = []
    
    for sid, r in unique_transfers.items():
        p = str(get_exact_val(r, 'ПАРТНЕР', 'ДИЛЕР', 'КОМПАНИЯ') or '').strip()
        c = str(get_exact_val(r, 'НАЗВАНИЕКОНТАКТА', 'КОНТАКТ') or '').strip()
        addr = str(get_exact_val(r, 'ADDRESS', 'АДРЕС') or '').strip()
        reg = str(get_exact_val(r, 'РЕГИОНКЛИЕНТАИЗSBERID', 'РЕГИОНКЛИЕНТА', 'РЕГИОН') or '').strip()
        cid = str(get_exact_val(r, 'CLIENTID', 'IDКЛИЕНТА') or '').strip()
        mod = str(get_exact_val(r, 'МОДЕЛЬ') or '').strip()
        d_val = parse_custom_date(get_exact_val(r, 'ДАТА', 'ДАТАСОБЫТИЯ'))
        
        all_geo = f"{reg} {addr}".lower()
        partner_txt = f"{p} {c}".lower()
        
        is_client_nn = any(k in all_geo for k in ['нижегород', 'нижний новгород', 'дзержин', 'кстов', 'арзамас', 'бор', 'балахн', 'выкс', 'павлов', 'саров', 'городец', 'заволжь', 'богородск'])
        is_dealer_nn = any(k in partner_txt for k in ['дзержинск', 'нижн', 'автопрофиль', 'юникор']) or ('агат' in partner_txt and 'нн' in partner_txt)
        
        info = {
            'sid': sid,
            'cid': cid,
            'date': d_val.strftime('%d.%m.%Y') if d_val else '-',
            'partner': p or c,
            'model': mod,
            'reg': reg,
            'addr': addr,
            'is_client_nn': is_client_nn,
            'is_dealer_nn': is_dealer_nn
        }
        
        if is_client_nn:
            nn_client_transfers.append(info)
        if is_dealer_nn:
            nn_dealer_transfers.append(info)

    print(f"\n--- A. Клиенты из Нижнего Новгорода и области (is_client_nn = True): {len(nn_client_transfers)} уникальных передач ---")
    client_dest_counter = Counter(t['partner'] for t in nn_client_transfers)
    for p, cnt in client_dest_counter.most_common():
        print(f"  -> Получатель: {p:50} | Лидов: {cnt:2d}")

    print(f"\n--- B. Дилеры, физически находящиеся в Нижегородской агломерации (is_dealer_nn = True): {len(nn_dealer_transfers)} уникальных передач ---")
    dealer_dest_counter = Counter(t['partner'] for t in nn_dealer_transfers)
    for p, cnt in dealer_dest_counter.most_common():
        print(f"  -> Дилер: {p:50} | Лидов: {cnt:2d}")

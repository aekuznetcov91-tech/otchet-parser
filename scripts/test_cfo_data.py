import sys
import os
import re
from collections import Counter, defaultdict
import pandas as pd

sys.path.append('.')
from scripts.parser_engine import read_tabular_file, parse_custom_date, normalize_brand, clean_key, get_exact_val

CFO_CITIES = {
    'москва', 'моск', 'одинцово', 'видное', 'балашиха', 'котельники', 'нагорное',
    'орехово-зуево', 'орехово- зуево', 'яхрома', 'химки', 'реутов', 'немчиновка',
    'московская обл., с. немчиновка', 'воронеж', 'владимир', 'ярославль', 'ярославь',
    'тамбов', 'tam6ob', 'тверь', 'боровлево', 'иваново', 'кострома', 'липецк',
    'сырское', 'брянск', 'калуга', 'рязань', 'курск', 'тула', 'новомосковск',
    'смоленск', 'cмоленск', 'орел', 'белгород', 'старый оскол', 'ковров', 'муром',
    'обнинск', 'рыбинск'
}

CFO_COMPANIES = {
    'автогермес', 'гермес-запад', 'кунцево', 'важная персона', 'млада', 'кармен',
    'корс', 'борисхоф', 'авторитэйл м', 'маркар', 'амкапитал', 'у сервис'
}

def is_cfo(city, company):
    c_lower = str(city).strip().lower()
    comp_lower = str(company).strip().lower()
    
    # Check city first
    if any(k in c_lower for k in CFO_CITIES):
        return True
        
    # If city is ambiguous/empty, check company known CFO locations
    if not c_lower or c_lower in ('2026', '3 099 000'):
        if any(k in comp_lower for k in CFO_COMPANIES):
            return True
        if 'рольф' in comp_lower and 'спб' not in comp_lower and 'петербург' not in comp_lower:
            return True
        if 'автомир' in comp_lower and 'симферополь' not in comp_lower and 'самар' not in comp_lower:
            return True
            
    return False

def identify_gk(company):
    comp = str(company).lower()
    if 'гермес' in comp or 'germes' in comp:
        return 'АвтоГЕРМЕС'
    if 'рольф' in comp or 'rolf' in comp or 'кунцево' in comp:
        return 'РОЛЬФ'
    if 'автомир' in comp:
        return 'АВТОМИР'
    if 'мажор' in comp or 'major' in comp or 'мэйджор' in comp:
        return 'МАЖОР'
    if 'корс' in comp or 'kors' in comp:
        return 'КОРС'
    if 'агат' in comp or 'agat' in comp:
        return 'АГАТ'
    return 'ДРУГИЕ'

reestr = read_tabular_file('raw_data/reestr_work_июнь _авг_filled(итог)_v2.xlsx')[0][1]
bitrix = read_tabular_file('raw_data/DEAL_20260917_49024c28_6aab926388945.xls')[0][1]

aux_keywords = ('КРЕДИТ', 'КАСКО', 'ОСАГО', 'ГАП', 'СТРАХОВ', 'СЕРТИФИКАТ', 'ВНЕСЕНИЕ АВАНСА', 'ВНЕСЕНИЕ', 'АВАНС', 'ОФОРМЛЕНИЕ', 'ДОГОВОР', 'УСЛУГА', 'КОМИССИЯ', 'ДОП')

deals = {}
def collect(rows, src):
    for r in rows:
        stream = str(get_exact_val(r, 'СТРИМ') or '').strip()
        if stream and stream != 'Импортеры': continue
        tovar = str(get_exact_val(r, 'ТОВАР') or '').upper()
        if any(kw in tovar for kw in aux_keywords): continue
        stage = str(get_exact_val(r, 'СТАДИЯСДЕЛКИ', 'СТАДИЯ') or '').upper()
        if 'ЗАКРЫТО И РЕАЛИЗОВАН' not in stage: continue
        dt = parse_custom_date(get_exact_val(r, 'ПРЕДПОЛАГАЕМАЯДАТАЗАКРЫТИЯ', 'ДАТАЗАКРЫТИЯ'))
        if not dt or dt.year != 2026 or dt.month not in (6, 7, 8): continue
        m = f'{dt.year:04d}-{dt.month:02d}'
        did = str(get_exact_val(r, 'ID', 'IDСДЕЛКИ') or '').strip()
        vin = str(get_exact_val(r, 'VIN', 'VINНОМЕР') or '').strip()
        city = str(get_exact_val(r, 'ГОРОДB2C', 'ГОРОД') or '').strip()
        comp = str(get_exact_val(r, 'КОМПАНИЯНАЗВАНИЕКОМПАНИИ', 'КОМПАНИЯ') or '').strip()
        brand = normalize_brand(tovar)
        b2c = str(get_exact_val(r, 'ТИПСДЕЛКИB2C', 'ТИПСДЕЛКИ') or '').strip()
        try: price = float(str(get_exact_val(r, 'ФИНАЛЬНАЯЦЕНАB2C', 'ЦЕНА') or 0).replace(' ', '').replace('\xa0', '').replace(',', '.'))
        except: price = 0.0

        key = f'{did}::{vin}' if (did and vin) else f'{did}::{tovar}'
        deals[key] = {
            'did': did, 'vin': vin, 'month': m, 'date': dt, 'city': city,
            'company': comp, 'brand': brand, 'tovar': tovar, 'price': price,
            'b2c': b2c, 'gk': identify_gk(comp), 'is_cfo': is_cfo(city, comp)
        }

collect(reestr, 'reestr')
collect(bitrix, 'bitrix')

df = pd.DataFrame(list(deals.values()))
print(f'Total deals: {len(df)}')
print('Deals by month:\n', df['month'].value_counts().sort_index())
print('Deals in CFO by month:\n', df[df['is_cfo']]['month'].value_counts().sort_index())

print('\n=== АВТОГЕРМЕС ===')
ag = df[df['gk'] == 'АвтоГЕРМЕС']
print('АвтоГЕРМЕС deals by month:\n', ag['month'].value_counts().sort_index())
print('АвтоГЕРМЕС in CFO:\n', ag[ag['is_cfo']]['month'].value_counts().sort_index())

# -*- coding: utf-8 -*-
"""
banking_dc_parser.py
====================
Автоматический парсер и аналитический модуль сквозного учета сделок ДЦ,
лидогенерации СберАвто и проникновения автокредитования (Сбер vs Др.Банки vs Наличные).

Принцип работы:
- Сканирует папку raw_data/ на наличие ЛЮБОГО файла Excel (.xlsx / .xls), содержащего столбец 'Банк' / 'банк'.
- Связывает сделки с передачами лидов ('Отправка лида') по client_id и партнерам.
- Формирует 8 макрорегионов РФ, доли проникновения, ТОП-10 Сбера и АНТИТОП-10 сторонних банков.
- Полностью изолирован от остальных модулей парсера.
"""

import os
import re
import openpyxl
from collections import Counter, defaultdict
from datetime import datetime

# 8 Макрорегионов РФ
MACRO_ORDER = [
    'Волга',
    'Волго-Вятка',
    'Москва',
    'Северо-Запад',
    'Сибирь',
    'Урал',
    'Центрально-Черноземный',
    'Юг'
]

REGION_TO_MACRO = {
    'татарстан': 'Волга', 'оренбургская': 'Волга', 'пензенская': 'Волга',
    'самарская': 'Волга', 'саратовская': 'Волга', 'ульяновская': 'Волга',
    'башкортостан': 'Волга',

    'владимирская': 'Волго-Вятка', 'ивановская': 'Волго-Вятка', 'кировская': 'Волго-Вятка',
    'нижегородская': 'Волго-Вятка', 'рязанская': 'Волго-Вятка', 'мордовия': 'Волго-Вятка',
    'коми': 'Волго-Вятка', 'чувашская': 'Волго-Вятка', 'чувашия': 'Волго-Вятка',
    'марий эл': 'Волго-Вятка', 'ярославская': 'Волго-Вятка', 'костромская': 'Волго-Вятка',

    'москва': 'Москва', 'московская': 'Москва',

    'архангельская': 'Северо-Запад', 'новгородская': 'Северо-Запад', 'псковская': 'Северо-Запад',
    'вологодская': 'Северо-Запад', 'калининградская': 'Северо-Запад', 'мурманская': 'Северо-Запад',
    'карелия': 'Северо-Запад', 'санкт-петербург': 'Северо-Запад', 'ленинградская': 'Северо-Запад',
    'тверская': 'Северо-Запад', 'ненецкий': 'Северо-Запад',

    'алтайский': 'Сибирь', 'алтай': 'Сибирь', 'приморский': 'Сибирь', 'иркутская': 'Сибирь',
    'кемеровская': 'Сибирь', 'кузбасс': 'Сибирь', 'красноярский': 'Сибирь', 'хакасия': 'Сибирь',
    'новосибирская': 'Сибирь', 'омская': 'Сибирь', 'томская': 'Сибирь', 'бурятия': 'Сибирь',
    'забайкальский': 'Сибирь', 'хабаровский': 'Сибирь', 'саха': 'Сибирь', 'якутия': 'Сибирь',
    'амурская': 'Сибирь', 'сахалинская': 'Сибирь', 'тыва': 'Сибирь', 'камчатский': 'Сибирь',
    'магаданская': 'Сибирь', 'еврейская': 'Сибирь', 'чукотский': 'Сибирь',

    'свердловская': 'Урал', 'удмуртская': 'Урал', 'удмуртия': 'Урал', 'пермский': 'Урал',
    'ханты-мансийский': 'Урал', 'югра': 'Урал', 'хмао': 'Урал', 'тюменская': 'Урал',
    'курганская': 'Урал', 'челябинская': 'Урал', 'ямало-ненецкий': 'Урал', 'янао': 'Урал',

    'белгородская': 'Центрально-Черноземный', 'брянская': 'Центрально-Черноземный',
    'орловская': 'Центрально-Черноземный', 'воронежская': 'Центрально-Черноземный',
    'калужская': 'Центрально-Черноземный', 'курская': 'Центрально-Черноземный',
    'липецкая': 'Центрально-Черноземный', 'смоленская': 'Центрально-Черноземный',
    'тамбовская': 'Центрально-Черноземный', 'тульская': 'Центрально-Черноземный',

    'астраханская': 'Юг', 'волгоградская': 'Юг', 'краснодарский': 'Юг',
    'кабардино-балкарская': 'Юг', 'ставропольский': 'Юг', 'ростовская': 'Юг',
    'крым': 'Юг', 'севастополь': 'Юг', 'адыгея': 'Юг', 'дагестан': 'Юг',
    'ингушетия': 'Юг', 'карачаево-черкесская': 'Юг', 'северная осетия': 'Юг',
    'чеченская': 'Юг', 'калмыкия': 'Юг', 'донецкая': 'Юг', 'луганская': 'Юг'
}

CITY_LOOKUP = {
    'казань': ('Казань', 'Волга'),
    'набережные челны': ('Набережные Челны', 'Волга'),
    'челны': ('Набережные Челны', 'Волга'),
    'нижнекамск': ('Набережные Челны', 'Волга'),
    'альметьевск': ('Альметьевск', 'Волга'),
    'оренбург': ('Оренбург', 'Волга'),
    'орск': ('Оренбург', 'Волга'),
    'пенза': ('Пенза', 'Волга'),
    'кузнецк': ('Пенза', 'Волга'),
    'самара': ('Самара', 'Волга'),
    'тольятти': ('Тольятти', 'Волга'),
    'сызрань': ('Самара', 'Волга'),
    'новокуйбышевск': ('Самара', 'Волга'),
    'саратов': ('Саратов', 'Волга'),
    'энгельс': ('Саратов', 'Волга'),
    'балаково': ('Саратов', 'Волга'),
    'ульяновск': ('Ульяновск', 'Волга'),
    'димитровград': ('Ульяновск', 'Волга'),
    'уфа': ('Уфа', 'Волга'),
    'стерлитамак': ('Уфа', 'Волга'),
    'салават': ('Уфа', 'Волга'),
    'нефтекамск': ('Уфа', 'Волга'),
    'октябрьский': ('Уфа', 'Волга'),

    'владимир': ('Владимир', 'Волго-Вятка'),
    'ковров': ('Владимир', 'Волго-Вятка'),
    'муром': ('Владимир', 'Волго-Вятка'),
    'иваново': ('Иваново', 'Волго-Вятка'),
    'кинешма': ('Иваново', 'Волго-Вятка'),
    'киров': ('Киров', 'Волго-Вятка'),
    'нижний новгород': ('Нижний Новгород', 'Волго-Вятка'),
    'дзержинск': ('Нижний Новгород', 'Волго-Вятка'),
    'арзамас': ('Нижний Новгород', 'Волго-Вятка'),
    'кстово': ('Нижний Новгород', 'Волго-Вятка'),
    'рязань': ('Рязань', 'Волго-Вятка'),
    'саранск': ('Саранск', 'Волго-Вятка'),
    'сыктывкар': ('Сыктывкар', 'Волго-Вятка'),
    'чебоксары': ('Чебоксары', 'Волго-Вятка'),
    'новочебоксарск': ('Чебоксары', 'Волго-Вятка'),
    'йошкар-ола': ('УРМ в г.Йошкар-Ола', 'Волго-Вятка'),
    'ярославль': ('Ярославль', 'Волго-Вятка'),
    'рыбинск': ('Ярославль', 'Волго-Вятка'),
    'кострома': ('Кострома', 'Волго-Вятка'),

    'москва': ('Москва', 'Москва'),
    'химки': ('Москва', 'Москва'),
    'балашиха': ('Москва', 'Москва'),
    'подольск': ('Москва', 'Москва'),
    'мытищи': ('Москва', 'Москва'),
    'люберцы': ('Москва', 'Москва'),
    'красногорск': ('Москва', 'Москва'),
    'одинцово': ('Москва', 'Москва'),
    'королев': ('Москва', 'Москва'),
    'домодедово': ('Москва', 'Москва'),
    'щелково': ('Москва', 'Москва'),
    'серпухов': ('Москва', 'Москва'),
    'коломна': ('Москва', 'Москва'),
    'раменское': ('Москва', 'Москва'),

    'архангельск': ('Архангельск', 'Северо-Запад'),
    'северодвинск': ('Архангельск', 'Северо-Запад'),
    'великий новгород': ('Великий Новгород', 'Северо-Запад'),
    'псков': ('УРМ в г. Псков', 'Северо-Запад'),
    'вологда': ('Вологда', 'Северо-Запад'),
    'череповец': ('Вологда', 'Северо-Запад'),
    'калининград': ('Калининград', 'Северо-Запад'),
    'мурманск': ('Мурманск', 'Северо-Запад'),
    'петрозаводск': ('Петрозаводск', 'Северо-Запад'),
    'санкт-петербург': ('Санкт-Петербург', 'Северо-Запад'),
    'петербург': ('Санкт-Петербург', 'Северо-Запад'),
    'спб': ('Санкт-Петербург', 'Северо-Запад'),
    'тверь': ('Тверь', 'Северо-Запад'),

    'барнаул': ('Барнаул', 'Сибирь'),
    'владивосток': ('Владивосток', 'Сибирь'),
    'иркутск': ('Иркутск', 'Сибирь'),
    'кемерово': ('Кемерово', 'Сибирь'),
    'новокузнецк': ('УРМ в г. Новокузнецк', 'Сибирь'),
    'красноярск': ('Красноярск', 'Сибирь'),
    'новосибирск': ('Новосибирск', 'Сибирь'),
    'омск': ('Омск', 'Сибирь'),
    'томск': ('Томск', 'Сибирь'),
    'хабаровск': ('Хабаровск', 'Сибирь'),

    'екатеринбург': ('Екатеринбург', 'Урал'),
    'ижевск': ('Ижевск', 'Урал'),
    'магнитогорск': ('Магнитогорск', 'Урал'),
    'пермь': ('Пермь', 'Урал'),
    'сургут': ('Сургут', 'Урал'),
    'тюмень': ('Тюмень', 'Урал'),
    'курган': ('УРМ в г. Курган', 'Урал'),
    'челябинск': ('Челябинск', 'Урал'),

    'белгород': ('Белгород', 'Центрально-Черноземный'),
    'брянск': ('Брянск', 'Центрально-Черноземный'),
    'орел': ('УРМ в г. Орел', 'Центрально-Черноземный'),
    'воронеж': ('Воронеж', 'Центрально-Черноземный'),
    'калуга': ('Калуга', 'Центрально-Черноземный'),
    'курск': ('Курск', 'Центрально-Черноземный'),
    'липецк': ('Липецк', 'Центрально-Черноземный'),
    'смоленск': ('Смоленск', 'Центрально-Черноземный'),
    'тамбов': ('Тамбов', 'Центрально-Черноземный'),
    'тула': ('Тула', 'Центрально-Черноземный'),

    'астрахань': ('Астрахань', 'Юг'),
    'волгоград': ('Волгоград', 'Юг'),
    'краснодар': ('Краснодар', 'Юг'),
    'сочи': ('УРМ в г. Сочи', 'Юг'),
    'новороссийск': ('Краснодар', 'Юг'),
    'пятигорск': ('Пятигорск', 'Юг'),
    'ростов-на-дону': ('Ростов-на-Дону', 'Юг'),
    'ростов': ('Ростов-на-Дону', 'Юг'),
    'ставрополь': ('УРМ в г. Ставрополь', 'Юг'),
}

PARTNER_DEFAULTS = {
    'рольф': ('Москва', 'Москва'),
    'автогермес': ('Москва', 'Москва'),
    'кунцево': ('Москва', 'Москва'),
    'автодом': ('Москва', 'Москва'),
    'авилон': ('Москва', 'Москва'),
    'фаворит': ('Москва', 'Москва'),
    'башавтоком': ('Уфа', 'Волга'),
    'кан авто': ('Казань', 'Волга'),
    'апельсин': ('Набережные Челны', 'Волга'),
    'максимум': ('Санкт-Петербург', 'Северо-Запад'),
    'вагнер': ('Санкт-Петербург', 'Северо-Запад'),
    'прагматика': ('Санкт-Петербург', 'Северо-Запад'),
    'бн-моторс': ('Брянск', 'Центрально-Черноземный'),
    'моторленд': ('Воронеж', 'Центрально-Черноземный'),
    'автосфера': ('Тамбов', 'Центрально-Черноземный'),
    'темп авто': ('Краснодар', 'Юг'),
    'техно-темп': ('Краснодар', 'Юг'),
    'фининвест': ('Ростов-на-Дону', 'Юг'),
    'арконт': ('Волгоград', 'Юг'),
    'дав-авто': ('Пермь', 'Урал'),
    'сатурн': ('Челябинск', 'Урал'),
    'форвард': ('Ижевск', 'Урал'),
}

def get_macro_from_region(text):
    if not text:
        return None
    t = str(text).strip().lower()
    for reg, macro in REGION_TO_MACRO.items():
        if reg in t:
            return macro
    return None

def resolve_location(address, contact, partner, client_reg_sber='', client_reg_brands=''):
    if address:
        a_low = str(address).lower()
        for kw, (city, macro) in CITY_LOOKUP.items():
            if re.search(r'\b' + re.escape(kw) + r'\b', a_low):
                return (city, macro)
        m = get_macro_from_region(a_low)
        if m:
            return ('Онлайн / Регион', m)

    if contact:
        c_low = str(contact).lower()
        for kw, (city, macro) in CITY_LOOKUP.items():
            if re.search(r'\b' + re.escape(kw) + r'\b', c_low):
                return (city, macro)
        m = get_macro_from_region(c_low)
        if m:
            return ('Онлайн / Регион', m)

    if partner:
        p_low = str(partner).lower()
        for kw, (city, macro) in CITY_LOOKUP.items():
            if re.search(r'\b' + re.escape(kw) + r'\b', p_low):
                return (city, macro)
        for kw, (city, macro) in PARTNER_DEFAULTS.items():
            if kw in p_low:
                return (city, macro)
        m = get_macro_from_region(p_low)
        if m:
            return ('Онлайн / Регион', m)

    for reg in [client_reg_brands, client_reg_sber]:
        if reg:
            r_low = str(reg).lower()
            for kw, (city, macro) in CITY_LOOKUP.items():
                if re.search(r'\b' + re.escape(kw) + r'\b', r_low):
                    return (city, macro)
            m = get_macro_from_region(r_low)
            if m:
                return ('Онлайн / Регион клиента', m)

    return ('Не определен', 'Не определен')


def find_file_with_bank_column(raw_dirs):
    candidates = []
    for d in raw_dirs:
        if not os.path.exists(d):
            continue
        for fname in os.listdir(d):
            if fname.startswith('~$') or not fname.endswith('.xlsx'):
                continue
            fpath = os.path.join(d, fname)
            try:
                wb = openpyxl.load_workbook(fpath, data_only=True)
                ws = wb.active
                row1 = next(ws.iter_rows(max_row=1, values_only=True), None)
                wb.close()
                if row1:
                    cols = [str(c or '').strip().lower() for c in row1]
                    if any('банк' == c or 'банк' in c for c in cols):
                        candidates.append((os.path.getmtime(fpath), fpath))
            except Exception:
                pass

    if not candidates:
        return None

    candidates.sort(key=lambda x: x[0], reverse=True)
    return candidates[0][1]


def load_lead_transfers(raw_dirs):
    f_transfers = None
    f_events = None

    for d in raw_dirs:
        if not os.path.exists(d):
            continue
        for fname in os.listdir(d):
            f_low = fname.lower()
            if 'data (22)' in f_low:
                f_transfers = os.path.join(d, fname)
            elif 'data (31)' in f_low and not f_transfers:
                f_transfers = os.path.join(d, fname)

            if 'data (23)' in f_low:
                f_events = os.path.join(d, fname)
            elif 'data (32)' in f_low and not f_events:
                f_events = os.path.join(d, fname)

    client_condition = {}
    brands_map = {}

    if f_events and os.path.exists(f_events):
        try:
            wb = openpyxl.load_workbook(f_events, data_only=True)
            ws = wb.active
            for r in ws.iter_rows(min_row=4, values_only=True):
                if not r or len(r) < 1:
                    continue
                cid = str(r[0] or '').strip()
                if not cid:
                    continue
                src = str(r[3] or '').lower() if len(r) > 3 else ''
                ev = str(r[7] or '').lower() if len(r) > 7 else ''
                reg_cl = str(r[21]).strip() if len(r) > 21 and r[21] else ''
                reg_rl = str(r[19]).strip() if len(r) > 19 and r[19] else ''
                brand = str(r[13]).strip() if len(r) > 13 and r[13] else ''

                if 'пробег' in src or 'б/у' in ev or 'avito' in src or 'autoru' in src:
                    cond = 'С пробегом'
                else:
                    cond = 'Новый'

                if cid not in client_condition or (cond == 'С пробегом' and client_condition[cid] != 'С пробегом'):
                    client_condition[cid] = cond

                if cid not in brands_map or (not brands_map[cid].get('reg_cl') and reg_cl):
                    brands_map[cid] = {'reg_cl': reg_cl, 'reg_rl': reg_rl, 'brand': brand}
            wb.close()
        except Exception as e:
            print(f'Warning loading events {f_events}: {e}')

    unique_transfers_list = []
    transfers_by_cid = defaultdict(list)

    if f_transfers and os.path.exists(f_transfers):
        try:
            wb = openpyxl.load_workbook(f_transfers, data_only=True)
            ws = wb.active
            seen_transfers = set()
            for r in ws.iter_rows(min_row=4, values_only=True):
                if not r or len(r) < 8:
                    continue
                ev = str(r[0] or '').strip()
                cid = str(r[2] or '').strip()
                partner = str(r[7] or '').strip()
                contact = str(r[6] or '').strip() if len(r) > 6 else ''
                addr = str(r[11] or '').strip() if len(r) > 11 else ''

                if ev == 'Отправка лида' and cid and partner:
                    cond = client_condition.get(cid, 'Новый')
                    key = (cid, partner)
                    if key not in seen_transfers:
                        seen_transfers.add(key)
                        item = {
                            'cid': cid,
                            'partner': partner,
                            'contact': contact,
                            'addr': addr,
                            'condition': cond
                        }
                        unique_transfers_list.append(item)
                    transfers_by_cid[cid].append({'partner': partner, 'contact': contact, 'addr': addr})
            wb.close()
        except Exception as e:
            print(f'Warning loading transfers {f_transfers}: {e}')

    return unique_transfers_list, transfers_by_cid, brands_map


def parse_banking_analytics(base_dir=None):
    if not base_dir:
        base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

    raw_dirs = [
        os.path.join(base_dir, 'raw_data'),
        os.path.join(base_dir, 'ready'),
        base_dir
    ]

    bank_file = find_file_with_bank_column(raw_dirs)
    if not bank_file:
        print('Banking analytics: no Excel file with "Банк" column found.')
        return None

    print(f'Banking analytics: parsing enriched deals from: {os.path.basename(bank_file)}')

    unique_transfers_list, transfers_by_cid, brands_map = load_lead_transfers(raw_dirs)
    transfers_total = len(unique_transfers_list)
    transfers_new = sum(1 for t in unique_transfers_list if t['condition'] == 'Новый')
    transfers_used = sum(1 for t in unique_transfers_list if t['condition'] == 'С пробегом')

    wb = openpyxl.load_workbook(bank_file, data_only=True)
    ws = wb.active

    header = [str(c or '').strip() for c in next(ws.iter_rows(max_row=1, values_only=True))]
    header_lower = [c.lower() for c in header]

    def col_idx(name):
        for i, h in enumerate(header_lower):
            if name == h or name in h:
                return i
        return None

    idx_cid = col_idx('client_id') or 10
    idx_prod = col_idx('название сделки') or col_idx('товар') or 5
    idx_comp = col_idx('компания') or 12
    idx_comp_full = col_idx('название компании') or 27
    idx_city = col_idx('город. b2c') or col_idx('город') or 18
    idx_bank = col_idx('банк')
    idx_zalog = col_idx('дата залога') or col_idx('залог')
    idx_fdc = col_idx('номер заявки фронтдц') or col_idx('фронтдц')
    idx_dt_app = col_idx('дата апп. b2c') or col_idx('дата апп') or 17
    idx_dt_odkp = col_idx('дата одкп') or 13

    deals_list = []
    partners_stats = defaultdict(lambda: {
        'total_deals': 0, 'sber_deals': 0, 'other_banks_deals': 0, 'cash_deals': 0,
        'lead_deals': 0, 'other_deals': 0,
        'macro': '', 'city': '', 'banks_breakdown': Counter()
    })

    for r_idx, r in enumerate(ws.iter_rows(min_row=2, values_only=True), start=2):
        if not r or not any(r):
            continue

        cid = str(r[idx_cid] or '').strip() if idx_cid < len(r) else ''
        prod = str(r[idx_prod] or '').strip() if idx_prod < len(r) else ''
        comp = str(r[idx_comp] or '').strip() if idx_comp < len(r) else ''
        comp_full = str(r[idx_comp_full] or '').strip() if idx_comp_full and idx_comp_full < len(r) and r[idx_comp_full] else comp
        city_b2c = str(r[idx_city] or '').strip() if idx_city < len(r) and r[idx_city] else ''
        bank = str(r[idx_bank] or '').strip() if idx_bank is not None and idx_bank < len(r) and r[idx_bank] else '—'
        zalog = str(r[idx_zalog] or '').strip() if idx_zalog is not None and idx_zalog < len(r) and r[idx_zalog] else '—'
        fdc = str(r[idx_fdc] or '').strip() if idx_fdc is not None and idx_fdc < len(r) and r[idx_fdc] else '—'

        dt_app = r[idx_dt_app] if idx_dt_app < len(r) else None
        dt_odkp = r[idx_dt_odkp] if idx_dt_odkp < len(r) else None
        dt_deal = dt_app or dt_odkp
        dt_str = dt_deal.strftime('%d.%m.%Y') if hasattr(dt_deal, 'strftime') else str(dt_deal or '—')

        if bank in ['—', '-', '', 'None', None]:
            bank_cat = 'Наличные'
            bank_clean = 'Наличные'
        elif bank.lower() == 'sber':
            bank_cat = 'Сбер'
            bank_clean = 'Сбербанк (Sber)'
        else:
            bank_cat = 'Другие банки'
            bank_clean = bank

        is_lead_deal = False
        lead_partner = ''
        if cid and cid in transfers_by_cid:
            is_lead_deal = True
            lead_partner = transfers_by_cid[cid][0]['partner']

        deal_partner = lead_partner or comp_full or comp or 'Не указан'

        b_info = brands_map.get(cid, {})
        reg_brands = b_info.get('reg_cl') or b_info.get('reg_rl') or ''
        city, macro = resolve_location(city_b2c, '', deal_partner, '', reg_brands)
        if (macro == 'Не определен' or not macro) and city_b2c:
            city, macro = resolve_location(city_b2c, '', '', '', '')

        car_parts = prod.split()
        brand = car_parts[0] if len(car_parts) > 0 else ''
        vin = ''
        model = ''
        if len(car_parts) > 1:
            if len(car_parts[-1]) >= 15:
                vin = car_parts[-1]
                model = ' '.join(car_parts[1:-1])
            else:
                model = ' '.join(car_parts[1:])

        deal_item = {
            'id': len(deals_list) + 1,
            'cid': cid,
            'date': dt_str,
            'product': prod,
            'brand': brand,
            'model': model,
            'vin': vin or '—',
            'partner': deal_partner,
            'comp': comp,
            'city': city,
            'macro': macro,
            'bank': bank_clean,
            'bank_cat': bank_cat,
            'deal_type': 'По переданному лиду' if is_lead_deal else 'Другие сделки ДЦ',
            'is_lead_deal': is_lead_deal,
            'fdc': fdc or '—',
            'zalog': zalog or '—'
        }
        deals_list.append(deal_item)

        st = partners_stats[deal_partner]
        st['total_deals'] += 1
        st['macro'] = macro if macro != 'Не определен' else st['macro']
        st['city'] = city if city != 'Не определен' else st['city']
        st['banks_breakdown'][bank_clean] += 1
        if bank_cat == 'Сбер':
            st['sber_deals'] += 1
        elif bank_cat == 'Другие банки':
            st['other_banks_deals'] += 1
        else:
            st['cash_deals'] += 1

        if is_lead_deal:
            st['lead_deals'] += 1
        else:
            st['other_deals'] += 1

    wb.close()

    lead_deals = [d for d in deals_list if d['is_lead_deal']]
    other_deals = [d for d in deals_list if not d['is_lead_deal']]

    all_partners_ranked = []
    for p, st in partners_stats.items():
        tot = st['total_deals']
        sber = st['sber_deals']
        ob = st['other_banks_deals']
        cash = st['cash_deals']
        credits = sber + ob

        sber_pct_credit = (sber / credits * 100) if credits > 0 else 0
        ob_pct_credit = (ob / credits * 100) if credits > 0 else 0
        sber_pct_total = (sber / tot * 100) if tot > 0 else 0
        ob_pct_total = (ob / tot * 100) if tot > 0 else 0
        cash_pct_total = (cash / tot * 100) if tot > 0 else 0

        competing = [f'{b} ({c})' for b, c in st['banks_breakdown'].most_common(5) if b not in ['Наличные', 'Сбербанк (Sber)']]

        all_partners_ranked.append({
            'partner': p,
            'macro': st['macro'] or 'Прочие',
            'city': st['city'] or 'Не указан',
            'total_deals': tot,
            'sber_deals': sber,
            'other_banks_deals': ob,
            'cash_deals': cash,
            'credits_total': credits,
            'lead_deals': st['lead_deals'],
            'other_deals': st['other_deals'],
            'sber_pct_credit': round(sber_pct_credit, 1),
            'ob_pct_credit': round(ob_pct_credit, 1),
            'sber_pct_total': round(sber_pct_total, 1),
            'ob_pct_total': round(ob_pct_total, 1),
            'cash_pct_total': round(cash_pct_total, 1),
            'competing_banks_str': ', '.join(competing) if competing else '—',
            'top_competing_bank': competing[0] if competing else '—'
        })

    left_group_all = [p for p in all_partners_ranked if p['credits_total'] > 0 and p['sber_pct_credit'] >= 50.0]
    left_group_all.sort(key=lambda x: (x['sber_pct_credit'], x['sber_deals'], x['total_deals']), reverse=True)

    right_group_all = [p for p in all_partners_ranked if p['credits_total'] > 0 and p['ob_pct_credit'] > 50.0]
    right_group_all.sort(key=lambda x: (x['ob_pct_credit'], x['other_banks_deals'], x['total_deals']), reverse=True)

    left_group_top10 = [p for p in left_group_all if p['total_deals'] >= 10][:10]
    right_group_top10 = [p for p in right_group_all if p['total_deals'] >= 10][:10]

    left_group_top10_by_units = sorted(left_group_all, key=lambda x: (x['sber_deals'], x['total_deals']), reverse=True)[:10]
    right_group_top10_by_units = sorted(right_group_all, key=lambda x: (x['other_banks_deals'], x['total_deals']), reverse=True)[:10]

    macro_stats = defaultdict(lambda: {
        'transfers': 0, 'lead_deals': 0, 'other_deals': 0, 'all_deals': 0,
        'sber': 0, 'other_banks': 0, 'cash': 0
    })

    for t in unique_transfers_list:
        p = t['partner']
        m = partners_stats[p]['macro'] if p in partners_stats else ''
        if not m:
            _, m = resolve_location(t.get('addr'), t.get('contact'), p)
        m = m if m in MACRO_ORDER else 'Прочие'
        macro_stats[m]['transfers'] += 1

    for d in deals_list:
        m = d['macro'] if d['macro'] in MACRO_ORDER else 'Прочие'
        st = macro_stats[m]
        st['all_deals'] += 1
        if d['bank_cat'] == 'Сбер':
            st['sber'] += 1
        elif d['bank_cat'] == 'Другие банки':
            st['other_banks'] += 1
        else:
            st['cash'] += 1

        if d['is_lead_deal']:
            st['lead_deals'] += 1
        else:
            st['other_deals'] += 1

    macro_rows = []
    for m in MACRO_ORDER:
        st = macro_stats[m]
        cr = (st['lead_deals'] / st['transfers'] * 100) if st['transfers'] > 0 else 0
        cred_share = ((st['sber'] + st['other_banks']) / st['all_deals'] * 100) if st['all_deals'] > 0 else 0
        sber_share = (st['sber'] / (st['sber'] + st['other_banks']) * 100) if (st['sber'] + st['other_banks']) > 0 else 0
        macro_rows.append({
            'macro': m,
            'transfers': st['transfers'],
            'lead_deals': st['lead_deals'],
            'other_deals': st['other_deals'],
            'all_deals': st['all_deals'],
            'cr': round(cr, 1),
            'sber': st['sber'],
            'other_banks': st['other_banks'],
            'cash': st['cash'],
            'credit_share': round(cred_share, 1),
            'sber_share': round(sber_share, 1)
        })

    result = {
        'updated_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'source_file': os.path.basename(bank_file),
        'transfers_total': transfers_total,
        'transfers_new': transfers_new,
        'transfers_used': transfers_used,
        'deals_total': len(deals_list),
        'deals_credit': sum(1 for d in deals_list if d['bank_cat'] != 'Наличные'),
        'deals_cash': sum(1 for d in deals_list if d['bank_cat'] == 'Наличные'),
        'deals_sber': sum(1 for d in deals_list if d['bank_cat'] == 'Сбер'),
        'deals_other_banks': sum(1 for d in deals_list if d['bank_cat'] == 'Другие банки'),

        'lead_deals_total': len(lead_deals),
        'lead_deals_credit': sum(1 for d in lead_deals if d['bank_cat'] != 'Наличные'),
        'lead_deals_sber': sum(1 for d in lead_deals if d['bank_cat'] == 'Сбер'),
        'lead_deals_other_banks': sum(1 for d in lead_deals if d['bank_cat'] == 'Другие банки'),
        'lead_deals_cash': sum(1 for d in lead_deals if d['bank_cat'] == 'Наличные'),
        'lead_cr': round(len(lead_deals) / transfers_total * 100, 1) if transfers_total > 0 else 0,

        'other_deals_total': len(other_deals),
        'other_deals_credit': sum(1 for d in other_deals if d['bank_cat'] != 'Наличные'),
        'other_deals_sber': sum(1 for d in other_deals if d['bank_cat'] == 'Сбер'),
        'other_deals_other_banks': sum(1 for d in other_deals if d['bank_cat'] == 'Другие банки'),
        'other_deals_cash': sum(1 for d in other_deals if d['bank_cat'] == 'Наличные'),

        'left_group_top10': left_group_top10,
        'left_group_all': left_group_all,
        'right_group_top10': right_group_top10,
        'right_group_all': right_group_all,
        'left_group_top10_by_units': left_group_top10_by_units,
        'right_group_top10_by_units': right_group_top10_by_units,

        'macro_rows': macro_rows,
        'all_partners': sorted(all_partners_ranked, key=lambda x: x['total_deals'], reverse=True),
        'lead_deals_db': lead_deals,
        'other_deals_db': other_deals
    }

    print(f'Banking analytics ready: {result["deals_total"]} deals ({result["lead_deals_total"]} lead deals, {result["other_deals_total"]} other deals). Sber: {result["deals_sber"]}, Other banks: {result["deals_other_banks"]}, Cash: {result["deals_cash"]}.')
    return result

if __name__ == '__main__':
    res = parse_banking_analytics()
    if res:
        print('SUCCESS: Deals total =', res['deals_total'], 'Lead deals =', res['lead_deals_total'], 'Transfers =', res['transfers_total'])
    else:
        print('FAILURE: No bank file found.')

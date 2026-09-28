import json
import os
import re

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE_DIR = os.path.join(PROJECT_ROOT, 'site')
DATA_DIR = os.path.join(PROJECT_ROOT, 'data')

# Target mergers: { donor_id: (target_id, target_canonical_name, target_kam) }
# Or groups of donor_ids to merge into target_id
MERGERS = [
    # 1. Автопрестиж: merge 1045, 1198 into 1076
    {
        'target_id': 1076,
        'target_name': 'ГК Автопрестиж',
        'target_kam': 'Алексей Чихарев',
        'donor_ids': [1045, 1198, 1127]
    },
    # 2. Прагматика: merge 1193, 1205 into 1022
    {
        'target_id': 1022,
        'target_name': 'Прагматика',
        'target_kam': 'Светлана Дариенко',
        'donor_ids': [1193, 1205]
    },
    # 3. Боравто: merge 1097, 1105, 1108, 1150, 1170 into 1094
    {
        'target_id': 1094,
        'target_name': 'ГК Боравто',
        'target_kam': 'Валерия Солдатова',
        'donor_ids': [1097, 1105, 1108, 1150, 1170]
    },
    # 4. Дав-Авто: merge 1088 into 1184
    {
        'target_id': 1184,
        'target_name': 'Дав-Авто',
        'target_kam': 'Андрей Кузнецов',
        'donor_ids': [1088]
    },
    # 5. Диалог Авто: merge 1178 into 1082
    {
        'target_id': 1082,
        'target_name': 'ГК Диалог Авто',
        'target_kam': 'Алексей Чихарев',
        'donor_ids': [1178]
    },
    # 6. Автоимпорт: merge 1074 into 1087
    {
        'target_id': 1087,
        'target_name': 'ГК Автоимпорт',
        'target_kam': 'Алексей Чихарев',
        'donor_ids': [1074]
    },
    # 7. Авто-Ревю: merge 632022 into 1006
    {
        'target_id': 1006,
        'target_name': 'ФДЦ Авто-Ревю',
        'target_kam': 'Валерия Солдатова',
        'donor_ids': [632022]
    },
    # 8. Ай-Би-Эм: merge 1164 into 1027
    {
        'target_id': 1027,
        'target_name': 'Ай-Би-Эм',
        'target_kam': 'Светлана Дариенко',
        'donor_ids': [1164]
    },
    # 9. Башавтоком: merge 1077, 1200 into 1176
    {
        'target_id': 1176,
        'target_name': 'ГК Башавтоком',
        'target_kam': 'Евгения Добролюбова',
        'donor_ids': [1077, 1200]
    },
    # 10. Сатурн 2: merge 1181 into 1072
    {
        'target_id': 1072,
        'target_name': 'ГК Сатурн 2',
        'target_kam': 'Евгения Добролюбова',
        'donor_ids': [1181]
    },
    # 11. КМ/Ч: merge 1203 into 1095
    {
        'target_id': 1095,
        'target_name': 'КМ/Ч',
        'target_kam': 'Валерия Солдатова',
        'donor_ids': [1203]
    },
    # 12. Петровский: merge 1204 into 1028
    {
        'target_id': 1028,
        'target_name': 'Петровский',
        'target_kam': 'Светлана Дариенко',
        'donor_ids': [1204]
    },
    # 13. Прайм Липецк: merge 1195 into 1033
    {
        'target_id': 1033,
        'target_name': 'ФДЦ Прайм Липецк',
        'target_kam': 'Валерия Солдатова',
        'donor_ids': [1195]
    },
    # 14. Русская Ладья: merge 632015 into 1147
    {
        'target_id': 1147,
        'target_name': 'Русская Ладья',
        'target_kam': 'Андрей Кузнецов',
        'donor_ids': [632015]
    },
    # 15. Интерпартнер: merge 1122 into 1123
    {
        'target_id': 1123,
        'target_name': 'Интерпартнер',
        'target_kam': 'Евгения Добролюбова',
        'donor_ids': [1122]
    },
    # 16. Автокласс: merge 1155 into 1103
    {
        'target_id': 1103,
        'target_name': 'ГК Автокласс',
        'target_kam': 'Алексей Чихарев',
        'donor_ids': [1155]
    },
    # 17. ТСАЦ Июль: merge 1214, 632023 into 1056
    {
        'target_id': 1056,
        'target_name': 'ТСАЦ Июль',
        'target_kam': 'Евгения Добролюбова',
        'donor_ids': [1214, 632023]
    },
    # 18. Форвард Ижевск/Сызрань: merge 632020 into 1060
    {
        'target_id': 1060,
        'target_name': 'Форвард Ижевск/Сызрань',
        'target_kam': 'Евгения Добролюбова',
        'donor_ids': [632020]
    },
    # 19. ЮНИКОР: merge 632014 into 1086
    {
        'target_id': 1086,
        'target_name': 'ЮНИКОР Дзержинск НН',
        'target_kam': 'Андрей Кузнецов',
        'donor_ids': [632014]
    },
    # 20. Автосеть РФ АМК: merge 632018 into 1053
    {
        'target_id': 1053,
        'target_name': 'ФДЦ Автосеть АМК РФ',
        'target_kam': 'Андрей Кузнецов',
        'donor_ids': [632018]
    },
    # 21. Major: merge 1202, 632040 into 1044
    {
        'target_id': 1044,
        'target_name': 'ГК Major/Мэйджор',
        'target_kam': 'Алексей Чихарев',
        'donor_ids': [1202, 632040]
    },
    # 22. Автобан: merge 1197 into 1243
    {
        'target_id': 1243,
        'target_name': 'ГК Автобан',
        'target_kam': 'Евгения Добролюбова',
        'donor_ids': [1197]
    },
    # 23. Авто Сити: merge 1175 into 1118
    {
        'target_id': 1118,
        'target_name': 'ООО "АВТО СИТИ"',
        'target_kam': 'Валерия Солдатова',
        'donor_ids': [1175]
    },
    # 24. Автофорум: merge 1085 into 1134
    {
        'target_id': 1134,
        'target_name': 'Чери Автофорум',
        'target_kam': 'Евгения Добролюбова',
        'donor_ids': [1085]
    },
    # 25. БН-Моторс: merge 1186 into 1177
    {
        'target_id': 1177,
        'target_name': 'ГК БН-МОТОРС',
        'target_kam': 'Евгения Добролюбова',
        'donor_ids': [1186]
    },
    # 26. ГК Сигма: merge 1024 into 1011
    {
        'target_id': 1011,
        'target_name': 'ГК Сигма',
        'target_kam': 'Светлана Дариенко',
        'donor_ids': [1024]
    }
]

def clean_list(lst):
    seen = set()
    res = []
    for x in lst:
        if not x: continue
        x_clean = str(x).strip()
        if x_clean.lower() not in seen:
            seen.add(x_clean.lower())
            res.append(x_clean)
    return res

def apply_merges_to_file(filepath):
    if not os.path.exists(filepath):
        print(f"File not found: {filepath}")
        return
    with open(filepath, 'r', encoding='utf-8') as f:
        data = json.load(f)

    partners = data.get('partners', [])
    partners_by_id = {}
    for p in partners:
        pid = p.get('partner_id') or p.get('id')
        if pid is not None:
            partners_by_id[pid] = p

    removed_pids = set()

    for m in MERGERS:
        tid = m['target_id']
        tname = m['target_name']
        tkam = m['target_kam']
        donors = m['donor_ids']

        target = partners_by_id.get(tid)
        if not target:
            # Create target if not exists
            target = {
                'partner_id': tid,
                'canonical_name': tname,
                'kam': tkam,
                'bitrix_aliases': [],
                'bi_aliases': [],
                'pochta_aliases': [],
                'oem_data': []
            }
            partners.append(target)
            partners_by_id[tid] = target

        # Update target name and kam
        target['canonical_name'] = tname
        if tkam: target['kam'] = tkam

        if 'bitrix_aliases' not in target or target['bitrix_aliases'] is None:
            target['bitrix_aliases'] = []
        if 'bi_aliases' not in target or target['bi_aliases'] is None:
            target['bi_aliases'] = []
        if 'pochta_aliases' not in target or target['pochta_aliases'] is None:
            target['pochta_aliases'] = []
        if 'oem_data' not in target or target['oem_data'] is None:
            target['oem_data'] = []

        target['bi_aliases'].append(tname)
        target['bitrix_aliases'].append(tname)

        for did in donors:
            donor = partners_by_id.get(did)
            if donor:
                d_cname = donor.get('canonical_name')
                if d_cname:
                    target['bi_aliases'].append(d_cname)
                    target['bitrix_aliases'].append(d_cname)

                for ba in donor.get('bitrix_aliases') or []:
                    target['bitrix_aliases'].append(ba)
                for bia in donor.get('bi_aliases') or []:
                    target['bi_aliases'].append(bia)
                for pa in donor.get('pochta_aliases') or []:
                    target['pochta_aliases'].append(pa)
                for oem in donor.get('oem_data') or []:
                    target['oem_data'].append(oem)

                removed_pids.add(did)

        target['bitrix_aliases'] = clean_list(target['bitrix_aliases'])
        target['bi_aliases'] = clean_list(target['bi_aliases'])
        target['pochta_aliases'] = clean_list(target['pochta_aliases'])

    # Explicit cleanup & allocations:
    # 1. Clean Sigma pochta aliases from non-Sigma partners
    p1012 = partners_by_id.get(1012)
    if p1012 and 'pochta_aliases' in p1012:
        p1012['pochta_aliases'] = [a for a in p1012['pochta_aliases'] if 'сигма' not in a.lower()]
    p1013 = partners_by_id.get(1013)
    if p1013 and 'pochta_aliases' in p1013:
        p1013['pochta_aliases'] = [a for a in p1013['pochta_aliases'] if 'сигма' not in a.lower()]
    
    # 2. Ensure ГК Сигма (1011) has both pochta aliases
    p1011 = partners_by_id.get(1011)
    if p1011:
        p1011['canonical_name'] = 'ГК Сигма'
        p1011['kam'] = 'Светлана Дариенко'
        if 'pochta_aliases' not in p1011 or not p1011['pochta_aliases']:
            p1011['pochta_aliases'] = []
        p1011['pochta_aliases'].extend(['Почта Сигма Чери СПб1', 'Почта Сигма Чери СПб2'])
        p1011['pochta_aliases'] = clean_list(p1011['pochta_aliases'])
        p1011['bi_aliases'].extend(['Приоритет_Сигма СПб', 'СберАвто (Почта Сигма Чери O&J СПб1, Почта Сигма Чери O&J СПб2)', 'Сигма'])
        p1011['bi_aliases'] = clean_list(p1011['bi_aliases'])

    # 3. Автопремиум: Тверь (1040) -> Алексей Чихарев, СПб (632032) -> Светлана Дариенко
    p1040 = partners_by_id.get(1040)
    if p1040:
        p1040['canonical_name'] = 'Авто Премиум Тверь'
        p1040['holding'] = 'Авто Премиум'
        p1040['kam'] = 'Алексей Чихарев'
        p1040['bitrix_aliases'] = ['ONLINE ООО "СОЮЗ-Т"', 'ООО "СОЮЗ-Т"', 'Авто Премиум Тверь', 'Авто Премиум Тверь ONLINE']
        p1040['bi_aliases'] = ['Авто Премиум Тверь']
    
    p632032 = partners_by_id.get(632032)
    if p632032:
        p632032['canonical_name'] = 'Премиум Авто ONLINE'
        p632032['holding'] = 'Премиум Авто'
        p632032['kam'] = 'Светлана Дариенко'
        p632032['bitrix_aliases'] = ['Премиум Авто ONLINE', 'Премиум Авто']
        p632032['bi_aliases'] = ['Премиум Авто ONLINE', 'Премиум Авто']

    # General cleanup of corrupted/truncated holdings like 'ONLIN', 'ONLINE', 'ООО', 'ИП'
    for p in partners:
        h = (p.get('holding') or '').strip()
        if h.upper() in ['ONLIN', 'ONLINE', 'ОНЛАЙН', 'ООО', 'ИП', 'АВТО']:
            p['holding'] = p.get('canonical_name') or ''
        p['bitrix_aliases'] = [a for a in p.get('bitrix_aliases', []) if a.strip().lower() not in ['onlin', 'online', 'онлайн', 'ооо', 'ип']]
        p['bi_aliases'] = [a for a in p.get('bi_aliases', []) if a.strip().lower() not in ['onlin', 'online', 'онлайн', 'ооо', 'ип']]

    # 4. Авторитет: Архангельск (1138) -> Светлана Дариенко (только Лада)
    #    Авторитет (Симферополь, 1286) -> Валерия Солдатова (Jetour, Soueast)
    p1138 = partners_by_id.get(1138)
    if p1138:
        p1138['canonical_name'] = 'Авторитет (Архангельск)'
        p1138['kam'] = 'Светлана Дариенко'
        p1138['bitrix_aliases'] = [a for a in p1138.get('bitrix_aliases', []) if 'авторитет-м' not in a.lower()]
        p1138['oem_data'] = [oem for oem in p1138.get('oem_data', []) if (oem.get('brand') or '').upper() == 'LADA' or (oem.get('city') or '').lower() == 'архангельск']

    p1286 = partners_by_id.get(1286)
    if not p1286:
        p1286 = {
            'partner_id': 1286,
            'canonical_name': 'Авторитет (Симферополь)',
            'holding': 'Автодель',
            'kam': 'Валерия Солдатова',
            'bitrix_aliases': ['Online Авторитет-М', 'Автодель', 'ООО "АВТОРИТЕТ-М"', 'Авторитет-М'],
            'bi_aliases': ['Авторитет-М', 'Автодель', 'Авторитет (Симферополь)'],
            'pochta_aliases': [],
            'oem_data': [
                {
                    'sheet': 'JETOUR',
                    'city': 'Симферополь',
                    'group_link': 'https://max.ru/join/AwIKqhz7UTgHun-C52ZtkX33cZom5Fe_N0sc4BESsTA',
                    'name': 'Автодель',
                    'legal_entity': 'ООО Авторитет-М',
                    'inn': '9102001105',
                    'address': 'г. Симферополь, ул. Киевская 187',
                    'back_name': '',
                    'email': 'vtovstokor@avtodel.com, manager3@jetour-avtodel.ru, manager2@jetour-avtodel.ru, manager4@jetour-avtodel.ru',
                    'responsible': 'Валерия Солдатова',
                    'brand': 'JETOUR'
                },
                {
                    'sheet': 'Soueast',
                    'city': 'Симферополь',
                    'group_link': 'https://max.ru/join/AwIKqhz7UTgHun-C52ZtkX33cZom5Fe_N0sc4BESsTA',
                    'name': 'Автодель',
                    'legal_entity': 'ООО Авторитет-М',
                    'inn': '9102001105',
                    'address': 'г. Симферополь, ул. Киевская 187',
                    'back_name': '-',
                    'email': 'vtovstokor@avtodel.com, manager3@jetour-avtodel.ru, manager2@jetour-avtodel.ru',
                    'responsible': 'Валерия Солдатова',
                    'brand': 'SOUEAST'
                }
            ],
            'status': 'verified'
        }
        partners.append(p1286)
        partners_by_id[1286] = p1286
    else:
        p1286['canonical_name'] = 'Авторитет (Симферополь)'
        p1286['kam'] = 'Валерия Солдатова'

    # Filter out removed donor partners
    new_partners = [p for p in partners if (p.get('partner_id') or p.get('id')) not in removed_pids]
    data['partners'] = new_partners
    data['total_master_partners'] = len(new_partners)

    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f"Successfully processed {filepath}: removed {len(removed_pids)} duplicate partners. Total remaining: {len(new_partners)}")

def apply_merges_to_data_json(filepath):
    if not os.path.exists(filepath):
        print(f"File not found: {filepath}")
        return
    with open(filepath, 'r', encoding='utf-8') as f:
        data = json.load(f)

    donor_to_target = {}
    for m in MERGERS:
        for did in m['donor_ids']:
            donor_to_target[did] = (m['target_id'], m['target_name'], m['target_kam'])

    modified = False
    for r in data.get('sys_db_partners', []):
        pid = r.get('PartnerId')
        if pid in donor_to_target:
            tid, tname, tkam = donor_to_target[pid]
            r['PartnerId'] = tid
            r['Partner'] = tname
            if tkam: r['KAM'] = tkam
            modified = True

    for r in data.get('deals', []):
        pid = r.get('PartnerId')
        if pid in donor_to_target:
            tid, tname, tkam = donor_to_target[pid]
            r['PartnerId'] = tid
            r['PartnerName'] = tname
            if tkam: r['KAM'] = tkam
            modified = True

    if modified:
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print(f"Successfully updated donor IDs in {filepath}")

if __name__ == '__main__':
    paths = [
        os.path.join(PROJECT_ROOT, 'partners_registry.json'),
        os.path.join(SITE_DIR, 'partners_registry.json'),
        os.path.join(DATA_DIR, 'partners_registry.json')
    ]
    for p in paths:
        apply_merges_to_file(p)

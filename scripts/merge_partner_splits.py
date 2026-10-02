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
        'target_kam': 'Евгения Добролюбова',
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
        'target_kam': 'Алексей Чихарев',
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
    # 18. Форвард Ижевск/Сызрань: merge 1051, 632013, 632020 into 1060
    {
        'target_id': 1060,
        'target_name': 'Форвард Ижевск/Сызрань',
        'target_kam': 'Евгения Добролюбова',
        'donor_ids': [1051, 632013, 632020]
    },
    # 19. ЮНИКОР: merge 632014 into 1086
    {
        'target_id': 1086,
        'target_name': 'ЮНИКОР Дзержинск НН',
        'target_kam': 'Евгения Добролюбова',
        'donor_ids': [632014]
    },
    # 20. Автосеть РФ АМК: merge 632018, 1236 into 1053
    {
        'target_id': 1053,
        'target_name': 'ФДЦ Автосеть АМК РФ',
        'target_kam': 'Евгения Добролюбова',
        'donor_ids': [632018, 1236]
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
    # 23. Воронеж-Авто-Сити: merge 1118, 1175 into 1114
    {
        'target_id': 1114,
        'target_name': 'ООО "ВОРОНЕЖ-АВТО-СИТИ',
        'target_kam': 'Валерия Солдатова',
        'donor_ids': [1118, 1175]
    },
    # 24. Автофорум: merge 1085 into 1134
    {
        'target_id': 1134,
        'target_name': 'Чери Автофорум',
        'target_kam': 'Евгения Добролюбова',
        'donor_ids': [1085]
    },
    # 25. Дебрянск Авто / БН-Моторс: merge 1186, 1187, 632038 into 1177
    {
        'target_id': 1177,
        'target_name': 'Дебрянск Авто',
        'target_kam': 'Валерия Солдатова',
        'donor_ids': [1186, 1187, 632038]
    },
    # 26. ГК Сигма: merge 1024 into 1011
    {
        'target_id': 1011,
        'target_name': 'ГК Сигма',
        'target_kam': 'Светлана Дариенко',
        'donor_ids': [1024]
    },
    # 27. Кунцево: merge 1116 into 1091
    {
        'target_id': 1091,
        'target_name': 'ТЦ Кунцево',
        'target_kam': 'Алексей Чихарев',
        'donor_ids': [1116]
    },
    # 28. Маркар: merge P_OEM_a7faf70c into 1120
    {
        'target_id': 1120,
        'target_name': 'ООО "МАРКАР ГРУПП',
        'target_kam': 'Алексей Чихарев',
        'donor_ids': ['P_OEM_a7faf70c']
    },
    # 29. Вагнер Авто и Авторитэйл М: merge 1015 into 1285
    {
        'target_id': 1285,
        'target_name': 'Вагнер Авто / Авторитэйл',
        'target_kam': 'Светлана Дариенко',
        'donor_ids': [1015]
    },
    # 30. Автопортрет и НеваАвто: merge 1222 into 1083
    {
        'target_id': 1083,
        'target_name': 'Автопортрет (Нева Авто)',
        'target_kam': 'Светлана Дариенко',
        'donor_ids': [1222]
    },
    # 31. ГК Оптима и O&J Оптима кубань: merge 1007 into 1030
    {
        'target_id': 1030,
        'target_name': 'ГК Оптима',
        'target_kam': 'Валерия Солдатова',
        'donor_ids': [1007]
    },
    # 32. ФДЦ Трансфор: merge 632021 into 1003
    {
        'target_id': 1003,
        'target_name': 'ФДЦ Трансфор',
        'target_kam': 'Валерия Солдатова',
        'donor_ids': [632021]
    },
    # 33. ГК Глобус: merge 1182, 632045, P_OEM_43cba4f4, 1115 into 1013
    {
        'target_id': 1013,
        'target_name': 'ГК Глобус',
        'target_kam': 'Валерия Солдатова',
        'donor_ids': [1182, 632045, 'P_OEM_43cba4f4', 1115]
    },
    # 34. ФДЦ Техно-Темп: merge 632016 into 1004
    {
        'target_id': 1004,
        'target_name': 'ФДЦ Техно-Темп',
        'target_kam': 'Валерия Солдатова',
        'donor_ids': [632016]
    },
    # 35. Р-Моторс: merge 1008, 1131 into 1025
    {
        'target_id': 1025,
        'target_name': 'Р-Моторс ЛАДА',
        'target_kam': 'Светлана Дариенко',
        'donor_ids': [1008, 1131]
    },
    # 36. Аларм-Моторс Озерки: merge 632048 into 1002
    {
        'target_id': 1002,
        'target_name': 'Аларм-Моторс ГК',
        'target_kam': 'Светлана Дариенко',
        'donor_ids': [632048]
    },
    # 37. Чери Арконт: merge 1223 into 1112
    {
        'target_id': 1112,
        'target_name': 'ГК Арконт Холдинг',
        'target_kam': 'Евгения Добролюбова',
        'donor_ids': [1223]
    },
    # 38. Нижегородец: 1071 -> Евгения Добролюбова
    {
        'target_id': 1071,
        'target_name': 'Нижегородец',
        'target_kam': 'Евгения Добролюбова',
        'donor_ids': []
    },
    # 39. Сатурн-Р: merge P_OEM_6e979ac2 into 1110
    {
        'target_id': 1110,
        'target_name': 'Сатурн-Р',
        'target_kam': 'Евгения Добролюбова',
        'donor_ids': ['P_OEM_6e979ac2']
    },
    # 40. Tenet / Haval Автопремьер М: merge P_OEM_b19664be into P_OEM_ac181614
    {
        'target_id': 'P_OEM_ac181614',
        'target_name': 'Уфа Haval / Tenet Автопремьер М',
        'target_kam': 'Евгения Добролюбова',
        'donor_ids': ['P_OEM_b19664be']
    },
    # 41. Автолидер: merge 632031 into 1266
    {
        'target_id': 1266,
        'target_name': 'Автолидер ГАК',
        'target_kam': 'Евгения Добролюбова',
        'donor_ids': [632031]
    },
    # 42. Армада: 1128 -> Евгения Добролюбова
    {
        'target_id': 1128,
        'target_name': 'ООО "ТД АРМАДА-АВТО',
        'target_kam': 'Евгения Добролюбова',
        'donor_ids': []
    },
    # 43. Автохолдинг Максимум: 1163 -> Светлана Дариенко
    {
        'target_id': 1163,
        'target_name': 'Автохолдинг Максимум',
        'target_kam': 'Светлана Дариенко',
        'donor_ids': []
    },
    # 44. Гедон-Юг: 1288 -> Валерия Солдатова
    {
        'target_id': 1288,
        'target_name': 'Гедон-Юг',
        'target_kam': 'Валерия Солдатова',
        'donor_ids': []
    },
    # 45. АсАвто: P_OEM_943c0828 -> Евгения Добролюбова
    {
        'target_id': 'P_OEM_943c0828',
        'target_name': 'АсАвто на Алмаатинской',
        'target_kam': 'Евгения Добролюбова',
        'donor_ids': []
    },
    # 46. Асмото: P_OEM_ae51d9c1 -> Евгения Добролюбова
    {
        'target_id': 'P_OEM_ae51d9c1',
        'target_name': 'ООО "Асмото"',
        'target_kam': 'Евгения Добролюбова',
        'donor_ids': []
    },
    # 47. КАН Авто: merge P_OEM_470bf314 into 1201
    {
        'target_id': 1201,
        'target_name': 'Приоритет_ГК КАН Авто',
        'target_kam': 'Алексей Чихарев',
        'donor_ids': ['P_OEM_470bf314']
    },
    # 48. Фаворит: merge P_OEM_c945ead6 into 1227
    {
        'target_id': 1227,
        'target_name': 'Фаворит',
        'target_kam': 'Алексей Чихарев',
        'donor_ids': ['P_OEM_c945ead6']
    },
    # 49. Барс Авто: merge P_OEM_8b1a007a into 1233
    {
        'target_id': 1233,
        'target_name': 'Барс Авто',
        'target_kam': 'Алексей Чихарев',
        'donor_ids': ['P_OEM_8b1a007a']
    },
    # 50. Автодин: merge P_OEM_4745e299 into 1042
    {
        'target_id': 1042,
        'target_name': 'Автодин',
        'target_kam': 'Алексей Чихарев',
        'donor_ids': ['P_OEM_4745e299']
    },
    # 51. У Сервис: merge P_OEM_146fadbd into 1111
    {
        'target_id': 1111,
        'target_name': 'Geely У Сервис',
        'target_kam': 'Алексей Чихарев',
        'donor_ids': ['P_OEM_146fadbd']
    },
    # 52. Автопассаж: merge P_OEM_47b351a7 into 1160
    {
        'target_id': 1160,
        'target_name': 'Автопассаж',
        'target_kam': 'Алексей Чихарев',
        'donor_ids': ['P_OEM_47b351a7']
    },
    # 53. Звезда Ярославии: merge P_OEM_56d7a4be into 1046
    {
        'target_id': 1046,
        'target_name': 'Звезда Ярославии',
        'target_kam': 'Алексей Чихарев',
        'donor_ids': ['P_OEM_56d7a4be']
    },
    # 54. Важная персона: merge P_OEM_a82c4866 into 1258
    {
        'target_id': 1258,
        'target_name': 'Важная персона',
        'target_kam': 'Алексей Чихарев',
        'donor_ids': ['P_OEM_a82c4866']
    },
    # 55. Независимость: merge P_OEM_d272d060 into 1261
    {
        'target_id': 1261,
        'target_name': 'Независимость',
        'target_kam': 'Алексей Чихарев',
        'donor_ids': ['P_OEM_d272d060']
    },
    # 56. АСЦ: merge P_OEM_8c6abb28 into 1130
    {
        'target_id': 1130,
        'target_name': 'АСЦ',
        'target_kam': 'Алексей Чихарев',
        'donor_ids': ['P_OEM_8c6abb28']
    },
    # 57. Измайлово: merge P_OEM_8a5198d4 into 1059
    {
        'target_id': 1059,
        'target_name': 'CHERY Измайлово',
        'target_kam': 'Алексей Чихарев',
        'donor_ids': ['P_OEM_8a5198d4']
    },
    # 58. Премиум Авто: merge 92941177, P_OEM_fb550c48 into 632032
    {
        'target_id': 632032,
        'target_name': 'Премиум Авто ONLINE',
        'target_kam': 'Светлана Дариенко',
        'donor_ids': [92941177, 'P_OEM_fb550c48']
    },
    # 59. Сократ (Моторленд СПб): merge P_OEM_a8949707 into 1280
    {
        'target_id': 1280,
        'target_name': 'Сократ (Моторленд СПб)',
        'target_kam': 'Светлана Дариенко',
        'donor_ids': ['P_OEM_a8949707']
    },
    # 60. Динамика: merge 1029, P_OEM_813ee700 into 1031
    {
        'target_id': 1031,
        'target_name': 'ГК ДИНАМИКА',
        'target_kam': 'Светлана Дариенко',
        'donor_ids': [1029, 'P_OEM_813ee700']
    },
    # 61. Автополе: merge P_OEM_8f342a86 into 1063
    {
        'target_id': 1063,
        'target_name': 'Автополе',
        'target_kam': 'Светлана Дариенко',
        'donor_ids': ['P_OEM_8f342a86']
    },
    # 62. Автопродикс: merge P_OEM_7a28d7b7 into 1017
    {
        'target_id': 1017,
        'target_name': 'Автопродикс',
        'target_kam': 'Светлана Дариенко',
        'donor_ids': ['P_OEM_7a28d7b7']
    },
    # 63. Форсаж: merge P_OEM_0a1da625 into 1032
    {
        'target_id': 1032,
        'target_name': 'ГК Форсаж',
        'target_kam': 'Светлана Дариенко',
        'donor_ids': ['P_OEM_0a1da625']
    },
    # 64. Элке Авто: merge P_OEM_fd463b78 into 1219
    {
        'target_id': 1219,
        'target_name': 'Элке Авто',
        'target_kam': 'Светлана Дариенко',
        'donor_ids': ['P_OEM_fd463b78']
    },
    # 65. Рус-Авто Трейд: merge P_OEM_02fba7db into 1242
    {
        'target_id': 1242,
        'target_name': 'Рус-Авто Трейд',
        'target_kam': 'Светлана Дариенко',
        'donor_ids': ['P_OEM_02fba7db']
    },
    # 66. Сармат: merge 1019, P_OEM_e014612a into 1068
    {
        'target_id': 1068,
        'target_name': 'Сармат',
        'target_kam': 'Светлана Дариенко',
        'donor_ids': [1019, 'P_OEM_e014612a']
    },
    # 67. АлексМоторс: merge 1009, P_OEM_9e68591b into 1257
    {
        'target_id': 1257,
        'target_name': 'АлексМоторс',
        'target_kam': 'Светлана Дариенко',
        'donor_ids': [1009, 'P_OEM_9e68591b']
    },
    # 68. Автотим: merge P_OEM_7cc355e9 into 1254
    {
        'target_id': 1254,
        'target_name': 'Автотим',
        'target_kam': 'Светлана Дариенко',
        'donor_ids': ['P_OEM_7cc355e9']
    },
    # 69. Автокласс: merge 1155, P_OEM_26fd34c3 into 1102
    {
        'target_id': 1102,
        'target_name': 'Чери Центр Автокласс (М-Авто)',
        'target_kam': 'Алексей Чихарев',
        'donor_ids': [1155, 'P_OEM_26fd34c3']
    },
    # 70. Автохолдинг Максимум: merge P_OEM_b2de613c into 1163
    {
        'target_id': 1163,
        'target_name': 'Автохолдинг Максимум',
        'target_kam': 'Светлана Дариенко',
        'donor_ids': ['P_OEM_b2de613c']
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
            if did == tid:
                continue
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
    if not p1040:
        p1040 = {
            'partner_id': 1040,
            'canonical_name': 'Авто Премиум Тверь',
            'holding': 'Авто Премиум',
            'kam': 'Алексей Чихарев',
            'bitrix_aliases': [],
            'bi_aliases': [],
            'pochta_aliases': [],
            'oem_data': []
        }
        partners.append(p1040)
        partners_by_id[1040] = p1040
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

    # Wagner / Avtoretail M (1285) oem_data for Krasnodar (Soldatova) and SPb (Darienko)
    p1285 = partners_by_id.get(1285)
    if p1285:
        if 'oem_data' not in p1285 or p1285['oem_data'] is None:
            p1285['oem_data'] = []
        if not any(oem.get('city') == 'Краснодар' for oem in p1285['oem_data']):
            p1285['oem_data'].append({
                'sheet': 'B2C',
                'city': 'Краснодар',
                'name': 'Авторитэйл М Краснодар',
                'legal_entity': 'ООО Авторитэйл М',
                'responsible': 'Валерия Солдатова'
            })
        if not any(oem.get('city') == 'Санкт-Петербург' for oem in p1285['oem_data']):
            p1285['oem_data'].append({
                'sheet': 'B2C',
                'city': 'Санкт-Петербург',
                'name': 'Вагнер Авто / Авторитэйл М',
                'legal_entity': 'ООО Авторитэйл М',
                'responsible': 'Светлана Дариенко'
            })

    # 4. КМ/ч: Москва (1095) -> Алексей Чихарев (план: 1)
    p1095 = partners_by_id.get(1095)
    if p1095:
        p1095['canonical_name'] = 'КМ/Ч'
        p1095['holding'] = 'КМ/Ч'
        p1095['kam'] = 'Алексей Чихарев'
        for oem in p1095.get('oem_data', []):
            oem['responsible'] = 'Алексей Чихарев'

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

    # 5. Моторленд: Воронеж (1014) -> Валерия Солдатова, СПб / Сократ (1280) -> Светлана Дариенко
    p1014 = partners_by_id.get(1014)
    if p1014:
        p1014['canonical_name'] = 'Моторленд (Воронеж)'
        p1014['kam'] = 'Валерия Солдатова'
        p1014['bitrix_aliases'] = [a for a in p1014.get('bitrix_aliases', []) if 'сократ' not in a.lower()]

    p1280 = partners_by_id.get(1280)
    if p1280:
        p1280['canonical_name'] = 'Сократ (Моторленд СПб)'
        p1280['holding'] = 'Моторленд'
        p1280['kam'] = 'Светлана Дариенко'
        if 'bitrix_aliases' not in p1280 or not p1280['bitrix_aliases']:
            p1280['bitrix_aliases'] = []
        p1280['bitrix_aliases'].extend(['ONLINE ООО "СОКРАТ СПБ"', 'Моторленд СПб', 'Сократ'])
        p1280['bitrix_aliases'] = clean_list(p1280['bitrix_aliases'])

    # 6. Вагнер Авто и Авторитэйл М: 1285 -> Вагнер Авто / Авторитэйл (СПб -> Дариенко)
    p1285 = partners_by_id.get(1285)
    if p1285:
        p1285['canonical_name'] = 'Вагнер Авто / Авторитэйл'
        p1285['holding'] = 'Авторитэйл'
        p1285['kam'] = 'Светлана Дариенко'

    # 7. Леон Авто: Йошкар-Ола (1016) -> Евгения Добролюбова, Краснодар (1023) -> Валерия Солдатова
    p1016 = partners_by_id.get(1016)
    if p1016:
        p1016['canonical_name'] = 'Леон Авто (Йошкар-Ола)'
        p1016['holding'] = 'Леон Авто'
        p1016['kam'] = 'Евгения Добролюбова'
        p1016['bitrix_aliases'] = clean_list(['Online ООО "ЛЕОН"', 'Леон Авто (Йошкар-Ола)', 'ООО Леон', 'Леон Авто Йошкар-Ола'])
        p1016['bi_aliases'] = clean_list(['Леон Авто (Йошкар-Ола)'])
        p1016['oem_data'] = [
            {
                'sheet': 'JETOUR',
                'city': 'Йошкар-Ола',
                'group_link': 'https://max.ru/join/MhIQluReOMyTsqTqX1FM17Zu9hT1YQNLRsXWeuQud3U',
                'name': 'Леон Авто',
                'legal_entity': 'ООО Леон',
                'inn': '1207901941',
                'address': 'Республика Марий Эл пгт. Медведево,ул. Чехова, д. 16, корп. А',
                'back_name': '',
                'email': 'ksapego@avto-yola.ru',
                'responsible': 'Евгения Добролюбова',
                'brand': 'JETOUR'
            }
        ]

    p1023 = partners_by_id.get(1023)
    if p1023:
        p1023['canonical_name'] = 'Леон Авто'
        p1023['holding'] = 'Леон Авто'
        p1023['kam'] = 'Валерия Солдатова'
        p1023['bitrix_aliases'] = [a for a in p1023.get('bitrix_aliases', []) if a.strip().lower() != 'online ооо "леон"' and 'йошкар' not in a.lower()]
        p1023['oem_data'] = [oem for oem in p1023.get('oem_data', []) if (oem.get('city') or '').lower() != 'йошкар-ола']

    # 8. Р-Моторс: 1025 -> Светлана Дариенко (все города)
    p1025 = partners_by_id.get(1025)
    if p1025:
        p1025['canonical_name'] = 'Р-Моторс ЛАДА'
        p1025['holding'] = 'Р-Моторс'
        p1025['kam'] = 'Светлана Дариенко'
        if p1025.get('oem_data'):
            for oem in p1025['oem_data']:
                oem['responsible'] = 'Светлана Дариенко'

    # 9. ГК Глобус: 1013 -> Валерия Солдатова
    p1013 = partners_by_id.get(1013)
    if p1013:
        p1013['canonical_name'] = 'ГК Глобус'
        p1013['holding'] = 'ГК Глобус'
        p1013['kam'] = 'Валерия Солдатова'

    # 10. ГК Оптима: 1030 -> Валерия Солдатова
    p1030 = partners_by_id.get(1030)
    if p1030:
        p1030['canonical_name'] = 'ГК Оптима'
        p1030['holding'] = 'ГК Оптима'
        p1030['kam'] = 'Валерия Солдатова'

    # 11. ФДЦ Трансфор: 1003 -> Валерия Солдатова
    p1003 = partners_by_id.get(1003)
    if p1003:
        p1003['canonical_name'] = 'ФДЦ Трансфор'
        p1003['holding'] = 'ФДЦ Трансфор'
        p1003['kam'] = 'Валерия Солдатова'

    # 12. ФДЦ Техно-Темп: 1004 -> Валерия Солдатова
    p1004 = partners_by_id.get(1004)
    if p1004:
        p1004['canonical_name'] = 'ФДЦ Техно-Темп'
        p1004['holding'] = 'ФДЦ Техно-Темп'
        p1004['kam'] = 'Валерия Солдатова'

    # 13. Аларм-Моторс ГК: 1002 -> Светлана Дариенко
    p1002 = partners_by_id.get(1002)
    if p1002:
        p1002['canonical_name'] = 'Аларм-Моторс ГК'
        p1002['holding'] = 'Аларм-Моторс'
        p1002['kam'] = 'Светлана Дариенко'

    # 14. ЧЕРИ ЦЕНТР ПЛАНЕТА АВТО ВОСТОК: 1058 -> Евгения Добролюбова (все города, кроме Махачкалы, Таганрога и Москвы относятся к Добролюбовой)
    p1058 = partners_by_id.get(1058)
    if p1058:
        p1058['canonical_name'] = 'ЧЕРИ ЦЕНТР ПЛАНЕТА АВТО ВОСТОК'
        p1058['holding'] = 'Планета Авто'
        p1058['kam'] = 'Евгения Добролюбова'
        p1058['bi_aliases'] = clean_list((p1058.get('bi_aliases', []) or []) + ['Планета Авто', 'ЧЕРИ ЦЕНТР ПЛАНЕТА АВТО ВОСТОК', 'Гольфстрим'])
        p1058['bi_aliases'] = [a for a in p1058['bi_aliases'] if 'автофорум' not in a.lower()]
        for oem in p1058.get('oem_data', []):
            city_str = (oem.get('city') or '').lower()
            if 'махачкала' in city_str or 'таганрог' in city_str:
                oem['responsible'] = 'Валерия Солдатова'
            elif 'москва' in city_str or 'мск' in city_str:
                oem['responsible'] = 'Алексей Чихарев'
            else:
                oem['responsible'] = 'Евгения Добролюбова'

    # 15. Автолюкс Кар (Махачкала, Solaris): 1287 -> Валерия Солдатова
    p1287 = partners_by_id.get(1287)
    if not p1287:
        p1287 = {
            'partner_id': 1287,
            'canonical_name': 'Автолюкс Кар',
            'holding': 'Автолюкс Кар',
            'kam': 'Валерия Солдатова',
            'bitrix_aliases': ['Автолюкс Кар', 'ООО "АВТОЛЮКС КАР"', 'ООО Автолюкс Кар'],
            'bi_aliases': ['Автолюкс Кар', 'Автолюкс Кар Махачкала'],
            'pochta_aliases': ['Magomed.magomedov@solaris-autoluxecar.ru'],
            'oem_data': [
                {
                    'sheet': 'SOLARIS',
                    'city': 'Махачкала',
                    'group_link': 'https://t.me/+bjGeqy85mbE4ZDMy',
                    'name': 'Автолюкс Кар',
                    'legal_entity': 'ООО Автолюкс Кар',
                    'inn': '0546024274',
                    'address': 'г. Махачкала, пгт. Ленинкент, ул. Кизилюртовская д.88',
                    'back_name': 'Нет',
                    'email': 'Magomed.magomedov@solaris-autoluxecar.ru',
                    'responsible': 'Валерия Солдатова',
                    'brand': 'SOLARIS'
                }
            ],
            'status': 'verified'
        }
        partners.append(p1287)
        partners_by_id[1287] = p1287
    else:
        p1287['canonical_name'] = 'Автолюкс Кар'
        p1287['holding'] = 'Автолюкс Кар'
        p1287['kam'] = 'Валерия Солдатова'

    # 16. Гедон-Юг (Таганрог, Chery & Tenet): 1288 -> Валерия Солдатова
    p1288 = partners_by_id.get(1288)
    if not p1288:
        p1288 = {
            'partner_id': 1288,
            'canonical_name': 'Гедон-Юг',
            'holding': 'Гедон-Юг',
            'kam': 'Валерия Солдатова',
            'bitrix_aliases': ['Гедон-Юг', 'ООО "ГЕДОН-ЮГ"', 'ООО Гедон-Юг', 'Гедон Юг'],
            'bi_aliases': ['Гедон-Юг', 'Гедон-Юг Таганрог'],
            'pochta_aliases': ['a.pogosjan@chery-gedon.ru'],
            'oem_data': [
                {
                    'sheet': 'CHERY&TENET',
                    'city': 'Таганрог',
                    'group_link': 'https://t.me/+jhmuSnom4WxjM2My',
                    'name': 'Гедон-Юг',
                    'legal_entity': 'ООО Гедон-Юг',
                    'inn': '6154112410',
                    'address': 'г.Таганрог, Ростовское шоссе, 10',
                    'back_name': 'Нет',
                    'email': 'a.pogosjan@chery-gedon.ru',
                    'responsible': 'Валерия Солдатова',
                    'brand': 'CHERY & TENET'
                }
            ],
            'status': 'verified'
        }
        partners.append(p1288)
        partners_by_id[1288] = p1288
    else:
        p1288['canonical_name'] = 'Гедон-Юг'
        p1288['holding'] = 'Гедон-Юг'
        p1288['kam'] = 'Валерия Солдатова'

    # 17. Авто для Вас Премиум: 1229 -> Валерия Солдатова (строго Армавир, убрать Смоленск и Псков)
    p1229 = partners_by_id.get(1229)
    if p1229:
        p1229['canonical_name'] = 'Авто для Вас Премиум'
        p1229['holding'] = 'Авто для Вас Премиум'
        p1229['kam'] = 'Валерия Солдатова'
        p1229['oem_data'] = [
            oem for oem in p1229.get('oem_data', [])
            if (oem.get('city') or '').lower() == 'армавир'
            or '2312310273' in str(oem.get('inn') or '')
        ]

    # 18. Автосалон № 1: 1289 -> Светлана Дариенко (Псков, Chery & Tenet)
    p1289 = partners_by_id.get(1289)
    if not p1289:
        p1289 = {
            'partner_id': 1289,
            'canonical_name': 'Автосалон № 1',
            'holding': 'Автосалон № 1',
            'kam': 'Светлана Дариенко',
            'bitrix_aliases': ['Автосалон № 1', 'ООО "АВТОСАЛОН 1"', 'ООО Автосалон 1'],
            'bi_aliases': ['Автосалон № 1 Псков'],
            'pochta_aliases': [],
            'oem_data': [
                {
                    'sheet': 'CHERY&TENET',
                    'city': 'Псков',
                    'name': 'Автосалон № 1',
                    'legal_entity': 'ООО Автосалон 1',
                    'inn': '6000005056',
                    'responsible': 'Светлана Дариенко',
                    'brand': 'CHERY & TENET'
                }
            ],
            'status': 'verified'
        }
        partners.append(p1289)
        partners_by_id[1289] = p1289

    # 19. ГК Арконт Холдинг: 1112 -> Евгения Добролюбова (объединен с Чери Арконт 1223)
    p1112 = partners_by_id.get(1112)
    if p1112:
        p1112['canonical_name'] = 'ГК Арконт Холдинг'
        p1112['holding'] = 'ГК Арконт Холдинг'
        p1112['kam'] = 'Евгения Добролюбова'
        p1112['bitrix_aliases'] = clean_list((p1112.get('bitrix_aliases', []) or []) + ['Чери Арконт', 'ГК Арконт', 'ГК Арконт Холдинг', 'ООО Арконт ЯЛР Филиал №1', 'Арконт'])
        p1112['bi_aliases'] = clean_list((p1112.get('bi_aliases', []) or []) + ['Чери Арконт', 'ГК Арконт', 'ГК Арконт Холдинг', 'Арконт'])
        for oem in p1112.get('oem_data', []):
            oem['responsible'] = 'Евгения Добролюбова'

    # 20. ФДЦ Автосеть АМК РФ: 1053 -> Евгения Добролюбова (все объединено и закреплено за Добролюбовой)
    p1053 = partners_by_id.get(1053)
    if p1053:
        p1053['canonical_name'] = 'ФДЦ Автосеть АМК РФ'
        p1053['holding'] = 'ФДЦ Автосеть АМК РФ'
        p1053['kam'] = 'Евгения Добролюбова'
        p1053['bitrix_aliases'] = clean_list((p1053.get('bitrix_aliases', []) or []) + [
            'ФДЦ Автосеть АМК РФ',
            'ONLINE АМК Тольятти (ООО "АМ Компани")',
            'ONLINE АМК Самара ООО "УРАЛ-ЛАДА"',
            'пилот ФДЦ Автосеть РФ АМК Самара Тольятти ЕКБ',
            'Online АМК-ЕКАТЕРИНБУРГ',
            'ООО АМК-ЕКАТЕРИНБУРГ',
            'АМК-Екатеринбург'
        ])
        p1053['bi_aliases'] = clean_list((p1053.get('bi_aliases', []) or []) + [
            'ФДЦ Автосеть АМК РФ',
            'ONLINE  пилот ФДЦ Автосеть РФ АМК Самара Тольятти ЕКБ',
            'пилот ФДЦ Автосеть РФ АМК Самара Тольятти ЕКБ',
            'ONLINE пилот ФДЦ Автосеть РФ АМК Самара Тольятти',
            'АМК-Екатеринбург'
        ])
        for oem in p1053.get('oem_data', []):
            oem['responsible'] = 'Евгения Добролюбова'

    # 21. Эксперт Авто (Новосибирск): 1035 -> Евгения Добролюбова (закреплен за Добролюбовой)
    p1035 = partners_by_id.get(1035)
    if p1035:
        p1035['canonical_name'] = 'Эксперт Авто (Новосибирск)'
        p1035['holding'] = 'Эксперт Авто'
        p1035['kam'] = 'Евгения Добролюбова'
        p1035['bitrix_aliases'] = clean_list((p1035.get('bitrix_aliases', []) or []) + [
            'Эксперт Авто (Новосибирск)',
            'ONLINE ГК Эксперт Авто \\ ООО "ЭКСПЕРТ АВТО НСК"',
            'ООО "ЭКСПЕРТ АВТО НСК"',
            'Эксперт Авто Новосибирск'
        ])
        p1035['oem_data'] = [oem for oem in p1035.get('oem_data', []) if 'уфа' not in (oem.get('city') or '').lower() and 'верра' not in (oem.get('name') or '').lower()]
        for oem in p1035['oem_data']:
            oem['responsible'] = 'Евгения Добролюбова'

    # 22. Дебрянск Авто: 1177 -> Валерия Солдатова (объединен с 1186, 1187, 632038)
    p1177 = partners_by_id.get(1177)
    if p1177:
        p1177['canonical_name'] = 'Дебрянск Авто'
        p1177['holding'] = 'Дебрянск Авто'
        p1177['kam'] = 'Валерия Солдатова'
        p1177['bitrix_aliases'] = clean_list((p1177.get('bitrix_aliases', []) or []) + [
            'Дебрянск Авто',
            'ГК БН-МОТОРС',
            'Дебрянск Авто (Дебрянск Авто)',
            'ООО "ДЕБРЯНСК АВТО" ONLINE',
            'ООО "МБ-БРЯНСК" ONLINE',
            'ONLINE ООО "БНМ-1"',
            'БНМ-3'
        ])
        p1177['bi_aliases'] = clean_list((p1177.get('bi_aliases', []) or []) + [
            'Дебрянск Авто',
            'ГК БН-МОТОРС, БНМ',
            'ГК БН-МОТОРС',
            'Дебрянск Авто (Дебрянск Авто)',
            'Дебрянск Авто (Крона Авто)'
        ])
        for oem in p1177.get('oem_data', []):
            oem['responsible'] = 'Валерия Солдатова'

    # 23. Юг-Авто (Краснодар): 1290 -> Валерия Солдатова (отделен от АвтоЮг 1228)
    p1228 = partners_by_id.get(1228)
    yug_avto_oem = []
    if p1228:
        kept_oem = []
        for oem in p1228.get('oem_data', []):
            if 'юг-авто' in (oem.get('name') or '').lower() or '2310079830' in str(oem.get('inn') or '') or '2311120713' in str(oem.get('inn') or ''):
                oem['responsible'] = 'Валерия Солдатова'
                yug_avto_oem.append(oem)
            else:
                kept_oem.append(oem)
        p1228['oem_data'] = kept_oem
        p1228['bitrix_aliases'] = [a for a in p1228.get('bitrix_aliases', []) if 'юг-авто' not in a.lower()]

    p1290 = partners_by_id.get(1290)
    if not p1290:
        p1290 = {
            'partner_id': 1290,
            'canonical_name': 'Юг-Авто',
            'holding': 'Юг-Авто',
            'kam': 'Валерия Солдатова',
            'bitrix_aliases': clean_list([
                'ONLINE ООО АК «Юг-Авто»',
                'Юг-Авто',
                'ООО "АК "ЮГ-АВТО"',
                'ООО АК «Юг-Авто»',
                'ООО "ДЦ ЮГ-АВТО"',
                'ООО ДЦ Юг-Авто',
                'ООО АК Юг-Авто',
                'ООО ДЦ Юг-Авто'
            ]),
            'bi_aliases': ['Юг-Авто'],
            'pochta_aliases': [],
            'oem_data': yug_avto_oem,
            'status': 'verified'
        }
        partners.append(p1290)
        partners_by_id[1290] = p1290
    else:
        p1290['canonical_name'] = 'Юг-Авто'
        p1290['holding'] = 'Юг-Авто'
        p1290['kam'] = 'Валерия Солдатова'
        if yug_avto_oem and not p1290.get('oem_data'):
            p1290['oem_data'] = yug_avto_oem

    # 24. ААА Моторс (Ростов-на-Дону): 1291 -> Валерия Солдатова (отделен от Артекс 1065)
    p1065 = partners_by_id.get(1065)
    aaa_oem = []
    if p1065:
        kept_oem = []
        for oem in p1065.get('oem_data', []):
            if 'ааа' in (oem.get('name') or '').lower() or '6168043686' in str(oem.get('inn') or ''):
                oem['responsible'] = 'Валерия Солдатова'
                aaa_oem.append(oem)
            else:
                kept_oem.append(oem)
        p1065['oem_data'] = kept_oem
        p1065['bitrix_aliases'] = [a for a in p1065.get('bitrix_aliases', []) if 'формула' not in a.lower() and 'ааа' not in a.lower()]

    p1291 = partners_by_id.get(1291)
    if not p1291:
        p1291 = {
            'partner_id': 1291,
            'canonical_name': 'ААА Моторс',
            'holding': 'ААА Моторс',
            'kam': 'Валерия Солдатова',
            'bitrix_aliases': clean_list([
                'Online ООО "ФОРМУЛА-Н"',
                'ААА Моторс',
                'ООО "Формула Н"',
                'ООО Формула Н',
                'Формула-Н',
                'Формула Н'
            ]),
            'bi_aliases': ['ААА Моторс', 'ААА-Моторс'],
            'pochta_aliases': [],
            'oem_data': aaa_oem,
            'status': 'verified'
        }
        partners.append(p1291)
        partners_by_id[1291] = p1291
    else:
        p1291['canonical_name'] = 'ААА Моторс'
        p1291['holding'] = 'ААА Моторс'
        p1291['kam'] = 'Валерия Солдатова'
        if aaa_oem and not p1291.get('oem_data'):
            p1291['oem_data'] = aaa_oem


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

    modified = False
    # Sync partners_registry in data.json with the canonical partners_registry.json
    reg_path = os.path.join(PROJECT_ROOT, 'partners_registry.json')
    if os.path.exists(reg_path):
        with open(reg_path, 'r', encoding='utf-8') as rf:
            reg_data = json.load(rf)
            data['partners_registry'] = reg_data.get('partners', [])
            modified = True

    donor_to_target = {}
    for m in MERGERS:
        for did in m['donor_ids']:
            donor_to_target[did] = (m['target_id'], m['target_name'], m['target_kam'])
    for r in data.get('sys_db_partners', []):
        pid = r.get('PartnerId')
        if pid in donor_to_target:
            tid, tname, tkam = donor_to_target[pid]
            r['PartnerId'] = tid
            r['Partner'] = tname
            if tkam: r['KAM'] = tkam
            modified = True

        # Fix Spektr / Apelsin (ООО "СПЕКТР" ONLINE АВТОСЕТЬ РФ/Апельсин) -> 1054 Апельсин-Челны (Чихарев)
        raw_p = (r.get('RawPartner') or '').upper()
        p_name = (r.get('Partner') or '').upper()
        raw_p_low = (r.get('RawPartner') or '').lower()
        p_name_low = (r.get('Partner') or '').lower()
        if ('СПЕКТР' in raw_p and 'АПЕЛЬСИН' in raw_p) or ('АПЕЛЬСИН' in p_name):
            if r.get('PartnerId') == 1049:
                r['PartnerId'] = 1054
                r['Partner'] = 'Апельсин-Челны'
                r['KAM'] = 'Алексей Чихарев'
                modified = True

        # Fix АнкарАвто -> 1090 Анкар Калуга (Чихарев)
        if (r.get('Partner') == 'АнкарАвто' or 'АНКАРАВТО' in raw_p) and r.get('PartnerId') == 1119:
            r['PartnerId'] = 1090
            r['Partner'] = 'Анкар Калуга'
            r['KAM'] = 'Алексей Чихарев'
            modified = True

        # Wagner / Autoretail allocation: SPb -> Svetlana Darienko, Krasnodar -> Valeria Soldatova
        if r.get('PartnerId') == 1285 or 'ВАГНЕР' in raw_p or 'АВТОРИТЭЙЛ' in raw_p:
            city_str = str(r.get('City') or '').lower()
            raw_str = raw_p.lower()
            r['PartnerId'] = 1285
            r['Partner'] = 'Вагнер Авто / Авторитэйл'
            if any(k in city_str or k in raw_str for k in ['краснодар', 'юг', 'кубань']):
                r['KAM'] = 'Валерия Солдатова'
            elif any(k in city_str or k in raw_str for k in ['спб', 'санкт-петербург', 'петербург', 'вагнер']):
                r['KAM'] = 'Светлана Дариенко'
            else:
                r['KAM'] = 'Светлана Дариенко'
            modified = True

        # Leon Auto allocation: Yoshkar-Ola -> Evgenia Dobrolyubova, Krasnodar -> Valeria Soldatova
        if r.get('PartnerId') in [1016, 1023] or 'ЛЕОН' in raw_p or 'ДМ-АВТО' in raw_p:
            city_str = str(r.get('City') or '').lower()
            raw_str = raw_p.lower()
            if 'йошкар' in city_str or 'йошкар' in raw_str or raw_str == 'online ооо "леон"' or raw_p == 'ONLINE ООО "ЛЕОН"':
                r['PartnerId'] = 1016
                r['Partner'] = 'Леон Авто (Йошкар-Ола)'
                r['KAM'] = 'Евгения Добролюбова'
                modified = True
            elif 'краснодар' in city_str or 'дм-авто' in raw_str or 'леон-авто' in raw_str or 'леон авто' in raw_str:
                r['PartnerId'] = 1023
                r['Partner'] = 'Леон Авто'
                r['KAM'] = 'Валерия Солдатова'
                modified = True

        # R-Motors allocation: all cities -> Svetlana Darienko
        if r.get('PartnerId') in [1008, 1025, 1131] or 'Р-МОТОРС' in raw_p or 'Р МОТОРС' in raw_p or 'Р-МОТОРС' in p_name:
            r['PartnerId'] = 1025
            r['Partner'] = 'Р-Моторс ЛАДА'
            r['KAM'] = 'Светлана Дариенко'
            modified = True

        # KM/Ch allocation: strictly Alexei Chikharev
        if r.get('PartnerId') in [1095, 1203] or 'км/ч' in raw_p or 'км/ч' in p_name or 'км-ч' in raw_p:
            r['PartnerId'] = 1095
            r['Partner'] = 'КМ/Ч'
            r['KAM'] = 'Алексей Чихарев'
            modified = True

        # Globus allocation (including Tambov-Auto 1115)
        if r.get('PartnerId') in [1013, 1115] or 'глобус' in (p_name or '').lower() or 'тамбов' in (raw_p or '').lower() or 'тамбов' in (p_name or '').lower():
            r['PartnerId'] = 1013
            r['Partner'] = 'ГК Глобус'
            r['KAM'] = 'Валерия Солдатова'
            modified = True

        # Motorland / Sokrat allocation:
        if r.get('PartnerId') == 1014 or r.get('PartnerId') == 1280 or 'МОТОРЛЕНД' in raw_p or 'СОКРАТ' in raw_p:
            city_str = str(r.get('City') or '').lower()
            raw_str = raw_p.lower()
            if 'сократ' in raw_str or any(k in city_str for k in ['спб', 'санкт-петербург']):
                r['PartnerId'] = 1280
                r['Partner'] = 'Сократ (Моторленд СПб)'
                r['KAM'] = 'Светлана Дариенко'
                modified = True
            else:
                r['PartnerId'] = 1014
                r['Partner'] = 'Моторленд (Воронеж)'
                r['KAM'] = 'Валерия Солдатова'
                modified = True

        # Autolux Car (Makhachkala): 1287 -> Valeria Soldatova
        if 'автолюкс кар' in raw_p or 'автолюкс кар' in p_name:
            r['PartnerId'] = 1287
            r['Partner'] = 'Автолюкс Кар'
            r['KAM'] = 'Валерия Солдатова'
            modified = True

        # Gedon-Yug (Taganrog): 1288 -> Valeria Soldatova
        if 'гедон-юг' in raw_p or 'гедон юг' in raw_p:
            r['PartnerId'] = 1288
            r['Partner'] = 'Гедон-Юг'
            r['KAM'] = 'Валерия Солдатова'
            modified = True

        # 1. Чери арконт и ГК Арконт холдинг - объединить (ID 1112, ГК Арконт Холдинг, KAM: Евгения Добролюбова)
        if r.get('PartnerId') in [1112, 1223] or 'арконт' in raw_p_low or 'арконт' in p_name_low:
            r['PartnerId'] = 1112
            r['Partner'] = 'ГК Арконт Холдинг'
            if r.get('Month', '') >= '2026-09':
                r['KAM'] = 'Евгения Добролюбова'
            elif r.get('KAM') != 'Андрей Кузнецов':
                r['KAM'] = 'Евгения Добролюбова'
            modified = True

        # 2. Чери Центр Планета АВто восток, все города, кроме Махачкалы, Таганрога и Москвы Относятся к Добролюбовой
        if r.get('PartnerId') == 1058 or 'планета авто' in raw_p_low or 'планета авто' in p_name_low or 'планета-авто' in raw_p_low or 'планета-авто' in p_name_low or 'автогарантия' in raw_p_low:
            r['PartnerId'] = 1058
            r['Partner'] = 'ЧЕРИ ЦЕНТР ПЛАНЕТА АВТО ВОСТОК'
            city_str = (str(r.get('City') or '') + ' ' + raw_p_low + ' ' + p_name_low).lower()
            if 'махачкала' in city_str or 'таганрог' in city_str:
                r['KAM'] = 'Валерия Солдатова'
            elif 'москва' in city_str or 'мск' in city_str:
                r['KAM'] = 'Алексей Чихарев'
            else:
                if r.get('Month', '') >= '2026-09':
                    r['KAM'] = 'Евгения Добролюбова'
            modified = True

        # 3. ФДЦ Автосеть АМК РФ объединить в одно и закрепить все за Добролюбовой (ID 1053)
        if (r.get('PartnerId') in [1053, 1236, 632018] or
            'автосеть амк' in raw_p_low or 'автосеть амк' in p_name_low or
            'автосеть рф амк' in raw_p_low or 'автосеть рф амк' in p_name_low or
            'амк-екатеринбург' in raw_p_low or 'амк-екатеринбург' in p_name_low or
            'амк екатеринбург' in raw_p_low or 'амк екатеринбург' in p_name_low or
            (('амк' in raw_p_low or 'амк' in p_name_low) and not any(ex in raw_p_low for ex in ['амкапитал', 'ам капитал', 'апельсин', 'автомир']))):
            r['PartnerId'] = 1053
            r['Partner'] = 'ФДЦ Автосеть АМК РФ'
            r['KAM'] = 'Евгения Добролюбова'
            modified = True

        # 4. Эксперт авто Новосибирск - Закрепить за Добролюбовой (сделки в сентябре на Дариенко, с октября на Добролюбовой)
        if (r.get('PartnerId') == 1035 or
            any(k in raw_p_low for k in ['эксперт авто нск', 'эксперт авто \\ ооо "эксперт авто нск"', 'эксперт авто новосибирск']) or
            (('эксперт авто' in raw_p_low or 'эксперт авто' in p_name_low or 'эксперт-авто' in raw_p_low) and
             any(c in (str(r.get('City') or '') + ' ' + raw_p_low).lower() for c in ['новосибирск', 'нск']))):
            r['PartnerId'] = 1035
            r['Partner'] = 'Эксперт Авто (Новосибирск)'
            m = r.get('Month') or ''
            if m == '2026-09':
                r['KAM'] = 'Светлана Дариенко'
            elif m >= '2026-10':
                r['KAM'] = 'Евгения Добролюбова'
            modified = True

        # 5. Дебрянск Авто (ID 1177, Валерия Солдатова)
        if (r.get('PartnerId') in [1177, 1186, 1187, 632038] or
            any(k in raw_p_low for k in ['дебрянск', 'мб-брянск', 'бнм-1', 'бнм-3', 'бн-моторс', 'бн моторс']) or
            any(k in p_name_low for k in ['дебрянск', 'мб-брянск', 'бн-моторс', 'бн моторс'])):
            r['PartnerId'] = 1177
            r['Partner'] = 'Дебрянск Авто'
            if r.get('Month', '') >= '2026-09':
                r['KAM'] = 'Валерия Солдатова'
            elif r.get('KAM') != 'Андрей Кузнецов':
                r['KAM'] = 'Валерия Солдатова'
            modified = True

        # 6. Юг-Авто (ID 1290, Валерия Солдатова) - Краснодар
        if (r.get('PartnerId') == 1290 or
            (('юг-авто' in raw_p_low or 'юг авто' in raw_p_low or 'ак «юг-авто»' in raw_p_low or 'дц юг-авто' in raw_p_low) and
             not ('автоюг' in raw_p_low and not 'юг-авто' in raw_p_low))):
            r['PartnerId'] = 1290
            r['Partner'] = 'Юг-Авто'
            r['KAM'] = 'Валерия Солдатова'
            modified = True

        # 7. ААА Моторс (ID 1291, Валерия Солдатова) - Ростов-на-Дону
        if (r.get('PartnerId') == 1291 or
            any(k in raw_p_low for k in ['формула-н', 'формула н', 'ааа моторс', 'ааа-моторс']) or
            any(k in p_name_low for k in ['ааа моторс', 'ааа-моторс'])):
            r['PartnerId'] = 1291
            r['Partner'] = 'ААА Моторс'
            r['KAM'] = 'Валерия Солдатова'
            modified = True

        # 8. Нижегородец -> 1071 Нижегородец, Евгения Добролюбова (все месяцы)
        if r.get('PartnerId') == 1071 or 'нижегородец' in raw_p_low or 'нижегородец' in p_name_low:
            r['PartnerId'] = 1071
            r['Partner'] = 'Нижегородец'
            r['KAM'] = 'Евгения Добролюбова'
            modified = True

        # 9. Форвард-Авто -> 1060 Форвард Ижевск/Сызрань, Евгения Добролюбова (все месяцы)
        if (r.get('PartnerId') in [1051, 1060, 632013, 632020] or
            (('форвард' in raw_p_low or 'форвард' in p_name_low) and not any(ex in raw_p_low for ex in ['диамант', 'диаманд']))):
            r['PartnerId'] = 1060
            r['Partner'] = 'Форвард Ижевск/Сызрань'
            r['KAM'] = 'Евгения Добролюбова'
            modified = True

        # 10. Дав-Авто -> 1184 Дав-Авто, Евгения Добролюбова (все месяцы)
        if r.get('PartnerId') in [1088, 1184] or 'дав-авто' in raw_p_low or 'дав-авто' in p_name_low or 'дав авто' in raw_p_low:
            r['PartnerId'] = 1184
            r['Partner'] = 'Дав-Авто'
            r['KAM'] = 'Евгения Добролюбова'
            modified = True

        # 11. Сатурн-Р -> 1110 Сатурн-Р, Евгения Добролюбова (Пермь)
        if (r.get('PartnerId') in [1110, 'P_OEM_6e979ac2'] or
            (('сатурн-р' in raw_p_low or 'сатурн-р' in p_name_low or 'сатурн р' in raw_p_low or 'сатурн р' in p_name_low) and not ('липецк' in raw_p_low or 'липецк' in p_name_low))):
            r['PartnerId'] = 1110
            r['Partner'] = 'Сатурн-Р'
            r['KAM'] = 'Евгения Добролюбова'
            modified = True

        # 12. Tenet / Haval Автопремьер М -> Уфа Haval / Tenet Автопремьер М, Евгения Добролюбова
        if (r.get('PartnerId') in ['P_OEM_b19664be', 'P_OEM_ac181614'] or
            'автопремьер м' in raw_p_low or 'автопремьер м' in p_name_low or 'авпремьер м' in raw_p_low):
            r['PartnerId'] = 'P_OEM_ac181614'
            r['Partner'] = 'Уфа Haval / Tenet Автопремьер М'
            r['KAM'] = 'Евгения Добролюбова'
            modified = True

        # 13. Асмото / Асмото Тагил -> ООО "Асмото", Евгения Добролюбова
        if r.get('PartnerId') == 'P_OEM_ae51d9c1' or 'асмото' in raw_p_low or 'асмото' in p_name_low:
            r['PartnerId'] = 'P_OEM_ae51d9c1'
            r['Partner'] = 'ООО "Асмото"'
            r['KAM'] = 'Евгения Добролюбова'
            modified = True

        # 14. Юникор Дзержинск -> 1086 ЮНИКОР Дзержинск НН, Евгения Добролюбова (все месяцы)
        if r.get('PartnerId') in [1086, 632014] or 'юникор' in raw_p_low or 'юникор' in p_name_low:
            r['PartnerId'] = 1086
            r['Partner'] = 'ЮНИКОР Дзержинск НН'
            r['KAM'] = 'Евгения Добролюбова'
            modified = True

        # 15. Автолидер ГАК / Автолидер online -> 1266 Автолидер ГАК, Евгения Добролюбова
        if r.get('PartnerId') in [1266, 632031] or 'автолидер' in raw_p_low or 'автолидер' in p_name_low:
            r['PartnerId'] = 1266
            r['Partner'] = 'Автолидер ГАК'
            r['KAM'] = 'Евгения Добролюбова'
            modified = True

        # 16. АсАвто на Алмаатинской -> P_OEM_943c0828, Евгения Добролюбова
        if r.get('PartnerId') == 'P_OEM_943c0828' or 'асавто' in raw_p_low or 'асавто' in p_name_low:
            r['PartnerId'] = 'P_OEM_943c0828'
            r['Partner'] = 'АсАвто на Алмаатинской'
            r['KAM'] = 'Евгения Добролюбова'
            modified = True

        # 17. Армада Уфа, Ульяновск -> 1128 ООО "ТД АРМАДА-АВТО, Евгения Добролюбова
        if r.get('PartnerId') == 1128 or 'армада-авто' in raw_p_low or 'армада-авто' in p_name_low or 'армада авто' in raw_p_low:
            r['PartnerId'] = 1128
            r['Partner'] = 'ООО "ТД АРМАДА-АВТО'
            r['KAM'] = 'Евгения Добролюбова'
            modified = True

        # 18. Гедон Юг -> 1288 Гедон-Юг, Валерия Солдатова (убрать с Добролюбовой)
        if r.get('PartnerId') in [1230, 1288] or 'гедон' in raw_p_low or 'гедон' in p_name_low:
            r['PartnerId'] = 1288
            r['Partner'] = 'Гедон-Юг'
            r['KAM'] = 'Валерия Солдатова'
            modified = True

        # 19. Автохолдинг Максимум -> 1163 Автохолдинг Максимум, Светлана Дариенко (убрать с Добролюбовой)
        if r.get('PartnerId') in [1163, 1234] or 'максимум' in raw_p_low or 'максимум' in p_name_low or 'lucky motors' in raw_p_low:
            r['PartnerId'] = 1163
            r['Partner'] = 'Автохолдинг Максимум'
            r['KAM'] = 'Светлана Дариенко'
            modified = True

        # 20. Авто Сити (1118) -> перенести сделки на 1114 ООО "ВОРОНЕЖ-АВТО-СИТИ", Валерия Солдатова
        if (r.get('PartnerId') in [1114, 1118, 1175] or
            'воронеж-авто-сити' in raw_p_low or 'воронеж-авто-сити' in p_name_low or
            (('авто сити' in raw_p_low or 'авто сити' in p_name_low or 'авто-сити' in raw_p_low) and not ('мэйджор' in raw_p_low or 'major' in raw_p_low))):
            r['PartnerId'] = 1114
            r['Partner'] = 'ООО "ВОРОНЕЖ-АВТО-СИТИ'
            r['KAM'] = 'Валерия Солдатова'
            modified = True

    for r in data.get('deals', []):
        pid = r.get('PartnerId')
        if pid in donor_to_target:
            tid, tname, tkam = donor_to_target[pid]
            r['PartnerId'] = tid
            r['PartnerName'] = tname
            if tkam: r['KAM'] = tkam
            modified = True

        raw_p = (r.get('RawPartner') or '').upper()
        p_name = (r.get('PartnerName') or '').upper()
        raw_p_low = (r.get('RawPartner') or '').lower()
        p_name_low = (r.get('PartnerName') or '').lower()
        if ('СПЕКТР' in raw_p and 'АПЕЛЬСИН' in raw_p) or ('АПЕЛЬСИН' in p_name):
            if r.get('PartnerId') == 1049:
                r['PartnerId'] = 1054
                r['PartnerName'] = 'Апельсин-Челны'
                r['KAM'] = 'Алексей Чихарев'
                modified = True

        if (r.get('PartnerName') == 'АнкарАвто' or 'АНКАРАВТО' in raw_p) and r.get('PartnerId') == 1119:
            r['PartnerId'] = 1090
            r['PartnerName'] = 'Анкар Калуга'
            r['KAM'] = 'Алексей Чихарев'
            modified = True

        if r.get('PartnerId') == 1285 or 'ВАГНЕР' in raw_p or 'АВТОРИТЭЙЛ' in raw_p:
            city_str = str(r.get('City') or '').lower()
            raw_str = raw_p.lower()
            r['PartnerId'] = 1285
            r['PartnerName'] = 'Вагнер Авто / Авторитэйл'
            if any(k in city_str or k in raw_str for k in ['краснодар', 'юг', 'кубань']):
                r['KAM'] = 'Валерия Солдатова'
            elif any(k in city_str or k in raw_str for k in ['спб', 'санкт-петербург', 'петербург', 'вагнер']):
                r['KAM'] = 'Светлана Дариенко'
            else:
                r['KAM'] = 'Светлана Дариенко'
            modified = True

        if r.get('PartnerId') in [1016, 1023] or 'ЛЕОН' in raw_p or 'ДМ-АВТО' in raw_p:
            city_str = str(r.get('City') or '').lower()
            raw_str = raw_p.lower()
            if 'йошкар' in city_str or 'йошкар' in raw_str or raw_str == 'online ооо "леон"' or raw_p == 'ONLINE ООО "ЛЕОН"':
                r['PartnerId'] = 1016
                r['PartnerName'] = 'Леон Авто (Йошкар-Ола)'
                r['KAM'] = 'Евгения Добролюбова'
                modified = True
            elif 'краснодар' in city_str or 'дм-авто' in raw_str or 'леон-авто' in raw_str or 'леон авто' in raw_str:
                r['PartnerId'] = 1023
                r['PartnerName'] = 'Леон Авто'
                r['KAM'] = 'Валерия Солдатова'
                modified = True

        if r.get('PartnerId') in [1008, 1025, 1131] or 'Р-МОТОРС' in raw_p or 'Р МОТОРС' in raw_p or 'Р-МОТОРС' in p_name:
            r['PartnerId'] = 1025
            r['PartnerName'] = 'Р-Моторс ЛАДА'
            r['KAM'] = 'Светлана Дариенко'
            modified = True

        # KM/Ch: strictly Alexei Chikharev
        if r.get('PartnerId') in [1095, 1203] or 'км/ч' in raw_p or 'км/ч' in p_name or 'км-ч' in raw_p:
            r['PartnerId'] = 1095
            r['PartnerName'] = 'КМ/Ч'
            r['KAM'] = 'Алексей Чихарев'
            modified = True

        # Globus allocation (including Tambov-Auto 1115)
        if r.get('PartnerId') in [1013, 1115] or 'глобус' in (p_name or '').lower() or 'тамбов' in (raw_p or '').lower() or 'тамбов' in (p_name or '').lower():
            r['PartnerId'] = 1013
            r['PartnerName'] = 'ГК Глобус'
            r['KAM'] = 'Валерия Солдатова'
            modified = True

        if r.get('PartnerId') == 1014 or r.get('PartnerId') == 1280 or 'МОТОРЛЕНД' in raw_p or 'СОКРАТ' in raw_p:
            city_str = str(r.get('City') or '').lower()
            raw_str = raw_p.lower()
            if 'сократ' in raw_str or any(k in city_str for k in ['спб', 'санкт-петербург']):
                r['PartnerId'] = 1280
                r['PartnerName'] = 'Сократ (Моторленд СПб)'
                r['KAM'] = 'Светлана Дариенко'
                modified = True
            else:
                r['PartnerId'] = 1014
                r['PartnerName'] = 'Моторленд (Воронеж)'
                r['KAM'] = 'Валерия Солдатова'
                modified = True

        # Autolux Car (Makhachkala): 1287 -> Valeria Soldatova
        if 'автолюкс кар' in raw_p or 'автолюкс кар' in p_name:
            r['PartnerId'] = 1287
            r['PartnerName'] = 'Автолюкс Кар'
            r['KAM'] = 'Валерия Солдатова'
            modified = True

        # Gedon-Yug (Taganrog): 1288 -> Valeria Soldatova
        if 'гедон-юг' in raw_p or 'гедон юг' in raw_p:
            r['PartnerId'] = 1288
            r['PartnerName'] = 'Гедон-Юг'
            r['KAM'] = 'Валерия Солдатова'
            modified = True

        # 1. Чери арконт и ГК Арконт холдинг - объединить (ID 1112, ГК Арконт Холдинг, KAM: Евгения Добролюбова)
        if r.get('PartnerId') in [1112, 1223] or 'арконт' in raw_p_low or 'арконт' in p_name_low:
            r['PartnerId'] = 1112
            r['PartnerName'] = 'ГК Арконт Холдинг'
            if r.get('Month', '') >= '2026-09':
                r['KAM'] = 'Евгения Добролюбова'
            elif r.get('KAM') != 'Андрей Кузнецов':
                r['KAM'] = 'Евгения Добролюбова'
            modified = True

        # 2. Чери Центр Планета АВто восток, все города, кроме Махачкалы, Таганрога и Москвы Относятся к Добролюбовой
        if r.get('PartnerId') == 1058 or 'планета авто' in raw_p_low or 'планета авто' in p_name_low or 'планета-авто' in raw_p_low or 'планета-авто' in p_name_low or 'автогарантия' in raw_p_low:
            r['PartnerId'] = 1058
            r['PartnerName'] = 'ЧЕРИ ЦЕНТР ПЛАНЕТА АВТО ВОСТОК'
            city_str = (str(r.get('City') or '') + ' ' + raw_p_low + ' ' + p_name_low).lower()
            if 'махачкала' in city_str or 'таганрог' in city_str:
                r['KAM'] = 'Валерия Солдатова'
            elif 'москва' in city_str or 'мск' in city_str:
                r['KAM'] = 'Алексей Чихарев'
            else:
                if r.get('Month', '') >= '2026-09':
                    r['KAM'] = 'Евгения Добролюбова'
            modified = True

        # 3. ФДЦ Автосеть АМК РФ объединить в одно и закрепить все за Добролюбовой (ID 1053)
        if (r.get('PartnerId') in [1053, 1236, 632018] or
            'автосеть амк' in raw_p_low or 'автосеть амк' in p_name_low or
            'автосеть рф амк' in raw_p_low or 'автосеть рф амк' in p_name_low or
            'амк-екатеринбург' in raw_p_low or 'амк-екатеринбург' in p_name_low or
            'амк екатеринбург' in raw_p_low or 'амк екатеринбург' in p_name_low or
            (('амк' in raw_p_low or 'амк' in p_name_low) and not any(ex in raw_p_low for ex in ['амкапитал', 'ам капитал', 'апельсин', 'автомир']))):
            r['PartnerId'] = 1053
            r['PartnerName'] = 'ФДЦ Автосеть АМК РФ'
            r['KAM'] = 'Евгения Добролюбова'
            modified = True

        # 4. Эксперт авто Новосибирск - Закрепить за Добролюбовой (сделки в сентябре на Дариенко, с октября на Добролюбовой)
        if (r.get('PartnerId') == 1035 or
            any(k in raw_p_low for k in ['эксперт авто нск', 'эксперт авто \\ ооо "эксперт авто нск"', 'эксперт авто новосибирск']) or
            (('эксперт авто' in raw_p_low or 'эксперт авто' in p_name_low or 'эксперт-авто' in raw_p_low) and
             any(c in (str(r.get('City') or '') + ' ' + raw_p_low).lower() for c in ['новосибирск', 'нск']))):
            r['PartnerId'] = 1035
            r['PartnerName'] = 'Эксперт Авто (Новосибирск)'
            m = r.get('Month') or ''
            if m == '2026-09':
                r['KAM'] = 'Светлана Дариенко'
            elif m >= '2026-10':
                r['KAM'] = 'Евгения Добролюбова'
            modified = True

        # 5. Дебрянск Авто (ID 1177, Валерия Солдатова)
        if (r.get('PartnerId') in [1177, 1186, 1187, 632038] or
            any(k in raw_p_low for k in ['дебрянск', 'мб-брянск', 'бнм-1', 'бнм-3', 'бн-моторс', 'бн моторс']) or
            any(k in p_name_low for k in ['дебрянск', 'мб-брянск', 'бн-моторс', 'бн моторс'])):
            r['PartnerId'] = 1177
            r['PartnerName'] = 'Дебрянск Авто'
            if r.get('KAM') != 'Андрей Кузнецов':
                r['KAM'] = 'Валерия Солдатова'
            modified = True

        # 6. Юг-Авто (ID 1290, Валерия Солдатова) - Краснодар
        if (r.get('PartnerId') == 1290 or
            (('юг-авто' in raw_p_low or 'юг авто' in raw_p_low or 'ак «юг-авто»' in raw_p_low or 'дц юг-авто' in raw_p_low) and
             not ('автоюг' in raw_p_low and not 'юг-авто' in raw_p_low))):
            r['PartnerId'] = 1290
            r['PartnerName'] = 'Юг-Авто'
            r['KAM'] = 'Валерия Солдатова'
            modified = True

        # 7. ААА Моторс (ID 1291, Валерия Солдатова) - Ростов-на-Дону
        if (r.get('PartnerId') == 1291 or
            any(k in raw_p_low for k in ['формула-н', 'формула н', 'ааа моторс', 'ааа-моторс']) or
            any(k in p_name_low for k in ['ааа моторс', 'ааа-моторс'])):
            r['PartnerId'] = 1291
            r['PartnerName'] = 'ААА Моторс'
            r['KAM'] = 'Валерия Солдатова'
            modified = True

    # Debtors allocation
    for d in data.get('debtors', []):
        raw_c = (d.get('raw_company') or d.get('company') or '').lower()
        if any(k in raw_c for k in ['дебрянск', 'бнм', 'бн-моторс', 'мб-брянск']):
            d['partner_id'] = 1177
            d['company'] = 'Дебрянск Авто'
            d['kam'] = 'Валерия Солдатова'
            modified = True
        elif ('юг-авто' in raw_c or 'юг авто' in raw_c) and not ('автоюг' in raw_c and not 'юг-авто' in raw_c):
            d['partner_id'] = 1290
            d['company'] = 'Юг-Авто'
            d['kam'] = 'Валерия Солдатова'
            modified = True
        elif any(k in raw_c for k in ['ааа', 'формула-н', 'формула н']):
            d['partner_id'] = 1291
            d['company'] = 'ААА Моторс'
            d['kam'] = 'Валерия Солдатова'
            modified = True

    if modified:
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, separators=(',', ':'))
        print(f"Successfully updated donor IDs in {filepath}")

if __name__ == '__main__':
    paths = [
        os.path.join(PROJECT_ROOT, 'partners_registry.json'),
        os.path.join(SITE_DIR, 'partners_registry.json'),
        os.path.join(DATA_DIR, 'partners_registry.json')
    ]
    for p in paths:
        apply_merges_to_file(p)

    data_paths = [
        os.path.join(PROJECT_ROOT, 'data.json'),
        os.path.join(SITE_DIR, 'data.json'),
        os.path.join(os.path.dirname(PROJECT_ROOT), 'data.json')
    ]
    for dp in data_paths:
        if os.path.exists(dp):
            apply_merges_to_data_json(dp)

import json
import os

def fix():
    paths = ['site/partners_registry.json', 'partners_registry.json']
    for path in paths:
        if not os.path.exists(path):
            continue
        with open(path, 'r', encoding='utf-8') as f:
            reg = json.load(f)

        oem_1153 = []
        for p in reg['partners']:
            if p['partner_id'] == 1153:
                oem_1153 = p.get('oem_data', [])

        for p in reg['partners']:
            if p['partner_id'] == 1098:
                p['canonical_name'] = 'АвтоГермес'
                p['kam'] = 'Андрей Кузнецов'
                p['bitrix_aliases'] = ['ONLINE АВТОГЕРМЕС-ЗАПАД (ООО "АВТОГЕРМЕС-ЗАПАД")', 'Приоритет_Автогермес', 'АвтоГермес']
                if oem_1153:
                    p['oem_data'] = oem_1153
            elif p['partner_id'] == 1153:
                p['canonical_name'] = 'Гермес (Мин. Воды)'
                p['kam'] = 'Андрей Кузнецов'
                p['bitrix_aliases'] = ['Гермес', 'Гермес Минводы', 'ООО "ГЕРМЕС"']
                p['oem_data'] = [
                    {'sheet': 'CHERY&TENET', 'brand': 'CHERY & TENET', 'city': 'Мин. Воды', 'name': 'Гермес', 'legal_entity': 'ООО Гермес'},
                    {'sheet': 'CHANGAN', 'brand': 'CHANGAN', 'city': 'Мин. Воды', 'name': 'Гермес', 'legal_entity': 'ООО Гермес'},
                    {'sheet': 'Geely&Belgee', 'brand': 'Geely & Belgee', 'city': 'Мин. Воды', 'name': 'Гермес', 'legal_entity': 'ООО Гермес'}
                ]

        with open(path, 'w', encoding='utf-8') as f:
            json.dump(reg, f, ensure_ascii=False, indent=2)
        print(f"Updated {path}")

if __name__ == '__main__':
    fix()

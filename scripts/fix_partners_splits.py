import json
import os

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE_DIR = os.path.join(PROJECT_ROOT, 'site')
DATA_DIR = os.path.join(PROJECT_ROOT, 'data')

def apply_partners_splits():
    paths = [
        os.path.join(PROJECT_ROOT, 'partners_registry.json'),
        os.path.join(SITE_DIR, 'partners_registry.json'),
        os.path.join(DATA_DIR, 'partners_registry.json')
    ]
    for pth in paths:
        if not os.path.exists(pth):
            continue
        with open(pth, 'r', encoding='utf-8') as f:
            reg = json.load(f)
        
        partners = reg.get('partners', [])
        
        # 1. Fix Alarm Motors (1002) and Autoclass (1103)
        p_alarm = next((p for p in partners if str(p.get('partner_id')) == '1002'), None)
        p_autoclass = next((p for p in partners if str(p.get('partner_id')) == '1103'), None)
        if p_autoclass:
            p_autoclass['kam'] = 'Алексей Чихарев'
        if p_alarm and p_autoclass:
            tula_oem = [o for o in p_alarm.get('oem_data', []) if '7106511456' in str(o) or 'ТУЛА' in str(o).upper()]
            p_alarm['oem_data'] = [o for o in p_alarm.get('oem_data', []) if '7106511456' not in str(o) and 'ТУЛА' not in str(o).upper()]
            for to in tula_oem:
                to['responsible'] = 'Алексей Чихарев'
                if not any(ex.get('inn') == to.get('inn') and ex.get('brand') == to.get('brand') for ex in p_autoclass.get('oem_data', [])):
                    p_autoclass['oem_data'].append(to)
                    
        # 2. Fix Motorland (1014) and Socrat (1280)
        p_motorland = next((p for p in partners if str(p.get('partner_id')) == '1014'), None)
        p_socrat = next((p for p in partners if str(p.get('partner_id')) == '1280'), None)
        if p_motorland:
            p_motorland['canonical_name'] = 'Моторленд (Воронеж)'
            p_motorland['kam'] = 'Валерия Солдатова'
            socrat_oem = [o for o in p_motorland.get('oem_data', []) if '3662259794' in str(o) or 'СОКРАТ' in str(o).upper() or 'СКОРАТ' in str(o).upper()]
            p_motorland['oem_data'] = [o for o in p_motorland.get('oem_data', []) if '3662259794' not in str(o) and 'СОКРАТ' not in str(o).upper() and 'СКОРАТ' not in str(o).upper()]
            
            if not p_socrat:
                p_socrat = {
                    'partner_id': 1280,
                    'canonical_name': 'Сократ (Моторленд)',
                    'kam': 'Светлана Дариенко',
                    'bitrix_aliases': ['Сократ', 'ООО Сократ', 'ООО "Сократ"', '3662259794', 'Скорат', 'ООО Скорат'],
                    'bi_aliases': ['Сократ'],
                    'pochta_aliases': [],
                    'oem_data': socrat_oem
                }
                partners.append(p_socrat)
            else:
                p_socrat['canonical_name'] = 'Сократ (Моторленд)'
                p_socrat['kam'] = 'Светлана Дариенко'
                p_socrat['oem_data'] = socrat_oem

        # 3. Fix Dynamica Vologda (1132)
        p_dyn_gk = next((p for p in partners if str(p.get('partner_id')) == '1031'), None)
        p_dyn_vol = next((p for p in partners if str(p.get('partner_id')) == '1132'), None)
        if p_dyn_vol:
            p_dyn_vol['canonical_name'] = 'Динамика Вологда'
            p_dyn_vol['kam'] = 'Светлана Дариенко'
            if '3525469447' not in p_dyn_vol.get('bitrix_aliases', []):
                p_dyn_vol.setdefault('bitrix_aliases', []).append('3525469447')
                p_dyn_vol.setdefault('bitrix_aliases', []).append('ООО Динамика Вологда')
        if p_dyn_gk and p_dyn_vol:
            vol_oem = [o for o in p_dyn_gk.get('oem_data', []) if '3525469447' in str(o) or 'ВОЛОГДА' in str(o).upper()]
            p_dyn_gk['oem_data'] = [o for o in p_dyn_gk.get('oem_data', []) if '3525469447' not in str(o)]
            for vo in vol_oem:
                if not any(ex.get('inn') == vo.get('inn') and ex.get('brand') == vo.get('brand') for ex in p_dyn_vol.get('oem_data', [])):
                    p_dyn_vol['oem_data'].append(vo)

        # 4. Fix Expert Auto (1035 Novosibirsk vs 1281 Samara)
        p_exp_nsk = next((p for p in partners if str(p.get('partner_id')) == '1035'), None)
        p_exp_sam = next((p for p in partners if str(p.get('partner_id')) == '1281'), None)
        if p_exp_nsk:
            p_exp_nsk['canonical_name'] = 'Эксперт Авто (Новосибирск)'
            p_exp_nsk['kam'] = 'Светлана Дариенко'
            sam_oem = [o for o in p_exp_nsk.get('oem_data', []) if '6314034107' in str(o) or '6312147970' in str(o) or 'САМАРА' in str(o).upper()]
            p_exp_nsk['oem_data'] = [o for o in p_exp_nsk.get('oem_data', []) if '6314034107' not in str(o) and '6312147970' not in str(o) and 'САМАРА' not in str(o).upper()]
            
            if not p_exp_sam:
                p_exp_sam = {
                    'partner_id': 1281,
                    'canonical_name': 'Эксперт Авто (Самара)',
                    'kam': 'Евгения Добролюбова',
                    'bitrix_aliases': ['Эксперт Авто Самара', 'ООО Эксперт Авто Самара', '6314034107', '6312147970', 'Эксперт Самара'],
                    'bi_aliases': ['Эксперт Авто Самара'],
                    'pochta_aliases': [],
                    'oem_data': sam_oem
                }
                partners.append(p_exp_sam)
            else:
                p_exp_sam['canonical_name'] = 'Эксперт Авто (Самара)'
                p_exp_sam['kam'] = 'Евгения Добролюбова'
                p_exp_sam['oem_data'] = sam_oem

        # 5. Fix Autodom Altufievo alias into Autodom GK (1007)
        p_autodom = next((p for p in partners if str(p.get('partner_id')) == '1007'), None)
        if p_autodom:
            p_autodom['kam'] = 'Андрей Кузнецов'
            alt_aliases = [
                'ГК Автодом / (ООО "ДЦ АЛТУФЬЕВО")',
                'ГК Автодом / (ООО "ДЦ Алтуфьево")',
                'ООО "ДЦ АЛТУФЬЕВО"',
                'ООО "ДЦ Алтуфьево"',
                'ДЦ АЛТУФЬЕВО',
                'ДЦ Алтуфьево',
                'Автодом JAECOO Алтуфьево ДЦА Москва, 85-й км МКАД, вл. 5, с. 1',
                'Автодом Алтуфьево'
            ]
            for aa in alt_aliases:
                if aa not in p_autodom.get('bitrix_aliases', []):
                    p_autodom.setdefault('bitrix_aliases', []).append(aa)

        with open(pth, 'w', encoding='utf-8') as f:
            json.dump(reg, f, ensure_ascii=False, indent=2)
        print(f"Successfully updated {pth}")

if __name__ == '__main__':
    apply_partners_splits()

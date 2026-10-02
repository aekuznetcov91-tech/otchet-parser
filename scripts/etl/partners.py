"""Partners stage of the dashboard ETL."""
from .config import PROJECT_ROOT
from .config import SITE_DIR
import json
import os

def load_master_partners_registry():
    registry_paths = [
        os.path.join(SITE_DIR, 'partners_registry.json'),
        os.path.join(PROJECT_ROOT, 'data', 'partners_registry.json'),
        os.path.join(PROJECT_ROOT, 'partners_registry.json')
    ]
    reg_data = None
    for rp in registry_paths:
        if os.path.exists(rp):
            try:
                with open(rp, 'r', encoding='utf-8') as f:
                    reg_data = json.load(f)
                break
            except Exception:
                pass

    if not reg_data or 'partners' not in reg_data:
        reg_data = {"partners": [], "unmatched_queue": [], "auto_matched_deals": [], "auto_matched_leads": []}

    partners = reg_data.get('partners', [])
    bitrix_map = {}
    bi_map = {}
    pochta_map = {}
    oem_map = {}

    for p in partners:
        pid = p['partner_id']
        cname = p['canonical_name']
        kam = p.get('kam', 'Не назначен')

        for a in p.get('bitrix_aliases', []):
            if a: bitrix_map[a.lower().strip()] = (pid, cname, kam)

        for a in p.get('bi_aliases', []):
            if a: bi_map[a.lower().strip()] = (pid, cname, kam)

        for a in p.get('pochta_aliases', []):
            if a: pochta_map[a.lower().strip()] = (pid, cname, kam)

        p_inn = str(p.get('inn', '')).strip()
        if p_inn:
            oem_map[p_inn.lower()] = (pid, cname, kam)
            if len(p_inn) == 9 or len(p_inn) == 11:
                oem_map['0' + p_inn.lower()] = (pid, cname, kam)

        for o in p.get('oem_data', []):
            inn = str(o.get('inn', '')).strip()
            fdc = str(o.get('fdc_code', '')).strip()
            back = str(o.get('back_name', '')).strip()
            legal = str(o.get('legal_entity', '')).strip()
            if inn:
                oem_map[inn.lower()] = (pid, cname, kam)
                if len(inn) == 9 or len(inn) == 11:
                    oem_map['0' + inn.lower()] = (pid, cname, kam)
            if fdc: oem_map[fdc.lower()] = (pid, cname, kam)
            if back: oem_map[back.lower()] = (pid, cname, kam)
            if legal: oem_map[legal.lower()] = (pid, cname, kam)

    return reg_data, bitrix_map, bi_map, pochta_map, oem_map


def apply_canonical_kam_mapping(pid, cname, partner_raw, kam, deal_city="", deal_inn="", month=""):
    """
    Enforces canonical partner IDs and KAM assignments for September 2026 and later.
    Reconciled with official records and Alexey Chikharev's manual portfolio check.
    """
    if not month or month < "2026-09":
        return pid, cname, kam

    p_text = f"{str(partner_raw or '').lower()} {str(cname or '').lower()}"
    city_low = str(deal_city or '').lower()
    inn_str = str(deal_inn or '').strip()

    # 1. ГК Автопрестиж (Чихарев) - strictly reconciled 50 deals in September (Лист2)
    if (any(k in p_text for k in ['автопрестиж', 'авто-ств', 'авто ств', 'эксперт авто оренбург', 'эксперт св оренбург', 'авто-смр', 'авто смр', 'авес-калуга', 'автопрестиж-полюс', 'авто-влг', 'авто-моторс лада', 'автомоторс лада']) or
        ('самарские автомобили' in p_text and 'север' in p_text) or
        inn_str in ('5638063829', '5638070618', '2635817810', '6313540673', '3443141624', '4029056455', '5038084557')):
        return 1076, 'ГК Автопрестиж', 'Алексей Чихарев'

    # 2. Online ООО МБ-Измайлово (Чихарев) - 8 deals
    if 'измайлово' in p_text or inn_str == '7719652251':
        return 1059, 'Online ООО МБ-Измайлово', 'Алексей Чихарев'

    # 3. БорисХоф (Чихарев) - 20 deals
    if any(k in p_text for k in ['борисхоф', 'борис хоф', 'квазар']) or inn_str in ('7736208620', '7736262947'):
        return 1098, 'БорисХоф', 'Алексей Чихарев'

    # 4. АвтоСпецЦентр / КАР АЦ (Чихарев) - 49 deals
    if any(k in p_text for k in ['автоспеццентр', 'кар ац']) or pid == 1130 or inn_str in ('5047120718', '7724795328'):
        return 1130, 'АвтоСпецЦентр', 'Алексей Чихарев'

    # 5. ТЦ Кунцево (Чихарев) - 36 deals
    if 'кунцево' in p_text or inn_str in ('7731281729', '7731557997'):
        return 1091, 'ТЦ Кунцево', 'Алексей Чихарев'

    # 6. Диалог Авто (Чихарев) - 50 deals
    if 'диалог' in p_text or inn_str in ('1650207558', '1649021206', '1644062657'):
        return 1082, 'Диалог Авто', 'Алексей Чихарев'

    # 7. Автоимпорт (Чихарев)
    if 'автоимпорт' in p_text or inn_str in ('6234151772', '6230095874'):
        return 1061, 'ONLINE Автоимпорт / ООО Автоимпорт Центр', 'Алексей Чихарев'

    # 8. Радар-авто (Чихарев)
    if 'радар' in p_text or inn_str == '7604107641':
        return 1253, 'Радар-авто', 'Алексей Чихарев'

    # 9. Пелетон (Чихарев)
    if 'пелетон' in p_text or inn_str == '1650369808':
        return 1248, 'Пелетон', 'Алексей Чихарев'

    # 10. Парус (Чихарев)
    if 'парус' in p_text or inn_str == '7604344840':
        return 1246, 'Парус', 'Алексей Чихарев'

    # 11. Major (Чихарев)
    if any(k in p_text for k in ['мэйджор', 'major']) or inn_str == '5024041031':
        return 1044, 'ГК Major/Мэйджор', 'Алексей Чихарев'

    # 12. ПНД (Чихарев)
    if 'пнд' in p_text or inn_str == '5047195230':
        return 1237, 'ПНД', 'Алексей Чихарев'

    # 13. КЦ Шереметьево (Чихарев)
    if 'шереметьево' in p_text or inn_str == '7743787723':
        return 1232, 'КЦ Шереметьево', 'Алексей Чихарев'

    # 14. СИМ (Чихарев)
    if any(k in p_text for k in ['сим-авто', 'сим авто']) or (p_text.strip().startswith('сим') or ' сим ' in p_text) or inn_str == '7721245050':
        return 1228, 'СИМ', 'Алексей Чихарев'

    # 15. ГК Автокласс (Чихарев)
    if any(k in p_text for k in ['автокласс', 'м-авто']) or inn_str == '7104044565':
        return 1102, 'ГК Автокласс', 'Алексей Чихарев'

    # 16. ООО Млада-Авто (Чихарев)
    if 'млада' in p_text or inn_str == '3328475254':
        return 1244, 'ООО "МЛАДА - АВТО', 'Алексей Чихарев'

    # 17. Важная персона (Чихарев)
    if 'важная персона' in p_text or inn_str == '6950207399':
        return 1258, 'Важная персона', 'Алексей Чихарев'

    # 18. Независимость (Чихарев)
    if 'независимость' in p_text or inn_str == '7736184288':
        return 1261, 'Независимость', 'Алексей Чихарев'

    # 19. Geely У Сервис (Чихарев)
    if any(k in p_text for k in ['у сервис', 'у-сервис']) or inn_str == '7725287754':
        return 1111, 'Geely У Сервис', 'Алексей Чихарев'

    # 20. Фаворит (Чихарев)
    if any(k in p_text for k in ['фаворит', 'favorit']) and not any(k in p_text for k in ['санкт-петербург', 'спб']):
        return 1227, 'Фаворит', 'Алексей Чихарев'

    # 21. АВИЛОН АГ (Чихарев)
    if 'авилон' in p_text or inn_str == '7705133757':
        return 1038, 'АВИЛОН АГ', 'Алексей Чихарев'

    # 22. Апельсин-Челны (Чихарев)
    if any(k in p_text for k in ['апельсин', 'автосеть рф']) or inn_str == '1657225323':
        return 1048, 'Апельсин-Челны', 'Алексей Чихарев'

    # 23. Авто Премиум Тверь (Чихарев)
    if any(k in p_text for k in ['авто премиум', 'премиум авто', 'союз-т']) and not any(k in p_text for k in ['санкт-петербург', 'спб']):
        return 1040, 'Авто Премиум Тверь', 'Алексей Чихарев'

    # 24. Автоград Калуга / Тюмень (Чихарев)
    if 'автоград' in p_text and not ('калининград' in p_text or 'калининград' in city_low):
        return 1121, 'АВТОЦЕНТР АВТОГРАД', 'Алексей Чихарев'

    # 25. ГК Глобус (Солдатова)
    if any(k in p_text for k in ['глобус', 'тамбов']) or inn_str == '6829074092':
        return 1013, 'ГК Глобус', 'Валерия Солдатова'

    # 26. ГК АГАТ (Кузнецов)
    if any(k in p_text for k in ['агат', 'аксион']) or inn_str in ('5258089355', '1831174660'):
        return 1049, 'ГК АГАТ', 'Андрей Кузнецов'

    # 27. Бизнес Кар (Кузнецов)
    if any(k in p_text for k in ['бизнес кар', 'бизнескар']):
        return 1084, 'Бизнес Кар', 'Андрей Кузнецов'

    # 28. Восток Моторс (Добролюбова)
    if any(k in p_text for k in ['восток моторс', 'восток-моторс']):
        return 1079, 'Восток Моторс', 'Евгения Добролюбова'

    # 29. Урал Моторс / Верра (Добролюбова)
    if any(k in p_text for k in ['урал моторс', 'урал-моторс', 'верра']):
        return 1265, 'ООО "УРАЛ-МОТОРС" ONLINE', 'Евгения Добролюбова'

    # 30. Самара Авто (Добролюбова)
    if any(k in p_text for k in ['самара авто', 'самара-авто']) and not ('север' in p_text):
        return 1077, 'ГК Самара-Авто', 'Евгения Добролюбова'

    return pid, cname, kam


"""Transactions stage of the dashboard ETL."""
from .config import DATA_DIR
from .config import PROJECT_ROOT
from .config import RAW_DATA_DIR
from .lead_geo import resolve_sberauto_lead_partner
from .normalization import clean_key
from .normalization import date_to_excel_serial
from .normalization import get_exact_val
from .normalization import normalize_brand
from .normalization import normalize_vin_str
from .normalization import parse_custom_date
from .partners import apply_canonical_kam_mapping
from .partners import load_master_partners_registry
from collections import defaultdict
import datetime
import json
import os
import re
import sys

def build_transactions(deals_data, leads_data, all_leads_data, directory_data):
    # 2. Build KAM dictionaries & Load Master Partner Registry
    reg_data, bitrix_map, bi_map, pochta_map, oem_map = load_master_partners_registry()
    print(f"[*] Master Partner Registry загружен: {len(reg_data.get('partners', []))} Master Partners.")

    september_bridge = {}
    september_bridge_vin = {}
    bridge_file = os.path.join(DATA_DIR, 'september_deals_bridge.json')
    if not os.path.exists(bridge_file):
        bridge_file = os.path.join(PROJECT_ROOT, 'data', 'september_deals_bridge.json')
    if os.path.exists(bridge_file):
        try:
            with open(bridge_file, 'r', encoding='utf-8') as f:
                b_data = json.load(f)
                september_bridge = b_data.get('deals_by_id', {})
                september_bridge_vin = b_data.get('deals_by_vin', {})
            print(f"[*] Мост сделок сентября загружен: {len(september_bridge)} по ID, {len(september_bridge_vin)} по VIN")
        except Exception as e:
            print(f"[!] Предупреждение при загрузке моста сделок сентября: {e}")

    try:
        if PROJECT_ROOT not in sys.path:
            sys.path.insert(0, PROJECT_ROOT)
        from scripts.oem_kam_resolver import OemKamResolver
        oem_excel_file = os.path.join(RAW_DATA_DIR, 'OEM СберАвто финал (15).xlsx')
        oem_resolver = OemKamResolver(oem_excel_file)
    except Exception as e:
        print(f"[!] Предупреждение при инициализации OemKamResolver: {e}")
        oem_resolver = None

    kam_dict_bitrix = {}
    kam_dict_bi = {}
    kam_dict_sber = {}

    if directory_data:
        for r in directory_data:
            bitrix = str(get_exact_val(r, 'БИТРИКС') or "").strip()
            bi = str(get_exact_val(r, 'BI') or "").strip()
            kam = str(get_exact_val(r, 'КАМ') or "").strip()
            pochta = str(get_exact_val(r, 'ПОЧТА') or "").strip()

            if bitrix: kam_dict_bitrix[bitrix.lower()] = kam
            if bi: kam_dict_bi[bi.lower()] = kam
            if pochta: kam_dict_sber[pochta.lower()] = kam
        print(f"[*] Справочник загружен: {len(directory_data)} записей КАМов.")

    # 3. Process Deals -> sys_db, sys_db_partners & debtors
    sys_db = []
    sys_db_partners = []
    debtors = []

    aux_keywords = ("КРЕДИТ", "КАСКО", "ОСАГО", "ГАП", "СТРАХОВ", "СЕРТИФИКАТ", "ДОП. ОБОРУДОВАНИЕ", "БРОНИРОВАНИЕ", "БРОНЬ", "БРОНИР")

    # Build lookup map for Lead ID and strictly transferred clients by month (deduplicated by client_id)
    leads_sum_id_by_client = {}
    transferred_clients_by_month = {}
    all_transferred_clients = set()

    for lr in all_leads_data:
        cid_l = str(get_exact_val(lr, 'CLIENTID', 'CLIENT_ID', 'IDКЛИЕНТА') or "").strip()
        sid_l = str(get_exact_val(lr, 'СУММАID', 'СУММА_ID', 'СУММА ID') or "").strip()
        if cid_l and sid_l and cid_l not in leads_sum_id_by_client:
            leads_sum_id_by_client[cid_l] = sid_l

        if cid_l:
            ev_l = str(get_exact_val(lr, 'СОБЫТИЕ', 'EVENTNAME', 'EVENT_NAME') or "").strip()
            ev_clean = clean_key(ev_l)
            is_trans = bool(sid_l) or ('ОТПРАВКАЛИДА' in ev_clean or 'ОТПРАВЛЕНДИЛЕРУ' in ev_clean or str(get_exact_val(lr, 'ОТПРАВЛЕНДИЛЕРУ', 'ПЕРЕДАНДИЛЕРУ', 'ПЕРЕДАН') or '').strip() == '1')

            if is_trans:
                d_val = str(get_exact_val(lr, 'ДАТАСОБЫТИЯ', 'ДАТАПЕРВОГОСОБЫТИЯ', 'ДАТА') or "").strip()
                p_date = parse_custom_date(d_val)
                m_str = p_date.strftime('%Y-%m') if p_date else '2026-08'
                if m_str not in transferred_clients_by_month:
                    transferred_clients_by_month[m_str] = set()
                transferred_clients_by_month[m_str].add(cid_l)
                all_transferred_clients.add(cid_l)

    for row in deals_data:
        stream = str(get_exact_val(row, 'СТРИМ') or "").strip()
        if stream and stream != 'Импортеры':
            continue

        tovar = str(get_exact_val(row, 'ТОВАР') or "").upper()
        if any(kw in tovar for kw in aux_keywords):
            continue

        b2c = str(get_exact_val(row, 'ТИПСДЕЛКИB2C') or "")
        try:
            price = float(str(get_exact_val(row, 'ФИНАЛЬНАЯЦЕНАB2C', 'ЦЕНА') or 0).replace(' ', '').replace('\xa0', '').replace(',', '.'))
        except ValueError:
            price = 0.0

        try:
            comm = float(str(get_exact_val(row, 'КОМИССИЯСДЕЛКИРУБ') or 0).replace(' ', '').replace('\xa0', '').replace(',', '.'))
        except ValueError:
            comm = 0.0

        raw_kv = get_exact_val(row, 'КВАВТОNEW', 'КВ. Авто NEW', 'КВ. АВТО NEW', 'КВАВТО')
        try:
            kv_auto_new = float(str(raw_kv).replace(' ', '').replace('\xa0', '').replace(',', '.')) if raw_kv else comm
        except ValueError:
            kv_auto_new = comm

        manager = str(get_exact_val(row, 'МЕНЕДЖЕРСДЕЛКИ') or "Не указан")
        stage = str(get_exact_val(row, 'СТАДИЯСДЕЛКИ') or "").upper()

        vin = str(get_exact_val(row, 'VIN', 'VINНОМЕР') or "").strip()
        if not vin:
            words = tovar.split()
            if words and len(words[-1]) > 10 and bool(re.search(r'[A-Z0-9]', words[-1])):
                vin = words[-1]
            else:
                vin = str(get_exact_val(row, 'ID') or "")

        client_id = str(get_exact_val(row, 'CLIENTID', 'CLIENT_ID') or "").strip()
        deal_id = str(get_exact_val(row, 'ID', 'IDСДЕЛКИ') or "").strip()
        lead_id = leads_sum_id_by_client.get(client_id) or ""

        raw_deal_date = get_exact_val(row, 'ПРЕДПОЛАГАЕМАЯДАТАЗАКРЫТИЯ')
        raw_prepay_date = get_exact_val(row, 'ДАТАВНЕСЕНИЯПРЕДОПЛАТЫРОЗНИЦА', 'ДАТАПОЛУЧЕНИЯАВАНСА') or raw_deal_date

        is_prepay = "ВНЕСЕНИЕ АВАНСА" in tovar
        is_sale = ("ЗАКРЫТО И РЕАЛИЗОВАН" in stage) and not is_prepay
        is_wait = (not is_sale) and not is_prepay

        d_deal_date = parse_custom_date(raw_deal_date)
        d_prepay_date = parse_custom_date(raw_prepay_date)

        deal_month_str = f"{d_deal_date.year}-{str(d_deal_date.month).zfill(2)}" if d_deal_date else ""
        prepay_month_str = f"{d_prepay_date.year}-{str(d_prepay_date.month).zfill(2)}" if d_prepay_date else ""

        deal_serial = date_to_excel_serial(d_deal_date)
        prepay_serial = date_to_excel_serial(d_prepay_date)

        b2c_upper = b2c.upper().replace(' ', '')
        chart_group = "Новые авто"
        if any(k in b2c_upper for k in ("МП1", "МП2", "МП3", "ВХОДЯЩАЯЗАЯВКА", "PARTNER")):
            chart_group = "Partners"

        final_brand = normalize_brand(tovar, month=deal_month_str or prepay_month_str)
        final_revenue = round(comm / 1.22, 2) if (is_sale and comm > 0) else 0.0

        # Model extraction
        model = tovar
        if final_brand and final_brand in model:
            model = model.replace(final_brand, '')
        if vin and vin in model:
            model = model.replace(vin, '')
        model = model.strip(' ,-')
        if not model:
            model = final_brand or ""

        sys_db.append({
            "SaleMonth": deal_month_str if is_sale else "",
            "PrepayMonth": prepay_month_str if is_prepay else "",
            "Brand": "ВНЕСЕНИЕ" if is_prepay else final_brand,
            "Model": model if is_sale else "",
            "B2C": b2c,
            "SaleQty": 1 if is_sale else 0,
            "Price": price if is_sale else 0,
            "Comm": comm if is_sale else 0,
            "KVAutoNew": kv_auto_new if is_sale else 0,
            "PrepayQty": 1 if is_prepay else 0,
            "WaitQty": 1 if is_wait else 0,
            "WaitMonth": deal_month_str if is_wait else "",
            "DealDate": deal_serial,
            "Manager": manager,
            "SeniorManager": str(get_exact_val(row, 'ОТВЕТСТВЕННЫЙЗАСДЕЛКУСТАРШИЙ', 'СТАРШИЙ') or "Без старшего"),
            "PrepayDate": prepay_serial,
            "Revenue": final_revenue,
            "VIN": vin,
            "ClientId": client_id,
            "LeadId": lead_id,
            "DealId": deal_id,
            "ChartGroup": chart_group
        })

        partner_raw = str(get_exact_val(row, 'КОМПАНИЯНАЗВАНИЕКОМПАНИИ', 'КОМПАНИЯ') or "").strip()
        deal_bridge = september_bridge.get(deal_id) or (september_bridge_vin.get(vin) if vin else None)
        deal_inn = str(deal_bridge.get('inn', '')).strip() if deal_bridge else ''
        if not partner_raw and deal_bridge:
            partner_raw = str(deal_bridge.get('company_name', '')).strip()

        if partner_raw or deal_inn:
            pid = None
            cname = partner_raw or (deal_bridge.get('company_name', '') if deal_bridge else '')
            kam_partner = "Не назначен"
            p_lower = partner_raw.lower() if partner_raw else ""

            # Exact INN match from OEM 15 / Master Partner Registry
            if deal_inn and deal_inn.lower() in oem_map:
                pid, cname, kam_partner = oem_map[deal_inn.lower()]
            elif p_lower in bitrix_map:
                pid, cname, kam_partner = bitrix_map[p_lower]
            elif p_lower in oem_map:
                pid, cname, kam_partner = oem_map[p_lower]
            elif kam_dict_bitrix.get(p_lower):
                kam_partner = kam_dict_bitrix.get(p_lower)

            c_lower = cname.lower() if cname else ""

            # Substring / Holding fallback if not matched or erroneously mapped:
            if 'рольф' in p_lower or 'рольф' in c_lower:
                pid, cname, kam_partner = (1084, 'РОЛЬФ', 'Андрей Кузнецов')
            elif 'автопрестиж' in p_lower or 'автопрестиж' in c_lower:
                pid, cname, kam_partner = (1076, 'ГК Автопрестиж', 'Алексей Чихарев')
            elif 'прагматика' in p_lower or 'прагматика' in c_lower:
                pid, cname, kam_partner = (1022, 'Прагматика', 'Светлана Дариенко')
            elif 'сигма' in p_lower or 'сигма' in c_lower:
                pid, cname, kam_partner = (1011, 'ГК Сигма', 'Светлана Дариенко')
            elif any(k in p_lower for k in ['премиум авто', 'авто премиум', 'автопремиум', 'союз-т']) or any(k in c_lower for k in ['премиум авто', 'авто премиум', 'автопремиум', 'союз-т']):
                deal_city = str(get_exact_val(row, 'ГОРОДB2C', 'ГОРОД.B2C', 'ГОРОД') or (deal_bridge.get('city', '') if deal_bridge else "")).strip().lower()
                if any(spb_k in deal_city for spb_k in ['санкт-петербург', 'спб']) or any(spb_k in p_lower for spb_k in ['санкт-петербург', 'спб']) or (final_brand and 'geely' in str(final_brand).lower()):
                    pid, cname, kam_partner = (632032, 'Премиум Авто ONLINE', 'Светлана Дариенко')
                else:
                    pid, cname, kam_partner = (1040, 'Авто Премиум Тверь', 'Алексей Чихарев')
            elif 'авторитет' in p_lower or 'авторитет' in c_lower or deal_inn in ('2902039507', '9102001105') or 'автодель' in p_lower:
                deal_city = str(get_exact_val(row, 'ГОРОДB2C', 'ГОРОД.B2C', 'ГОРОД') or (deal_bridge.get('city', '') if deal_bridge else "")).strip().lower()
                if deal_inn == '9102001105' or any(k in deal_city for k in ['симферополь', 'крым']) or 'авторитет-м' in p_lower or 'автодель' in p_lower:
                    pid, cname, kam_partner = (1286, 'Авторитет (Симферополь)', 'Валерия Солдатова')
                else:
                    pid, cname, kam_partner = (1138, 'Авторитет (Архангельск)', 'Светлана Дариенко')
            elif 'боравто' in p_lower or 'боравто' in c_lower:
                pid, cname, kam_partner = (1094, 'ГК Боравто', 'Валерия Солдатова')
            elif ('диалог' in p_lower and 'авто' in p_lower) or ('диалог' in c_lower and 'авто' in c_lower):
                pid, cname, kam_partner = (1082, 'ГК Диалог Авто', 'Алексей Чихарев')
            elif ('дав-авто' in p_lower or 'дав авто' in p_lower) or ('дав-авто' in c_lower or 'дав авто' in c_lower):
                pid, cname, kam_partner = (1184, 'Дав-Авто', 'Андрей Кузнецов')
            elif not pid or pid in (1116, 1045, 1198, 1127, 1193, 1205):
                if any(k in p_lower for k in ['агат', 'автопрофиль', 'аркада', 'платинум']) or any(k in c_lower for k in ['агат', 'автопрофиль', 'аркада', 'платинум']):
                    pid, cname, kam_partner = (1049, 'ГК АГАТ', 'Андрей Кузнецов')
                elif 'кунцево' in p_lower or 'кунцево' in c_lower:
                    pid, cname, kam_partner = (1091, 'ТЦ Кунцево', 'Алексей Чихарев')
                elif 'прагматика' in p_lower or 'прагматика' in c_lower:
                    pid, cname, kam_partner = (1022, 'Прагматика', 'Светлана Дариенко')
                elif ('вагнер' in p_lower or 'вагнер' in c_lower) and 'авторитэйл' not in p_lower:
                    pid, cname, kam_partner = (1015, 'Вагнер Авто (СПб)', 'Светлана Дариенко')
                elif 'авторитэйл м' in p_lower or 'авторитэйл' in p_lower or 'авторитэйл' in c_lower:
                    deal_city = str(get_exact_val(row, 'ГОРОДB2C', 'ГОРОД.B2C', 'ГОРОД') or (deal_bridge.get('city', '') if deal_bridge else "")).strip().lower()
                    if any(spb_k in deal_city or spb_k in p_lower for spb_k in ['санкт-петербург', 'спб']):
                        pid, cname, kam_partner = (1285, 'Вагнер Авто / Авторитэйл', 'Светлана Дариенко')
                    else:
                        pid, cname, kam_partner = (1285, 'ГК Авторитэйл М', 'Валерия Солдатова')
                elif 'р-моторс' in p_lower or 'р моторс' in p_lower or pid == 1025 or 'р-моторс' in c_lower:
                    pid, cname, kam_partner = (1025, 'Р-Моторс ЛАДА', 'Светлана Дариенко')
                elif pid == 1016 or 'online ооо "леон"' in p_lower or 'леон авто (йошкар-ола)' in c_lower:
                    pid, cname, kam_partner = (1016, 'Леон Авто (Йошкар-Ола)', 'Евгения Добролюбова')

            # Explicit KAM reallocations (strictly for August 2026 and earlier):
            if deal_month_str <= "2026-08" or not deal_month_str:
                if 'рольф' in p_lower or 'рольф' in c_lower:
                    kam_partner = "Андрей Кузнецов"
                elif ('кунцево' in p_lower or 'кунцево' in c_lower) and 'рольф' not in p_lower:
                    kam_partner = "Алексей Чихарев"
                elif 'борис' in p_lower or 'борис' in c_lower:
                    kam_partner = "Алексей Чихарев"
                elif 'тд армада-авто' in p_lower or 'тд армада-авто' in c_lower or 'армада-авто' in p_lower or 'армада-авто' in c_lower or 'армада' in p_lower:
                    kam_partner = "Евгения Добролюбова"
                elif 'оренбург' in p_lower or 'оренбург' in c_lower:
                    kam_partner = "Алексей Чихарев"
                elif 'автолидер' in p_lower or 'автолидер' in c_lower:
                    kam_partner = "Евгения Добролюбова"
                elif any(k in p_lower for k in ['агат', 'автопрофиль', 'аркада', 'квант', 'альтаир', 'приоритет моторс', 'максима авто', 'платинум', 'планета авто', 'гольфстрим', 'lucky motors', 'эксперт самара', 'эксперт авто']) or any(k in c_lower for k in ['агат', 'автопрофиль', 'аркада', 'квант', 'альтаир', 'приоритет моторс', 'максима авто', 'платинум', 'планета авто', 'гольфстрим', 'lucky motors', 'эксперт самара', 'эксперт авто']):
                    kam_partner = "Андрей Кузнецов"
                elif any(k in p_lower for k in ['лидер сервис', 'лидер online', 'автопилот', 'максимум', 'вагнер авто']) or any(k in c_lower for k in ['лидер сервис', 'лидер online', 'автопилот', 'максимум', 'вагнер авто']) or ('фаворит' in p_lower and ('санкт-петербург' in p_lower or 'спб' in p_lower)):
                    kam_partner = "Светлана Дариенко"
                elif 'автоград' in p_lower or 'автоград' in c_lower:
                    deal_city = str(get_exact_val(row, 'ГОРОДB2C', 'ГОРОД.B2C', 'ГОРОД') or (deal_bridge.get('city', '') if deal_bridge else "")).strip().lower()
                    if 'калининград' in deal_city:
                        kam_partner = "Светлана Дариенко"
                    else:
                        kam_partner = "Алексей Чихарев"
                elif any(k in p_lower for k in ['премиум авто', 'авто премиум', 'автопремиум', 'союз-т']) or any(k in c_lower for k in ['премиум авто', 'авто премиум', 'автопремиум', 'союз-т']):
                    deal_city = str(get_exact_val(row, 'ГОРОДB2C', 'ГОРОД.B2C', 'ГОРОД') or (deal_bridge.get('city', '') if deal_bridge else "")).strip().lower()
                    if any(spb_k in deal_city for spb_k in ['санкт-петербург', 'спб']) or any(spb_k in p_lower for spb_k in ['санкт-петербург', 'спб']) or (final_brand and 'geely' in str(final_brand).lower()):
                        kam_partner = "Светлана Дариенко"
                    else:
                        kam_partner = "Алексей Чихарев"
                elif any(k in p_lower for k in ['эксперт св', 'автоимпорт центр']) or any(k in c_lower for k in ['эксперт св', 'автоимпорт центр']):
                    kam_partner = "Алексей Чихарев"
                elif 'спектр' in p_lower and 'апельсин' in p_lower:
                    kam_partner = "Алексей Чихарев"
                elif 'авторитэйл' in p_lower or 'авторитэйл' in c_lower:
                    deal_city = str(get_exact_val(row, 'ГОРОДB2C', 'ГОРОД.B2C', 'ГОРОД') or (deal_bridge.get('city', '') if deal_bridge else "")).strip().lower()
                    if any(spb_k in deal_city or spb_k in p_lower for spb_k in ['санкт-петербург', 'спб']):
                        kam_partner = "Светлана Дариенко"
                    else:
                        kam_partner = "Валерия Солдатова"
                elif 'олимп' in p_lower or 'темп авто кубань' in p_lower or 'олимп' in c_lower:
                    kam_partner = "Андрей Кузнецов"
                elif any(k in p_lower for k in ['техно-темп', 'трансфор', 'темп авто к', 'темп авто дон']) or any(k in c_lower for k in ['техно-темп', 'трансфор', 'темп авто к', 'темп авто дон']):
                    kam_partner = "Валерия Солдатова"

            k_low = (kam_partner or "").lower()
            if 'кузнецов' in k_low:
                kam_partner = "Андрей Кузнецов"
            elif 'чихарев' in k_low or 'чихарёв' in k_low:
                kam_partner = "Алексей Чихарев"
            elif 'дариенко' in k_low:
                kam_partner = "Светлана Дариенко"
            elif 'солдатова' in k_low:
                kam_partner = "Валерия Солдатова"
            elif 'добролюбова' in k_low:
                kam_partner = "Евгения Добролюбова"

            # Explicit overrides that supersede all fallbacks:
            if pid == 1025 or 'р-моторс' in p_lower or 'р моторс' in p_lower:
                pid, cname, kam_partner = (1025, 'Р-Моторс ЛАДА', 'Светлана Дариенко')
            elif pid == 1016 or 'online ооо "леон"' in p_lower:
                pid, cname, kam_partner = (1016, 'Леон Авто (Йошкар-Ола)', 'Евгения Добролюбова')
            elif pid == 1285 and any(spb_k in p_lower or spb_k in c_lower for spb_k in ['санкт-петербург', 'спб']):
                pid, cname, kam_partner = (1285, 'Вагнер Авто / Авторитэйл', 'Светлана Дариенко')
            elif 'нижегородец' in p_lower:
                pid, cname, kam_partner = (1071, 'Нижегородец', 'Евгения Добролюбова')
            elif (pid in [1051, 1060, 632013, 632020] or 'форвард' in p_lower) and not any(ex in p_lower for ex in ['диамант', 'диаманд']):
                pid, cname, kam_partner = (1060, 'Форвард Ижевск/Сызрань', 'Евгения Добролюбова')
            elif pid == 1184 or 'дав-авто' in p_lower or 'дав авто' in p_lower:
                pid, cname, kam_partner = (1184, 'Дав-Авто', 'Евгения Добролюбова')
            elif ('сатурн-р' in p_lower or 'сатурн р' in p_lower) and not ('липецк' in p_lower or 'липецк' in c_lower):
                pid, cname, kam_partner = (1110, 'Сатурн-Р', 'Евгения Добролюбова')
            elif 'автопремьер м' in p_lower or 'авпремьер м' in p_lower or 'автопремьер-м' in p_lower:
                pid, cname, kam_partner = ('P_OEM_ac181614', 'Уфа Haval / Tenet Автопремьер М', 'Евгения Добролюбова')
            elif 'асмото' in p_lower:
                pid, cname, kam_partner = ('P_OEM_ae51d9c1', 'ООО "Асмото"', 'Евгения Добролюбова')
            elif 'юникор' in p_lower:
                pid, cname, kam_partner = (1086, 'ЮНИКОР Дзержинск НН', 'Евгения Добролюбова')
            elif 'автолидер' in p_lower:
                pid, cname, kam_partner = (1266, 'Автолидер ГАК', 'Евгения Добролюбова')
            elif 'асавто' in p_lower:
                pid, cname, kam_partner = ('P_OEM_943c0828', 'АсАвто на Алмаатинской', 'Евгения Добролюбова')
            elif 'армада-авто' in p_lower or 'армада авто' in p_lower or 'армада' in p_lower:
                pid, cname, kam_partner = (1128, 'ООО "ТД АРМАДА-АВТО', 'Евгения Добролюбова')
            elif 'гедон' in p_lower:
                pid, cname, kam_partner = (1288, 'Гедон-Юг', 'Валерия Солдатова')
            elif 'максимум' in p_lower or 'lucky motors' in p_lower:
                pid, cname, kam_partner = (1163, 'Автохолдинг Максимум', 'Светлана Дариенко')
            elif any(k in p_lower for k in ['воронеж-авто-сити', 'воронеж авто сити', 'авто сити', 'авто-сити']) and not any(ex in p_lower for ex in ['мэйджор', 'major']):
                pid, cname, kam_partner = (1114, 'ООО "ВОРОНЕЖ-АВТО-СИТИ', 'Валерия Солдатова')

            # Portfolio handover rule: in August 2026 and earlier, deals of Dobrolyubova's portfolio are attributed to Kuznetsov (excluding Leon Yoshkar-Ola and explicitly assigned partners)
            dobro_full_pids = {1016, 1071, 1060, 1051, 632013, 1184, 1110, 1086, 1128, 1266, 632031, 'P_OEM_6e979ac2', 'P_OEM_b19664be', 'P_OEM_ac181614', 'P_OEM_ae51d9c1', 'P_OEM_943c0828'}
            dobro_full_kws = ['нижегородец', 'дав-авто', 'дав авто', 'сатурн-р', 'сатурн р', 'юникор', 'армада', 'автолидер', 'асавто', 'асмото', 'автопремьер м', 'автопремьер-м', 'форвард']
            is_full_dobro = (pid in dobro_full_pids) or any(k in p_lower for k in dobro_full_kws) or any(k in (cname or '').lower() for k in dobro_full_kws)

            if kam_partner == "Евгения Добролюбова" and (deal_month_str <= "2026-08" or not deal_month_str) and not is_full_dobro:
                kam_partner = "Андрей Кузнецов"

            kam_prepay = kam_partner
            if kam_prepay == "Евгения Добролюбова" and (prepay_month_str <= "2026-08" or not prepay_month_str) and not is_full_dobro:
                kam_prepay = "Андрей Кузнецов"

            # Priority OEM (15) routing and user-verified overrides for September 2026 and later:
            if oem_resolver:
                deal_city = str(get_exact_val(row, 'ГОРОДB2C', 'ГОРОД.B2C', 'ГОРОД') or (deal_bridge.get('city', '') if deal_bridge else "")).strip()
                if deal_month_str and deal_month_str >= "2026-09":
                    # Нижегородец -> Добролюбова
                    if 'нижегородец' in p_lower:
                        pid, cname, kam_partner = (1071, 'Нижегородец', 'Евгения Добролюбова')
                    # Форвард-Авто -> Добролюбова
                    elif (pid in [1051, 1060, 632013, 632020] or 'форвард' in p_lower) and not any(ex in p_lower for ex in ['диамант', 'диаманд']):
                        pid, cname, kam_partner = (1060, 'Форвард Ижевск/Сызрань', 'Евгения Добролюбова')
                    # Дав-Авто -> Добролюбова
                    elif pid == 1184 or 'дав-авто' in p_lower or 'дав авто' in p_lower:
                        pid, cname, kam_partner = (1184, 'Дав-Авто', 'Евгения Добролюбова')
                    # Сатурн-Р -> Добролюбова (Пермь)
                    elif ('сатурн-р' in p_lower or 'сатурн р' in p_lower) and not ('липецк' in p_lower or 'липецк' in deal_city.lower()):
                        pid, cname, kam_partner = (1110, 'Сатурн-Р', 'Евгения Добролюбова')
                    # Tenet Уфа Автопремьер М / Haval -> Добролюбова
                    elif 'автопремьер м' in p_lower or 'авпремьер м' in p_lower or 'автопремьер-м' in p_lower:
                        pid, cname, kam_partner = ('P_OEM_ac181614', 'Уфа Haval / Tenet Автопремьер М', 'Евгения Добролюбова')
                    # Асмото -> Добролюбова
                    elif 'асмото' in p_lower:
                        pid, cname, kam_partner = ('P_OEM_ae51d9c1', 'ООО "Асмото"', 'Евгения Добролюбова')
                    # Юникор Дзержинск -> Добролюбова
                    elif 'юникор' in p_lower:
                        pid, cname, kam_partner = (1086, 'ЮНИКОР Дзержинск НН', 'Евгения Добролюбова')
                    # Автолидер -> Добролюбова
                    elif 'автолидер' in p_lower:
                        pid, cname, kam_partner = (1266, 'Автолидер ГАК', 'Евгения Добролюбова')
                    # АсАвто на Алмаатинской -> Добролюбова
                    elif 'асавто' in p_lower:
                        pid, cname, kam_partner = ('P_OEM_943c0828', 'АсАвто на Алмаатинской', 'Евгения Добролюбова')
                    # Армада -> Добролюбова
                    elif 'армада-авто' in p_lower or 'армада авто' in p_lower or 'армада' in p_lower:
                        pid, cname, kam_partner = (1128, 'ООО "ТД АРМАДА-АВТО', 'Евгения Добролюбова')
                    # Гедон Юг -> Солдатова
                    elif 'гедон' in p_lower:
                        pid, cname, kam_partner = (1288, 'Гедон-Юг', 'Валерия Солдатова')
                    # Автохолдинг Максимум -> Дариенко
                    elif 'максимум' in p_lower or 'lucky motors' in p_lower:
                        pid, cname, kam_partner = (1163, 'Автохолдинг Максимум', 'Светлана Дариенко')
                    # Авто Сити -> Воронеж-Авто-Сити (Солдатова)
                    elif any(k in p_lower for k in ['воронеж-авто-сити', 'воронеж авто сити', 'авто сити', 'авто-сити']) and not any(ex in p_lower for ex in ['мэйджор', 'major']):
                        pid, cname, kam_partner = (1114, 'ООО "ВОРОНЕЖ-АВТО-СИТИ', 'Валерия Солдатова')
                    # Диалог авто (в т.ч. КЗН, Альметьевск, Челны) -> Чихарев
                    elif 'диалог' in p_lower or deal_inn in ('1650207558', '1649021206', '1644062657'):
                        cname = 'Диалог Авто'
                        kam_partner = 'Алексей Чихарев'
                    # Ринг Авто / ONLINE Ринг -> Солдатова
                    elif 'ринг' in p_lower:
                        cname = 'Ринг Авто'
                        kam_partner = 'Валерия Солдатова'
                    # Альфа-Сервис -> Добролюбова
                    elif any(k in p_lower for k in ['альфа-сервис', 'альфа сервис']):
                        cname = 'Альфа-Сервис'
                        kam_partner = 'Евгения Добролюбова'
                    # Tenet центр Ника авто -> Добролюбова
                    elif any(k in p_lower for k in ['ника', 'велес авто']) or deal_inn == '5638074027':
                        cname = 'Tenet Центр Ника Авто'
                        kam_partner = 'Евгения Добролюбова'
                    # Автомир Симферополь -> Солдатова
                    elif 'автомир' in p_lower and any(k in p_lower or k in deal_city.lower() for k in ['симферополь', 'крым']) or deal_inn == '9102289123':
                        cname = 'Автомир (Симферополь)'
                        kam_partner = 'Валерия Солдатова'
                    # ГК Автомир (все остальные ДЦ, в т.ч. ООО "АМКапитал", Автомир-Трейд, Легат) -> Кузнецов
                    elif any(k in p_lower for k in ['автомир', 'амкапитал', 'ам капитал', 'легат']):
                        pid, cname, kam_partner = (1043, 'ГК Автомир', 'Андрей Кузнецов')
                    # Олимп (Темп Авто Кубань) -> Добролюбова
                    elif 'олимп' in p_lower or 'темп авто кубань' in p_lower or deal_inn == '2311093925':
                        cname = 'Олимп (Кубань)'
                        kam_partner = 'Евгения Добролюбова'
                    # Дебрянск Авто (БНМ) -> Солдатова
                    elif any(k in p_lower for k in ['дебрянск', 'бн', 'бнм', 'бн-моторс']) or deal_inn in ('3250521481', '3257002460', '3257014272'):
                        pid = 1177
                        cname = 'Дебрянск Авто'
                        kam_partner = 'Валерия Солдатова'
                    # Юг-Авто (Краснодар) -> Солдатова
                    elif ('юг-авто' in p_lower or 'юг авто' in p_lower or deal_inn in ('2310079830', '2311120713')) and not ('автоюг' in p_lower and not 'юг-авто' in p_lower):
                        pid = 1290
                        cname = 'Юг-Авто'
                        kam_partner = 'Валерия Солдатова'
                    # ААА Моторс (Ростов-на-Дону) -> Солдатова
                    elif any(k in p_lower for k in ['ааа', 'aaa', 'формула-н', 'формула н']) or deal_inn == '6168043686':
                        pid = 1291
                        cname = 'ААА Моторс'
                        kam_partner = 'Валерия Солдатова'
                    # Автобан / Приоритет Автобан -> Добролюбова
                    elif any(k in p_lower for k in ['автобан', 'автобан-восток']) or deal_inn == '6679163711':
                        cname = 'Приоритет_Автобан'
                        kam_partner = 'Евгения Добролюбова'
                    # Чанган центр / Башавтоком -> Добролюбова
                    elif any(k in p_lower for k in ['чанган центр', 'changan центр', 'башавтоком']):
                        cname = 'Башавтоком / Чанган Центр'
                        kam_partner = 'Евгения Добролюбова'
                    # Чери автофорум / Автофорум -> Добролюбова
                    elif 'автофорум' in p_lower or deal_inn in ('7718240330', '0278184650'):
                        cname = 'Чери Автофорум'
                        kam_partner = 'Евгения Добролюбова'
                    # 5-6. Fresh -> Fresh Auto (Кузнецов)
                    elif any(k in p_lower for k in ['фреш', 'fresh']):
                        cname = 'Fresh Auto'
                        kam_partner = 'Андрей Кузнецов'
                    # 14. Спектр: Апельсин vs Агат
                    elif 'спектр' in p_lower:
                        if deal_inn == '1657225323' or any(k in p_lower for k in ['апельсин', 'автосеть']):
                            cname = 'Апельсин (Автосеть РФ)'
                            kam_partner = 'Алексей Чихарев'
                        elif deal_inn == '5258089355' or 'агат' in p_lower:
                            cname = 'ГК АГАТ'
                            kam_partner = 'Андрей Кузнецов'
                    # 13. Эксперт авто Оренбург -> ГК Автопрестиж (Чихарев)
                    elif 'оренбург' in p_lower and 'эксперт' in p_lower:
                        pid = 1076
                        cname = 'ГК Автопрестиж'
                        kam_partner = 'Алексей Чихарев'
                    # 12. Авто-моторс Сургут -> Чихарев
                    elif any(k in p_lower for k in ['сургут', 'авто-моторс', 'автомоторс']):
                        cname = 'ФДЦ АВТО-МОТОРС Сургут'
                        kam_partner = 'Алексей Чихарев'
                    # 1. Арконт -> Добролюбова
                    elif 'арконт' in p_lower or deal_inn == '3443113810':
                        pid = 1112
                        cname = 'ГК Арконт Холдинг'
                        kam_partner = 'Евгения Добролюбова'
                    # 2. Сильвер-авто -> Добролюбова
                    elif 'сильвер' in p_lower:
                        cname = 'ГК Сильвер'
                        kam_partner = 'Евгения Добролюбова'
                    # 3. ТВС Моторс -> Добролюбова
                    elif 'твс' in p_lower or deal_inn == '5610215334':
                        cname = 'ТВС Моторс'
                        kam_partner = 'Евгения Добролюбова'
                    # 4. Нижегородец -> Добролюбова
                    elif 'нижегородец' in p_lower or deal_inn == '5257164835':
                        cname = 'Нижегородец'
                        kam_partner = 'Евгения Добролюбова'
                    # 7. Авторитет: Симферополь -> Солдатова, Архангельск -> Дариенко (только Лада)
                    elif 'авторитет' in p_lower or deal_inn in ('2902039507', '9102001105') or 'автодель' in p_lower:
                        if deal_inn == '9102001105' or any(k in deal_city.lower() for k in ['симферополь', 'крым']) or 'авторитет-м' in p_lower or 'автодель' in p_lower:
                            pid = 1286
                            cname = 'Авторитет (Симферополь)'
                            kam_partner = 'Валерия Солдатова'
                        else:
                            pid = 1138
                            cname = 'Авторитет (Архангельск)'
                            kam_partner = 'Светлана Дариенко'
                    # Автопремиум: Тверь -> Чихарев, СПб -> Дариенко
                    elif any(k in p_lower for k in ['премиум авто', 'авто премиум', 'автопремиум', 'союз-т']):
                        if any(spb_k in deal_city.lower() for spb_k in ['санкт-петербург', 'спб']) or (final_brand and 'geely' in str(final_brand).lower()):
                            pid = 632032
                            cname = 'Премиум Авто ONLINE'
                            kam_partner = 'Светлана Дариенко'
                        else:
                            pid = 1040
                            cname = 'Авто Премиум Тверь'
                            kam_partner = 'Алексей Чихарев'
                    # Сигма -> Дариенко
                    elif 'сигма' in p_lower:
                        pid = 1011
                        cname = 'ГК Сигма'
                        kam_partner = 'Светлана Дариенко'
                    # 8. Сатурн 2 / Сатурн-Р
                    elif 'сатурн' in p_lower:
                        if deal_inn == '4826051045' or 'липецк' in p_lower or 'липецк' in deal_city.lower():
                            cname = 'ГК Сатурн Липецк'
                            kam_partner = 'Валерия Солдатова'
                        else:
                            cname = 'ГК Сатурн 2' if '2' in p_lower else 'Сатурн-Р'
                            kam_partner = 'Евгения Добролюбова'
                    # 9. Автосеть АМК РФ -> Добролюбова
                    elif (any(k in p_lower for k in ['амк', 'автосеть амк', 'автосеть рф амк']) or deal_inn == '6320070000') and not any(ex in p_lower for ex in ['амкапитал', 'ам капитал', 'апельсин', 'автомир']):
                        pid = 1053
                        cname = 'ФДЦ Автосеть АМК РФ'
                        kam_partner = 'Евгения Добролюбова'
                    # 10. Планета Авто -> все города, кроме Махачкалы, Таганрога и Москвы относятся к Добролюбовой
                    elif 'планета авто' in p_lower or 'планета-авто' in p_lower or 'чери центр планета авто восток' in p_lower or deal_inn == '7453298640':
                        pid = 1058
                        cname = 'ЧЕРИ ЦЕНТР ПЛАНЕТА АВТО ВОСТОК'
                        d_city_low = (deal_city or '').lower()
                        if 'махачкала' in d_city_low or 'таганрог' in d_city_low:
                            kam_partner = 'Валерия Солдатова'
                        elif 'москва' in d_city_low or 'мск' in d_city_low:
                            kam_partner = 'Алексей Чихарев'
                        else:
                            kam_partner = 'Евгения Добролюбова'
                    # 11. Эксперт Авто: Самара -> Добролюбова, Новосибирск -> в сентябре Дариенко, с октября Добролюбова
                    elif 'эксперт' in p_lower:
                        if any(k in p_lower or k in deal_city.lower() for k in ['новосибирск', 'нск']):
                            pid = 1035
                            cname = 'Эксперт Авто (Новосибирск)'
                            if deal_month_str == '2026-09':
                                kam_partner = 'Светлана Дариенко'
                            elif deal_month_str and deal_month_str >= '2026-10':
                                kam_partner = 'Евгения Добролюбова'
                            else:
                                kam_partner = 'Светлана Дариенко'
                        elif any(k in p_lower or k in deal_city.lower() for k in ['оренбург']) or deal_inn in ('5638063829', '5638070618'):
                            pid = 1076
                            cname = 'ГК Автопрестиж'
                            kam_partner = 'Алексей Чихарев'
                        else:
                            cname = 'Эксперт Авто (Самара)'
                            kam_partner = 'Евгения Добролюбова'
                    # Р-Моторс -> Дариенко (во всех городах)
                    elif 'р-моторс' in p_lower or 'р моторс' in p_lower or pid == 1025:
                        pid = 1025
                        cname = 'Р-Моторс ЛАДА'
                        kam_partner = 'Светлана Дариенко'
                    # Авторитэйл М: СПб -> Дариенко, иначе -> Солдатова
                    elif 'авторитэйл' in p_lower:
                        pid = 1285
                        if any(spb_k in p_lower or spb_k in deal_city.lower() for spb_k in ['санкт-петербург', 'спб']):
                            cname = 'Вагнер Авто / Авторитэйл'
                            kam_partner = 'Светлана Дариенко'
                        else:
                            cname = 'ГК Авторитэйл М'
                            kam_partner = 'Валерия Солдатова'
                    # Леон Авто: Йошкар-Ола -> Добролюбова, иначе -> Солдатова
                    elif 'леон' in p_lower or pid in (1016, 1023):
                        if pid == 1016 or 'online ооо "леон"' in p_lower or 'йошкар' in deal_city.lower():
                            pid = 1016
                            cname = 'Леон Авто (Йошкар-Ола)'
                            kam_partner = 'Евгения Добролюбова'
                        else:
                            pid = 1023
                            cname = 'Леон Авто'
                            kam_partner = 'Валерия Солдатова'
                    else:
                        resolved_deal_kam = oem_resolver.resolve(
                            inn=deal_inn,
                            partner_name=partner_raw or cname,
                            brand=final_brand or '',
                            city=deal_city,
                            fallback_kam=kam_partner
                        )
                        if resolved_deal_kam and resolved_deal_kam != "Не назначен":
                            kam_partner = resolved_deal_kam

                if prepay_month_str and prepay_month_str >= "2026-09":
                    # Нижегородец -> Добролюбова
                    if 'нижегородец' in p_lower:
                        kam_prepay = 'Евгения Добролюбова'
                    # Форвард-Авто -> Добролюбова
                    elif (pid in [1051, 1060, 632013, 632020] or 'форвард' in p_lower) and not any(ex in p_lower for ex in ['диамант', 'диаманд']):
                        kam_prepay = 'Евгения Добролюбова'
                    # Дав-Авто -> Добролюбова
                    elif pid == 1184 or 'дав-авто' in p_lower or 'дав авто' in p_lower:
                        kam_prepay = 'Евгения Добролюбова'
                    # Сатурн-Р -> Добролюбова (Пермь)
                    elif ('сатурн-р' in p_lower or 'сатурн р' in p_lower) and not ('липецк' in p_lower or 'липецк' in deal_city.lower()):
                        kam_prepay = 'Евгения Добролюбова'
                    # Tenet Уфа Автопремьер М / Haval -> Добролюбова
                    elif 'автопремьер м' in p_lower or 'авпремьер м' in p_lower or 'автопремьер-м' in p_lower:
                        kam_prepay = 'Евгения Добролюбова'
                    # Асмото -> Добролюбова
                    elif 'асмото' in p_lower:
                        kam_prepay = 'Евгения Добролюбова'
                    # Юникор Дзержинск -> Добролюбова
                    elif 'юникор' in p_lower:
                        kam_prepay = 'Евгения Добролюбова'
                    # Автолидер -> Добролюбова
                    elif 'автолидер' in p_lower:
                        kam_prepay = 'Евгения Добролюбова'
                    # АсАвто на Алмаатинской -> Добролюбова
                    elif 'асавто' in p_lower:
                        kam_prepay = 'Евгения Добролюбова'
                    # Армада -> Добролюбова
                    elif 'армада-авто' in p_lower or 'армада авто' in p_lower or 'армада' in p_lower:
                        kam_prepay = 'Евгения Добролюбова'
                    # Гедон Юг -> Солдатова
                    elif 'гедон' in p_lower:
                        kam_prepay = 'Валерия Солдатова'
                    # Автохолдинг Максимум -> Дариенко
                    elif 'максимум' in p_lower or 'lucky motors' in p_lower:
                        kam_prepay = 'Светлана Дариенко'
                    # Авто Сити -> Воронеж-Авто-Сити (Солдатова)
                    elif any(k in p_lower for k in ['воронеж-авто-сити', 'воронеж авто сити', 'авто сити', 'авто-сити']) and not any(ex in p_lower for ex in ['мэйджор', 'major']):
                        kam_prepay = 'Валерия Солдатова'
                    # Диалог авто -> Чихарев
                    elif 'диалог' in p_lower or deal_inn in ('1650207558', '1649021206', '1644062657'):
                        kam_prepay = 'Алексей Чихарев'
                    # Ринг Авто / ONLINE Ринг -> Солдатова
                    elif 'ринг' in p_lower:
                        kam_prepay = 'Валерия Солдатова'
                    # Альфа-Сервис -> Добролюбова
                    elif any(k in p_lower for k in ['альфа-сервис', 'альфа сервис']):
                        kam_prepay = 'Евгения Добролюбова'
                    # Ника авто -> Добролюбова
                    elif any(k in p_lower for k in ['ника', 'велес авто']) or deal_inn == '5638074027':
                        kam_prepay = 'Евгения Добролюбова'
                    # Автомир Симферополь -> Солдатова
                    elif 'автомир' in p_lower and any(k in p_lower or k in deal_city.lower() for k in ['симферополь', 'крым']) or deal_inn == '9102289123':
                        kam_prepay = 'Валерия Солдатова'
                    # ГК Автомир (все остальные ДЦ, в т.ч. ООО "АМКапитал", Автомир-Трейд, Легат) -> Кузнецов
                    elif any(k in p_lower for k in ['автомир', 'амкапитал', 'ам капитал', 'легат']):
                        kam_prepay = 'Андрей Кузнецов'
                    # Олимп -> Добролюбова
                    elif 'олимп' in p_lower or 'темп авто кубань' in p_lower or deal_inn == '2311093925':
                        kam_prepay = 'Евгения Добролюбова'
                    # Дебрянск Авто -> Солдатова
                    elif any(k in p_lower for k in ['дебрянск', 'бн', 'бнм', 'бн-моторс']) or deal_inn in ('3250521481', '3257002460', '3257014272'):
                        kam_prepay = 'Валерия Солдатова'
                    # Юг-Авто -> Солдатова
                    elif ('юг-авто' in p_lower or 'юг авто' in p_lower or deal_inn in ('2310079830', '2311120713')) and not ('автоюг' in p_lower and not 'юг-авто' in p_lower):
                        kam_prepay = 'Валерия Солдатова'
                    # ААА Моторс -> Солдатова
                    elif any(k in p_lower for k in ['ааа', 'aaa', 'формула-н', 'формула н']) or deal_inn == '6168043686':
                        kam_prepay = 'Валерия Солдатова'
                    # Автобан -> Добролюбова
                    elif any(k in p_lower for k in ['автобан', 'автобан-восток']) or deal_inn == '6679163711':
                        kam_prepay = 'Евгения Добролюбова'
                    # Чанган центр / Башавтоком -> Добролюбова
                    elif any(k in p_lower for k in ['чанган центр', 'changan центр', 'башавтоком']):
                        kam_prepay = 'Евгения Добролюбова'
                    # Автофорум -> Добролюбова
                    elif 'автофорум' in p_lower or deal_inn in ('7718240330', '0278184650'):
                        kam_prepay = 'Евгения Добролюбова'
                    elif any(k in p_lower for k in ['фреш', 'fresh']):
                        kam_prepay = 'Андрей Кузнецов'
                    elif 'спектр' in p_lower:
                        if deal_inn == '1657225323' or any(k in p_lower for k in ['апельсин', 'автосеть']):
                            kam_prepay = 'Алексей Чихарев'
                        elif deal_inn == '5258089355' or 'агат' in p_lower:
                            kam_prepay = 'Андрей Кузнецов'
                    elif 'оренбург' in p_lower and 'эксперт' in p_lower:
                        kam_prepay = 'Алексей Чихарев'
                    elif any(k in p_lower for k in ['сургут', 'авто-моторс', 'автомоторс']):
                        kam_prepay = 'Алексей Чихарев'
                    elif 'планета авто' in p_lower or 'планета-авто' in p_lower or 'чери центр планета авто восток' in p_lower:
                        d_city_low = (deal_city or '').lower()
                        if 'махачкала' in d_city_low or 'таганрог' in d_city_low:
                            kam_prepay = 'Валерия Солдатова'
                        elif 'москва' in d_city_low or 'мск' in d_city_low:
                            kam_prepay = 'Алексей Чихарев'
                        else:
                            kam_prepay = 'Евгения Добролюбова'
                    elif (any(k in p_lower for k in ['амк', 'автосеть амк', 'автосеть рф амк']) or deal_inn == '6320070000') and not any(ex in p_lower for ex in ['амкапитал', 'ам капитал', 'апельсин', 'автомир']):
                        kam_prepay = 'Евгения Добролюбова'
                    elif any(k in p_lower for k in ['арконт', 'сильвер', 'твс', 'нижегородец']) and not any(ex in p_lower for ex in ['амкапитал', 'ам капитал']):
                        kam_prepay = 'Евгения Добролюбова'
                    elif 'авторитет' in p_lower:
                        kam_prepay = 'Светлана Дариенко'
                    elif 'сатурн' in p_lower:
                        if deal_inn == '4826051045' or 'липецк' in p_lower or 'липецк' in deal_city.lower():
                            kam_prepay = 'Валерия Солдатова'
                        else:
                            kam_prepay = 'Евгения Добролюбова'
                    elif 'эксперт' in p_lower:
                        if any(k in p_lower or k in deal_city.lower() for k in ['новосибирск', 'нск']):
                            if prepay_month_str == '2026-09':
                                kam_prepay = 'Светлана Дариенко'
                            elif prepay_month_str and prepay_month_str >= '2026-10':
                                kam_prepay = 'Евгения Добролюбова'
                            else:
                                kam_prepay = 'Светлана Дариенко'
                        elif any(k in p_lower or k in deal_city.lower() for k in ['оренбург']) or deal_inn in ('5638063829', '5638070618'):
                            kam_prepay = 'Алексей Чихарев'
                        else:
                            kam_prepay = 'Евгения Добролюбова'
                    # Р-Моторс -> Дариенко (во всех городах)
                    elif 'р-моторс' in p_lower or 'р моторс' in p_lower or pid == 1025:
                        kam_prepay = 'Светлана Дариенко'
                    # Авторитэйл М: СПб -> Дариенко, иначе -> Солдатова
                    elif 'авторитэйл' in p_lower:
                        if any(spb_k in p_lower or spb_k in deal_city.lower() for spb_k in ['санкт-петербург', 'спб']):
                            kam_prepay = 'Светлана Дариенко'
                        else:
                            kam_prepay = 'Валерия Солдатова'
                    # Леон Авто: Йошкар-Ола -> Добролюбова, иначе -> Солдатова
                    elif 'леон' in p_lower or pid in (1016, 1023):
                        if pid == 1016 or 'online ооо "леон"' in p_lower or 'йошкар' in deal_city.lower():
                            kam_prepay = 'Евгения Добролюбова'
                        else:
                            kam_prepay = 'Валерия Солдатова'
                    else:
                        resolved_prepay_kam = oem_resolver.resolve(
                            inn=deal_inn,
                            partner_name=partner_raw or cname,
                            brand=final_brand or '',
                            city=deal_city,
                            fallback_kam=kam_prepay
                        )
                        if resolved_prepay_kam and resolved_prepay_kam != "Не назначен":
                            kam_prepay = resolved_prepay_kam

            if is_sale:
                pid, cname, kam_partner = apply_canonical_kam_mapping(pid, cname, partner_raw, kam_partner, deal_city, deal_inn, deal_month_str)
                is_mp = any(k in b2c.upper() for k in ['МП1', 'МП2', 'МП3', 'MP1', 'MP2', 'MP3'])
                raw_prepay_val = get_exact_val(row, 'ДАТАВНЕСЕНИЯПРЕДОПЛАТЫРОЗНИЦА', 'ДАТАПОЛУЧЕНИЯАВАНСА')
                has_prepay_date = bool(raw_prepay_val and str(raw_prepay_val).strip())
                # Strictly match by client_id against transferred leads
                is_trans_deal = bool((client_id and (client_id in transferred_clients_by_month.get(deal_month_str, set()) or client_id in all_transferred_clients)) or ('ПЕРЕДАЧА' in b2c.upper()))
                sys_db_partners.append({
                    "Month": deal_month_str,
                    "PartnerId": pid,
                    "Partner": cname,
                    "RawPartner": partner_raw,
                    "KAM": kam_partner,
                    "Type": "Сделка",
                    "Qty": 1,
                    "B2C": b2c,
                    "Brand": final_brand,
                    "Model": model,
                    "VIN": vin,
                    "Comm": kv_auto_new,
                    "Price": price,
                    "Date": deal_serial,
                    "ClientId": client_id,
                    "LeadId": lead_id,
                    "DealId": deal_id,
                    "Manager": manager,
                    "IsLeadSaleNoPrepay": 1 if is_trans_deal else 0,
                    "IsMpSale": 1 if is_mp else 0,
                    "HasPrepay": 1 if has_prepay_date else 0
                })
            elif is_prepay:
                pid, cname, kam_prepay = apply_canonical_kam_mapping(pid, cname, partner_raw, kam_prepay, deal_city, deal_inn, prepay_month_str)
                sys_db_partners.append({
                    "Month": prepay_month_str,
                    "PartnerId": pid,
                    "Partner": cname,
                    "RawPartner": partner_raw,
                    "KAM": kam_prepay,
                    "Type": "Предоплата",
                    "Qty": 1,
                    "Date": prepay_serial
                })
            elif is_wait:
                pid, cname, kam_partner = apply_canonical_kam_mapping(pid, cname, partner_raw, kam_partner, deal_city, deal_inn, deal_month_str)
                sys_db_partners.append({
                    "Month": deal_month_str,
                    "PartnerId": pid,
                    "Partner": cname,
                    "RawPartner": partner_raw,
                    "KAM": kam_partner,
                    "Type": "Без сделки",
                    "Qty": 1,
                    "Date": deal_serial
                })
                if not is_prepay:
                    debtor_calc_date = d_prepay_date or d_deal_date
                    debtor_age = (datetime.date.today() - debtor_calc_date).days if debtor_calc_date else 0
                    debtors.append({
                        "company": cname,
                        "raw_company": partner_raw,
                        "partner_id": pid,
                        "client_id": client_id,
                        "deal_id": deal_id,
                        "prepay_date": d_prepay_date.strftime("%d.%m.%Y") if d_prepay_date else (d_deal_date.strftime("%d.%m.%Y") if d_deal_date else ""),
                        "prepay_serial": prepay_serial or deal_serial,
                        "aging_days": max(0, debtor_age),
                        "brand": final_brand,
                        "model": model,
                        "vin": vin,
                        "kam": kam_partner,
                        "manager": manager,
                        "stage": stage,
                        "price": price,
                        "b2c": b2c
                    })

    # Deduplicate & exclude from debtors if the car (VIN) was already closed and sold in a main deal or replaced
    sold_vins_norm = {normalize_vin_str(r['VIN']) for r in sys_db if r.get('SaleQty') == 1 and r.get('VIN') and len(normalize_vin_str(r['VIN'])) >= 8}
    sales_by_client = defaultdict(list)
    sales_by_deal = defaultdict(list)
    for r in sys_db:
        if r.get('SaleQty') == 1:
            cid_s = str(r.get('ClientId') or '').strip()
            if cid_s:
                sales_by_client[cid_s].append(r)
            did_s = str(r.get('DealId') or '').strip()
            if did_s:
                sales_by_deal[did_s].append(r)

    filtered_debtors = []
    seen_debtor_keys = set()
    for d in debtors:
        d_vin = str(d.get('vin') or '').strip()
        d_vin_norm = normalize_vin_str(d_vin)
        cid = str(d.get('client_id') or '').strip()
        did = str(d.get('deal_id') or '').strip()
        company = str(d.get('company') or '').strip()
        brand = str(d.get('brand') or '').strip().upper()

        # 1. Exact or homoglyph/typo normalized VIN match against closed sales
        if d_vin_norm and len(d_vin_norm) >= 8 and d_vin_norm in sold_vins_norm:
            continue

        # 2. Check if this exact DealId is already closed and realized as a sale
        if did and did in sales_by_deal:
            continue

        # 3. Check if client already completed purchase at this dealer/brand (replacement VIN or duplicate deal)
        if cid and cid in sales_by_client:
            client_sales = sales_by_client[cid]
            matched_sale = None
            for s in client_sales:
                s_brand = str(s.get('Brand') or '').strip().upper()
                if s_brand == brand or not brand or brand == 'NONE' or len(client_sales) == 1:
                    matched_sale = s
                    break
            if matched_sale:
                continue

        # 4. Deduplicate exact duplicate records in debtors (same normalized VIN and same client)
        dedup_key = (d_vin_norm, cid, company) if (d_vin_norm and len(d_vin_norm) >= 8) else (did, company)
        if dedup_key in seen_debtor_keys:
            continue
        seen_debtor_keys.add(dedup_key)

        filtered_debtors.append(d)

    debtors = filtered_debtors

    # 4. Process Leads
    # Build a lookup of clients with prepayments to tag leads with HasPrepay
    clients_with_prepay = set()
    for r in sys_db:
        cid = str(r.get('ClientId') or '').strip()
        if cid and (r.get('PrepayQty', 0) > 0 or r.get('PrepayDate')):
            clients_with_prepay.add(cid)
    for r in deals_data:
        cid = str(get_exact_val(r, 'IDКЛИЕНТА', 'CLIENTID') or '').strip()
        raw_prepay = get_exact_val(r, 'ДАТАВНЕСЕНИЯПРЕДОПЛАТЫРОЗНИЦА', 'ДАТАПОЛУЧЕНИЯАВАНСА')
        if cid and raw_prepay and str(raw_prepay).strip():
            clients_with_prepay.add(cid)
    print(f"[*] Сформирован реестр клиентов с предоплатами: {len(clients_with_prepay)} уникальных ClientId")

    if leads_data:
        seen_partner_leads = set()
        for row in leads_data:
            sid = str(get_exact_val(row, 'СУММАID', 'СУММА_ID', 'СУММА ID') or "").strip()
            if not sid:
                continue

            client_id = str(get_exact_val(row, 'CLIENTID', 'IDКЛИЕНТА') or "").strip()
            if not client_id:
                continue

            partner_raw = str(get_exact_val(row, 'BI', 'ПАРТНЕР') or "").strip()
            if not partner_raw:
                continue

            pid = None
            cname = partner_raw
            kam = "Не назначен"
            p_lower = partner_raw.lower()

            if "сберавто" in p_lower or "сбер авто" in p_lower:
                contact_name = str(get_exact_val(row, 'НАЗВАНИЕКОНТАКТА', 'КОНТАКТ') or "").strip()
                sber_res = resolve_sberauto_lead_partner(contact_name, partner_raw)
                if sber_res:
                    pid, cname, kam = sber_res
                elif contact_name:
                    c_low = contact_name.lower()
                    if c_low in pochta_map:
                        pid, cname, kam = pochta_map[c_low]
                    elif c_low in kam_dict_sber:
                        cname = contact_name
                        kam = kam_dict_sber.get(c_low, "")
                    else:
                        cname = contact_name
                elif p_lower in bi_map:
                    pid, cname, kam = bi_map[p_lower]
            elif p_lower in bi_map:
                pid, cname, kam = bi_map[p_lower]
            elif p_lower in oem_map:
                pid, cname, kam = oem_map[p_lower]
            elif p_lower in kam_dict_bi:
                kam = kam_dict_bi.get(p_lower, "")

            # Substring / Holding fallback if not matched or erroneously mapped:
            if 'рольф' in p_lower:
                pid, cname, kam = (1084, 'РОЛЬФ', 'Андрей Кузнецов')
            elif 'автопрестиж' in p_lower:
                pid, cname, kam = (1076, 'ГК Автопрестиж', 'Алексей Чихарев')
            elif 'прагматика' in p_lower:
                pid, cname, kam = (1022, 'Прагматика', 'Светлана Дариенко')
            elif 'сигма' in p_lower:
                pid, cname, kam = (1011, 'ГК Сигма', 'Светлана Дариенко')
            elif any(k in p_lower for k in ['премиум авто', 'авто премиум', 'автопремиум', 'союз-т']):
                lead_city = str(get_exact_val(row, 'ГОРОДB2C', 'ГОРОД.B2C', 'ГОРОД') or "").strip().lower()
                if any(spb_k in p_lower for spb_k in ['санкт-петербург', 'спб']) or any(spb_k in lead_city for spb_k in ['санкт-петербург', 'спб']):
                    pid, cname, kam = (632032, 'Премиум Авто ONLINE', 'Светлана Дариенко')
                else:
                    pid, cname, kam = (1040, 'Авто Премиум Тверь', 'Алексей Чихарев')
            elif 'авторитет' in p_lower or 'автодель' in p_lower:
                lead_city = str(get_exact_val(row, 'ГОРОДB2C', 'ГОРОД.B2C', 'ГОРОД') or "").strip().lower()
                if any(k in p_lower or k in lead_city for k in ['симферополь', 'крым']) or 'авторитет-м' in p_lower or 'автодель' in p_lower:
                    pid, cname, kam = (1286, 'Авторитет (Симферополь)', 'Валерия Солдатова')
                else:
                    pid, cname, kam = (1138, 'Авторитет (Архангельск)', 'Светлана Дариенко')
            elif 'боравто' in p_lower:
                pid, cname, kam = (1094, 'ГК Боравто', 'Валерия Солдатова')
            elif 'диалог' in p_lower and 'авто' in p_lower:
                pid, cname, kam = (1082, 'ГК Диалог Авто', 'Алексей Чихарев')
            elif 'дав-авто' in p_lower or 'дав авто' in p_lower:
                pid, cname, kam = (1184, 'Дав-Авто', 'Андрей Кузнецов')
            elif not pid or pid in (1116, 1045, 1198, 1127, 1193, 1205):
                if any(k in p_lower for k in ['агат', 'автопрофиль', 'аркада', 'платинум']):
                    pid, cname, kam = (1049, 'ГК АГАТ', 'Андрей Кузнецов')
                elif 'кунцево' in p_lower:
                    pid, cname, kam = (1091, 'ТЦ Кунцево', 'Алексей Чихарев')
                elif 'прагматика' in p_lower:
                    pid, cname, kam = (1022, 'Прагматика', 'Светлана Дариенко')
                elif 'вагнер' in p_lower and 'авторитэйл' not in p_lower:
                    pid, cname, kam = (1015, 'Вагнер Авто (СПб)', 'Светлана Дариенко')
                elif 'авторитэйл м' in p_lower or 'авторитэйл' in p_lower:
                    pid, cname, kam = (1285, 'ГК Авторитэйл М', 'Валерия Солдатова')

            d_lead_date = parse_custom_date(get_exact_val(row, 'ДАТА', 'ДАТАСОБЫТИЯ'))
            lead_month_str = f"{d_lead_date.year}-{str(d_lead_date.month).zfill(2)}" if d_lead_date else ""
            lead_serial = date_to_excel_serial(d_lead_date)
            lead_city = str(get_exact_val(row, 'ГОРОДB2C', 'ГОРОД.B2C', 'ГОРОД') or "").strip()

            # Explicit KAM reallocations:
            if lead_month_str <= "2026-08" or not lead_month_str:
                if 'рольф' in p_lower:
                    kam = "Андрей Кузнецов"
                elif 'кунцево' in p_lower and 'рольф' not in p_lower:
                    kam = "Алексей Чихарев"
                elif 'борис' in p_lower or 'борис' in cname.lower():
                    kam = "Алексей Чихарев"
                elif 'тд армада-авто' in p_lower:
                    kam = "Андрей Кузнецов"
                elif 'армада-авто' in p_lower:
                    kam = "Алексей Чихарев"
                elif 'оренбург' in p_lower:
                    kam = "Алексей Чихарев"
                elif any(k in p_lower for k in ['агат', 'автопрофиль', 'аркада', 'квант', 'альтаир', 'приоритет моторс', 'максима авто', 'платинум', 'планета авто', 'гольфстрим', 'lucky motors', 'эксперт самара', 'эксперт авто', 'автолидер']):
                    kam = "Андрей Кузнецов"
                elif any(k in p_lower for k in ['лидер сервис', 'лидер online', 'автопилот', 'максимум', 'вагнер авто']) or ('фаворит' in p_lower and ('санкт-петербург' in p_lower or 'спб' in p_lower)):
                    kam = "Светлана Дариенко"
                elif 'автоград' in p_lower:
                    lead_city = str(get_exact_val(row, 'ГОРОДB2C', 'ГОРОД.B2C', 'ГОРОД') or "").strip().lower()
                    if 'калининград' in lead_city:
                        kam = "Светлана Дариенко"
                    else:
                        kam = "Алексей Чихарев"
                elif 'премиум авто' in p_lower:
                    if any(spb_k in p_lower for spb_k in ['санкт-петербург', 'спб']):
                        kam = "Светлана Дариенко"
                    else:
                        kam = "Алексей Чихарев"
                elif any(k in p_lower for k in ['эксперт св', 'автоимпорт центр']):
                    kam = "Алексей Чихарев"
                elif 'авторитэйл м' in p_lower:
                    lead_city = str(get_exact_val(row, 'ГОРОДB2C', 'ГОРОД.B2C', 'ГОРОД') or "").strip().lower()
                    if any(spb_k in lead_city for spb_k in ['санкт-петербург', 'спб']):
                        kam = "Светлана Дариенко"
                    else:
                        kam = "Валерия Солдатова"
                elif 'олимп' in p_lower or 'темп авто кубань' in p_lower:
                    kam = "Андрей Кузнецов"
                elif any(k in p_lower for k in ['техно-темп', 'трансфор', 'авторитэйл', 'темп авто к', 'темп авто дон']):
                    kam = "Валерия Солдатова"

                dobro_full_pids = {1016, 1071, 1060, 1051, 632013, 1184, 1110, 1086, 1128, 1266, 632031, 'P_OEM_6e979ac2', 'P_OEM_b19664be', 'P_OEM_ac181614', 'P_OEM_ae51d9c1', 'P_OEM_943c0828'}
                dobro_full_kws = ['нижегородец', 'дав-авто', 'дав авто', 'сатурн-р', 'сатурн р', 'юникор', 'армада', 'автолидер', 'асавто', 'асмото', 'автопремьер м', 'автопремьер-м', 'форвард']
                is_full_dobro = (pid in dobro_full_pids) or any(k in p_lower for k in dobro_full_kws) or any(k in (cname or '').lower() for k in dobro_full_kws)
                if kam == "Евгения Добролюбова" and not is_full_dobro:
                    kam = "Андрей Кузнецов"
            elif oem_resolver:
                lead_city = str(get_exact_val(row, 'ГОРОДB2C', 'ГОРОД.B2C', 'ГОРОД') or "").strip()
                # User explicit overrides for September leads
                if 'нижегородец' in p_lower:
                    pid, cname, kam = (1071, 'Нижегородец', 'Евгения Добролюбова')
                elif (pid in [1051, 1060, 632013, 632020] or 'форвард' in p_lower) and not any(ex in p_lower for ex in ['диамант', 'диаманд']):
                    pid, cname, kam = (1060, 'Форвард Ижевск/Сызрань', 'Евгения Добролюбова')
                elif pid == 1184 or 'дав-авто' in p_lower or 'дав авто' in p_lower:
                    pid, cname, kam = (1184, 'Дав-Авто', 'Евгения Добролюбова')
                elif ('сатурн-р' in p_lower or 'сатурн р' in p_lower) and not ('липецк' in p_lower or 'липецк' in lead_city.lower()):
                    pid, cname, kam = (1110, 'Сатурн-Р', 'Евгения Добролюбова')
                elif 'автопремьер м' in p_lower or 'авпремьер м' in p_lower or 'автопремьер-м' in p_lower:
                    pid, cname, kam = ('P_OEM_ac181614', 'Уфа Haval / Tenet Автопремьер М', 'Евгения Добролюбова')
                elif 'асмото' in p_lower:
                    pid, cname, kam = ('P_OEM_ae51d9c1', 'ООО "Асмото"', 'Евгения Добролюбова')
                elif 'юникор' in p_lower:
                    pid, cname, kam = (1086, 'ЮНИКОР Дзержинск НН', 'Евгения Добролюбова')
                elif 'автолидер' in p_lower:
                    pid, cname, kam = (1266, 'Автолидер ГАК', 'Евгения Добролюбова')
                elif 'асавто' in p_lower:
                    pid, cname, kam = ('P_OEM_943c0828', 'АсАвто на Алмаатинской', 'Евгения Добролюбова')
                elif 'армада-авто' in p_lower or 'армада авто' in p_lower or 'армада' in p_lower:
                    pid, cname, kam = (1128, 'ООО "ТД АРМАДА-АВТО', 'Евгения Добролюбова')
                elif 'гедон' in p_lower:
                    pid, cname, kam = (1288, 'Гедон-Юг', 'Валерия Солдатова')
                elif 'максимум' in p_lower or 'lucky motors' in p_lower:
                    pid, cname, kam = (1163, 'Автохолдинг Максимум', 'Светлана Дариенко')
                elif any(k in p_lower for k in ['воронеж-авто-сити', 'воронеж авто сити', 'авто сити', 'авто-сити']) and not any(ex in p_lower for ex in ['мэйджор', 'major']):
                    pid, cname, kam = (1114, 'ООО "ВОРОНЕЖ-АВТО-СИТИ', 'Валерия Солдатова')
                elif 'диалог' in p_lower:
                    cname = 'Диалог Авто'
                    kam = 'Алексей Чихарев'
                elif 'ринг' in p_lower:
                    cname = 'Ринг Авто'
                    kam = 'Валерия Солдатова'
                elif any(k in p_lower for k in ['альфа-сервис', 'альфа сервис']):
                    cname = 'Альфа-Сервис'
                    kam = 'Евгения Добролюбова'
                elif any(k in p_lower for k in ['ника', 'велес авто']):
                    cname = 'Tenet Центр Ника Авто'
                    kam = 'Евгения Добролюбова'
                elif 'автомир' in p_lower and any(k in p_lower or k in lead_city.lower() for k in ['симферополь', 'крым']):
                    cname = 'Автомир (Симферополь)'
                    kam = 'Валерия Солдатова'
                elif any(k in p_lower for k in ['автомир', 'амкапитал', 'ам капитал', 'легат']):
                    pid, cname, kam = (1043, 'ГК Автомир', 'Андрей Кузнецов')
                elif 'олимп' in p_lower or 'темп авто кубань' in p_lower:
                    cname = 'Олимп (Кубань)'
                    kam = 'Евгения Добролюбова'
                elif any(k in p_lower for k in ['дебрянск', 'бн', 'бнм', 'бн-моторс']):
                    pid = 1177
                    cname = 'Дебрянск Авто'
                    kam = 'Валерия Солдатова'
                elif ('юг-авто' in p_lower or 'юг авто' in p_lower) and not ('автоюг' in p_lower and not 'юг-авто' in p_lower):
                    pid = 1290
                    cname = 'Юг-Авто'
                    kam = 'Валерия Солдатова'
                elif any(k in p_lower for k in ['ааа', 'aaa', 'формула-н', 'формула н']):
                    pid = 1291
                    cname = 'ААА Моторс'
                    kam = 'Валерия Солдатова'
                elif any(k in p_lower for k in ['автобан', 'автобан-восток']):
                    cname = 'Приоритет_Автобан'
                    kam = 'Евгения Добролюбова'
                elif any(k in p_lower for k in ['чанган центр', 'changan центр', 'башавтоком']):
                    cname = 'Башавтоком / Чанган Центр'
                    kam = 'Евгения Добролюбова'
                elif 'автофорум' in p_lower:
                    cname = 'Чери Автофорум'
                    kam = 'Евгения Добролюбова'
                elif 'планета авто' in p_lower or 'планета-авто' in p_lower or 'чери центр планета авто восток' in p_lower:
                    pid = 1058
                    cname = 'ЧЕРИ ЦЕНТР ПЛАНЕТА АВТО ВОСТОК'
                    l_city_low = (lead_city or '').lower()
                    if 'махачкала' in l_city_low or 'таганрог' in l_city_low:
                        kam = 'Валерия Солдатова'
                    elif 'москва' in l_city_low or 'мск' in l_city_low:
                        kam = 'Алексей Чихарев'
                    else:
                        kam = 'Евгения Добролюбова'
                elif 'арконт' in p_lower:
                    pid = 1112
                    cname = 'ГК Арконт Холдинг'
                    kam = 'Евгения Добролюбова'
                elif (any(k in p_lower for k in ['амк', 'автосеть амк', 'автосеть рф амк'])) and not any(ex in p_lower for ex in ['амкапитал', 'ам капитал', 'апельсин', 'автомир']):
                    pid = 1053
                    cname = 'ФДЦ Автосеть АМК РФ'
                    kam = 'Евгения Добролюбова'
                elif any(k in p_lower for k in ['сильвер', 'твс', 'нижегородец']) and not any(ex in p_lower for ex in ['амкапитал', 'ам капитал']):
                    kam = 'Евгения Добролюбова'
                elif 'эксперт' in p_lower:
                    if any(k in p_lower or k in lead_city.lower() for k in ['новосибирск', 'нск']):
                        pid = 1035
                        cname = 'Эксперт Авто (Новосибирск)'
                        if lead_month_str == '2026-09':
                            kam = 'Светлана Дариенко'
                        elif lead_month_str and lead_month_str >= '2026-10':
                            kam = 'Евгения Добролюбова'
                        else:
                            kam = 'Светлана Дариенко'
                    elif any(k in p_lower or k in lead_city.lower() for k in ['оренбург']):
                        pid = 1076
                        cname = 'ГК Автопрестиж'
                        kam = 'Алексей Чихарев'
                    else:
                        cname = 'Эксперт Авто (Самара)'
                        kam = 'Евгения Добролюбова'
                elif any(k in p_lower for k in ['мэйджор', 'major']):
                    pid, cname, kam = (1044, 'ГК Major/Мэйджор', 'Алексей Чихарев')
                elif 'dss' in p_lower:
                    cname = 'DSS Group'
                    kam = 'Алексей Чихарев'
                elif 'вилледж' in p_lower or 'аутлет' in p_lower:
                    cname = 'Аутлет Авто Вилледж'
                    kam = 'Светлана Дариенко'
                elif 'автомобилия' in p_lower:
                    cname = 'Автомобилия (Ярославль)'
                    kam = 'Алексей Чихарев'
                elif 'rekord' in p_lower or 'рекорд' in p_lower:
                    cname = 'Автосалон REKORD'
                    kam = 'Алексей Чихарев'
                elif 'альянс' in p_lower:
                    cname = 'Альянс Select'
                    kam = 'Алексей Чихарев'
                elif 'тверь' in p_lower or 'макон' in p_lower:
                    cname = 'Единый центр Trade-In Тверь' if 'trade-in' in p_lower else 'Макон Авто'
                    kam = 'Алексей Чихарев'
                elif 'км/ч' in p_lower or 'км-ч' in p_lower:
                    pid, cname, kam = (1095, 'КМ/Ч', 'Алексей Чихарев')
                elif 'yes auto' in p_lower or 'иркутск' in p_lower:
                    cname = 'Yes Auto Иркутск'
                    kam = 'Светлана Дариенко'
                elif 'аксель' in p_lower or 'мурманск' in p_lower:
                    cname = 'Аксель Мурманск'
                    kam = 'Светлана Дариенко'
                elif 'брайт парк' in p_lower:
                    cname = 'Брайт Парк'
                    kam = 'Евгения Добролюбова'
                elif 'прайм авто' in p_lower or 'prime auto' in p_lower:
                    cname = 'Прайм Авто PRIME AUTO Новосибирск'
                    kam = 'Светлана Дариенко'
                elif 'ситидрайв' in p_lower:
                    cname = 'СитиДрайв'
                    kam = 'Алексей Чихарев'
                elif 'тауэр' in p_lower:
                    cname = 'Тауэр Авто Jetour'
                    kam = 'Алексей Чихарев'
                elif 'глобус' in p_lower or 'автосфера' in p_lower or 'тамбов-авто' in p_lower or 'тамбов авто' in p_lower:
                    pid, cname, kam = (1013, 'ГК Глобус', 'Валерия Солдатова')
                else:
                    res_kam = oem_resolver.resolve(partner_name=partner_raw or cname, city=lead_city, fallback_kam=kam)
                    if res_kam and res_kam != "Не назначен":
                        kam = res_kam

            lead_inn = str(get_exact_val(row, 'ИНН', 'ИННКОМПАНИИ') or '')
            pid, cname, kam = apply_canonical_kam_mapping(pid, cname, partner_raw, kam, lead_city, lead_inn, lead_month_str)

            # Per-partner and month deduplication
            p_key = pid if pid is not None else cname
            lead_dedup_key = (p_key, client_id, lead_month_str)
            if lead_dedup_key in seen_partner_leads:
                continue
            seen_partner_leads.add(lead_dedup_key)

            raw_brand = str(get_exact_val(row, 'БРЕНД', 'БРЕНДB2C') or "").strip()
            final_brand = normalize_brand(raw_brand, month=lead_month_str) if raw_brand else ""
            has_client_prepay = 1 if (client_id and client_id in clients_with_prepay) else 0

            sys_db_partners.append({
                "Month": lead_month_str,
                "PartnerId": pid,
                "Partner": cname,
                "RawPartner": partner_raw,
                "KAM": kam,
                "Type": "Лид",
                "Qty": 1,
                "Brand": final_brand,
                "Date": lead_serial,
                "ClientId": client_id,
                "LeadId": sid,
                "HasPrepay": has_client_prepay
            })


    return sys_db, sys_db_partners, debtors, reg_data

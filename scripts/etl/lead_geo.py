"""Lead geo stage of the dashboard ETL."""
from .normalization import clean_key
from .normalization import get_exact_val
from .normalization import normalize_brand
from .normalization import parse_custom_date
from collections import defaultdict
import re

def normalize_region_clean(raw_reg, dealer=''):
    if not raw_reg or str(raw_reg).lower() in ('не указан', 'nan', 'null', 'без региона', ''):
        raw_reg = ''
    r = str(raw_reg).strip()
    r = re.sub(r'\s+', ' ', r)
    r_up = r.upper()
    d_up = str(dealer or '').upper()

    # 1. Direct region & city patterns
    if any(k in r_up for k in ['МОСКВ', 'ЗЕЛЕНОГРАД']): return 'Москва и Московская область'
    if any(k in r_up for k in ['САНКТ-ПЕТЕРБУРГ', 'ПЕТЕРБУРГ', 'ЛЕНИНГРАДСК', 'СПБ', 'ВЫБОРГ', 'ГАТЧИН']): return 'Санкт-Петербург и Ленинградская область'
    if any(k in r_up for k in ['КРАСНОДАР', 'СОЧИ', 'НОВОРОССИЙСК', 'АРМАВИР', 'АНАПА', 'ГЕЛЕНДЖИК']): return 'Краснодарский край'
    if any(k in r_up for k in ['ТАТАРСТАН', 'КАЗАН', 'ЧЕЛНЫ', 'АЛЬМЕТЬЕВ', 'НИЖНЕКАМ', 'ЕЛАБУГ']): return 'Республика Татарстан'
    if any(k in r_up for k in ['БАШКОРТОСТАН', 'УФА', 'СТЕРЛИТАМАК', 'САЛАВАТ', 'НЕФТЕКАМ']): return 'Республика Башкортостан'
    if any(k in r_up for k in ['РОСТОВ', 'ТАГАНРОГ', 'ШАХТЫ', 'БАТАЙСК', 'НОВОЧЕРКАССК']): return 'Ростовская область'
    if any(k in r_up for k in ['СВЕРДЛОВСК', 'ЕКАТЕРИНБУРГ', 'ТАГИЛ', 'КАМЕНСК-УРАЛЬСК', 'ПЕРВОУРАЛЬСК']): return 'Свердловская область'
    if any(k in r_up for k in ['САМАР', 'ТОЛЬЯТТИ', 'СЫЗРАН']): return 'Самарская область'
    if any(k in r_up for k in ['НИЖЕГОРОД', 'НИЖНИЙ НОВГОРОД', 'ДЗЕРЖИНСК', 'АРЗАМАС']): return 'Нижегородская область'
    if any(k in r_up for k in ['ЧЕЛЯБИНСК', 'МАГНИТОГОРСК', 'ЗЛАТОУСТ', 'МИАСС']): return 'Челябинская область'
    if any(k in r_up for k in ['ПЕРМ', 'БЕРЕЗНИК', 'СОЛИКАМСК']): return 'Пермский край'
    if any(k in r_up for k in ['СТАВРОПОЛЬ', 'ПЯТИГОРСК', 'КИСЛОВОДСК', 'НЕВИННОМЫССК', 'ЕССЕНТУК']): return 'Ставропольский край'
    if any(k in r_up for k in ['ВОРОНЕЖ', 'БОРИСОГЛЕБСК', 'РОССОШ']): return 'Воронежская область'
    if any(k in r_up for k in ['НОВОСИБИРСК', 'БЕРДСК', 'ИСКИТИМ']): return 'Новосибирская область'
    if any(k in r_up for k in ['ТЮМЕН', 'ТОБОЛЬСК', 'ИШИМ']): return 'Тюменская область'
    if any(k in r_up for k in ['ВОЛГОГРАД', 'ВОЛЖСК', 'КАМЫШИН']): return 'Волгоградская область'
    if any(k in r_up for k in ['САРАТОВ', 'ЭНГЕЛЬС', 'БАЛАКОВО']): return 'Саратовская область'
    if any(k in r_up for k in ['УЛЬЯНОВСК', 'ДИМИТРОВГРАД']): return 'Ульяновская область'
    if any(k in r_up for k in ['ЯРОСЛАВ', 'РЫБИНСК', 'ПЕРЕСЛАВЛЬ']): return 'Ярославская область'
    if any(k in r_up for k in ['ТУЛЬСК', 'ТУЛА', 'НОВОМОСКОВСК']): return 'Тульская область'
    if any(k in r_up for k in ['РЯЗАН']): return 'Рязанская область'
    if any(k in r_up for k in ['ВЛАДИМИР', 'КОВРОВ', 'МУРОМ']): return 'Владимирская область'
    if any(k in r_up for k in ['БЕЛГОРОД', 'СТАРЫЙ ОСКОЛ', 'ГУБКИН']): return 'Белгородская область'
    if any(k in r_up for k in ['КАЛУЖ', 'КАЛУГА', 'ОБНИНСК']): return 'Калужская область'
    if any(k in r_up for k in ['УДМУРТ', 'ИЖЕВСК', 'САРАПУЛ', 'ВОТКИНСК']): return 'Удмуртская Республика'
    if any(k in r_up for k in ['ЧУВАШ', 'ЧЕБОКСАР', 'НОВОЧЕБОКСАРСК']): return 'Чувашская Республика'
    if any(k in r_up for k in ['КИРОВ', 'КИРОВО-ЧЕПЕЦК']): return 'Кировская область'
    if any(k in r_up for k in ['ЛИПЕЦК', 'ЕЛЕЦ']): return 'Липецкая область'
    if any(k in r_up for k in ['ОРЕНБУРГ', 'ОРСК', 'НОВОТРОИЦК']): return 'Оренбургская область'
    if any(k in r_up for k in ['КУРСК', 'ЖЕЛЕЗНОГОРСК']): return 'Курская область'
    if any(k in r_up for k in ['БРЯНСК', 'КЛИНЦЫ']): return 'Брянская область'
    if any(k in r_up for k in ['ИВАНОВ', 'КИНЕШМА', 'ШУЯ']): return 'Ивановская область'
    if any(k in r_up for k in ['ТВЕР', 'РЖЕВ', 'ВЫШНИЙ ВОЛОЧЕК']): return 'Тверская область'
    if any(k in r_up for k in ['ОМСК', 'ТАРА']): return 'Омская область'
    if any(k in r_up for k in ['КРАСНОЯРСК', 'НОРИЛЬСК', 'АЧИНСК', 'КАНСК']): return 'Красноярский край'
    if any(k in r_up for k in ['ХАНТЫ', 'ХМАО', 'СУРГУТ', 'НИЖНЕВАРТОВСК', 'НЕФТЕЮГАНСК']): return 'ХМАО — Югра'
    if any(k in r_up for k in ['КЕМЕРОВ', 'НОВОКУЗНЕЦК', 'ПРОКОПЬЕВСК', 'КУЗБАСС']): return 'Кемеровская область (Кузбасс)'
    if any(k in r_up for k in ['ИРКУТСК', 'БРАТСК', 'АНГАРСК']): return 'Иркутская область'
    if any(k in r_up for k in ['АЛТАЙ', 'БАРНАУЛ', 'БИЙСК', 'РУБЦОВСК']): return 'Алтайский край'
    if any(k in r_up for k in ['ХАБАРОВСК', 'КОМСОМОЛЬСК']): return 'Хабаровский край'
    if any(k in r_up for k in ['ПРИМОР', 'ВЛАДИВОСТОК', 'УССУРИЙСК', 'НАХОДКА']): return 'Приморский край'
    if any(k in r_up for k in ['АРХАНГЕЛЬСК', 'СЕВЕРОДВИНСК', 'КОТЛАС']): return 'Архангельская область'
    if any(k in r_up for k in ['МУРМАНСК', 'АПАТИТЫ', 'СЕВЕРОМОРСК']): return 'Мурманская область'
    if any(k in r_up for k in ['КАЛИНИНГРАД']): return 'Калининградская область'
    if any(k in r_up for k in ['ВОЛОГОД', 'ВОЛОГДА', 'ЧЕРЕПОВЕЦ']): return 'Вологодская область'
    if any(k in r_up for k in ['ПЕНЗ', 'ЗАРЕЧНЫЙ']): return 'Пензенская область'
    if any(k in r_up for k in ['ТАМБОВ', 'МИЧУРИНСК']): return 'Тамбовская область'
    if any(k in r_up for k in ['КОСТРОМ']): return 'Костромская область'
    if any(k in r_up for k in ['СМОЛЕНСК', 'ВЯЗЬМА']): return 'Смоленская область'
    if any(k in r_up for k in ['ОРЛОВ', 'ОРЕЛ', 'ОРЁЛ']): return 'Орловская область'
    if any(k in r_up for k in ['ПСКОВ', 'ВЕЛИКИЕ ЛУКИ']): return 'Псковская область'
    if any(k in r_up for k in ['НОВГОРОДСК', 'ВЕЛИКИЙ НОВГОРОД', 'БОРОВИЧИ']): return 'Новгородская область'
    if any(k in r_up for k in ['КАРЕЛ', 'ПЕТРОЗАВОДСК']): return 'Республика Карелия'
    if any(k in r_up for k in ['МОРДОВ', 'САРАНСК']): return 'Республика Мордовия'
    if any(k in r_up for k in ['МАРИЙ', 'ЙОШКАР-ОЛА']): return 'Республика Марий Эл'
    if any(k in r_up for k in ['ХАКАС', 'АБАКАН']): return 'Республика Хакасия'
    if any(k in r_up for k in ['БУРЯТ', 'УЛАН-УДЭ']): return 'Республика Бурятия'
    if any(k in r_up for k in ['ДАГЕСТАН', 'МАХАЧКАЛА', 'ДЕРБЕНТ']): return 'Республика Дагестан'
    if any(k in r_up for k in ['КАБАРДИН', 'НАЛЬЧИК']): return 'Кабардино-Балкарская Республика'
    if any(k in r_up for k in ['СЕВЕРНАЯ ОСЕТИЯ', 'ВЛАДИКАВКАЗ']): return 'Республика Северная Осетия — Алания'
    if any(k in r_up for k in ['ЧЕЧНЯ', 'ГРОЗНЫЙ']): return 'Чеченская Республика'
    if any(k in r_up for k in ['ЯМАЛО-НЕНЕЦ', 'ЯНАО', 'НОВЫЙ УРЕНГОЙ', 'НОЯБРЬСК']): return 'ЯНАО'

    # 2. Fallback to dealer location if client address was empty
    if d_up and d_up != 'ПУЛ СБЕРАВТО (ДЦ НЕ НАЗНАЧЕН)':
        if any(k in d_up for k in ['АМКАПИТАЛ', 'АВТОГЕРМЕС', 'АЛТУФЬЕВО', 'КАР АЦ', 'АВИЛОН', 'КУНЦЕВО', 'МЭЙДЖОР', 'MAJOR']):
            return 'Москва и Московская область'
        if any(k in d_up for k in ['АВТОПОЛЕ', 'МАКСИМУМ', 'ВАГНЕР', 'ПРАГМАТИКА', 'СИГМА', 'ЛАХТА']):
            return 'Санкт-Петербург и Ленинградская область'
        if any(k in d_up for k in ['ТЕМП АВТО К', 'ТЕХНО-ТЕМП', 'ТРАНСФОР', 'ОПТИМА КУБАНЬ', 'КРАСНОДАР']):
            return 'Краснодарский край'
        if any(k in d_up for k in ['ДИАЛОГ', 'АПЕЛЬСИН', 'ТТС', 'ТРАНСТЕХСЕРВИС', 'КАЗАН']):
            return 'Республика Татарстан'
        if any(k in d_up for k in ['БАШАВТОКОМ', 'ТЕНЕТ УФА', 'УРАЛ-МОТОРС']):
            return 'Республика Башкортостан'
        if any(k in d_up for k in ['НОВОМОСКОВСК', 'КОРС']):
            return 'Тульская область'
        if any(k in d_up for k in ['ВОСТОК МОТОРС', 'АВТОБАН', 'ИЮЛЬ', 'ЕКАТЕРИНБУРГ']):
            return 'Свердловская область'
        if any(k in d_up for k in ['САМАРА АВТО', 'ВИП АВТО']):
            return 'Самарская область'
        if any(k in d_up for k in ['НИЖЕГОРОДЕЦ', 'ЮНИКОР']):
            return 'Нижегородская область'
        if any(k in d_up for k in ['ФРЕШ', 'FRESH']):
            return 'Воронежская область'

    if r:
        return r.title()
    return 'Другие регионы'


def resolve_sberauto_lead_partner(contact_name, raw_partner=""):
    """
    Distributes SberAuto platform leads to their actual dealer queues and KAMs by contact name.
    """
    c_low = (contact_name or "").lower().strip()
    p_low = (raw_partner or "").lower().strip()
    if not ("сберавто" in p_low or "сбер авто" in p_low or not p_low):
        return None
    if not c_low:
        return None

    # Substring match known dealer queues
    if any(k in c_low for k in ['борисхоф', ' бх', 'бх ']):
        return (1070, 'БорисХоф', 'Алексей Чихарев')
    elif any(k in c_low for k in ['фреш', 'fresh']):
        return (1039, 'Fresh Auto', 'Андрей Кузнецов')
    elif any(k in c_low for k in ['тенет уфа', 'башавтоком']):
        return (1176, 'ГК Башавтоком', 'Евгения Добролюбова')
    elif 'форвард' in c_low:
        if 'тюмень' in c_low:
            return (1128, 'ГК Форвард-Авто', 'Алексей Чихарев')
        else:
            return (1128, 'ГК Форвард-Авто', 'Евгения Добролюбова')
    elif 'лунаавто' in c_low or 'чери нвск' in c_low or 'нск' in c_low:
        if 'o&j' in c_low:
            return (1029, 'O&J Новосибирск', 'Светлана Дариенко')
        else:
            return (1029, 'ЛунаАвто', 'Светлана Дариенко')
    elif 'авто-континент' in c_low or 'иркутск' in c_low:
        return (1287, 'Авто-Континент', 'Светлана Дариенко')
    elif 'вип авто' in c_low:
        return (1139, 'ООО "ВИП АВТО САМАРА"', 'Евгения Добролюбова')
    elif 'арконт' in c_low:
        return (1112, 'ГК Арконт Холдинг', 'Евгения Добролюбова')
    elif 'темп авто' in c_low or 'авто дон' in c_low:
        return (1010, 'ЧЕРИ ЦЕНТР ТЕМП АВТО ДОН', 'Валерия Солдатова')
    elif 'сигма' in c_low:
        return (1011, 'ГК Сигма', 'Светлана Дариенко')
    elif 'оптима' in c_low:
        return (1030, 'ГК Оптима', 'Валерия Солдатова')
    elif 'ай-би-эм' in c_low or 'би-эм' in c_low or 'кемерово' in c_low:
        return (1027, 'Ай-Би-Эм', 'Светлана Дариенко')
    elif 'диалог' in c_low:
        return (1082, 'ГК Диалог Авто', 'Алексей Чихарев')
    elif any(k in c_low for k in ['автосеть амк', 'автосеть рф амк', 'амк самара', 'амк тольятти', 'амк екб', 'амк-екатеринбург', 'амк']) and not any(ex in c_low for ex in ['амкапитал', 'ам капитал', 'апельсин', 'автомир']):
        return (1053, 'ФДЦ Автосеть АМК РФ', 'Евгения Добролюбова')
    elif 'апельсин' in c_low:
        return (1054, 'Апельсин-Челны', 'Алексей Чихарев')
    elif 'планета авто' in c_low or 'планета-авто' in c_low or 'чери центр планета авто восток' in c_low:
        if 'махачкала' in c_low or 'таганрог' in c_low:
            return (1058, 'ЧЕРИ ЦЕНТР ПЛАНЕТА АВТО ВОСТОК', 'Валерия Солдатова')
        elif 'москва' in c_low or 'мск' in c_low:
            return (1058, 'ЧЕРИ ЦЕНТР ПЛАНЕТА АВТО ВОСТОК', 'Алексей Чихарев')
        else:
            return (1058, 'ЧЕРИ ЦЕНТР ПЛАНЕТА АВТО ВОСТОК', 'Евгения Добролюбова')
    elif 'эксперт' in c_low and any(k in c_low for k in ['новосибирск', 'нск']):
        return (1035, 'Эксперт Авто (Новосибирск)', 'Евгения Добролюбова')
    elif 'твс' in c_low:
        return (1079, 'CHERY ТВС Моторс', 'Евгения Добролюбова')
    elif 'автогарантия' in c_low or 'челябинск' in c_low:
        return (1125, 'Автогарантия', 'Евгения Добролюбова')
    elif 'интерпартнер' in c_low or 'ижевск' in c_low:
        return (1123, 'Интерпартнер', 'Евгения Добролюбова')
    elif 'леон' in c_low:
        return (1023, 'Леон Авто', 'Валерия Солдатова')
    elif 'автокласс' in c_low or 'тула' in c_low:
        return (1103, 'ГК Автокласс', 'Алексей Чихарев')
    elif 'анкаравто' in c_low or 'калуга' in c_low:
        return (1119, 'АнкарАвто', 'Алексей Чихарев')
    elif 'автолюкс' in c_low or 'пятигорск' in c_low:
        return (1225, 'Автолюкс Пятигорск', 'Валерия Солдатова')
    elif 'таганрог' in c_low:
        return (1094, 'Таганрог Модус/Ринг', 'Валерия Солдатова')
    elif 'автоград' in c_low or 'калининград' in c_low:
        return (1121, 'АВТОЦЕНТР АВТОГРАД', 'Светлана Дариенко')
    elif 'автостиль' in c_low or 'новгород' in c_low:
        return (1034, 'Автостиль', 'Светлана Дариенко')
    elif 'брянск' in c_low or 'бн-моторс' in c_low or 'дебрянск' in c_low:
        return (1177, 'Дебрянск Авто', 'Валерия Солдатова')
    elif 'юг-авто' in c_low or 'юг авто' in c_low:
        return (1290, 'Юг-Авто', 'Валерия Солдатова')
    elif 'ааа' in c_low or 'формула-н' in c_low or 'формула н' in c_low:
        return (1291, 'ААА Моторс', 'Валерия Солдатова')
    elif 'архангельск' in c_low:
        return (1138, 'Авторитет (Архангельск)', 'Светлана Дариенко')
    elif 'нижегородец' in c_low or 'чери нн' in c_low:
        return (1071, 'CHERY/TENET Нижегородец', 'Евгения Добролюбова')
    elif 'экскурс' in c_low or 'пермь' in c_low:
        return (1288, 'Экскурс Пермь', 'Евгения Добролюбова')
    elif 'омода самара' in c_low or 'самара' in c_low:
        return (1179, 'ГК Самара Авто', 'Евгения Добролюбова')
    elif 'o&j екб' in c_low or 'екб' in c_low:
        return (1180, 'O&J Екатеринбург', 'Евгения Добролюбова')
    elif 'o&j казань' in c_low:
        return (1082, 'O&J Казань', 'Алексей Чихарев')
    elif 'o&j крд' in c_low:
        return (1010, 'O&J Краснодар', 'Валерия Солдатова')
    elif 'o&j мск' in c_low:
        return (1070, 'O&J Москва', 'Алексей Чихарев')
    elif 'tenet' in c_low:
        return (1176, 'Башавтоком / Чанган Центр', 'Евгения Добролюбова')
    return None


def calculate_lead_geo_dealers_analytics(leads_data, deals_data=None):
    """
    Build detailed breakdown of transferred and qualified leads by Region and Dealer.
    Includes client-level database for interactive drilldown with BFS URLs.
    Includes monthly breakdown ('all', '2026-08', '2026-07').
    """
    aux_keywords = ("КРЕДИТ", "КАСКО", "ОСАГО", "ГАП", "СТРАХОВ", "СЕРТИФИКАТ", "ВНЕСЕНИЕ АВАНСА", "АВАНС", "БРОНИРОВАНИЕ", "БРОНЬ", "БРОНИР")
    d12_client_map = {}
    deals_client_map = {}

    if deals_data:
        for r in deals_data:
            cid = str(get_exact_val(r, 'CLIENTID', 'IDКЛИЕНТА') or '').strip()
            if cid:
                raw_deal_date = get_exact_val(r, 'ПРЕДПОЛАГАЕМАЯДАТАЗАКРЫТИЯ')
                d_deal_date = parse_custom_date(raw_deal_date)
                deal_month_str = f"{d_deal_date.year}-{str(d_deal_date.month).zfill(2)}" if d_deal_date else "2026-08"
                stage = str(get_exact_val(r, 'СТАДИЯСДЕЛКИ') or "").upper()
                is_sale = ("ЗАКРЫТО И РЕАЛИЗОВАН" in stage) and not ("ВНЕСЕНИЕ АВАНСА" in str(get_exact_val(r, 'ТОВАР') or "").upper())

                deals_client_map[cid] = {
                    'partner': str(get_exact_val(r, 'КОМПАНИЯНАЗВАНИЕКОМПАНИИ', 'КОМПАНИЯ', 'ПАРТНЕР') or '').strip(),
                    'brand': normalize_brand(str(get_exact_val(r, 'ТОВАР', 'БРЕНД') or '').strip()),
                    'price': float(str(get_exact_val(r, 'ЦЕНА', 'ФИНАЛЬНАЯЦЕНАB2C') or 0).replace(' ', '').replace('\xa0', '').replace(',', '.') or 0),
                    'month': deal_month_str,
                    'is_sale': is_sale,
                    'region': str(get_exact_val(r, 'ГОРОД', 'РЕГИОН', 'АДРЕС') or '').strip()
                }

    client_crm_events = defaultdict(set)
    client_new_lead_dt = {}
    client_mgr_assign_dt = {}

    # Pass 1: Extract client details and event timestamps from leads data
    for r in leads_data:
        cid = str(get_exact_val(r, 'CLIENTID', 'IDКЛИЕНТА', 'ID') or '').strip()
        if not cid:
            continue

        ev_str = str(get_exact_val(r, 'СОБЫТИЕ', 'EVENTNAME', 'EVENT_NAME') or '').strip()
        ev_clean = clean_key(ev_str)
        client_crm_events[cid].add(ev_clean)

        d_val = str(get_exact_val(r, 'ДАТАСОБЫТИЯ', 'ДАТАПЕРВОГОСОБЫТИЯ', 'ДАТА') or '').strip()
        p_dt = parse_custom_date(d_val)
        if 'НОВЫЙЛИД' in ev_clean and p_dt:
            if cid not in client_new_lead_dt or p_dt < client_new_lead_dt[cid]:
                client_new_lead_dt[cid] = p_dt
        if 'ЗАКРЕПЛЕНИЕМЕНЕДЖЕРА' in ev_clean and p_dt:
            if cid not in client_mgr_assign_dt or p_dt > client_mgr_assign_dt[cid]:
                client_mgr_assign_dt[cid] = p_dt

        reg = str(get_exact_val(r, 'РЕГИОНКЛИЕНТАИЗSBERID', 'РЕГИОНКЛИЕНТА', 'РЕГИОНРЛ', 'РЕГИОН', 'ADDRESS', 'АДРЕС') or '').strip()
        partner = str(get_exact_val(r, 'ПАРТНЕР', 'ДИЛЕР', 'КОМПАНИЯ') or '').strip()
        contact_name = str(get_exact_val(r, 'НАЗВАНИЕКОНТАКТА', 'КОНТАКТ') or '').strip()
        sber_res = resolve_sberauto_lead_partner(contact_name, partner)
        if sber_res:
            partner = sber_res[1]

        raw_b = str(get_exact_val(r, 'БРЕНД', 'МАРКА') or '').strip()
        brand = normalize_brand(raw_b) or 'Другие'
        model = str(get_exact_val(r, 'МОДЕЛЬ') or '').strip()
        vin = str(get_exact_val(r, 'VIN', 'ВИН') or '').strip()

        try:
            price = float(str(get_exact_val(r, 'ЦЕНААВТО', 'ЦЕНА') or 0).replace(' ', '').replace('\xa0', '').replace(',', '.'))
        except Exception:
            price = 0.0

        if cid not in d12_client_map:
            d12_client_map[cid] = {
                'region': reg,
                'partner': partner,
                'brand': brand,
                'model': model,
                'vin': vin,
                'price': price
            }
        else:
            if reg and not d12_client_map[cid]['region']: d12_client_map[cid]['region'] = reg
            if partner and (not d12_client_map[cid]['partner'] or 'сберавто' in d12_client_map[cid]['partner'].lower()): d12_client_map[cid]['partner'] = partner
            if brand and (not d12_client_map[cid]['brand'] or d12_client_map[cid]['brand'] == 'Другие'): d12_client_map[cid]['brand'] = brand
            if model and not d12_client_map[cid]['model']: d12_client_map[cid]['model'] = model
            if vin and not d12_client_map[cid]['vin']: d12_client_map[cid]['vin'] = vin
            if price > 0 and d12_client_map[cid]['price'] == 0: d12_client_map[cid]['price'] = price

    # Identification of qualified clients: 'Новый лид', followed by 'Закрепление менеджера'
    qual_clients_by_new_lead_mgr = set()
    for cid, ev_set in client_crm_events.items():
        has_new = any('НОВЫЙЛИД' in e for e in ev_set)
        has_mgr = any('ЗАКРЕПЛЕНИЕМЕНЕДЖЕРА' in e for e in ev_set)
        if has_new and has_mgr:
            l_dt = client_new_lead_dt.get(cid)
            m_dt = client_mgr_assign_dt.get(cid)
            if not l_dt or not m_dt or m_dt >= l_dt:
                qual_clients_by_new_lead_mgr.add(cid)

    oem_13_brands = {'JETOUR', 'LADA', 'HAVAL', 'CHANGAN', 'GEELY', 'BELGEE', 'KNEWSTAR', 'CHERY', 'TENET', 'SOLARIS', 'SOUEAST', 'GAC', 'МОСКВИЧ', 'OMODA', 'JAECOO', 'HONGQI', 'XCITE'}

    # Pass 2: Aggregate events, qualification and transfer flags by client_id (deduplicated by client_id)
    clients_by_id = {}
    for r in leads_data:
        cid = str(get_exact_val(r, 'CLIENTID', 'IDКЛИЕНТА', 'ID') or '').strip()
        if not cid:
            continue

        raw_src = str(get_exact_val(r, 'SOURCE', 'ИСТОЧНИК', 'ДЕТАЛИ') or '').lower()
        raw_brand = str(get_exact_val(r, 'БРЕНД', 'МАРКА') or '').upper()

        event = str(get_exact_val(r, 'СОБЫТИЕ', 'EVENTNAME', 'EVENT_NAME') or '').strip()
        ev_clean = clean_key(event)

        is_trans_row = ('ОТПРАВКАЛИДА' in ev_clean or 'ОТПРАВЛЕНДИЛЕРУ' in ev_clean or str(get_exact_val(r, 'ОТПРАВЛЕНДИЛЕРУ', 'ПЕРЕДАНДИЛЕРУ', 'ПЕРЕДАН') or '').strip() == '1')
        has_used_row = ('б/у' in raw_src or 'бу' in raw_src or 'пробег' in raw_src)
        has_oem_row = any(ob in raw_brand for ob in oem_13_brands)
        has_fdc_row = ('фдц' in raw_src)

        d12_info = d12_client_map.get(cid, {})
        deal_info = deals_client_map.get(cid, {})

        dealer = d12_info.get('partner') or deal_info.get('partner') or str(get_exact_val(r, 'ПАРТНЕР', 'ДИЛЕР') or '').strip()
        contact_name = str(get_exact_val(r, 'НАЗВАНИЕКОНТАКТА', 'КОНТАКТ') or '').strip()
        sber_res = resolve_sberauto_lead_partner(contact_name, dealer)
        if sber_res:
            dealer = sber_res[1]
        elif not dealer or 'сберавто' in dealer.lower() or 'сбер авто' in dealer.lower():
            dealer = 'Пул СберАвто (ДЦ не назначен)'

        raw_reg = d12_info.get('region') or deal_info.get('region') or str(get_exact_val(r, 'РЕГИОНКЛИЕНТА', 'РЕГИОНРЛ', 'РЕГИОНКЛИЕНТАИЗSBERID', 'РЕГИОН', 'АДРЕС') or '').strip()
        norm_reg = normalize_region_clean(raw_reg, dealer=dealer)

        raw_b = d12_info.get('brand') or deal_info.get('brand') or str(get_exact_val(r, 'БРЕНД', 'МАРКА') or '').strip()
        brand = normalize_brand(raw_b) or 'Другие'
        model = d12_info.get('model') or str(get_exact_val(r, 'МОДЕЛЬ') or '').strip()

        has_deal = bool(deal_info.get('is_sale'))
        deal_month = deal_info.get('month')

        date_val = str(get_exact_val(r, 'ДАТАСОБЫТИЯ', 'ДАТАПЕРВОГОСОБЫТИЯ', 'ДАТА') or '').strip()
        p_date = parse_custom_date(date_val)
        lead_month = p_date.strftime('%Y-%m') if p_date else '2026-08'
        client_month = deal_month if has_deal else lead_month

        is_client_qual = (cid in qual_clients_by_new_lead_mgr) or is_trans_row or has_deal

        if cid not in clients_by_id:
            clients_by_id[cid] = {
                'id': cid,
                'bfs_url': f"https://backoffice.x.sberauto.com/crm/manager/{cid}",
                'region': norm_reg,
                'dealer': dealer,
                'brand': brand,
                'model': model,
                'month': client_month,
                'is_qual': is_client_qual,
                'is_raw_trans': is_trans_row or has_deal,
                'has_used': has_used_row,
                'has_oem': has_oem_row or has_deal,
                'has_fdc': has_fdc_row,
                'has_deal': has_deal,
                'event': event or ('Сделка' if has_deal else 'В обработке'),
                'date': date_val,
                'price': d12_info.get('price', 0) or deal_info.get('price', 0),
                'vin': d12_info.get('vin', '')
            }
        else:
            c_entry = clients_by_id[cid]
            if is_client_qual: c_entry['is_qual'] = True
            if is_trans_row or has_deal: c_entry['is_raw_trans'] = True
            if has_used_row: c_entry['has_used'] = True
            if has_oem_row or has_deal: c_entry['has_oem'] = True
            if has_fdc_row: c_entry['has_fdc'] = True
            if has_deal: c_entry['has_deal'] = True
            if (not c_entry['brand'] or c_entry['brand'] == 'Другие') and brand != 'Другие':
                c_entry['brand'] = brand
            if not c_entry['model']:
                c_entry['model'] = model
            if dealer and c_entry['dealer'] == 'Пул СберАвто (ДЦ не назначен)':
                c_entry['dealer'] = dealer
            if norm_reg != 'Другие регионы' and c_entry['region'] == 'Другие регионы':
                c_entry['region'] = norm_reg

    # Finalize BI transfer flag for each client (strictly qualified + OEM + not used + not fdc)
    for c_entry in clients_by_id.values():
        cid_val = c_entry.get('id')
        if (cid_val in qual_clients_by_new_lead_mgr) or c_entry.get('has_deal') or c_entry.get('is_raw_trans'):
            c_entry['is_qual'] = True

        if c_entry.get('has_deal'):
            c_entry['is_qual'] = True
            c_entry['is_raw_trans'] = True
            c_entry['has_oem'] = True
            c_entry['is_trans'] = True
        elif c_entry.get('is_raw_trans'):
            c_entry['is_qual'] = True
            c_entry['is_trans'] = (
                c_entry.get('has_oem', False) and
                (not c_entry.get('has_used', False)) and
                (not c_entry.get('has_fdc', False))
            )
        else:
            c_entry['is_trans'] = False

    clients_all = list(clients_by_id.values())

    def build_tree_for_clients(subset_clients, include_clients=True, max_clients_per_dealer=150):
        tot_c = len(subset_clients)
        q_c = sum(1 for c in subset_clients if c['is_qual'])
        t_c = sum(1 for c in subset_clients if c['is_trans'])
        t_q_pct = round((t_c / q_c * 100), 1) if q_c > 0 else 0.0
        d_cnt = sum(1 for c in subset_clients if c['has_deal'])
        d_cr_pct = round((d_cnt / t_c * 100), 1) if t_c > 0 else 0.0

        reg_map = {}
        for c in subset_clients:
            r_name = c['region']
            d_name = c['dealer']

            if r_name not in reg_map:
                reg_map[r_name] = {
                    'region_name': r_name,
                    'total_clients': 0,
                    'qual_clients': 0,
                    'trans_clients': 0,
                    'trans_qual_clients': 0,
                    'deals': 0,
                    'dealers_dict': {}
                }

            r_entry = reg_map[r_name]
            r_entry['total_clients'] += 1
            if c['is_qual']: r_entry['qual_clients'] += 1
            if c['is_trans']: r_entry['trans_clients'] += 1
            if c['is_qual'] and c['is_trans']: r_entry['trans_qual_clients'] += 1
            if c['has_deal']: r_entry['deals'] += 1

            if d_name not in r_entry['dealers_dict']:
                r_entry['dealers_dict'][d_name] = {
                    'dealer_name': d_name,
                    'region_name': r_name,
                    'total_clients': 0,
                    'qual_clients': 0,
                    'trans_clients': 0,
                    'trans_qual_clients': 0,
                    'deals': 0,
                    'brands_count': {},
                    'clients': []
                }

            d_entry = r_entry['dealers_dict'][d_name]
            d_entry['total_clients'] += 1
            if c['is_qual']: d_entry['qual_clients'] += 1
            if c['is_trans']: d_entry['trans_clients'] += 1
            if c['is_qual'] and c['is_trans']: d_entry['trans_qual_clients'] += 1
            if c['has_deal']: d_entry['deals'] += 1

            b = c['brand'] or 'Другие'
            d_entry['brands_count'][b] = d_entry['brands_count'].get(b, 0) + 1

            if include_clients and len(d_entry['clients']) < max_clients_per_dealer:
                d_entry['clients'].append({
                    'id': c['id'],
                    'bfs_url': c['bfs_url'],
                    'brand': c['brand'],
                    'model': c['model'],
                    'month': c.get('month', '2026-08'),
                    'is_qual': c['is_qual'],
                    'is_trans': c['is_trans'],
                    'has_deal': c['has_deal'],
                    'event': c['event'],
                    'vin': c['vin'],
                    'price': c['price']
                })

        regions_list = []
        for r_name, r_data in reg_map.items():
            dealers_list = []
            for d_name, d_data in r_data['dealers_dict'].items():
                top_brands = sorted(d_data['brands_count'].items(), key=lambda x: x[1], reverse=True)
                dealers_list.append({
                    'dealer_name': d_name,
                    'region_name': r_name,
                    'total_clients': d_data['total_clients'],
                    'qual_clients': d_data['qual_clients'],
                    'trans_clients': d_data['trans_clients'],
                    'trans_qual_clients': d_data['trans_qual_clients'],
                    'trans_qual_pct': round((d_data['trans_qual_clients'] / d_data['qual_clients'] * 100), 1) if d_data['qual_clients'] > 0 else 0.0,
                    'deals': d_data['deals'],
                    'deals_cr_pct': round((d_data['deals'] / d_data['trans_clients'] * 100), 1) if d_data['trans_clients'] > 0 else 0.0,
                    'top_brands': [tb[0] for tb in top_brands[:3] if tb[0] not in aux_keywords],
                    'clients': d_data['clients']
                })

            dealers_list.sort(key=lambda x: (x['trans_clients'], x['qual_clients']), reverse=True)

            regions_list.append({
                'region_name': r_name,
                'total_clients': r_data['total_clients'],
                'qual_clients': r_data['qual_clients'],
                'trans_clients': r_data['trans_clients'],
                'trans_qual_clients': r_data['trans_qual_clients'],
                'trans_qual_pct': round((r_data['trans_qual_clients'] / r_data['qual_clients'] * 100), 1) if r_data['qual_clients'] > 0 else 0.0,
                'deals': r_data['deals'],
                'deals_cr_pct': round((r_data['deals'] / r_data['trans_clients'] * 100), 1) if r_data['trans_clients'] > 0 else 0.0,
                'dealers_count': len(dealers_list),
                'dealers': dealers_list
            })

        regions_list.sort(key=lambda x: (x['trans_clients'], x['qual_clients']), reverse=True)

        return {
            'summary': {
                'total_clients': tot_c,
                'qual_clients': q_c,
                'trans_clients': t_c,
                'trans_qual_clients': t_c,
                'trans_qual_pct': t_q_pct,
                'deals_from_trans': d_cnt,
                'deals_cr_pct': d_cr_pct
            },
            'regions': regions_list
        }

    clients_all_sorted = sorted(clients_all, key=lambda c: str(c.get('date') or ''), reverse=True)
    all_tree = build_tree_for_clients(clients_all_sorted, include_clients=True, max_clients_per_dealer=150)
    all_tree_no_clients = build_tree_for_clients(clients_all, include_clients=False)
    aug_clients = [c for c in clients_all_sorted if c.get('month') == '2026-08']
    jul_clients = [c for c in clients_all_sorted if c.get('month') == '2026-07']
    sep_clients = [c for c in clients_all_sorted if c.get('month') == '2026-09']
    aug_tree = build_tree_for_clients(aug_clients, include_clients=False)
    jul_tree = build_tree_for_clients(jul_clients, include_clients=False)
    sep_tree = build_tree_for_clients(sep_clients, include_clients=False)

    # Performance split: return two versions — lightweight (for data.json) and full (for geo_clients.json)
    lightweight_result = {
        'summary': all_tree['summary'],
        'regions': all_tree_no_clients['regions'],   # aggregate stats only, NO client-level data
        'by_month': {
            'all': all_tree_no_clients,
            '2026-09': sep_tree,
            '2026-08': aug_tree,
            '2026-07': jul_tree
        }
    }
    full_result = {
        'summary': all_tree['summary'],
        'regions': all_tree['regions'],   # full tree with clients arrays (for lazy-loaded geo_clients.json)
        'by_month': {
            'all': all_tree_no_clients,
            '2026-09': sep_tree,
            '2026-08': aug_tree,
            '2026-07': jul_tree
        }
    }
    return lightweight_result, full_result


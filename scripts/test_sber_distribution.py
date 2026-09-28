import glob, os, sys
sys.path.insert(0, '.')
from scripts.parser_engine import read_tabular_file, get_exact_val

files = glob.glob('raw_data/data (*).xlsx')
latest_file = sorted(files, key=os.path.getmtime)[-1]
datasets = read_tabular_file(latest_file)
leads_rows = datasets[0][1] if datasets else []

def resolve_sberauto_lead_partner(contact_name, raw_partner=""):
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
    elif 'апельсин' in c_low:
        return (1053, 'ФДЦ Автосеть АМК РФ', 'Алексей Чихарев')
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
    elif 'брянск' in c_low or 'бн-моторс' in c_low:
        return (1177, 'ГК БН-МОТОРС, БНМ', 'Евгения Добролюбова')
    elif 'архангельск' in c_low:
        return (1138, 'Архангельск Динамика', 'Светлана Дариенко')
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
    return None

resolved_counts = {}
unresolved = {}
for r in leads_rows:
    p = str(get_exact_val(r, 'BI', 'ПАРТНЕР') or '')
    if 'сбер' in p.lower():
        c = str(get_exact_val(r, 'НАЗВАНИЕКОНТАКТА', 'КОНТАКТ') or '')
        res = resolve_sberauto_lead_partner(c, p)
        if res:
            pid, cname, kam = res
            key = f"{cname} ({kam})"
            resolved_counts[key] = resolved_counts.get(key, 0) + 1
        else:
            unresolved[c] = unresolved.get(c, 0) + 1

lines = []
lines.append(f"Total resolved leads: {sum(resolved_counts.values())}")
lines.append(f"Total unresolved leads: {sum(unresolved.values())}")
lines.append("\nResolved breakdown:")
for k, cnt in sorted(resolved_counts.items(), key=lambda x: -x[1]):
    lines.append(f"  {cnt}: {k}")
lines.append("\nUnresolved contacts:")
for k, cnt in sorted(unresolved.items(), key=lambda x: -x[1]):
    lines.append(f"  {cnt}: {repr(k)}")

with open('temp_sber_distribution_test.txt', 'w', encoding='utf-8') as f:
    f.write('\n'.join(lines))
print('Done test')

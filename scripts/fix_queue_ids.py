with open('scripts/parser_engine.py', 'r', encoding='utf-8') as f:
    text = f.read()

s_old = """                    # Substring match known dealer queues
                    if any(k in c_low for k in ['борисхоф', ' бх', 'бх ']):
                        pid, cname, kam = (1205, 'БорисХоф', 'Алексей Чихарев')
                    elif any(k in c_low for k in ['фреш', 'fresh']):
                        pid, cname, kam = (1073, 'Fresh Auto', 'Андрей Кузнецов')
                    elif any(k in c_low for k in ['тенет уфа', 'башавтоком']):
                        pid, cname, kam = (1134, 'Башавтоком / Чанган Центр', 'Евгения Добролюбова')
                    elif 'форвард' in c_low:
                        if 'тюмень' in c_low:
                            pid, cname, kam = (1128, 'ГК Форвард-Авто', 'Алексей Чихарев')
                        else:
                            pid, cname, kam = (1128, 'ГК Форвард-Авто', 'Евгения Добролюбова')
                    elif 'лунаавто' in c_low or 'чери нвск' in c_low or 'нск' in c_low:
                        if 'o&j' in c_low:
                            cname = 'O&J Новосибирск'
                            kam = 'Светлана Дариенко'
                        else:
                            pid, cname, kam = (1232, 'ЛунаАвто', 'Светлана Дариенко')
                    elif 'авто-континент' in c_low or 'иркутск' in c_low:
                        pid, cname, kam = (1138, 'Авто-Континент', 'Светлана Дариенко')
                    elif 'вип авто' in c_low:
                        pid, cname, kam = (1248, 'ООО "ВИП АВТО САМАРА"', 'Евгения Добролюбова')
                    elif 'арконт' in c_low:
                        pid, cname, kam = (1253, 'ГК Арконт', 'Евгения Добролюбова')
                    elif 'темп авто' in c_low or 'авто дон' in c_low:
                        pid, cname, kam = (1186, 'ЧЕРИ ЦЕНТР ТЕМП АВТО ДОН', 'Валерия Солдатова')
                    elif 'сигма' in c_low:
                        pid, cname, kam = (1028, 'Сигма', 'Светлана Дариенко')
                    elif 'оптима' in c_low:
                        pid, cname, kam = (1281, 'ГК Оптима', 'Валерия Солдатова')
                    elif 'ай-би-эм' in c_low or 'би-эм' in c_low or 'кемерово' in c_low:
                        pid, cname, kam = (1265, 'Ай-Би-Эм Кемерово', 'Алексей Чихарев')
                    elif 'диалог' in c_low:
                        pid, cname, kam = (1237, 'Диалог Авто', 'Алексей Чихарев')
                    elif 'апельсин' in c_low:
                        pid, cname, kam = (1243, 'Апельсин (Автосеть РФ)', 'Алексей Чихарев')
                    elif 'твс' in c_low:
                        pid, cname, kam = (1259, 'ТВС Моторс', 'Евгения Добролюбова')
                    elif 'автогарантия' in c_low or 'челябинск' in c_low:
                        pid, cname, kam = (1125, 'Автогарантия', 'Евгения Добролюбова')
                    elif 'интерпартнер' in c_low or 'ижевск' in c_low:
                        pid, cname, kam = (1122, 'Интерпартнер', 'Евгения Добролюбова')
                    elif 'леон' in c_low:
                        pid, cname, kam = (1246, 'Леон Авто КРД', 'Валерия Солдатова')
                    elif 'автокласс' in c_low or 'тула' in c_low:
                        pid, cname, kam = (1118, 'Автокласс', 'Алексей Чихарев')
                    elif 'анкаравто' in c_low or 'калуга' in c_low:
                        pid, cname, kam = (1119, 'АнкарАвто', 'Алексей Чихарев')
                    elif 'автолюкс' in c_low or 'пятигорск' in c_low:
                        pid, cname, kam = (1225, 'Автолюкс Пятигорск', 'Валерия Солдатова')
                    elif 'таганрог' in c_low:
                        cname = 'Таганрог Модус/Ринг'
                        kam = 'Валерия Солдатова'
                    elif 'автоград' in c_low or 'калининград' in c_low:
                        pid, cname, kam = (1266, 'ONLINE АВТОЦЕНТР АВТОГРАД', 'Светлана Дариенко')
                    elif 'автостиль' in c_low or 'новгород' in c_low:
                        pid, cname, kam = (1034, 'Автостиль', 'Светлана Дариенко')
                    elif 'брянск' in c_low or 'бн-моторс' in c_low:
                        pid, cname, kam = (1260, 'ГК БН-Моторс', 'Евгения Добролюбова')
                    elif 'архангельск' in c_low:
                        cname = 'Архангельск Динамика'
                        kam = 'Светлана Дариенко'
                    elif 'нижегородец' in c_low or 'чери нн' in c_low:
                        pid, cname, kam = (1048, 'Нижегородец', 'Евгения Добролюбова')
                    elif 'экскурс' in c_low or 'пермь' in c_low:
                        cname = 'Экскурс Пермь'
                        kam = 'Евгения Добролюбова'
                    elif 'омода самара' in c_low or 'самара' in c_low:
                        pid, cname, kam = (1106, 'ГК Самара-Авто', 'Евгения Добролюбова')"""

s_new = """                    # Substring match known dealer queues
                    if any(k in c_low for k in ['борисхоф', ' бх', 'бх ']):
                        pid, cname, kam = (1070, 'БорисХоф', 'Алексей Чихарев')
                    elif any(k in c_low for k in ['фреш', 'fresh']):
                        pid, cname, kam = (1039, 'Fresh Auto', 'Андрей Кузнецов')
                    elif any(k in c_low for k in ['тенет уфа', 'башавтоком']):
                        pid, cname, kam = (1176, 'ГК Башавтоком', 'Евгения Добролюбова')
                    elif 'форвард' in c_low:
                        if 'тюмень' in c_low:
                            pid, cname, kam = (1128, 'ГК Форвард-Авто', 'Алексей Чихарев')
                        else:
                            pid, cname, kam = (1128, 'ГК Форвард-Авто', 'Евгения Добролюбова')
                    elif 'лунаавто' in c_low or 'чери нвск' in c_low or 'нск' in c_low:
                        if 'o&j' in c_low:
                            cname = 'O&J Новосибирск'
                            kam = 'Светлана Дариенко'
                        else:
                            pid, cname, kam = (1029, 'ЛунаАвто', 'Светлана Дариенко')
                    elif 'авто-континент' in c_low or 'иркутск' in c_low:
                        pid, cname, kam = (1138, 'Авто-Континент', 'Светлана Дариенко')
                    elif 'вип авто' in c_low:
                        pid, cname, kam = (1139, 'ООО "ВИП АВТО САМАРА"', 'Евгения Добролюбова')
                    elif 'арконт' in c_low:
                        pid, cname, kam = (1112, 'ГК Арконт Холдинг', 'Евгения Добролюбова')
                    elif 'темп авто' in c_low or 'авто дон' in c_low:
                        pid, cname, kam = (1010, 'ЧЕРИ ЦЕНТР ТЕМП АВТО ДОН', 'Валерия Солдатова')
                    elif 'сигма' in c_low:
                        pid, cname, kam = (1028, 'Сигма', 'Светлана Дариенко')
                    elif 'оптима' in c_low:
                        pid, cname, kam = (1030, 'ГК Оптима', 'Валерия Солдатова')
                    elif 'ай-би-эм' in c_low or 'би-эм' in c_low or 'кемерово' in c_low:
                        pid, cname, kam = (1027, 'Ай-Би-Эм', 'Светлана Дариенко')
                    elif 'диалог' in c_low:
                        pid, cname, kam = (1082, 'ГК Диалог Авто', 'Алексей Чихарев')
                    elif 'апельсин' in c_low:
                        pid, cname, kam = (1053, 'ФДЦ Автосеть АМК РФ', 'Алексей Чихарев')
                    elif 'твс' in c_low:
                        pid, cname, kam = (1079, 'CHERY ТВС Моторс', 'Евгения Добролюбова')
                    elif 'автогарантия' in c_low or 'челябинск' in c_low:
                        pid, cname, kam = (1125, 'Автогарантия', 'Евгения Добролюбова')
                    elif 'интерпартнер' in c_low or 'ижевск' in c_low:
                        pid, cname, kam = (1123, 'Интерпартнер', 'Евгения Добролюбова')
                    elif 'леон' in c_low:
                        pid, cname, kam = (1023, 'Леон Авто', 'Валерия Солдатова')
                    elif 'автокласс' in c_low or 'тула' in c_low:
                        pid, cname, kam = (1103, 'ГК Автокласс', 'Алексей Чихарев')
                    elif 'анкаравто' in c_low or 'калуга' in c_low:
                        pid, cname, kam = (1119, 'АнкарАвто', 'Алексей Чихарев')
                    elif 'автолюкс' in c_low or 'пятигорск' in c_low:
                        pid, cname, kam = (1225, 'Автолюкс Пятигорск', 'Валерия Солдатова')
                    elif 'таганрог' in c_low:
                        cname = 'Таганрог Модус/Ринг'
                        kam = 'Валерия Солдатова'
                    elif 'автоград' in c_low or 'калининград' in c_low:
                        pid, cname, kam = (1121, 'АВТОЦЕНТР АВТОГРАД', 'Светлана Дариенко')
                    elif 'автостиль' in c_low or 'новгород' in c_low:
                        pid, cname, kam = (1034, 'Автостиль', 'Светлана Дариенко')
                    elif 'брянск' in c_low or 'бн-моторс' in c_low:
                        pid, cname, kam = (1177, 'ГК БН-МОТОРС, БНМ', 'Евгения Добролюбова')
                    elif 'архангельск' in c_low:
                        cname = 'Архангельск Динамика'
                        kam = 'Светлана Дариенко'
                    elif 'нижегородец' in c_low or 'чери нн' in c_low:
                        pid, cname, kam = (1071, 'CHERY/TENET Нижегородец', 'Евгения Добролюбова')
                    elif 'экскурс' in c_low or 'пермь' in c_low:
                        cname = 'Экскурс Пермь'
                        kam = 'Евгения Добролюбова'
                    elif 'омода самара' in c_low or 'самара' in c_low:
                        pid, cname, kam = (1179, 'ГК Самара Авто', 'Евгения Добролюбова')"""

assert s_old in text, "s_old not found!"
text = text.replace(s_old, s_new, 1)

with open('scripts/parser_engine.py', 'w', encoding='utf-8') as f:
    f.write(text)

print("Successfully replaced SberAuto queue IDs!")

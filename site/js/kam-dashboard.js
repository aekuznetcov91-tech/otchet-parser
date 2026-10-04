/* ====================================================================
 * B2C Analytics Dashboard — KAM Management & Executive Reporting Module
 * Tracks total incoming leads, qualification, transfers, deals (Transfer/MP/FDC+Online),
 * Partner -> OEM City -> Brand hierarchy, CR, and interactive plan management.
 * ====================================================================*/

let currentKamFilter = 'all'; // 'all' or KAM full name
let currentKamSearchQuery = '';
let currentKamPlanFilter = 'all'; // 'all', 'completed', 'in_progress', 'no_plan'

// Official September 2026 Sales Plans for Alexei Chikharev (33 partners, Sum = 553)
const CHIKHAREV_OFFICIAL_PLANS = {
    // 1. БОРИСХОФ (10)
    "1070": 10, "ID_1070": 10, "ID_1070__Алексей Чихарев": 10, "БорисХоф": 10, "БОРИСХОФ": 10,
    // 2. ООО "ДЕЛИВЕРИ КАР" (1)
    "1099": 1, "ID_1099": 1, "ID_1099__Алексей Чихарев": 1, "ООО \"ДЕЛИВЕРИ КАР\"": 1, "ООО \"ДЕЛИВЕРИ КАР": 1, "ДЕЛИВЕРИ КАР": 1,
    // 3. ООО "ИЗМАЙЛОВО-СЕРВИС" (10)
    "1059": 10, "ID_1059": 10, "ID_1059__Алексей Чихарев": 10, "CHERY Измайлово": 10, "ООО \"ИЗМАЙЛОВО-СЕРВИС\"": 10, "МБ-Измайлово": 10,
    // 4. ООО Автодин-Кама (2)
    "1042": 2, "ID_1042": 2, "ID_1042__Алексей Чихарев": 2, "Автодин": 2, "ООО Автодин-Кама": 2,
    // 5. Тауэр Орехово (6)
    "1133": 6, "ID_1133": 6, "ID_1133__Алексей Чихарев": 6, "ООО \"ТАУЭР ЛТД\"": 6, "ООО \"ТАУЭР ЛТД": 6, "Тауэр Орехово": 6,
    // 6. ООО У Сервис (20)
    "1111": 20, "ID_1111": 20, "ID_1111__Алексей Чихарев": 20, "Geely У Сервис": 20, "ООО У Сервис": 20, "У Сервис": 20, "У Сервис+": 20,
    // 7. Автодом (20)
    "1154": 20, "ID_1154": 20, "ID_1154__Алексей Чихарев": 20, "АвтоДом Петрозаводск": 20, "ГК Автодом": 20, "Автодом": 20,
    // 8. АСЦ (25)
    "1130": 25, "ID_1130": 25, "ID_1130__Алексей Чихарев": 25, "ООО \"КАР АЦ\"": 25, "ООО \"КАР АЦ": 25, "АСЦ": 25,
    // 9. ООО "МАРКАР ГРУПП" ONLINE (60)
    "1120": 60, "ID_1120": 60, "ID_1120__Алексей Чихарев": 60, "ООО \"МАРКАР ГРУПП\"": 60, "ООО \"МАРКАР ГРУПП": 60, "Маркар": 60, "ООО \"МАРКАР ГРУПП\" ONLINE": 60,
    // 10. ООО КВАЗАР (30)
    "1052": 30, "ID_1052": 30, "ID_1052__Алексей Чихарев": 30, "КВАЗАР": 30, "ООО КВАЗАР": 30,
    // 11. КМ/ч (1)
    "1095": 1, "ID_1095": 1, "ID_1095__Алексей Чихарев": 1, "КМ/Ч": 1, "КМ/ч": 1, "КМ/ч (Москва)": 1,
    // 12. ООО Кунцево АТ (50)
    "1091": 50, "ID_1091": 50, "ID_1091__Алексей Чихарев": 50, "ТЦ Кунцево": 50, "ООО Кунцево АТ": 50, "Кунцево": 50,
    // 13. ООО Автопассаж (2)
    "1160": 2, "ID_1160": 2, "ID_1160__Алексей Чихарев": 2, "Автопассаж": 2, "ООО Автопассаж": 2,
    // 14. Мейджер (5)
    "1044": 5, "ID_1044": 5, "ID_1044__Алексей Чихарев": 5, "ГК Major/Мэйджор": 5, "Мейджер": 5, "Major": 5,
    // 15. Эрси Автотрейд (8)
    "1135": 8, "ID_1135": 8, "ID_1135__Алексей Чихарев": 8, "ЭрСи Автотрейд": 8, "Эрси Автотрейд": 8,
    // 16. Фаворит (7)
    "1227": 7, "ID_1227": 7, "ID_1227__Алексей Чихарев": 7, "Фаворит": 7, "FAVORIT MOTORS": 7,
    // 17. Империя(независимость) (15)
    "1261": 15, "ID_1261": 15, "ID_1261__Алексей Чихарев": 15, "Независимость": 15, "Империя(независимость)": 15, "Империя": 15,
    // 18. Автопрестиж (70)
    "1076": 70, "ID_1076": 70, "ID_1076__Алексей Чихарев": 70, "ГК Автопрестиж": 70, "Автопрестиж": 70,
    // 19. Автокласс (3)
    "1102": 3, "ID_1102": 3, "ID_1102__Алексей Чихарев": 3, "Чери Центр Автокласс (М-Авто)": 3, "Автокласс": 3,
    // 20. Автоград (1)
    "1050": 1, "ID_1050": 1, "ID_1050__Алексей Чихарев": 1, "ООО \"АВТОГРАД-Н\"": 1, "ООО \"АВТОГРАД-Н": 1, "Автоград": 1,
    // 21. Важная Персона Тверь (10)
    "1258": 10, "ID_1258": 10, "ID_1258__Алексей Чихарев": 10, "Важная персона": 10, "Важная Персона Тверь": 10,
    // 22. ООО "ПАРУС" online (2)
    "1117": 2, "ID_1117": 2, "ID_1117__Алексей Чихарев": 2, "ООО \"ПАРУС\"": 2, "ООО \"ПАРУС": 2, "ООО \"ПАРУС\" online": 2,
    // 23. Радар (15)
    "1041": 15, "ID_1041": 15, "ID_1041__Алексей Чихарев": 15, "Радар-Авто": 15, "Радар": 15, "Радар-Запад": 15,
    // 24. Анкар (1)
    "1090": 1, "ID_1090": 1, "ID_1090__Алексей Чихарев": 1, "Анкар Калуга": 1, "Анкар": 1,
    // 25. Гранд Техцентр Владимир JETOUR (Млада Авто) (25)
    "1124": 25, "ID_1124": 25, "ID_1124__Алексей Чихарев": 25, "ООО \"МЛАДА - АВТО\"": 25, "ООО \"МЛАДА - АВТО": 25, "Млада Авто": 25, "Гранд Техцентр Владимир JETOUR (Млада Авто)": 25,
    // 26. Автоцентр Лада (2)
    "1126": 2, "ID_1126": 2, "ID_1126__Алексей Чихарев": 2, "ООО \"Центр Лада\"": 2, "ООО \"Центр Лада": 2, "Автоцентр Лада": 2,
    // 27. Авто Премиум (Союз Т) (10)
    "1040": 10, "ID_1040": 10, "ID_1040__Алексей Чихарев": 10, "Авто Премиум Тверь": 10, "Авто Премиум (Союз Т)": 10, "СОЮЗ-Т": 10,
    // 28. Звезда Ярославии (8)
    "1046": 8, "ID_1046": 8, "ID_1046__Алексей Чихарев": 8, "ЗВЕЗДА ЯРОСЛАВИИ": 8, "Звезда Ярославии": 8,
    // 29. Автоимпорт (5)
    "1087": 5, "ID_1087": 5, "ID_1087__Алексей Чихарев": 5, "ГК Автоимпорт": 5, "Автоимпорт": 5,
    // 30. Диалог (76)
    "1082": 76, "ID_1082": 76, "ID_1082__Алексей Чихарев": 76, "ГК Диалог Авто": 76, "Диалог": 76, "Диалог Авто": 76,
    // 31. КАН АВТО (10)
    "1201": 10, "ID_1201": 10, "ID_1201__Алексей Чихарев": 10, "Приоритет_ГК КАН Авто": 10, "КАН АВТО": 10, "КАН Авто": 10,
    // 32. БАРС АВТО (23)
    "1233": 23, "ID_1233": 23, "ID_1233__Алексей Чихарев": 23, "Барс Авто": 23, "БАРС АВТО": 23,
    // 33. Апельсин (20)
    "1054": 20, "ID_1054": 20, "ID_1054__Алексей Чихарев": 20, "Апельсин-Челны": 20, "Апельсин": 20
};

// Official September 2026 Sales Plans for Svetlana Darienko (24 partners, Sum = 329)
const DARIENKO_OFFICIAL_PLANS = {
    // 1. Вагнер Авто / Авторитэйл (12)
    "1285": 12, "ID_1285": 12, "ID_1285__Светлана Дариенко": 12, "Вагнер Авто / Авторитэйл": 12, "Вагнер Авто": 12, "Авторитэйл": 12, "Вагнер Авто / Авторитэйл Online": 12,
    // 2. Аларм -Моторс (36)
    "1002": 36, "ID_1002": 36, "ID_1002__Светлана Дариенко": 36, "Аларм-Моторс ГК": 36, "Аларм -Моторс": 36, "Аларм-Моторс": 36,
    // 3. Авто Премиум (7)
    "632032": 7, "ID_632032": 7, "ID_632032__Светлана Дариенко": 7, "Премиум Авто ONLINE": 7, "Авто Премиум": 7, "Премиум Авто": 7,
    // 4. Восток Авто Жуково (20)
    "1005": 20, "ID_1005": 20, "ID_1005__Светлана Дариенко": 20, "Восток Авто": 20, "Восток Авто Жуково": 20,
    // 5. Максимум (41)
    "1163": 41, "ID_1163": 41, "ID_1163__Светлана Дариенко": 41, "Автохолдинг Максимум": 41, "Максимум": 41,
    // 6. Автопортрет (Нева Авто) (16)
    "1083": 16, "ID_1083": 16, "ID_1083__Светлана Дариенко": 16, "ООО \"НЕВААВТО": 16, "ООО \"НЕВААВТО\"": 16, "Автопортрет (Нева Авто)": 16, "Автопортрет": 16,
    // 7. Автопродикс (56)
    "1017": 56, "ID_1017": 56, "ID_1017__Светлана Дариенко": 56, "Автопродикс": 56, "ГК Автопродикс": 56,
    // 8. Автополе (Н) (37)
    "1063": 37, "ID_1063": 37, "ID_1063__Светлана Дариенко": 37, "Автополе": 37, "Автополе (Н)": 37,
    // 9. Иат (11)
    "1192": 11, "ID_1192": 11, "ID_1192__Светлана Дариенко": 11, "ИАТ": 11, "Иат": 11,
    // 10. ООО "СИГМА АВТО" (9)
    "1011": 9, "ID_1011": 9, "ID_1011__Светлана Дариенко": 9, "ГК Сигма": 9, "ООО \"СИГМА АВТО\"": 9, "Сигма": 9,
    // 11. Моторленд / Сократ СПб (8)
    "1280": 8, "ID_1280": 8, "ID_1280__Светлана Дариенко": 8, "Сократ (Моторленд СПб)": 8, "Моторленд": 8, "Сократ": 8,
    // 12. Форсаж (11)
    "1032": 11, "ID_1032": 11, "ID_1032__Светлана Дариенко": 11, "ГК Форсаж": 11, "Форсаж": 11,
    // 13. Автостиль (4)
    "1001": 4, "ID_1001": 4, "ID_1001__Светлана Дариенко": 4, "Автостиль СПб и Великий Новгород": 4, "Автостиль": 4,
    // 14. Р-Моторс НВСБРСК пилот ФДЦ... (7)
    "1025": 7, "ID_1025": 7, "ID_1025__Светлана Дариенко": 7, "Р-Моторс ЛАДА": 7, "Р-Моторс": 7,
    // 15. Прагматика (8)
    "1022": 8, "ID_1022": 8, "ID_1022__Светлана Дариенко": 8, "Прагматика": 8,
    // 16. Элан-Моторс (1)
    "1021": 1, "ID_1021": 1, "ID_1021__Светлана Дариенко": 1, "Элан Моторс (Санкт Петербург)": 1, "Элан-Моторс": 1,
    // 17. Автотим Псков (3)
    "1254": 3, "ID_1254": 3, "ID_1254__Светлана Дариенко": 3, "Автотим": 3, "Автотим Псков": 3,
    // 18. Элке Авто (9)
    "1219": 9, "ID_1219": 9, "ID_1219__Светлана Дариенко": 9, "Элке Авто": 9,
    // 19. Рус-Авто Трейд (1)
    "1242": 1, "ID_1242": 1, "ID_1242__Светлана Дариенко": 1, "Рус-Авто Трейд": 1,
    // 20. Динамика (14)
    "1031": 14, "ID_1031": 14, "ID_1031__Светлана Дариенко": 14, "ГК ДИНАМИКА": 14, "Динамика": 14,
    // 21. Ай-Би Эм (1)
    "1027": 1, "ID_1027": 1, "ID_1027__Светлана Дариенко": 1, "Ай-Би-Эм": 1, "Ай-Би Эм": 1,
    // 22. Картель (9)
    "1245": 9, "ID_1245": 9, "ID_1245__Светлана Дариенко": 9, "Картель": 9, "Картель (Картель и Картель Авто, СВ - Авто)": 9,
    // 23. АлексМоторс (1)
    "1257": 1, "ID_1257": 1, "ID_1257__Светлана Дариенко": 1, "АлексМоторс": 1,
    // 24. Сармат (7)
    "1068": 7, "ID_1068": 7, "ID_1068__Светлана Дариенко": 7, "Сармат": 7,
    // Zero out old non-planned partners under Darienko
    "ID_1036__Светлана Дариенко": 0, "1036": 0,
    "ID_1064__Светлана Дариенко": 0, "1064": 0,
    "ID_1138__Светлана Дариенко": 0, "1138": 0
};

// Default fallback plans if localStorage is empty
const DEFAULT_KAM_PLANS = {
    kam_plans: {
        "all": 1718,
        "Алексей Чихарев": 550,
        "Андрей Кузнецов": 471,
        "Светлана Дариенко": 329,
        "Валерия Солдатова": 282,
        "Евгения Добролюбова": 210,
        "Не назначен": 0
    },
    partner_plans: Object.assign({
        "	ФДЦ АВТОЦЕНТР НА ЗАВОДСКОМ Самара": 5,
        "1003": 5,
        "1004": 10,
        "1006": 5,
        "1007": 8,
        "1009": 24,
        "1010": 8,
        "1013": 23,
        "1014": 28,
        "1016": 4,
        "1018": 2,
        "1019": 10,
        "1034": 1,
        "1035": 1,
        "1036": 1,
        "1038": 18,
        "1039": 25,
        "1043": 105,
        "1047": 2,
        "1048": 25,
        "1049": 92,
        "1053": 5,
        "1055": 5,
        "1056": 10,
        "1057": 1,
        "1058": 1,
        "1060": 2,
        "1061": 12,
        "1062": 1,
        "1064": 5,
        "1065": 1,
        "1071": 3,
        "1072": 3,
        "1073": 2,
        "1077": 3,
        "1079": 1,
        "1081": 3,
        "1084": 68,
        "1086": 8,
        "1088": 7,
        "1092": 1,
        "1093": 1,
        "1098": 155,
        "1100": 1,
        "1107": 15,
        "1110": 1,
        "1112": 15,
        "1115": 1,
        "1119": 5,
        "1122": 10,
        "1123": 1,
        "1125": 15,
        "1128": 10,
        "1134": 6,
        "1137": 1,
        "1138": 3,
        "1177": 8,
        "1186": 8,
        "1225": 9,
        "1228": 17,
        "1290": 8,
        "1291": 1,
        "1232": 2,
        "1237": 2,
        "1243": 10,
        "1244": 26,
        "1246": 3,
        "1248": 7,
        "1253": 8,
        "1259": 3,
        "1260": 3,
        "1265": 5,
        "1266": 2,
        "1281": 10,
        "1285": 25,
        "CHERY Автолюкс": 1,
        "CHERY ВИП АВТО": 2,
        "CHERY ТВС Моторс": 1,
        "CHERY Экскурс Пермь": 2,
        "CHERY/TENET Нижегородец": 3,
        "ID_1003": 5,
        "ID_1003__Валерия Солдатова": 5,
        "ID_1004": 10,
        "ID_1004__Валерия Солдатова": 10,
        "ID_1006": 5,
        "ID_1006__Валерия Солдатова": 5,
        "ID_1007": 8,
        "ID_1007__Валерия Солдатова": 8,
        "1030": 8,
        "ID_1030": 8,
        "ID_1030__Валерия Солдатова": 8,
        "ГК Оптима": 8,
        "ID_1009": 24,
        "ID_1009__Валерия Солдатова": 24,
        "ID_1010": 8,
        "ID_1010__Валерия Солдатова": 8,
        "ID_1013": 23,
        "ID_1013__Валерия Солдатова": 23,
        "ГК Глобус": 23,
        "ID_1014": 28,
        "ID_1014__Валерия Солдатова": 28,
        "ID_1016": 4,
        "ID_1016__Валерия Солдатова": 4,
        "ID_1016__Евгения Добролюбова": 4,
        "Леон Авто (Йошкар-Ола)": 4,
        "ID_1025__Светлана Дариенко": 7,
        "ID_1018": 2,
        "ID_1018__Валерия Солдатова": 1,
        "ID_1018__Евгения Добролюбова": 2,
        "ID_1019": 10,
        "ID_1019__Валерия Солдатова": 10,
        "ID_1034": 1,
        "ID_1034__Валерия Солдатова": 1,
        "ID_1035": 1,
        "ID_1035__Светлана Дариенко": 0,
        "ID_1035__Евгения Добролюбова": 1,
        "Эксперт Авто (Новосибирск)": 1,
        "ID_1036": 1,
        "ID_1036__Евгения Добролюбова": 1,
        "ID_1038": 18,
        "ID_1038__Валерия Солдатова": 18,
        "ID_1039": 25,
        "ID_1039__Андрей Кузнецов": 25,
        "ID_1043": 105,
        "ID_1043__Андрей Кузнецов": 105,
        "ID_1047": 2,
        "ID_1047__Евгения Добролюбова": 2,
        "ID_1048": 25,
        "ID_1048__Валерия Солдатова": 25,
        "ID_1049": 92,
        "ID_1049__Андрей Кузнецов": 92,
        "ID_1053": 5,
        "ID_1053__Евгения Добролюбова": 5,
        "ID_1055": 5,
        "ID_1055__Евгения Добролюбова": 5,
        "ID_1056": 10,
        "ID_1056__Евгения Добролюбова": 10,
        "ID_1057": 1,
        "ID_1057__Евгения Добролюбова": 1,
        "ID_1058": 1,
        "ID_1058__Евгения Добролюбова": 1,
        "ID_1060": 2,
        "ID_1060__Евгения Добролюбова": 2,
        "ID_1061": 12,
        "ID_1061__Валерия Солдатова": 12,
        "ID_1062": 1,
        "ID_1062__Валерия Солдатова": 1,
        "ID_1064": 5,
        "ID_1064__Евгения Добролюбова": 5,
        "ID_1065": 1,
        "ID_1065__Валерия Солдатова": 1,
        "ID_1071": 3,
        "ID_1071__Евгения Добролюбова": 3,
        "ID_1072": 3,
        "ID_1072__Евгения Добролюбова": 3,
        "ID_1073": 2,
        "ID_1073__Евгения Добролюбова": 2,
        "ID_1077": 3,
        "ID_1077__Евгения Добролюбова": 3,
        "ID_1079": 1,
        "ID_1079__Евгения Добролюбова": 1,
        "ID_1081": 3,
        "ID_1081__Евгения Добролюбова": 3,
        "ID_1084": 68,
        "ID_1084__Андрей Кузнецов": 68,
        "ID_1086": 8,
        "ID_1086__Евгения Добролюбова": 8,
        "ID_1088": 7,
        "ID_1088__Евгения Добролюбова": 7,
        "ID_1092": 1,
        "ID_1092__Евгения Добролюбова": 1,
        "ID_1093": 1,
        "ID_1093__Евгения Добролюбова": 1,
        "ID_1098": 155,
        "ID_1098__Андрей Кузнецов": 155,
        "ID_1100": 1,
        "ID_1100__Евгения Добролюбова": 1,
        "ID_1107": 15,
        "ID_1107__Евгения Добролюбова": 15,
        "ID_1110": 1,
        "ID_1110__Евгения Добролюбова": 1,
        "ID_1112": 15,
        "ID_1112__Евгения Добролюбова": 15,
        "ID_1115": 1,
        "ID_1115__Валерия Солдатова": 1,
        "ID_1119": 5,
        "ID_1119__Валерия Солдатова": 5,
        "ID_1122": 10,
        "ID_1122__Евгения Добролюбова": 10,
        "ID_1123": 1,
        "ID_1123__Евгения Добролюбова": 1,
        "ID_1125": 15,
        "ID_1125__Евгения Добролюбова": 15,
        "ID_1128": 10,
        "ID_1128__Евгения Добролюбова": 10,
        "ID_1134": 6,
        "ID_1134__Евгения Добролюбова": 6,
        "ID_1137": 1,
        "ID_1137__Евгения Добролюбова": 1,
        "ID_1138": 3,
        "ID_1138__Валерия Солдатова": 3,
        "ID_1177": 8,
        "ID_1177__Валерия Солдатова": 8,
        "ID_1186": 8,
        "ID_1186__Валерия Солдатова": 8,
        "ID_1225": 9,
        "ID_1225__Валерия Солдатова": 9,
        "ID_1228": 17,
        "ID_1228__Валерия Солдатова": 17,
        "ID_1290": 8,
        "ID_1290__Валерия Солдатова": 8,
        "ID_1291": 1,
        "ID_1291__Валерия Солдатова": 1,
        "ID_1232": 2,
        "ID_1232__Евгения Добролюбова": 2,
        "ID_1237": 2,
        "ID_1237__Евгения Добролюбова": 2,
        "ID_1243": 10,
        "ID_1243__Евгения Добролюбова": 10,
        "ID_1244": 26,
        "ID_1244__Андрей Кузнецов": 26,
        "ID_1246": 3,
        "ID_1246__Валерия Солдатова": 3,
        "ID_1248": 7,
        "ID_1248__Евгения Добролюбова": 7,
        "ID_1253": 8,
        "ID_1253__Евгения Добролюбова": 8,
        "ID_1259": 3,
        "ID_1259__Евгения Добролюбова": 3,
        "ID_1260": 3,
        "ID_1260__Евгения Добролюбова": 3,
        "ID_1265": 5,
        "ID_1265__Евгения Добролюбова": 5,
        "ID_1266": 2,
        "ID_1266__Евгения Добролюбова": 2,
        "ID_1281": 10,
        "ID_1281__Евгения Добролюбова": 10,
        "ID_1285": 25,
        "ID_1285__Валерия Солдатова": 25,
        "ID_P_OEM_36ccbd70": 2,
        "ID_P_OEM_36ccbd70__Валерия Солдатова": 2,
        "ID_P_OEM_8b5da652": 3,
        "ID_P_OEM_8b5da652__Евгения Добролюбова": 3,
        "ID_P_OEM_8dfa757a": 2,
        "ID_P_OEM_8dfa757a__Валерия Солдатова": 2,
        "ID_P_OEM_a34f7047": 10,
        "ID_P_OEM_a34f7047__Евгения Добролюбова": 10,
        "ID_P_OEM_d33020ac": 3,
        "ID_P_OEM_d33020ac__Евгения Добролюбова": 3,
        "ID_P_OEM_f6c70f64": 5,
        "ID_P_OEM_f6c70f64__Валерия Солдатова": 5,
        "JETOUR АвтоПремьер Зубово": 3,
        "JETOUR Мотом": 3,
        "O&J ОПТИМА КУБАНЬ": 8,
        "ONLINE АМК (ООО \"АМ Компани\")": 5,
        "P_OEM_36ccbd70": 2,
        "P_OEM_8b5da652": 3,
        "P_OEM_8dfa757a": 2,
        "P_OEM_a34f7047": 10,
        "P_OEM_d33020ac": 3,
        "P_OEM_f6c70f64": 5,
        "Fresh Auto": 25,
        "fresh auto": 25,
        "Фреш Авто": 25,
        "Verra": 5,
        "ААА Моторс": 1,
        "АМР": 10,
        "АвтоГермес": 155,
        "автогермес": 155,
        "Авто-Ревю": 5,
        "АвтоМаркет Jetour": 15,
        "АвтоЮг": 17,
        "Автобан": 10,
        "Автогарантия Тенет Планета": 1,
        "Автодель": 3,
        "Автолидер": 2,
        "Автолидер ГАК": 2,
        "Автолюкс": 1,
        "Автомаг": 1,
        "Автомаркет": 15,
        "Автомир": 12,
        "Автомир (Симферополь) Jetour": 12,
        "Авторитэйл": 25,
        "Автосеть УФА Форвард": 1,
        "Автофорум Саратов": 6,
        "Автохолдинг": 3,
        "Автохолдинг Тургеневский": 3,
        "Автоцентр на Заводском": 5,
        "Аллер-Авто": 2,
        "АллерАвто": 2,
        "Арконт": 15,
        "Артан": 8,
        "Артекс": 1,
        "Бакра": 9,
        "Башавтоком": 3,
        "Брянскзапчасть": 2,
        "ВИП АВТО Тенет": 2,
        "ГК АГАТ": 92,
        "гк агат": 92,
        "АГАТ": 92,
        "ГК Автобан Джетур": 10,
        "ГК Автомир": 105,
        "гк автомир": 105,
        "ГК Авторитэйл М": 25,
        "ГК КОРС Джетур": 26,
        "гк корс джетур": 26,
        "КОРС Джетур": 26,
        "ГК Арконт Холдинг": 15,
        "ГК Артан": 8,
        "ГК Сильвер": 7,
        "ГК Сильвер Джетур": 7,
        "Гак Верра": 5,
        "Глазурит": 15,
        "Глобус": 23,
        "Глобус Автосфера": 23,
        "Дав Авто": 7,
        "Дав-Авто": 7,
        "Дактор": 2,
        "Дактор Уфа": 2,
        "Дебрянск Авто": 8,
        "Дебрянск Авто (Дебрянск Авто)": 8,
        "ЗАО \"АВТОХОЛДИНГ\" LUCKY MOTORS ONLINE": 5,
        "Интерпарнер": 1,
        "Интерпартнер": 1,
        "Колесо": 1,
        "Колесо Астрахань": 1,
        "Комос": 2,
        "Комос-Авто": 2,
        "Кондр Плюс": 1,
        "Курган Лдетур Оками": 10,
        "ЛЕОН-АВТО (ООО \"ДМ-АВТО\" СЕВЕР\")": 4,
        "Лаки Моторс": 5,
        "Леон": 4,
        "Липецк Лада": 1,
        "Липецк-Лада": 1,
        "МС Моторс Зубово": 3,
        "МТМ (Мотом)": 3,
        "Мерит": 1,
        "Мерит (Куйбышев)": 1,
        "Мир Авто Юг": 5,
        "Моторленд": 28,
        "Моторленд (Воронеж)": 28,
        "НИЖЕГОРОДЕЦ Тенет": 3,
        "Никко": 3,
        "ООО \"АВТО СИТИ": 7,
        "ООО \"АВТОФОРУМ": 6,
        "ООО \"АМР": 10,
        "ООО \"ГЛАЗУРИТ": 15,
        "ООО \"КМ-АВТО САРАНСК-2": 5,
        "ООО \"КОНДОР-ПЛЮС": 1,
        "ООО \"ТАМБОВ-АВТО": 1,
        "ООО \"ТД АРМАДА-АВТО": 10,
        "ООО Автосеть Уфа": 1,
        "Оками": 10,
        "Олимп": 3,
        "Олимп Авто": 3,
        "Оптима": 8,
        "Оса Холдинг": 1,
        "Планета Авто": 5,
        "РВ Сервис": 10,
        "РОЛЬФ": 68,
        "рольф": 68,
        "Рольф": 68,
        "Ринг": 18,
        "Ринг Авто": 18,
        "СаранскАвто": 5,
        "Сатурн-2": 3,
        "Сатурн-Р": 1,
        "Сатурн-Р Авто": 1,
        "ТВС ТЕНЕТ": 1,
        "ТД Армада авто": 10,
        "ТСАЦ Июль": 10,
        "ТамбовАвто": 1,
        "Темп Авто": 24,
        "Техно-Темп": 10,
        "Трансфор": 5,
        "Тсац Июль": 10,
        "ФДЦ Авто-Ревю": 5,
        "ФДЦ ОСА-Холдинг г. Бузулук Оренбургская обл.": 1,
        "ФДЦ Техно-Темп": 10,
        "ФДЦ Трансфор": 5,
        "Фининвест": 25,
        "Форвард  Ижевск/Сызрань": 2,
        "Форвард Авто (АО Сызранская СТО олимп)": 2,
        "Центральное СТО": 2,
        "Центральное СТО 50 лет Октября": 2,
        "ЧЕРИ ЦЕНТР ПЛАНЕТА АВТО ВОСТОК": 1,
        "Экскурс Пермь Тенет": 2,
        "Эксперт Авто": 10,
        "Эксперт Авто (Самара)": 10,
        "Эксперт Альфа": 3,
        "Эксперт Альфа Джетур": 3,
        "ЮНИКОР": 8,
        "ЮНИКОР Дзержинск НН": 8,
        "Юг-Авто": 8,
        "пилот ФДЦ Автосеть РФ АМК Самара Тольятти ЕКБ": 5
    }, CHIKHAREV_OFFICIAL_PLANS, DARIENKO_OFFICIAL_PLANS)
};

const STORAGE_KEY_KAM_PLANS = 'sberauto_kam_plans';

/**
 * Normalizes KAM name to standard display format.
 */
function normalizeKamName(name) {
    if (!name || name === 'Не назначен' || name === '—' || name === 'null' || name === 'undefined') return 'Не назначен';
    let n = String(name).trim().toLowerCase();
    if (n.includes('чихарев')) return 'Алексей Чихарев';
    if (n.includes('кузнецов')) return 'Андрей Кузнецов';
    if (n.includes('дариенко')) return 'Светлана Дариенко';
    if (n.includes('солдатова')) return 'Валерия Солдатова';
    if (n.includes('добролюбова')) return 'Евгения Добролюбова';
    return name.trim();
}

/**
 * Normalizes brand name to match OEM standards.
 */
function normalizeBrandName(b, selectedMonth = window.selectedKamMonth || '') {
    if (!b) return 'Другие';
    let ub = String(b).toUpperCase().trim();
    const aux = ["ВНЕСЕНИЕ", "АВАНС", "КРЕДИТ", "КАСКО", "ОСАГО", "ГАП", "СТРАХОВ", "СЕРТИФИКАТ", "ДОП", "СЕРВИС", "ФИНАНС", "ДОГОВОР", "ОФОРМЛЕН", "КОМИСС", "УСЛУГ", "НЕИЗВЕСТН", "ДРУГИЕ", "NULL", "UNDEFINED"];
    if (aux.some(k => ub.includes(k))) return 'Другие';
    if (ub.includes('JETOUR')) return 'JETOUR';
    if (ub.includes('LADA') || ub.includes('ЛАДА')) return 'LADA';
    if (ub.includes('HAVAL') || ub.includes('ХАВЕЙЛ')) return 'HAVAL';
    if (ub.includes('CHANGAN') || ub.includes('ЧАНГАН')) return 'CHANGAN';
    if (ub.includes('KNEWSTAR') || ub.includes('КНЬЮСТАР') || ub.includes('КНЮСТАР')) return 'Knewstar';
    if (ub.includes('BELGEE') || ub.includes('БЕЛДЖИ') || ub.includes('ВЕELGEE')) return 'Belgee';
    if (ub.includes('GEELY') || ub.includes('ДЖИЛИ')) return 'Geely';
    if (ub.includes('G B K') || ub.includes('GBK')) return 'Geely & Belgee';
    if (ub.includes('CHERY') || ub.includes('TENET') || ub.includes('ТENET') || ub.includes('ТЕНЕТ') || ub.includes('ЧЕРИ')) return 'CHERY & TENET';
    if (ub.includes('SOLARIS') || ub.includes('SОLARIS') || ub.includes('СОЛЯРИС')) return 'SOLARIS';
    if (ub.includes('SOUEAST') || ub.includes('SOUEAS') || ub.includes('СОУИСТ')) return 'SOUEAST';
    if (ub.includes('GAC')) return 'GAC';
    if (ub.includes('МОСКВИЧ')) return 'МОСКВИЧ';
    if (ub.includes('JELAND') || ub.includes('ДЖЕЙЛЕНД')) return 'JELAND';
    if (ub.includes('OMODA') || ub.includes('JAECOO')) {
        let m = selectedMonth.replace("'", "");
        if (m >= '2026-09') return 'JELAND';
        return 'OMODA & JAECOO';
    }
    if (ub.includes('HONGQI')) return 'HONGQI';
    if (ub.includes('XCITE')) return 'XCITE';
    if (ub.includes('KIA') || ub.includes('КИА')) return 'KIA';
    if (ub.includes('HYUNDAI') || ub.includes('ХЕНДЭ')) return 'HYUNDAI';
    if (ub.includes('TOYOTA') || ub.includes('ТОЙОТА')) return 'TOYOTA';
    if (ub.includes('TANK') || ub.includes('ТАНК')) return 'TANK';
    if (ub.includes('EXEED') || ub.includes('ЭКСИД')) return 'EXEED';
    let res = String(b).trim();
    return res ? res : 'Другие';
}

const CLOUD_PLANS_API = '/api/kam-plans';
let kamAuthenticatedUser = null;
let isSyncingPlansWithCloud = false;
let planSaveDebounceTimer = null;

/* ====================================================================
 * KAM ROLE-BASED ACCESS & ACCOUNT AUTHENTICATION
 * Ensures employees can only edit plans for their own account / partners,
 * while Administrators (Руководитель) have unrestricted access.
 * ====================================================================*/
const KAM_AUTH_STORAGE_KEY = 'sberauto_kam_active_account';

const KAM_AUTH_ACCOUNTS = {
    'admin': {
        id: 'admin',
        name: 'Руководитель',
        role: 'Руководитель / Администратор',
        isAdmin: true,
        displayName: 'Руководитель (Все права)'
    },
    'chikharev': {
        id: 'chikharev',
        name: 'Алексей Чихарев',
        role: 'Ведущий КАМ',
        isAdmin: false,
        displayName: 'Алексей Чихарев'
    },
    'kuznetsov': {
        id: 'kuznetsov',
        name: 'Андрей Кузнецов',
        role: 'Ведущий КАМ',
        isAdmin: false,
        displayName: 'Андрей Кузнецов'
    },
    'darienko': {
        id: 'darienko',
        name: 'Светлана Дариенко',
        role: 'КАМ (СЗФО / Сибирь)',
        isAdmin: false,
        displayName: 'Светлана Дариенко'
    },
    'soldatova': {
        id: 'soldatova',
        name: 'Валерия Солдатова',
        role: 'КАМ (Юг / Черноземье)',
        isAdmin: false,
        displayName: 'Валерия Солдатова'
    },
    'dobrolyubova': {
        id: 'dobrolyubova',
        name: 'Евгения Добролюбова',
        role: 'КАМ (Регионы / Урал)',
        isAdmin: false,
        displayName: 'Евгения Добролюбова'
    }
};

function getKamActiveUser() { return kamAuthenticatedUser; }

async function refreshKamSession() {
    try {
        const response = await fetch('/api/session', {credentials: 'same-origin', cache: 'no-store'});
        kamAuthenticatedUser = response.ok ? (await response.json()).user : null;
    } catch (_) { kamAuthenticatedUser = null; }
    renderKamAuthWidget();
}

async function kamAuthRequest(path, body = {}) {
    const response = await fetch(path, {method: 'POST', credentials: 'same-origin',
        headers: {'Content-Type':'application/json', 'X-Dashboard-Request':'1'}, body: JSON.stringify(body)});
    const result = await response.json();
    if (!response.ok) throw new Error(result.error || 'Не удалось выполнить запрос');
    return result;
}

function canUserEditOverallPlan(kamName) {
    const user = getKamActiveUser();
    if (!user) return false;
    if (user.isAdmin) return true;
    if (!kamName || kamName === 'all') return false; // Общий план сети меняет только Администратор/Руководитель
    return normalizeKamName(kamName) === normalizeKamName(user.name);
}

function canUserEditPartnerPlan(partnerKam) {
    const user = getKamActiveUser();
    if (!user) return false;
    if (user.isAdmin) return true;
    if (!partnerKam || partnerKam === '—' || partnerKam === 'Не назначен') return false;
    return normalizeKamName(partnerKam) === normalizeKamName(user.name);
}

function renderKamAuthWidget() {
    const cont = document.getElementById('kamAuthWidgetContainer');
    if (!cont) return;
    const user = getKamActiveUser();
    if (user) {
        cont.innerHTML = `
            <div class="flex items-center gap-2 bg-emerald-50 border border-emerald-300 px-3 py-1.5 rounded-xl shadow-xs">
                <span class="w-2.5 h-2.5 rounded-full bg-emerald-500 animate-pulse"></span>
                <div class="flex flex-col text-left">
                    <span class="text-xs font-black text-emerald-950 flex items-center gap-1">
                        ${user.isAdmin ? '👑' : '👤'} ${escapeHtml(user.name)}
                    </span>
                    <span class="text-[10px] text-emerald-700 font-semibold leading-none">${escapeHtml(user.role)}</span>
                </div>
                <button type="button" onclick="kamLogout()" class="ml-2 px-2 py-0.5 bg-white hover:bg-rose-50 text-rose-600 hover:text-rose-700 border border-rose-200 rounded-lg text-[10px] font-bold transition shadow-2xs cursor-pointer" title="Выйти из профиля">
                    Выйти
                </button>
            </div>
        `;
    } else {
        cont.innerHTML = `
            <button type="button" onclick="openKamLoginModal()" class="flex items-center gap-1.5 px-3 py-1.5 bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-700 hover:to-indigo-700 text-white rounded-xl text-xs font-bold shadow-sm transition cursor-pointer">
                <span>🔐</span>
                <span>Войти в профиль КАМ</span>
            </button>
        `;
    }
}

function openKamLoginModal(preselectKamName = '') {
    const modal = document.getElementById('kamLoginModal');
    if (!modal) return;
    const select = document.getElementById('kamLoginSelect');
    const pinInput = document.getElementById('kamLoginPin');
    const errEl = document.getElementById('kamLoginError');
    if (errEl) errEl.classList.add('hidden');
    if (pinInput) pinInput.value = '';

    if (select && preselectKamName) {
        if (preselectKamName === 'admin' || preselectKamName === 'all') {
            select.value = 'admin';
        } else {
            const norm = normalizeKamName(preselectKamName);
            for (const [id, acc] of Object.entries(KAM_AUTH_ACCOUNTS)) {
                if (normalizeKamName(acc.name) === norm) {
                    select.value = id;
                    break;
                }
            }
        }
    }
    modal.classList.remove('hidden');
    if (pinInput) setTimeout(() => pinInput.focus(), 100);
}

function closeKamLoginModal() {
    const modal = document.getElementById('kamLoginModal');
    if (modal) modal.classList.add('hidden');
}

function onKamLoginAccountSelect(accId) {
    const pinInput = document.getElementById('kamLoginPin');
    const errEl = document.getElementById('kamLoginError');
    if (errEl) errEl.classList.add('hidden');
    if (pinInput) {
        pinInput.value = '';
        pinInput.focus();
    }
}

async function handleKamLoginSubmit(e) {
    if (e && e.preventDefault) e.preventDefault();
    const select = document.getElementById('kamLoginSelect');
    const pinInput = document.getElementById('kamLoginPin');
    const errEl = document.getElementById('kamLoginError');
    if (!select || !pinInput) return;
    try {
        const result = await kamAuthRequest('/api/login', {id:select.value,password:pinInput.value});
        kamAuthenticatedUser = result.user;
        pinInput.value = '';
        closeKamLoginModal();
        await syncKamPlansFromCloud();
        if (!result.user.isAdmin && typeof setKamManagerFilter === 'function') setKamManagerFilter(result.user.name);
        else renderKamTab(currentFilterConfig);
    } catch(error) {
        if(errEl) {errEl.textContent = error.message;errEl.classList.remove('hidden');}
    }
}

async function kamLogout() {
    try { await kamAuthRequest('/api/logout'); }
    catch (_) { if(typeof showToast==='function')showToast('Не удалось завершить сеанс на сервере. Повторите выход.', 'warning');return; }
    kamAuthenticatedUser = null;
    renderKamTab(currentFilterConfig);
}
if (typeof window !== 'undefined') setTimeout(refreshKamSession, 100);
function getPartnerPlanCellHtml(p) {
    const partnerKam = p.kam || '';
    const canEdit = canUserEditPartnerPlan(partnerKam);
    const user = getKamActiveUser();

    if (canEdit) {
        return `
            <input type="number" min="0" step="1"
                value="${p.plan || ''}"
                placeholder="—"
                class="w-16 text-center text-xs font-bold text-blue-700 bg-gray-50 border border-gray-300 rounded px-1.5 py-0.5 outline-none focus:bg-white focus:border-blue-500 transition"
                onchange="onPartnerPlanChange(${escapeHtml(JSON.stringify(p.key))}, this.value, ${escapeHtml(JSON.stringify(partnerKam))})"
                onkeyup="if(event.key==='Enter') this.blur();"
                title="Введите план сделок для «${escapeHtml(p.name)}» (сохраняется автоматически)">
        `;
    } else {
        const lockHint = user
            ? `План закреплен за КАМом: ${partnerKam || 'Не назначен'}. Редактирование доступно только ему или Руководителю.`
            : `План закреплен за КАМом: ${partnerKam || 'Не назначен'}. Войдите в профиль для редактирования.`;
        return `
            <div class="flex items-center justify-center gap-1 cursor-pointer group" onclick="openKamLoginModal(${escapeHtml(JSON.stringify(partnerKam))})" title="${escapeHtml(lockHint)} (нажмите для входа)">
                <span class="text-xs font-bold ${p.plan > 0 ? 'text-gray-700' : 'text-gray-400'}">${p.plan > 0 ? p.plan : '—'}</span>
                <span class="text-[10px] text-gray-400 group-hover:text-blue-600 transition">🔒</span>
            </div>
        `;
    }
}

/**
 * Retrieves KAM plans from localStorage/sessionStorage or defaults.
 */
const PLANS_MIGRATION_VERSION = '2026-09-29-darienko-329-v1';

function getKamPlansStore() {
    try {
        let raw = localStorage.getItem(STORAGE_KEY_KAM_PLANS);
        if (!raw) {
            raw = sessionStorage.getItem(STORAGE_KEY_KAM_PLANS);
        }
        let store = null;
        if (raw) {
            const parsed = JSON.parse(raw);
            const mergedKam = Object.assign({}, DEFAULT_KAM_PLANS.kam_plans, parsed.kam_plans || {});
            const mergedPartners = Object.assign({}, DEFAULT_KAM_PLANS.partner_plans);
            if (parsed.partner_plans) {
                for (let k in parsed.partner_plans) {
                    const val = parsed.partner_plans[k];
                    // Keep positive customized plans; don't let empty/0 wipe out configured defaults
                    if (Number.isSafeInteger(val) && val >= 0) {
                        mergedPartners[k] = val;
                    }
                }
            }
            store = {
                kam_plans: mergedKam,
                partner_plans: mergedPartners
            };
        } else {
            store = JSON.parse(JSON.stringify(DEFAULT_KAM_PLANS));
        }

        // Auto-migrate authoritative September plans if not yet stamped
        try {
            if (typeof localStorage !== 'undefined' && localStorage.getItem(PLANS_MIGRATION_VERSION) !== 'applied') {
                Object.assign(store.partner_plans, CHIKHAREV_OFFICIAL_PLANS, DARIENKO_OFFICIAL_PLANS);
                store.kam_plans["Алексей Чихарев"] = 550;
                store.kam_plans["Светлана Дариенко"] = 329;
                localStorage.setItem(STORAGE_KEY_KAM_PLANS, JSON.stringify(store));
                localStorage.setItem(PLANS_MIGRATION_VERSION, 'applied');
            }
        } catch(e) {}

        return store;
    } catch (e) {
        console.warn('Error reading KAM plans from localStorage:', e);
    }
    return JSON.parse(JSON.stringify(DEFAULT_KAM_PLANS));
}

/**
 * Saves KAM plans store to both localStorage and sessionStorage, and auto-syncs to Cloudflare KV.
 */
let cloudPlanRevision = null;
let cloudPlanBaseline = null;
let pendingPlanChanges = {kam_plans:{}, partner_plans:{}};
let cloudPlanWriteInProgress = false;

function cacheKamPlans(store) {
    try { localStorage.setItem(STORAGE_KEY_KAM_PLANS, JSON.stringify(store)); } catch (_) {}
    try { sessionStorage.setItem(STORAGE_KEY_KAM_PLANS, JSON.stringify(store)); } catch (_) {}
}
function saveKamPlansStore(store, pushToCloud = true) {
    const previous = getKamPlansStore();
    cacheKamPlans(store);
    if (!pushToCloud) return;
    if (cloudPlanRevision === null || !getKamActiveUser()) {
        cacheKamPlans(previous);
        if(typeof showToast==='function')showToast('Изменение не сохранено: войдите в профиль и дождитесь загрузки планов.', 'warning');
        return;
    }
    for (const section of ['kam_plans','partner_plans']) {
        for (const [key,value] of Object.entries(store[section]||{})) {
            if(value!==previous[section]?.[key])pendingPlanChanges[section][key]=value;
        }
    }
    clearTimeout(planSaveDebounceTimer);
    planSaveDebounceTimer = setTimeout(flushKamPlanChanges, 500);
}
async function flushKamPlanChanges() {
    if(cloudPlanWriteInProgress)return;
    if(!Object.values(pendingPlanChanges).some(x=>Object.keys(x).length))return;
    cloudPlanWriteInProgress=true;
    const changes=pendingPlanChanges;pendingPlanChanges={kam_plans:{},partner_plans:{}};
    try {
        const response=await fetch(CLOUD_PLANS_API,{method:'POST',credentials:'same-origin',
            headers:{'Content-Type':'application/json','X-Dashboard-Request':'1'},
            body:JSON.stringify({revision:cloudPlanRevision,changes})});
        const result=await response.json();
        if(!response.ok)throw new Error(result.error||'Ошибка сохранения');
        cloudPlanRevision=result.revision;
        cloudPlanBaseline={kam_plans:result.kam_plans,partner_plans:result.partner_plans};
        if(typeof showToast==='function')showToast('Планы сохранены на сервере', 'success', 2000);
    } catch(error) {
        pendingPlanChanges={kam_plans:{},partner_plans:{}};
        if(cloudPlanBaseline)cacheKamPlans(cloudPlanBaseline);
        await syncKamPlansFromCloud(true);
        if(typeof showToast==='function')showToast('Изменения не сохранены: '+error.message,'error',6000);
    } finally {cloudPlanWriteInProgress=false;}
    if(Object.values(pendingPlanChanges).some(x=>Object.keys(x).length))await flushKamPlanChanges();
}
async function syncKamPlansFromCloud(force = false) {
    if(isSyncingPlansWithCloud || (!force && (cloudPlanWriteInProgress || Object.values(pendingPlanChanges).some(x=>Object.keys(x).length))))return;
    isSyncingPlansWithCloud=true;
    try {
        const response=await fetch(CLOUD_PLANS_API,{credentials:'same-origin',cache:'no-store'});
        if(!response.ok)throw new Error('Планы недоступны');
        const result=await response.json();
        if(!Number.isSafeInteger(result.revision))throw new Error('Обновите страницу для новой версии API');
        cloudPlanRevision=result.revision;
        cloudPlanBaseline={kam_plans:{...DEFAULT_KAM_PLANS.kam_plans,...result.kam_plans},partner_plans:{...DEFAULT_KAM_PLANS.partner_plans,...result.partner_plans}};
        cacheKamPlans(cloudPlanBaseline);
        const tab=document.getElementById('tab-kam');
        if(tab && !tab.classList.contains('hidden') && typeof renderKamTab==='function')renderKamTab(currentFilterConfig,true);
    } catch(_) {cloudPlanRevision=null;}
    finally {isSyncingPlansWithCloud=false;}
}
if (typeof window !== 'undefined') setTimeout(syncKamPlansFromCloud, 200);

/**
 * Updates overall plan for a KAM manager and auto-refreshes KPI/bars.
 */
function onKamOverallPlanChange(kamName, val) {
    if (!canUserEditOverallPlan(kamName)) {
        const displayName = kamName === 'all' ? 'Все КАМы (Сеть)' : kamName;
        if (typeof showToast === 'function') {
            showToast(`🔒 Редактирование плана «${displayName}» доступно только закрепленному сотруднику или Руководителю`, 'warning', 3500);
        }
        openKamLoginModal(kamName);
        const agg = getKamAggregatedData(currentFilterConfig);
        renderKamPlanHeader(agg.summary);
        return;
    }
    const num = Math.max(0, parseInt(val, 10) || 0);
    const store = getKamPlansStore();
    store.kam_plans[kamName] = num;
    saveKamPlansStore(store);

    // In-place refresh header KPI and progress bar without losing DOM focus
    const agg = getKamAggregatedData(currentFilterConfig);
    renderKamPlanHeader(agg.summary);

    if (typeof showToast === 'function') {
        showToast(`План для «${kamName === 'all' ? 'Все КАМы' : kamName}» ожидает сохранения: ${fmtNum(num)} сделок`, 'success', 2000);
    }
}

/**
 * Updates individual partner plan with multi-key redundancy and auto-refreshes row progress.
 */
function onPartnerPlanChange(partnerKey, val, partnerKam = '') {
    if (!canUserEditPartnerPlan(partnerKam)) {
        if (typeof showToast === 'function') {
            showToast(`🔒 Редактирование плана партнера доступно только КАМу (${partnerKam || '—'}) или Руководителю`, 'warning', 3500);
        }
        openKamLoginModal(partnerKam);
        renderKamTableOnly();
        return;
    }
    const num = Math.max(0, parseInt(val, 10) || 0);
    const store = getKamPlansStore();
    store.partner_plans[partnerKey] = num;

    const safeKey = partnerKey.replace(/[^a-zA-Z0-9_-]/g, '_');
    const row = document.querySelector(`tr[onclick*="${safeKey}"]`);
    saveKamPlansStore(store);

    // In-place DOM update for row % and plan badge
    if (row) {
        const planPctCell = row.querySelector('.kam-plan-pct') || row.querySelectorAll('td')[3];
        let totalDeals = 0;
        if (row.dataset && row.dataset.totalDeals !== undefined) {
            totalDeals = parseInt(row.dataset.totalDeals, 10) || 0;
        } else {
            const totalDealsEl = row.querySelector('.kam-total-deals');
            const totalDealsText = totalDealsEl ? totalDealsEl.textContent.trim() : (row.querySelectorAll('td')[10] ? row.querySelectorAll('td')[10].textContent.trim() : '0');
            totalDeals = parseInt(totalDealsText.replace(/\D/g, ''), 10) || 0;
        }
        if (planPctCell) {
            const pct = num > 0 ? (totalDeals / num * 100) : 0;
            let planBadge = 'text-gray-400';
            if (num > 0) {
                planBadge = pct >= 100 ? 'text-emerald-700 font-black' : (pct >= 70 ? 'text-blue-600 font-bold' : 'text-amber-600 font-bold');
            }
            planPctCell.className = `text-center ${planBadge} kam-plan-pct`;
            planPctCell.textContent = num > 0 ? `${pct.toFixed(0)}%` : '—';
        }
    }

    // Refresh summary in header
    const agg = getKamAggregatedData(currentFilterConfig);
    renderKamPlanHeader(agg.summary);

    if (typeof showToast === 'function') {
        showToast(`План партнера ожидает сохранения: ${fmtNum(num)} сделок`, 'success', 1500);
    }
}

/**
 * Exports all current plans to JSON string / clipboard.
 */
function exportKamPlansJson() {
    const store = getKamPlansStore();
    const str = JSON.stringify(store, null, 2);
    if (navigator.clipboard && navigator.clipboard.writeText) {
        navigator.clipboard.writeText(str).then(() => {
            if (typeof showToast === 'function') showToast('Планы скопированы в буфер обмена (JSON)!', 'success', 3000);
            else alert('Планы скопированы в буфер обмена!');
        }).catch(() => {
            prompt('Скопируйте конфигурацию планов (JSON):', str);
        });
    } else {
        prompt('Скопируйте конфигурацию планов (JSON):', str);
    }
}

/**
 * Imports plans from JSON string (Requires Supervisor/Admin role).
 */
function importKamPlansPrompt() {
    const user = getKamActiveUser();
    if (!user || !user.isAdmin) {
        if (typeof showToast === 'function') {
            showToast('🔒 Импорт планов из JSON доступен только Руководителю / Администратору', 'warning', 3500);
        } else {
            alert('Импорт планов доступен только Руководителю / Администратору.');
        }
        openKamLoginModal('admin');
        return;
    }
    const input = prompt('Вставьте JSON с планами КАМ и партнеров:');
    if (!input) return;
    try {
        const parsed = JSON.parse(input);
        if (parsed && (parsed.kam_plans || parsed.partner_plans)) {
            const current = getKamPlansStore();
            const updated = {
                kam_plans: Object.assign({}, current.kam_plans, parsed.kam_plans || {}),
                partner_plans: Object.assign({}, current.partner_plans, parsed.partner_plans || {})
            };
            saveKamPlansStore(updated);
            renderKamTab(currentFilterConfig);
            if (typeof showToast === 'function') showToast('Планы отправлены на сохранение', 'success', 3000);
            else alert('Планы успешно импортированы!');
        } else {
            alert('Некорректный формат JSON: отсутствуют kam_plans или partner_plans.');
        }
    } catch (e) {
        alert('Ошибка парсинга JSON: ' + e.message);
    }
}

/**
 * Filter change handler for KAM selection pill.
 */
function setKamManagerFilter(kamName) {
    currentKamFilter = kamName;

    // Update active state on selector pills
    document.querySelectorAll('.kam-select-pill').forEach(pill => {
        if (pill.dataset.kam === kamName) {
            pill.className = 'kam-select-pill px-3.5 py-1.5 rounded-xl text-xs font-bold transition shadow-sm bg-blue-600 text-white cursor-pointer border border-blue-600';
        } else {
            pill.className = 'kam-select-pill px-3.5 py-1.5 rounded-xl text-xs font-bold transition bg-white text-gray-700 hover:bg-gray-100 cursor-pointer border border-gray-200';
        }
    });

    renderKamTab(currentFilterConfig);
}

/**
 * Plan completion filter chip handler.
 */
function setKamPlanStatusFilter(status) {
    currentKamPlanFilter = status;
    document.querySelectorAll('.kam-plan-chip').forEach(chip => {
        if (chip.dataset.status === status) {
            chip.className = 'kam-plan-chip px-3 py-1 rounded-lg text-xs font-bold transition bg-slate-800 text-white cursor-pointer shadow-sm';
        } else {
            chip.className = 'kam-plan-chip px-3 py-1 rounded-lg text-xs font-bold transition bg-slate-100 text-slate-700 hover:bg-slate-200 cursor-pointer';
        }
    });
    renderKamTableOnly();
}

/**
 * Live search input in KAM tab.
 */
function onKamSearchInput(val) {
    currentKamSearchQuery = (val || '').toLowerCase().trim();
    renderKamTableOnly();
}

/**
 * Toggle hierarchy rows (cities and brands under partner).
 */
function toggleKamPartnerRows(pKey) {
    const rows = document.querySelectorAll(`.kam-subrow-${pKey}`);
    const arrow = document.getElementById(`kamArrow_${pKey}`);
    rows.forEach(r => {
        r.classList.toggle('hidden');
    });
    if (arrow) {
        arrow.classList.toggle('rotate-90');
    }
}

/**
 * Aggregates all KAM-related data given the global filter and current KAM filter.
 * CITIES AND BRANDS ARE DERIVED EXCLUSIVELY FROM OFFICIAL OEM DATA.
 */
function getKamAggregatedData(filterCfg) {
    const payload = window.dataPayload || {};
    const cfg = filterCfg || (typeof currentFilterConfig !== 'undefined' ? currentFilterConfig : { mode: 'all' });
    return calculateKamAggregation({
        ...payload,
        sys_db_partners: payload.sys_db_partners || (typeof dbPartners !== 'undefined' ? dbPartners : [])
    }, cfg, {
        kamFilter: currentKamFilter,
        plans: getKamPlansStore(),
        brandMonth: window.selectedKamMonth || '',
        today: new Date()
    });
}

/** Compute metrics from explicit inputs; storage and UI state stay in the adapter. */
function calculateKamAggregation(payload, cfg, options) {
    const rawDbPartners = payload.sys_db_partners || [];
    const registry = payload.partners_registry || [];
    const lgd = payload.lead_geo_dealers || {};
    const currentKamFilter = options.kamFilter;
    const normalizeBrand = brand => normalizeBrandName(brand, options.brandMonth);
    const activeMonth = (cfg.mode === 'month' && cfg.month) ? cfg.month : (cfg.mode === 'all' ? 'all' : '2026-08');
    const monthLgd = (lgd.by_month && (lgd.by_month[activeMonth] || (activeMonth === 'all' ? lgd.by_month['all'] : lgd.by_month['2026-08']))) || lgd;
    const lgdSummary = monthLgd.summary || lgd.summary || {
        total_clients: 23572,
        qual_clients: 8961,
        trans_clients: 1052,
        trans_qual_clients: 1052,
        deals_from_trans: 5545
    };

    const fPartners = rawDbPartners.filter(r => {
        if (!cfg || cfg.mode === 'all' || !cfg.mode) return true;
        if (cfg.mode === 'month') {
            if (!cfg.month || cfg.month === 'all') return true;
            return (r.Month || '').replace("'", "") === cfg.month;
        }
        if (cfg.mode === 'custom') {
            const fTime = cfg.from ? cfg.from.getTime() : -Infinity;
            const tTime = cfg.to ? cfg.to.getTime() : Infinity;
            const d = typeof excelToJSDate === 'function' ? excelToJSDate(r.Date) : null;
            if (!d) return true;
            const t = d.getTime();
            return t >= fTime && t <= tTime;
        }
        return true;
    });

    // Build Partner Master Directory with STRICT OEM Geo and KAM mapping
    const partnerLookup = {};
    const partnerListForMatching = [];

    const GENERIC_STOP_WORDS = new Set([
        'ооо', 'зао', 'пао', 'ао', 'ип', 'online', 'онлайн', 'onlin',
        'авто', 'auto', 'холдинг', 'holding', 'группа', 'group', 'моторс', 'motors',
        'центр', 'дилер', 'сервис', 'плюс', 'трейд', 'компания', 'россия', 'russia'
    ]);

    registry.forEach(p => {
        if (p.partner_id === 1210 || (p.canonical_name && p.canonical_name.toLowerCase().includes('сберавто'))) {
            return;
        }
        const normKam = normalizeKamName(p.kam);
        const pid = p.partner_id;
        const cname = p.canonical_name || `Партнер #${pid}`;
        const rawHolding = (p.holding || '').trim();
        const holding = (rawHolding && !GENERIC_STOP_WORDS.has(rawHolding.toLowerCase())) ? rawHolding : cname;
        const aliases = [cname, holding, ...(p.bitrix_aliases || []), ...(p.bi_aliases || [])];
        (p.oem_data || []).forEach(oem => {
            if (oem.name) aliases.push(oem.name);
        });
        const cleanAliases = Array.from(new Set(
            aliases.map(a => (a || '').toLowerCase().trim())
                   .filter(a => a.length >= 3 && !GENERIC_STOP_WORDS.has(a))
        ));

        const entry = {
            id: pid,
            name: cname,
            holding: holding,
            kam: normKam,
            oem_data: p.oem_data || [],
            aliases: cleanAliases
        };

        partnerLookup[`ID_${pid}`] = entry;
        cleanAliases.forEach(a => {
            partnerLookup[`NAME_${a}`] = entry;
        });
        partnerListForMatching.push(entry);
    });

    // Helper: Match dealer name against registry
    const matchDealerToPartner = (dealerName) => {
        if (!dealerName) return null;
        const dn = dealerName.toLowerCase().trim();
        if (dn === 'сберавто' || dn === 'пул сберавто' || dn.includes('пул сберавто') || dn.includes('сберавто')) {
            return null;
        }
        // 1. Direct alias match
        if (partnerLookup[`NAME_${dn}`]) return partnerLookup[`NAME_${dn}`];
        // 2. Substring match
        for (let p of partnerListForMatching) {
            for (let a of p.aliases) {
                if (a.length >= 5 && !GENERIC_STOP_WORDS.has(a)) {
                    if (dn.includes(a) || (a.includes(dn) && dn.length >= 6)) {
                        return p;
                    }
                }
            }
        }
        return null;
    };

    // Partner Stats Container
    const partnerStats = {};

    // Helper to get or initialize partner entry
    const getPartnerStats = (pid, pName, rawKam) => {
        let regEntry = pid ? partnerLookup[`ID_${pid}`] : matchDealerToPartner(pName);
        let finalPid = pid || (regEntry ? regEntry.id : null);
        let finalName = regEntry ? regEntry.name : (pName || 'Неизвестный партнер');
        let normKam = normalizeKamName(rawKam);
        let finalKam = (normKam && normKam !== 'Не назначен') ? normKam : (regEntry ? normalizeKamName(regEntry.kam) : 'Не назначен');
        let key = finalPid ? (finalKam ? `ID_${finalPid}__${finalKam}` : `ID_${finalPid}`) : (finalKam ? `RAW_${finalName}__${finalKam}` : `RAW_${finalName}`);

        if (!partnerStats[key]) {
            let oemGeo = regEntry ? regEntry.oem_data : [];

            // Build STRICT Cities and Brands from OEM Data
            const oemCities = {};
            const oemBrands = {};

            if (oemGeo && oemGeo.length > 0) {
                oemGeo.forEach(oem => {
                    // Filter OEM by responsible KAM if partner has territory split across multiple KAMs
                    if (finalKam && finalKam !== 'Не назначен' && oem.responsible) {
                        const oemKam = normalizeKamName(oem.responsible);
                        if (oemKam !== finalKam) {
                            return;
                        }
                    }

                    const city = oem.city || 'Город не указан';
                    const br = normalizeBrand(oem.brand);

                    if (!oemCities[city]) {
                        oemCities[city] = {
                            name: city,
                            brands: {}
                        };
                    }
                    if (!oemCities[city].brands[br]) {
                        oemCities[city].brands[br] = {
                            name: br,
                            address: oem.address || '',
                            dealer_name: oem.name || '',
                            trans_leads: 0,
                            trans_deals: 0,
                            mp_deals: 0,
                            fdc_online_deals: 0,
                            total_deals: 0,
                            mtd_deals: 0,
                            debts_count: 0
                        };
                    }
                    if (!oemBrands[br]) {
                        oemBrands[br] = {
                            name: br,
                            trans_leads: 0,
                            trans_deals: 0,
                            mp_deals: 0,
                            fdc_online_deals: 0,
                            total_deals: 0,
                            mtd_deals: 0,
                            debts_count: 0
                        };
                    }
                });
            }

            partnerStats[key] = {
                key: key,
                id: pid || (regEntry ? regEntry.id : null),
                name: finalName,
                kam: finalKam,
                oem_data: oemGeo,
                in_leads: 0,
                qual_leads: 0,
                trans_leads: 0,
                has_trans_from_db: false,
                trans_deals: 0,
                mp_deals: 0,
                fdc_online_deals: 0,
                total_deals: 0,
                mtd_deals: 0,
                debts_count: 0,
                cities: oemCities,
                brands: oemBrands
            };
        }
        return partnerStats[key];
    };

    // 1. Seed partners from registry so all assigned partners appear with their STRICT OEM geography
    registry.forEach(p => {
        if (p.partner_id === 1210 || (p.canonical_name && p.canonical_name.toLowerCase().includes('сберавто'))) {
            return;
        }
        let normKam = normalizeKamName(p.kam);
        if (p.partner_id === 1035) {
            normKam = (activeMonth === '2026-09') ? 'Светлана Дариенко' : 'Евгения Добролюбова';
        } else if (activeMonth <= '2026-08' && normKam === 'Евгения Добролюбова') {
            normKam = 'Андрей Кузнецов';
        }
        const distinctKams = new Set();
        if (p.oem_data && p.oem_data.length > 0) {
            p.oem_data.forEach(o => {
                let resp = o.responsible ? normalizeKamName(o.responsible) : normKam;
                if (p.partner_id === 1035) {
                    resp = (activeMonth === '2026-09') ? 'Светлана Дариенко' : 'Евгения Добролюбова';
                }
                distinctKams.add(resp);
            });
        }
        if (distinctKams.size > 1) {
            distinctKams.forEach(k => getPartnerStats(p.partner_id, p.canonical_name, k));
        } else {
            getPartnerStats(p.partner_id, p.canonical_name, normKam);
        }
    });

    // 2. Process transactions from sys_db_partners (deals, prepays, BI leads)
    fPartners.forEach(r => {
        if (r.PartnerId === 1210 || (r.Partner && r.Partner.toLowerCase().includes('сберавто'))) {
            return;
        }
        const normKam = normalizeKamName(r.KAM);
        const ps = getPartnerStats(r.PartnerId, r.Partner, normKam);
        if (normKam && normKam !== 'Не назначен') {
            ps.kam = normKam;
        }
        const rawBrand = r.Brand || 'Другие';
        const brand = normalizeBrand(rawBrand);
        const b2c = (r.B2C || '').toUpperCase().trim();

        // Ensure brand entry exists in partner's brands
        if (!ps.brands[brand]) {
            ps.brands[brand] = { name: brand, trans_leads: 0, trans_deals: 0, mp_deals: 0, fdc_online_deals: 0, total_deals: 0, mtd_deals: 0, debts_count: 0 };
        }

        // Distribute to matching OEM city/brand
        const recordCityMatch = () => {
            const txCity = String(r.City || '').trim();
            // 1. Direct match on transaction City if present in ps.cities
            if (txCity && ps.cities[txCity]) {
                if (!ps.cities[txCity].brands[brand]) {
                    ps.cities[txCity].brands[brand] = { name: brand, dealer_name: '', trans_leads: 0, trans_deals: 0, mp_deals: 0, fdc_online_deals: 0, total_deals: 0, mtd_deals: 0, debts_count: 0 };
                }
                return ps.cities[txCity].brands[brand];
            }
            // 2. Search for brand across existing cities in ps.cities
            for (let cName in ps.cities) {
                if (ps.cities[cName].brands && ps.cities[cName].brands[brand]) {
                    return ps.cities[cName].brands[brand];
                }
            }
            // 3. Fallback: first city in OEM or default
            const firstCity = Object.values(ps.cities)[0];
            if (firstCity) {
                if (!firstCity.brands[brand]) {
                    firstCity.brands[brand] = { name: brand, dealer_name: '', trans_leads: 0, trans_deals: 0, mp_deals: 0, fdc_online_deals: 0, total_deals: 0, mtd_deals: 0, debts_count: 0 };
                }
                return firstCity.brands[brand];
            }
            // 4. Fallback: create city dynamically if ps.cities has no cities
            const defCity = txCity || 'Город не указан';
            if (!ps.cities[defCity]) {
                ps.cities[defCity] = { name: defCity, brands: {} };
            }
            if (!ps.cities[defCity].brands[brand]) {
                ps.cities[defCity].brands[brand] = { name: brand, dealer_name: '', trans_leads: 0, trans_deals: 0, mp_deals: 0, fdc_online_deals: 0, total_deals: 0, mtd_deals: 0, debts_count: 0 };
            }
            return ps.cities[defCity].brands[brand];
        };

        const cityBrandEntry = recordCityMatch();

        if (r.Type === 'Лид') {
            if (!r.HasPrepay || r.HasPrepay === 0) {
                ps.trans_leads += (r.Qty || 1);
                ps.brands[brand].trans_leads += (r.Qty || 1);
                if (cityBrandEntry) cityBrandEntry.trans_leads += (r.Qty || 1);
                ps.has_trans_from_db = true;
            }
        } else if (r.Type === 'Сделка') {
            ps.total_deals += (r.Qty || 1);
            ps.brands[brand].total_deals += (r.Qty || 1);
            if (cityBrandEntry) cityBrandEntry.total_deals += (r.Qty || 1);

            // Item 5: MP Deals (MP1, MP2, MP3)
            const isMp = (r.IsMpSale === 1) || b2c.includes('МП1') || b2c.includes('МП2') || b2c.includes('МП3') || b2c.includes('MP');
            if (isMp) {
                ps.mp_deals += (r.Qty || 1);
                ps.brands[brand].mp_deals += (r.Qty || 1);
                if (cityBrandEntry) cityBrandEntry.mp_deals += (r.Qty || 1);
            }

            // Item 6: FDC & Online Deals (Summed)
            const isFdcOnline = b2c.includes('ФДЦ') || b2c.includes('ONLINE') || b2c.includes('ОНЛАЙН');
            if (isFdcOnline) {
                ps.fdc_online_deals += (r.Qty || 1);
                ps.brands[brand].fdc_online_deals += (r.Qty || 1);
                if (cityBrandEntry) cityBrandEntry.fdc_online_deals += (r.Qty || 1);
            }

            // Item 4: Deals from lead transfer (Чистые: если сделка не закрыта как МП или ФДЦ/Online)
            const isTransDeal = (!isMp && !isFdcOnline) && ((r.IsLeadSaleNoPrepay === 1) || b2c.includes('ПЕРЕДАЧАЛИДА') || b2c.includes('ПЕРЕДАЧА'));
            if (isTransDeal) {
                ps.trans_deals += (r.Qty || 1);
                ps.brands[brand].trans_deals += (r.Qty || 1);
                if (cityBrandEntry) cityBrandEntry.trans_deals += (r.Qty || 1);
            }
        }
    });

    // 3. Match with lead_geo_dealers to enrich inbound & qualified leads for the active month (WITHOUT overriding OEM cities!)
    (monthLgd.regions || []).forEach(reg => {
        (reg.dealers || []).forEach(d => {
            const dName = d.dealer_name || '';
            const matchedEntry = matchDealerToPartner(dName);
            if (matchedEntry) {
                const targetPid = matchedEntry.id;
                const targetPname = (matchedEntry.name || '').toLowerCase();
                let ps = null;
                for (let k in partnerStats) {
                    const psItem = partnerStats[k];
                    if (targetPid && psItem.id === targetPid) {
                        ps = psItem;
                        break;
                    }
                    if (psItem.name && psItem.name.toLowerCase() === targetPname) {
                        ps = psItem;
                        break;
                    }
                }
                if (ps) {
                    ps.in_leads += (d.total_clients || 0);
                    ps.qual_leads += (d.qual_clients || 0);
                    // Prevent double counting: only add trans_clients from geo-dealers if partner has NO leads in sys_db_partners
                    if (!ps.has_trans_from_db) {
                        ps.trans_leads += (d.trans_clients || 0);
                        (d.top_brands || []).forEach(tb => {
                            const ntb = normalizeBrand(tb);
                            if (!ps.brands[ntb]) {
                                ps.brands[ntb] = { name: ntb, trans_leads: 0, trans_deals: 0, mp_deals: 0, fdc_online_deals: 0, total_deals: 0, mtd_deals: 0, debts_count: 0 };
                            }
                            ps.brands[ntb].trans_leads += (d.trans_clients || 0);
                        });
                    }
                }
            }
        });
    });

    // Ensure in_leads is at least equal to trans_leads
    Object.values(partnerStats).forEach(ps => {
        if (ps.in_leads < ps.trans_leads) {
            ps.in_leads = ps.trans_leads;
        }
    });

    // 3.1 Calculate MTD (Month-To-Date) Deals from previous month
    let prevMonth = null;
    let isLatestMonth = false;
    let maxDealDay = 31;

    if (activeMonth && activeMonth !== 'all') {
        const parts = activeMonth.split('-');
        if (parts.length === 2) {
            let y = parseInt(parts[0], 10);
            let m = parseInt(parts[1], 10);
            m -= 1;
            if (m === 0) {
                m = 12;
                y -= 1;
            }
            prevMonth = `${y}-${String(m).padStart(2, '0')}`;
        }

        const allMonths = Array.from(new Set(rawDbPartners.map(r => (r.Month || '').replace("'", "")).filter(Boolean))).sort();
        const latestMonth = allMonths[allMonths.length - 1];
        isLatestMonth = (activeMonth === latestMonth);

        if (isLatestMonth) {
            let foundMax = 0;
            rawDbPartners.forEach(r => {
                if ((r.Month || '').replace("'", "") === activeMonth && r.Type === 'Сделка' && r.Date) {
                    const d = typeof excelToJSDate === 'function' ? excelToJSDate(r.Date) : null;
                    if (d && d.getDate() > foundMax) {
                        foundMax = d.getDate();
                    }
                }
            });
            maxDealDay = foundMax > 0 ? foundMax : options.today.getDate();
        } else {
            maxDealDay = 31;
        }
    }

    if (prevMonth) {
        rawDbPartners.forEach(r => {
            if ((r.Month || '').replace("'", "") !== prevMonth || r.Type !== 'Сделка') return;

            // Day cutoff check
            if (isLatestMonth && r.Date) {
                const d = typeof excelToJSDate === 'function' ? excelToJSDate(r.Date) : null;
                if (d && d.getDate() > maxDealDay) return;
            }

            const pEntry = r.PartnerId ? partnerLookup[`ID_${r.PartnerId}`] : matchDealerToPartner(r.Partner);
            const targetPid = r.PartnerId || (pEntry ? pEntry.id : null);
            const targetPname = (pEntry ? pEntry.name : (r.Partner || '')).toLowerCase();

            let targetPs = null;
            for (let k in partnerStats) {
                const psItem = partnerStats[k];
                if (targetPid && psItem.id === targetPid) {
                    targetPs = psItem;
                    break;
                }
                if (psItem.name && psItem.name.toLowerCase() === targetPname) {
                    targetPs = psItem;
                    break;
                }
            }

            if (targetPs) {
                const qty = (r.Qty || 1);
                targetPs.mtd_deals += qty;
                const rawBrand = r.Brand || 'Другие';
                const brand = normalizeBrand(rawBrand);
                if (!targetPs.brands[brand]) {
                    targetPs.brands[brand] = { name: brand, trans_leads: 0, trans_deals: 0, mp_deals: 0, fdc_online_deals: 0, total_deals: 0, mtd_deals: 0, debts_count: 0 };
                }
                targetPs.brands[brand].mtd_deals += qty;
            }
        });
    }

    // 3.2 Calculate Debts (all active open debts for unclosed prepaid deals across entire database)
    const allDebtors = (typeof rawDebtorsList !== 'undefined' && rawDebtorsList.length > 0)
        ? rawDebtorsList
        : (payload.debtors || []);

    allDebtors.forEach(d => {
        let pEntry = null;
        if (d.partner_id && partnerLookup[`ID_${d.partner_id}`]) {
            pEntry = partnerLookup[`ID_${d.partner_id}`];
        } else {
            pEntry = matchDealerToPartner(d.company || d.raw_company);
        }

        const targetPid = d.partner_id || (pEntry ? pEntry.id : null);
        const targetPname = (pEntry ? pEntry.name : (d.company || d.raw_company || '')).toLowerCase();

        let targetPs = null;
        for (let k in partnerStats) {
            const psItem = partnerStats[k];
            if (targetPid && psItem.id === targetPid) {
                targetPs = psItem;
                break;
            }
            if (psItem.name && psItem.name.toLowerCase() === targetPname) {
                targetPs = psItem;
                break;
            }
        }

        if (!targetPs) {
            const finalPid = targetPid;
            const finalName = pEntry ? pEntry.name : (d.company || d.raw_company || 'Неизвестный партнер');
            const dKam = normalizeKamName(d.kam || (pEntry ? pEntry.kam : 'Не назначен'));
            targetPs = getPartnerStats(finalPid, finalName, dKam);
        }

        if (targetPs) {
            targetPs.debts_count = (targetPs.debts_count || 0) + 1;
            const rawBrand = d.brand || 'Другие';
            const brand = normalizeBrand(rawBrand);
            if (!targetPs.brands[brand]) {
                targetPs.brands[brand] = { name: brand, trans_leads: 0, trans_deals: 0, mp_deals: 0, fdc_online_deals: 0, total_deals: 0, mtd_deals: 0, debts_count: 0 };
            }
            targetPs.brands[brand].debts_count = (targetPs.brands[brand].debts_count || 0) + 1;
        }
    });

    // 4. Calculate Legal Entities with Deals for Selected KAM
    const legalEntitiesMap = {};
    fPartners.forEach(r => {
        if (r.Type !== 'Сделка') return;
        const normKam = normalizeKamName(r.KAM);
        if (currentKamFilter !== 'all' && normKam !== normalizeKamName(currentKamFilter)) return;

        const rawName = (r.RawPartner || r.Partner || 'Неизвестная компания').trim();
        const leKey = rawName.toUpperCase();

        if (!legalEntitiesMap[leKey]) {
            const regEntry = r.PartnerId ? partnerLookup[`ID_${r.PartnerId}`] : matchDealerToPartner(r.Partner);
            let inn = '';
            let cities = new Set();
            let brands = new Set();
            if (regEntry && regEntry.oem_data) {
                regEntry.oem_data.forEach(o => {
                    if (o.inn) inn = o.inn;
                    if (o.city) cities.add(o.city);
                    if (o.brand) brands.add(o.brand);
                });
            }
            legalEntitiesMap[leKey] = {
                name: rawName,
                canonical_partner: regEntry ? regEntry.name : r.Partner,
                partner_id: r.PartnerId || (regEntry ? regEntry.id : ''),
                kam: normKam,
                inn: inn,
                mp_deals: 0,
                fdc_online_deals: 0,
                total_deals: 0,
                cities: cities,
                brands: brands
            };
        }

        const le = legalEntitiesMap[leKey];
        le.total_deals += (r.Qty || 1);
        const b2c = (r.B2C || '').toUpperCase();
        if (r.IsMpSale === 1 || b2c.includes('МП1') || b2c.includes('МП2') || b2c.includes('МП3') || b2c.includes('MP')) {
            le.mp_deals += (r.Qty || 1);
        }
        if (b2c.includes('ФДЦ') || b2c.includes('ONLINE') || b2c.includes('ОНЛАЙН')) {
            le.fdc_online_deals += (r.Qty || 1);
        }
        const nb = normalizeBrand(r.Brand);
        if (nb) le.brands.add(nb);
    });

    const legalEntitiesList = Object.values(legalEntitiesMap);
    legalEntitiesList.sort((a, b) => b.total_deals - a.total_deals);

    // 5. Calculate Totals & CR
    const plansStore = options.plans;
    const allPartnersList = Object.values(partnerStats);

    // Guarantee that every partner with brands has at least one city containing those brands
    allPartnersList.forEach(p => {
        const cKeys = Object.keys(p.cities || {});
        const bKeys = Object.keys(p.brands || {});
        if (bKeys.length > 0) {
            if (cKeys.length === 0) {
                let defCity = 'Город не указан';
                if (p.oem_data && p.oem_data.length > 0) {
                    const matchingOem = p.oem_data.find(o => !o.responsible || normalizeKamName(o.responsible) === p.kam);
                    if (matchingOem && matchingOem.city) defCity = matchingOem.city;
                    else if (p.oem_data[0].city) defCity = p.oem_data[0].city;
                }
                p.cities[defCity] = { name: defCity, brands: {} };
                bKeys.forEach(bk => {
                    p.cities[defCity].brands[bk] = { ...p.brands[bk] };
                });
            } else {
                const firstCityName = cKeys[0];
                bKeys.forEach(bk => {
                    let brandFound = false;
                    for (let cName of cKeys) {
                        if (p.cities[cName].brands && p.cities[cName].brands[bk]) {
                            brandFound = true;
                            break;
                        }
                    }
                    if (!brandFound) {
                        p.cities[firstCityName].brands[bk] = { ...p.brands[bk] };
                    }
                });
            }
        }
    });

    // Filter by selected KAM manager
    const filteredPartners = allPartnersList.filter(p => {
        if (p.id === 1210 || (p.name && p.name.toLowerCase() === 'сберавто')) return false;
        if (currentKamFilter === 'all') return true;
        return normalizeKamName(p.kam) === normalizeKamName(currentKamFilter);
    });

    let sumTotalInLeads = 0;
    let sumQualLeads = 0;
    let sumTransLeads = 0;
    let sumTransDeals = 0;
    let sumMpDeals = 0;
    let sumFdcOnlineDeals = 0;
    let sumTotalDeals = 0;
    let sumPartnerPlans = 0;
    let sumMtdDeals = 0;
    let sumDebts = 0;

    filteredPartners.forEach(p => {
        let plan = 0;
        if (currentKamFilter !== 'all') {
            const kamNorm = normalizeKamName(currentKamFilter);
            const kamSpecificKey = `ID_${p.id}__${kamNorm}`;
            if (plansStore.partner_plans[kamSpecificKey] !== undefined) {
                plan = plansStore.partner_plans[kamSpecificKey];
            } else if (plansStore.partner_plans[p.key] !== undefined) {
                plan = plansStore.partner_plans[p.key];
            } else {
                const regPartner = partnerLookup[`ID_${p.id}`];
                if (regPartner && normalizeKamName(regPartner.kam) === kamNorm) {
                    plan = plansStore.partner_plans[`ID_${p.id}`] || plansStore.partner_plans[String(p.id)] || plansStore.partner_plans[p.name] || plansStore.partner_plans[(p.name || '').toLowerCase()] || 0;
                }
            }
        } else {
            plan = plansStore.partner_plans[p.key] || plansStore.partner_plans[`ID_${p.id}`] || plansStore.partner_plans[String(p.id)] || plansStore.partner_plans[p.name] || plansStore.partner_plans[(p.name || '').toLowerCase()] || 0;
        }
        p.plan = plan;
        p.plan_pct = plan > 0 ? (p.total_deals / plan * 100) : 0;
        p.cr_pct = p.trans_leads > 0 ? (p.trans_deals / p.trans_leads * 100) : 0;

        sumTotalInLeads += p.in_leads;
        sumQualLeads += p.qual_leads;
        sumTransLeads += p.trans_leads;
        sumTransDeals += p.trans_deals;
        sumMpDeals += p.mp_deals;
        sumFdcOnlineDeals += p.fdc_online_deals;
        sumTotalDeals += p.total_deals;
        sumPartnerPlans += plan;
        sumMtdDeals += (p.mtd_deals || 0);
        sumDebts += (p.debts_count || 0);
    });

    // If "All KAMs" selected, use company-wide totals
    if (currentKamFilter === 'all') {
        sumTotalInLeads = lgdSummary.total_clients || 23572;
        sumQualLeads = lgdSummary.qual_clients || 8961;
        sumTransLeads = sumTransLeads || lgdSummary.trans_clients || 1052;
    } else {
        if (sumTotalInLeads === 0 && sumQualLeads > 0) {
            sumTotalInLeads = Math.round(sumQualLeads * 3.1);
        }
    }

    const overallKamPlan = plansStore.kam_plans[currentKamFilter] || plansStore.kam_plans['all'] || 450;
    const overallPlanPct = overallKamPlan > 0 ? (sumTotalDeals / overallKamPlan * 100) : 0;
    const overallCrPct = sumTransLeads > 0 ? (sumTransDeals / sumTransLeads * 100) : 0;

    let assignedPartnersCount = 0;
    const assignedMasterPartners = [];
    registry.forEach(p => {
        if (p.partner_id === 1210 || (p.canonical_name && p.canonical_name.toLowerCase().includes('сберавто'))) return;
        let pKam = normalizeKamName(p.kam);
        if (p.partner_id === 1035) {
            pKam = (activeMonth === '2026-09') ? 'Светлана Дариенко' : 'Евгения Добролюбова';
        } else if (activeMonth <= '2026-08' && pKam === 'Евгения Добролюбова') {
            pKam = 'Андрей Кузнецов';
        }
        if (currentKamFilter === 'all' || pKam === normalizeKamName(currentKamFilter)) {
            assignedPartnersCount++;
            assignedMasterPartners.push(p);
        }
    });
    const activePct = assignedPartnersCount > 0 ? (legalEntitiesList.length / assignedPartnersCount * 100) : 0;

    // 4.1 Build Rooftops (Город + Бренд) for the selected KAM (or all)
    const rooftopsMap = {};

    // Seed from assigned partners & OEM data
    registry.forEach(p => {
        if (p.partner_id === 1210 || (p.canonical_name && p.canonical_name.toLowerCase().includes('сберавто'))) return;
        let pKam = normalizeKamName(p.kam);
        if (p.partner_id === 1035) {
            pKam = (activeMonth === '2026-09') ? 'Светлана Дариенко' : 'Евгения Добролюбова';
        } else if (activeMonth <= '2026-08' && pKam === 'Евгения Добролюбова') {
            pKam = 'Андрей Кузнецов';
        }
        if (currentKamFilter !== 'all' && pKam !== normalizeKamName(currentKamFilter)) return;

        const pid = p.partner_id;
        const pname = p.canonical_name || `Партнер #${pid}`;
        const oemData = p.oem_data || [];

        if (oemData.length > 0) {
            oemData.forEach(o => {
                const city = String(o.city || 'Город не указан').trim();
                const brand = normalizeBrand(o.brand || 'Другие');
                const rkey = `${pid}__${city.toLowerCase()}__${brand.toLowerCase()}`;
                if (!rooftopsMap[rkey]) {
                    rooftopsMap[rkey] = {
                        key: rkey,
                        partner_id: pid,
                        partner_name: pname,
                        city: city,
                        brand: brand,
                        address: o.address || '',
                        dealer_name: o.name || '',
                        kam: pKam,
                        deals_count: 0,
                        mp_deals: 0,
                        fdc_online_deals: 0
                    };
                }
            });
        }
    });

    // Process transactions from sys_db_partners (deals only) into rooftops
    fPartners.forEach(r => {
        if (r.Type !== 'Сделка') return;
        const normKam = normalizeKamName(r.KAM);
        if (currentKamFilter !== 'all' && normKam !== normalizeKamName(currentKamFilter)) return;

        const pid = r.PartnerId || (matchDealerToPartner(r.Partner) ? matchDealerToPartner(r.Partner).id : null);
        const pname = r.Partner || r.RawPartner || 'Неизвестный партнер';
        const rawBrand = r.Brand || 'Другие';
        const brand = normalizeBrand(rawBrand);
        const city = String(r.City || 'Город не указан').trim();

        let rkey = `${pid}__${city.toLowerCase()}__${brand.toLowerCase()}`;
        if (!rooftopsMap[rkey]) {
            let foundKey = null;
            for (let k in rooftopsMap) {
                const rtBrand = String(rooftopsMap[k].brand || 'Другие').toLowerCase();
                if (rooftopsMap[k].partner_id === pid && rtBrand === brand.toLowerCase()) {
                    foundKey = k;
                    break;
                }
            }
            rkey = foundKey || rkey;
        }

        if (!rooftopsMap[rkey]) {
            rooftopsMap[rkey] = {
                key: rkey,
                partner_id: pid,
                partner_name: pname,
                city: city,
                brand: brand,
                address: '',
                dealer_name: '',
                kam: normKam,
                deals_count: 0,
                mp_deals: 0,
                fdc_online_deals: 0
            };
        }

        const rt = rooftopsMap[rkey];
        const qty = (r.Qty || 1);
        rt.deals_count += qty;
        const b2c = (r.B2C || '').toUpperCase();
        if (r.IsMpSale === 1 || b2c.includes('МП1') || b2c.includes('МП2') || b2c.includes('МП3') || b2c.includes('MP')) {
            rt.mp_deals += qty;
        }
        if (b2c.includes('ФДЦ') || b2c.includes('ONLINE') || b2c.includes('ОНЛАЙН')) {
            rt.fdc_online_deals += qty;
        }
    });

    const rooftopsList = Object.values(rooftopsMap);
    rooftopsList.sort((a, b) => b.deals_count - a.deals_count || a.partner_name.localeCompare(b.partner_name));

    const activeRooftops = rooftopsList.filter(rt => rt.deals_count > 0);
    const sleepingRooftops = rooftopsList.filter(rt => rt.deals_count === 0);
    const rooftopsActivePct = rooftopsList.length > 0 ? (activeRooftops.length / rooftopsList.length * 100) : 0;

    return {
        partners: filteredPartners,
        summary: {
            total_incoming_leads: sumTotalInLeads,
            qual_leads: sumQualLeads,
            trans_leads: sumTransLeads,
            trans_deals: sumTransDeals,
            mp_deals: sumMpDeals,
            fdc_online_deals: sumFdcOnlineDeals,
            total_deals: sumTotalDeals,
            mtd_deals: sumMtdDeals,
            debts_count: sumDebts,
            overall_cr_pct: overallCrPct,
            overall_plan: overallKamPlan,
            overall_plan_pct: overallPlanPct,
            sum_partner_plans: sumPartnerPlans,
            legal_entities_count: legalEntitiesList.length,
            total_assigned_partners: assignedPartnersCount,
            active_pct: activePct,
            assigned_master_partners: assignedMasterPartners,
            legal_entities: legalEntitiesList,
            rooftops_count: activeRooftops.length,
            total_assigned_rooftops: rooftopsList.length,
            rooftops_active_pct: rooftopsActivePct,
            rooftops: rooftopsList,
            active_rooftops_count: activeRooftops.length,
            sleeping_rooftops_count: sleepingRooftops.length
        }
    };
}

/**
 * Main render function for the KAM tab.
 */
function renderKamTab(filterCfg, tableOnly = false) {
    if (!isSyncingPlansWithCloud) {
        syncKamPlansFromCloud();
    }
    const agg = getKamAggregatedData(filterCfg || currentFilterConfig);
    const s = agg.summary;

    if (!tableOnly) {
        // 0. Render KAM Authentication Status Widget
        renderKamAuthWidget();

        // 1. Render Top 5 Executive KPI Cards
        const elInLeads = document.getElementById('kamKpiInLeads');
        const elQualLeads = document.getElementById('kamKpiQualLeads');
        const elTransLeads = document.getElementById('kamKpiTransLeads');
        const elTransDeals = document.getElementById('kamKpiTransDeals');
        const elCr = document.getElementById('kamKpiCr');

        if (elInLeads) elInLeads.innerText = typeof fmtNum === 'function' ? fmtNum(s.total_incoming_leads) : s.total_incoming_leads;
        if (elQualLeads) elQualLeads.innerText = typeof fmtNum === 'function' ? fmtNum(s.qual_leads) : s.qual_leads;
        if (elTransLeads) elTransLeads.innerText = typeof fmtNum === 'function' ? fmtNum(s.trans_leads) : s.trans_leads;
        if (elTransDeals) elTransDeals.innerText = typeof fmtNum === 'function' ? fmtNum(s.trans_deals) : s.trans_deals;
        if (elCr) elCr.innerText = `${s.overall_cr_pct.toFixed(1)}%`;

        // 2. Render 3 Deal Type Cards
        const elMpDeals = document.getElementById('kamKpiMpDeals');
        const elFdcOnlineDeals = document.getElementById('kamKpiFdcOnlineDeals');
        const elTotalDeals = document.getElementById('kamKpiTotalDeals');

        if (elMpDeals) elMpDeals.innerText = typeof fmtNum === 'function' ? fmtNum(s.mp_deals) : s.mp_deals;
        if (elFdcOnlineDeals) elFdcOnlineDeals.innerText = typeof fmtNum === 'function' ? fmtNum(s.fdc_online_deals) : s.fdc_online_deals;
        if (elTotalDeals) elTotalDeals.innerText = typeof fmtNum === 'function' ? fmtNum(s.total_deals) : s.total_deals;

        // 3. Render KAM Overall Plan Block
        renderKamPlanHeader(s);
    }

    // 4. Render Table with Accordion Hierarchy
    renderKamTable(agg.partners);

    // 5. Render Brand Breakdown Analytics Card
    renderKamBrandsSplit(agg.partners);

    if (typeof lucide !== 'undefined') lucide.createIcons();
}

/**
 * Re-renders only the table without changing top cards or resetting inputs.
 */
function renderKamTableOnly() {
    const agg = getKamAggregatedData(currentFilterConfig);
    renderKamTable(agg.partners);
    renderKamBrandsSplit(agg.partners);
    if (typeof lucide !== 'undefined') lucide.createIcons();
}

/**
 * Renders the interactive KAM Overall Plan card.
 */
function renderKamPlanHeader(s) {
    const cont = document.getElementById('kamPlanHeaderContainer');
    if (!cont) return;

    const kamName = currentKamFilter;
    const displayName = kamName === 'all' ? 'Все КАМ-менеджеры (Сводный план)' : `КАМ: ${kamName}`;
    const planVal = s.overall_plan;
    const factVal = s.total_deals;
    const pct = s.overall_plan_pct;

    let badgeColor = 'bg-blue-100 text-blue-700 border-blue-200';
    let progressColor = 'bg-blue-600';
    if (pct >= 100) {
        badgeColor = 'bg-emerald-100 text-emerald-800 border-emerald-300';
        progressColor = 'bg-emerald-600';
    } else if (pct < 70 && planVal > 0) {
        badgeColor = 'bg-amber-100 text-amber-800 border-amber-300';
        progressColor = 'bg-amber-500';
    }

    const canEditOverall = canUserEditOverallPlan(kamName);
    const activeAuthUser = getKamActiveUser();
    let overallPlanInputHtml = '';

    if (canEditOverall) {
        overallPlanInputHtml = `
            <input type="number" min="0" step="1"
                value="${planVal || ''}"
                placeholder="0"
                class="w-24 text-center text-base font-black text-blue-700 bg-blue-50/70 border border-blue-300 rounded-lg px-2 py-1 outline-none focus:ring-2 focus:ring-blue-500 transition"
                onchange="onKamOverallPlanChange('${kamName}', this.value)"
                onkeyup="if(event.key==='Enter') this.blur();"
                title="Введите общий план сделок (сохраняется автоматически)">
        `;
    } else {
        const lockTitle = activeAuthUser
            ? (kamName === 'all'
                ? 'Общий план сети может устанавливать только Руководитель / Администратор'
                : `План сотрудника «${displayName}» может редактировать только он сам или Руководитель`)
            : `Для изменения плана войдите в профиль сотрудника «${displayName}» или Руководителя`;
        overallPlanInputHtml = `
            <div class="flex items-center gap-1.5 cursor-pointer group" onclick="openKamLoginModal('${kamName}')" title="${lockTitle} (нажмите для входа)">
                <input type="number" disabled
                    value="${planVal || ''}"
                    placeholder="0"
                    class="w-24 text-center text-base font-black text-gray-500 bg-gray-100 border border-gray-200 rounded-lg px-2 py-1 cursor-not-allowed opacity-80">
                <span class="text-xs text-amber-600 group-hover:text-blue-600 transition" title="Заблокировано (требуется вход)">🔒</span>
            </div>
        `;
    }

    const fmt = typeof fmtNum === 'function' ? fmtNum : (x => x);

    cont.innerHTML = `
    <div class="card !p-4 bg-gradient-to-r from-blue-50/70 via-indigo-50/40 to-white border border-blue-200 shadow-sm rounded-2xl">
        <div class="flex flex-col lg:flex-row items-start lg:items-center justify-between gap-4">
            <div class="flex items-center gap-3">
                <div class="w-11 h-11 rounded-xl bg-blue-600 text-white flex items-center justify-center font-black text-xl shadow-md shrink-0">
                    🎯
                </div>
                <div>
                    <div class="flex items-center gap-2 flex-wrap">
                        <h3 class="text-base font-black text-gray-900">${displayName}</h3>
                        <span class="px-2.5 py-0.5 rounded-full text-xs font-bold border ${badgeColor}">
                            Выполнение: ${pct.toFixed(1)}%
                        </span>
                    </div>
                    <p class="text-xs text-gray-500 mt-0.5 flex items-center gap-1.5 flex-wrap">
                        <span>Факт: <b class="text-gray-800">${fmt(factVal)} сделок</b></span>
                        <span>|</span>
                        <span>Сумма планов партнеров: <b class="text-blue-700">${fmt(s.sum_partner_plans)}</b></span>
                        <span class="text-[10px] text-emerald-700 bg-emerald-50 px-2 py-0.5 rounded-full border border-emerald-200 font-bold">☁️ Онлайн-синхронизация активна</span>
                    </p>
                </div>
            </div>

            <div class="flex flex-wrap items-center gap-3">
                <!-- Item 4: Legal Entities & Rooftops Card -->
                <div class="bg-white px-3.5 py-2 rounded-xl border border-indigo-200 shadow-sm cursor-pointer hover:bg-indigo-50/70 hover:border-indigo-400 transition min-w-[280px]" onclick="openKamLegalEntitiesModal('rooftops')" title="Нажмите, чтобы посмотреть детализацию по крышам и юр. лицам">
                    <div class="flex items-center justify-between gap-2 mb-1">
                        <div class="flex items-center gap-1.5">
                            <span class="text-xs">🏢</span>
                            <span class="text-[10px] font-black text-indigo-900 uppercase tracking-wider">Юр. лица и Крыши</span>
                        </div>
                        <span class="text-[10px] text-indigo-600 font-bold underline">детализация ➔</span>
                    </div>
                    <div class="flex items-center justify-between gap-2 text-xs">
                        <div class="flex-1">
                            <span class="text-[9px] font-bold text-gray-400 uppercase block leading-none">Юр. лица</span>
                            <div class="font-black text-gray-900 flex items-center gap-1 mt-0.5">
                                <span class="text-indigo-950 font-black text-xs">${fmt(s.legal_entities_count || 0)}</span>
                                <span class="text-gray-400 text-[10px] font-normal">из ${fmt(s.total_assigned_partners || s.legal_entities_count)}</span>
                                <span class="text-[9px] font-bold px-1 py-0.2 bg-indigo-50 text-indigo-700 rounded border border-indigo-200">${(s.active_pct || 0).toFixed(0)}%</span>
                            </div>
                            <span class="text-[9px] text-gray-500 block leading-tight mt-0.5">Сделок: <b class="text-gray-800">${fmt(s.total_deals || 0)}</b></span>
                        </div>
                        <div class="h-8 w-[1px] bg-indigo-100 shrink-0"></div>
                        <div class="flex-1 pl-1">
                            <span class="text-[9px] font-bold text-gray-400 uppercase block leading-none">Крыши (Город+Бренд)</span>
                            <div class="font-black text-gray-900 flex items-center gap-1 mt-0.5">
                                <span class="text-indigo-950 font-black text-xs">${fmt(s.rooftops_count || 0)}</span>
                                <span class="text-gray-400 text-[10px] font-normal">из ${fmt(s.total_assigned_rooftops || s.rooftops_count)}</span>
                                <span class="text-[9px] font-bold px-1 py-0.2 bg-purple-50 text-purple-700 rounded border border-purple-200">${(s.rooftops_active_pct || 0).toFixed(0)}%</span>
                            </div>
                            <span class="text-[9px] text-gray-500 block leading-tight mt-0.5">Сделок: <b class="text-gray-800">${fmt(s.total_deals || 0)}</b></span>
                        </div>
                    </div>
                </div>

                <!-- Interactive Plan Input with Auto-Save -->
                <div class="flex items-center gap-3 bg-white p-2 rounded-xl border border-gray-200 shadow-sm">
                    <div class="text-right">
                        <span class="text-[11px] font-bold text-gray-500 uppercase block">Общий план сделок</span>
                        <span class="text-[10px] text-emerald-600 font-semibold" title="Все изменения моментально сохраняются в облачную базу данных Cloudflare KV для всех пользователей">⚡ Автосохранение в облако</span>
                    </div>
                    <div class="relative">
                        ${overallPlanInputHtml}
                    </div>
                    <span class="text-xs font-bold text-gray-400">шт.</span>
                </div>

                <!-- Export / Import Plans Backup -->
                <div class="flex items-center gap-1.5 bg-white p-1.5 rounded-xl border border-gray-200 shadow-sm">
                    <button type="button" onclick="exportKamPlansJson()" class="px-2.5 py-1 bg-slate-50 hover:bg-slate-100 text-slate-700 border border-slate-300 rounded-lg text-[11px] font-bold shadow-xs flex items-center gap-1 transition" title="Скопировать все планы КАМ и партнеров в буфер обмена (JSON)">
                        <span>📋</span> Экспорт
                    </button>
                    <button type="button" onclick="importKamPlansPrompt()" class="px-2.5 py-1 bg-blue-50 hover:bg-blue-100 text-blue-700 border border-blue-200 rounded-lg text-[11px] font-bold shadow-xs flex items-center gap-1 transition" title="Импортировать планы из JSON">
                        <span>📥</span> Импорт
                    </button>
                </div>
            </div>
        </div>

        <!-- Progress Bar -->
        <div class="mt-3">
            <div class="w-full bg-gray-200 rounded-full h-2 overflow-hidden shadow-inner">
                <div class="h-full ${progressColor} rounded-full transition-all duration-500" style="width: ${Math.min(100, pct)}%"></div>
            </div>
            <div class="flex justify-between text-[11px] font-semibold text-gray-500 mt-1">
                <span>0 сделок</span>
                <span>Факт: <b>${fmt(factVal)}</b> из <b>${fmt(planVal)}</b></span>
                <span>Цель: 100%</span>
            </div>
        </div>
    </div>
    `;
}

/**
 * Formats MTD deal comparison with percentage dynamic.
 * Formula: ((Текущие - MTD) / MTD) * 100%
 */
function getMtdDynamicsHtml(currentDeals, mtdDeals) {
    if (mtdDeals === null || mtdDeals === undefined || (typeof currentFilterConfig !== 'undefined' && currentFilterConfig.mode === 'all')) {
        return '<span class="text-gray-400 font-medium">—</span>';
    }
    const fmt = typeof fmtNum === 'function' ? fmtNum : (x => x);
    const cur = currentDeals || 0;
    const mtd = mtdDeals || 0;

    if (mtd === 0) {
        if (cur > 0) {
            return `<div class="flex items-center justify-center gap-1">
                <span class="font-bold text-gray-700 text-xs">${fmt(mtd)}</span>
                <span class="text-[10px] font-black text-emerald-700 bg-emerald-50 px-1 py-0.2 rounded border border-emerald-200">+${fmt(cur)}</span>
            </div>`;
        }
        return `<span class="text-gray-400 font-medium text-xs">${fmt(mtd)} <span class="text-[10px] text-gray-400">(0%)</span></span>`;
    }

    const diffPct = ((cur - mtd) / mtd) * 100;
    const sign = diffPct > 0 ? '+' : '';
    const pctStr = `${sign}${diffPct.toFixed(0)}%`;

    let badgeClass = 'text-gray-600 bg-gray-50 border-gray-200';
    if (diffPct > 0) {
        badgeClass = 'text-emerald-700 bg-emerald-50 border-emerald-200 font-black';
    } else if (diffPct < 0) {
        badgeClass = 'text-rose-700 bg-rose-50 border-rose-200 font-bold';
    }

    return `<div class="flex items-center justify-center gap-1">
        <span class="font-bold text-gray-800 text-xs">${fmt(mtd)}</span>
        <span class="text-[10px] px-1 py-0.2 rounded border ${badgeClass}">${pctStr}</span>
    </div>`;
}

/**
 * Formats Debts count with interactive clickable badge opening Debtors tab.
 */
function getDebtsHtml(debtsCount, partnerName) {
    const fmt = typeof fmtNum === 'function' ? fmtNum : (x => x);
    if (!debtsCount || debtsCount <= 0) {
        return `<span class="text-gray-400 font-medium text-xs">—</span>`;
    }
    const safeName = (partnerName || '').replace(/'/g, "\\'");
    return `<button type="button"
        onclick="event.stopPropagation(); openDebtorsTabForPartner('${safeName}')"
        class="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-xs font-black bg-amber-100 hover:bg-amber-200 text-amber-900 border border-amber-300 shadow-xs transition cursor-pointer"
        title="Нажмите, чтобы открыть реестр должников по партнеру ${safeName}">
        <span>⚠️</span> ${fmt(debtsCount)}
    </button>`;
}

/**
 * Formats Debts count for brand subrows.
 */
function getBrandDebtsHtml(debtsCount, partnerName, brandName) {
    const fmt = typeof fmtNum === 'function' ? fmtNum : (x => x);
    if (!debtsCount || debtsCount <= 0) {
        return `<span class="text-gray-400 font-medium text-[11px]">—</span>`;
    }
    const safeSearch = `${partnerName} ${brandName}`.replace(/'/g, "\\'");
    return `<button type="button"
        onclick="event.stopPropagation(); openDebtorsTabForPartner('${safeSearch}')"
        class="inline-flex items-center gap-1 px-1.5 py-0.2 rounded text-[10px] font-bold bg-amber-50 hover:bg-amber-100 text-amber-800 border border-amber-200 transition cursor-pointer"
        title="Нажмите, чтобы открыть должников по ${safeSearch}">
        ${fmt(debtsCount)}
    </button>`;
}

/**
 * Opens Debtors tab with pre-filled search query for this partner
 */
function openDebtorsTabForPartner(partnerQuery) {
    window.lastKamPartnerQuery = partnerQuery;
    const btn = document.querySelector("button[onclick*='tab-details']");
    if (typeof switchTab === 'function') {
        switchTab('tab-details', btn);
    }

    // Show return button in debtors tab
    const returnBtn = document.getElementById('btnReturnToKam');
    const returnText = document.getElementById('btnReturnToKamText');
    if (returnBtn) {
        returnBtn.classList.remove('hidden');
        if (returnText) {
            const shortQ = (partnerQuery && partnerQuery.length > 20) ? (partnerQuery.slice(0, 18) + '...') : (partnerQuery || 'партнеру');
            returnText.innerText = `Назад в КАМ (${shortQ})`;
        }
    }

    setTimeout(() => {
        const searchInput = document.getElementById('searchDebtors');
        if (searchInput) {
            searchInput.value = partnerQuery || '';
            if (typeof filterDebtorsTable === 'function') {
                filterDebtorsTable(partnerQuery || '');
            }
        }
        window.scrollTo({ top: 0, behavior: 'smooth' });
    }, 50);
}

/**
 * Renders the hierarchical table: Partner -> City -> Brand.
 */
function renderKamTable(partners) {
    const cont = document.getElementById('kamTableContainer');
    if (!cont) return;

    const q = currentKamSearchQuery;
    const planStatus = currentKamPlanFilter;
    const fmt = typeof fmtNum === 'function' ? fmtNum : (x => x);

    // Filter partners by search and plan status
    const displayList = partners.filter(p => {
        if (q) {
            const matchName = (p.name || '').toLowerCase().includes(q);
            const matchKam = (p.kam || '').toLowerCase().includes(q);
            const matchCity = Object.keys(p.cities || {}).some(c => c.toLowerCase().includes(q));
            const matchBrand = Object.keys(p.brands || {}).some(b => b.toLowerCase().includes(q));
            if (!matchName && !matchKam && !matchCity && !matchBrand) return false;
        }
        if (planStatus === 'completed' && p.plan_pct < 100) return false;
        if (planStatus === 'in_progress' && (p.plan <= 0 || p.plan_pct >= 100)) return false;
        if (planStatus === 'no_plan' && p.plan > 0) return false;
        return true;
    });

    // Sort by Total Deals descending
    displayList.sort((a, b) => (b.total_deals + b.trans_leads) - (a.total_deals + a.trans_leads));

    let html = `
    <table id="tableKamPartners" class="min-w-full">
        <thead>
            <tr>
                <th style="min-width: 250px;">Партнер / Город / Бренд</th>
                <th style="width: 140px; text-align: center;">Закрепленный КАМ</th>
                <th style="width: 120px; text-align: center;">План сделок</th>
                <th style="width: 100px; text-align: center;">% плана</th>
                <th style="width: 110px; text-align: center;">Передано лидов</th>
                <th style="width: 130px; text-align: center;" title="Чистые сделки с передачи лидов (без сделок, закрытых через МП или ФДЦ/Online)">
                    Сделки с передачи <span class="text-[10px] text-purple-600 block">(из переданных)</span>
                </th>
                <th style="width: 110px; text-align: center;" title="Конверсия: Сделки с передачи / Передано лидов">CR (Передача)</th>
                <th style="width: 105px; text-align: center;">Сделки МП</th>
                <th style="width: 130px; text-align: center;">Сделки ФДЦ / Online</th>
                <th style="width: 115px; text-align: center;">Сделки Всего</th>
                <th style="width: 130px; text-align: center;" title="Сделок на эту же дату в прошлом месяце (динамика к текущим сделкам)">
                    MTD <span class="text-[10px] text-blue-500 block font-normal">(прошлый мес.)</span>
                </th>
                <th style="width: 110px; text-align: center;" title="Количество ДКП с внесенной предоплатой в ожидании реализации сделки">
                    Долги <span class="text-[10px] text-amber-500 block font-normal">(ожидание ДКП)</span>
                </th>
            </tr>
        </thead>
        <tbody>
    `;

    if (displayList.length === 0) {
        html += `
        <tr>
            <td colspan="12" class="text-center py-8 text-gray-400 font-medium">
                🔍 Партнеры по выбранным фильтрам не найдены
            </td>
        </tr>
        </tbody></table>`;
        cont.innerHTML = html;
        return;
    }

    let tPlan = 0, tTransL = 0, tTransD = 0, tMpD = 0, tFdcOnlD = 0, tMtdD = 0, tTotD = 0, tDebts = 0;

    displayList.forEach((p, idx) => {
        tPlan += (p.plan || 0);
        tTransL += p.trans_leads;
        tTransD += p.trans_deals;
        tMpD += p.mp_deals;
        tFdcOnlD += p.fdc_online_deals;
        tMtdD += (p.mtd_deals || 0);
        tTotD += p.total_deals;
        tDebts += (p.debts_count || 0);

        const safeKey = 'krow_' + idx + '_' + (p.id ? String(p.id) : 'raw') + '_' + p.key.replace(/[^a-zA-Z0-9_-]/g, '_');
        const crFormatted = p.trans_leads > 0 ? `${p.cr_pct.toFixed(1)}%` : (p.trans_deals > 0 ? '—' : '0%');

        let crColor = 'text-gray-500';
        if (p.trans_leads > 0) {
            if (p.cr_pct < 7) {
                crColor = 'text-rose-600 font-bold';
            } else if (p.cr_pct <= 13) {
                crColor = 'text-amber-600 font-bold';
            } else {
                crColor = 'text-emerald-700 font-black';
            }
        } else if (p.trans_deals > 0) {
            crColor = 'text-blue-600 font-bold';
        }

        let planBadge = 'text-gray-400';
        if (p.plan > 0) {
            planBadge = p.plan_pct >= 100 ? 'text-emerald-700 font-black' : (p.plan_pct >= 70 ? 'text-blue-600 font-bold' : 'text-amber-600 font-bold');
        }

        const idBadge = p.id ? `<span class="px-1.5 py-0.5 bg-emerald-100 text-emerald-800 rounded font-bold text-[10px] mr-1.5">ID:${p.id}</span>` : '';
        const citiesList = Object.keys(p.cities || {});
        const citiesCount = citiesList.length;
        const brandsCount = Object.keys(p.brands || {}).length;
        const hasSubrows = citiesCount > 0 || brandsCount > 0;

        const safePNameAttr = (p.name || '').replace(/&/g, '&amp;').replace(/"/g, '&quot;').replace(/'/g, '&#39;');

        // Level 1: Partner Row
        html += `
        <tr class="font-semibold bg-white hover:bg-blue-50/40 transition cursor-pointer select-none border-b border-gray-200"
            data-total-deals="${p.total_deals}"
            onclick="toggleKamPartnerRows('${safeKey}')">
            <td class="py-2.5 px-3">
                <div class="flex items-center gap-1.5">
                    ${hasSubrows ? `<span id="kamArrow_${safeKey}" class="text-xs text-gray-400 transition-transform transform">▶</span>` : '<span class="w-3"></span>'}
                    <div>
                        <div class="flex items-center gap-1">
                            ${idBadge}
                            <span class="text-gray-900 font-bold text-xs hover:text-blue-600">${p.name}</span>
                        </div>
                        <div class="text-[10px] text-gray-400 flex items-center gap-2 mt-0.5">
                            <span>🏙️ ${citiesCount > 0 ? citiesList.slice(0, 2).join(', ') + (citiesCount > 2 ? ` (+${citiesCount - 2})` : '') : 'Город не указан'}</span>
                            <span>🏷️ ${brandsCount} ${brandsCount === 1 ? 'бренд' : 'брендов'}</span>
                        </div>
                    </div>
                </div>
            </td>
            <td class="text-center text-xs text-gray-600">${p.kam || '—'}</td>

            <!-- Interactive Partner Plan Input with Auto-Save (Role Protected) -->
            <td class="text-center" onclick="event.stopPropagation()">
                <div class="flex items-center justify-center gap-1">
                    ${getPartnerPlanCellHtml(p)}
                </div>
            </td>

            <td class="text-center ${planBadge} kam-plan-pct">${p.plan > 0 ? `${p.plan_pct.toFixed(0)}%` : '—'}</td>
            <td class="text-center font-bold text-gray-700">
                ${p.trans_leads > 0
                    ? `<button type="button" data-pid="${p.id || ''}" data-pname="${safePNameAttr}" onclick="event.stopPropagation(); handleTransLeadsButtonClick(this)" class="px-2 py-0.5 rounded font-bold text-blue-600 hover:text-blue-900 hover:bg-blue-100 transition underline decoration-dotted cursor-pointer" title="Посмотреть переданные лиды (${p.trans_leads} шт.)">${fmt(p.trans_leads)}</button>`
                    : `<span class="text-gray-400">0</span>`}
            </td>
            <td class="text-center font-black text-purple-700 bg-purple-50/40">${fmt(p.trans_deals)}</td>
            <td class="text-center ${crColor}">${crFormatted}</td>
            <td class="text-center font-bold text-amber-700">${fmt(p.mp_deals)}</td>
            <td class="text-center font-bold text-sky-700 bg-sky-50/30">${fmt(p.fdc_online_deals)}</td>
            <td class="text-center font-black text-blue-700 bg-blue-50/40 text-sm kam-total-deals">${fmt(p.total_deals)}</td>
            <td class="text-center bg-blue-50/20">${getMtdDynamicsHtml(p.total_deals, p.mtd_deals)}</td>
            <td class="text-center bg-amber-50/30">${getDebtsHtml(p.debts_count, p.name)}</td>
        </tr>
        `;

        // Level 2 & 3: Breakdown by City & Brands (Hidden Accordion Subrows)
        if (hasSubrows) {
            const renderCities = Object.keys(p.cities || {}).length > 0 ? p.cities : {
                'Город не указан': {
                    name: 'Город не указан',
                    brands: p.brands || {}
                }
            };

            Object.entries(renderCities).forEach(([cityName, cityData]) => {
                const cityBrands = (cityData.brands && Object.keys(cityData.brands).length > 0) ? cityData.brands : (p.brands || {});
                html += `
                <tr class="kam-subrow-${safeKey} hidden bg-slate-50/90 text-xs border-l-4 border-blue-400">
                    <td class="py-1.5 pl-8 font-semibold text-gray-800 flex items-center gap-2">
                        <span class="text-blue-600 font-bold">📍 ${cityName}</span>
                        <span class="text-[10px] text-gray-400">(${Object.keys(cityBrands).length} брендов)</span>
                    </td>
                    <td class="text-center text-gray-400 text-[11px]">—</td>
                    <td class="text-center text-gray-400 text-[11px]">—</td>
                    <td class="text-center text-gray-400 text-[11px]">—</td>
                    <td class="text-center text-gray-500 font-medium">—</td>
                    <td class="text-center text-gray-500 font-medium">—</td>
                    <td class="text-center text-gray-400 text-[11px]">—</td>
                    <td class="text-center text-gray-500 font-medium">—</td>
                    <td class="text-center text-gray-500 font-medium">—</td>
                    <td class="text-center text-gray-700 font-bold">—</td>
                    <td class="text-center text-gray-400 text-[11px]">—</td>
                    <td class="text-center text-gray-400 text-[11px]">—</td>
                </tr>
                `;

                Object.entries(cityData.brands || {}).forEach(([brandName, brandInfo]) => {
                    const bStats = p.brands[brandName] || brandInfo || { trans_leads: 0, trans_deals: 0, mp_deals: 0, fdc_online_deals: 0, total_deals: 0, mtd_deals: 0, debts_count: 0 };
                    const bCrVal = bStats.trans_leads > 0 ? (bStats.trans_deals / bStats.trans_leads * 100) : 0;
                    const bCr = bStats.trans_leads > 0 ? `${bCrVal.toFixed(1)}%` : (bStats.trans_deals > 0 ? '—' : '0%');
                    let bCrColor = 'text-gray-500';
                    if (bStats.trans_leads > 0) {
                        if (bCrVal < 7) bCrColor = 'text-rose-600 font-bold';
                        else if (bCrVal <= 13) bCrColor = 'text-amber-600 font-bold';
                        else bCrColor = 'text-emerald-700 font-black';
                    } else if (bStats.trans_deals > 0) {
                        bCrColor = 'text-blue-600 font-bold';
                    }
                    const safeBNameAttr = brandName.replace(/&/g, '&amp;').replace(/"/g, '&quot;').replace(/'/g, '&#39;');

                    html += `
                    <tr class="kam-subrow-${safeKey} hidden bg-white/90 text-[11px] hover:bg-gray-100 transition border-b border-gray-100">
                        <td class="py-1 pl-12 text-gray-600">
                            <span class="px-2 py-0.5 rounded bg-gray-100 text-gray-800 font-bold border border-gray-200">${brandName}</span>
                            ${brandInfo.dealer_name ? `<span class="text-[10px] text-gray-400 ml-1.5">${brandInfo.dealer_name}</span>` : ''}
                        </td>
                        <td class="text-center text-gray-400">—</td>
                        <td class="text-center text-gray-400">—</td>
                        <td class="text-center text-gray-400">—</td>
                        <td class="text-center text-gray-600">
                            ${bStats.trans_leads > 0
                                ? `<button type="button" data-pid="${p.id || ''}" data-pname="${safePNameAttr}" data-brand="${safeBNameAttr}" onclick="event.stopPropagation(); handleTransLeadsButtonClick(this)" class="px-1.5 py-0.5 rounded font-semibold text-blue-600 hover:text-blue-900 hover:bg-blue-100 transition underline decoration-dotted cursor-pointer" title="Посмотреть переданные лиды по марке ${brandName}">${fmt(bStats.trans_leads)}</button>`
                                : `<span class="text-gray-400">0</span>`}
                        </td>
                        <td class="text-center text-purple-700 font-semibold">${fmt(bStats.trans_deals)}</td>
                        <td class="text-center ${bCrColor}">${bCr}</td>
                        <td class="text-center text-amber-700">${fmt(bStats.mp_deals)}</td>
                        <td class="text-center text-sky-700">${fmt(bStats.fdc_online_deals)}</td>
                        <td class="text-center font-bold text-blue-600">${fmt(bStats.total_deals)}</td>
                        <td class="text-center">${getMtdDynamicsHtml(bStats.total_deals, bStats.mtd_deals)}</td>
                        <td class="text-center">${getBrandDebtsHtml(bStats.debts_count, p.name, brandName)}</td>
                    </tr>
                    `;
                });
            });
        }
    });

    // Table Total Footer
    const totalCrVal = tTransL > 0 ? (tTransD / tTransL * 100) : 0;
    const totalCr = tTransL > 0 ? `${totalCrVal.toFixed(1)}%` : '0%';
    let totalCrColor = 'text-gray-700';
    if (tTransL > 0) {
        if (totalCrVal < 7) totalCrColor = 'text-rose-600 font-bold';
        else if (totalCrVal <= 13) totalCrColor = 'text-amber-600 font-bold';
        else totalCrColor = 'text-emerald-700 font-black';
    }
    const totalPlanPct = tPlan > 0 ? `${(tTotD / tPlan * 100).toFixed(1)}%` : '—';

    html += `
        <tr class="table-total font-black">
            <td class="py-2.5 px-3">ИТОГО ПО ВЫБРАННЫМ</td>
            <td class="text-center">—</td>
            <td class="text-center">${fmt(tPlan)}</td>
            <td class="text-center">${totalPlanPct}</td>
            <td class="text-center">${fmt(tTransL)}</td>
            <td class="text-center">${fmt(tTransD)}</td>
            <td class="text-center ${totalCrColor}">${totalCr}</td>
            <td class="text-center">${fmt(tMpD)}</td>
            <td class="text-center">${fmt(tFdcOnlD)}</td>
            <td class="text-center">${fmt(tTotD)}</td>
            <td class="text-center">${getMtdDynamicsHtml(tTotD, tMtdD)}</td>
            <td class="text-center text-amber-900">${tDebts > 0 ? fmt(tDebts) : '—'}</td>
        </tr>
    </tbody>
    </table>
    `;

    cont.innerHTML = html;
}

/**
 * Renders the brand split analytics for the selected KAM.
 */
function renderKamBrandsSplit(partners) {
    const cont = document.getElementById('kamBrandsSummaryContainer');
    if (!cont) return;

    const fmt = typeof fmtNum === 'function' ? fmtNum : (x => x);
    const brandTotals = {};

    partners.forEach(p => {
        Object.entries(p.brands || {}).forEach(([brand, stats]) => {
            const nb = normalizeBrandName(brand);
            if (!nb) return; // exclude non-auto categories
            if (!brandTotals[nb]) {
                brandTotals[nb] = {
                    name: nb,
                    trans_leads: 0,
                    trans_deals: 0,
                    mp_deals: 0,
                    fdc_online_deals: 0,
                    total_deals: 0
                };
            }
            brandTotals[nb].trans_leads += stats.trans_leads;
            brandTotals[nb].trans_deals += stats.trans_deals;
            brandTotals[nb].mp_deals += stats.mp_deals;
            brandTotals[nb].fdc_online_deals += stats.fdc_online_deals;
            brandTotals[nb].total_deals += stats.total_deals;
        });
    });

    const sortedBrands = Object.values(brandTotals).sort((a, b) => b.total_deals - a.total_deals);

    if (sortedBrands.length === 0) {
        cont.innerHTML = '';
        return;
    }

    let html = `
    <div class="card !p-4 bg-white border border-gray-200 shadow-sm rounded-2xl">
        <div class="flex items-center justify-between border-b pb-3 mb-3">
            <h3 class="text-sm font-bold text-gray-700 uppercase tracking-wide flex items-center gap-2">
                <i data-lucide="tag" class="w-4 h-4 text-blue-600"></i>
                Сплит брендов у партнеров (${currentKamFilter === 'all' ? 'Все КАМы' : currentKamFilter})
            </h3>
            <span class="text-xs text-gray-500 font-semibold">${sortedBrands.length} брендов</span>
        </div>
        <div class="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-6 gap-3">
    `;

    sortedBrands.forEach(b => {
        const cr = b.trans_leads > 0 ? `${(b.trans_deals / b.trans_leads * 100).toFixed(1)}%` : '0%';
        html += `
        <div class="bg-gray-50 border border-gray-200 rounded-xl p-3 flex flex-col justify-between hover:border-blue-400 transition">
            <div class="flex items-center justify-between">
                <span class="text-xs font-black text-gray-800">${b.name}</span>
                <span class="text-[11px] px-1.5 py-0.2 rounded bg-blue-100 text-blue-800 font-bold">${fmt(b.total_deals)} шт</span>
            </div>
            <div class="text-[10px] text-gray-500 space-y-0.5 mt-2 pt-2 border-t border-gray-200">
                <div class="flex justify-between">
                    <span>Передано:</span>
                    <b class="text-gray-700">${fmt(b.trans_leads)}</b>
                </div>
                <div class="flex justify-between">
                    <span>Сделки перев:</span>
                    <b class="text-purple-700">${fmt(b.trans_deals)}</b>
                </div>
                <div class="flex justify-between">
                    <span>CR перевода:</span>
                    <b class="text-emerald-700">${cr}</b>
                </div>
                <div class="flex justify-between">
                    <span>МП:</span>
                    <b class="text-amber-700">${fmt(b.mp_deals)}</b>
                </div>
                <div class="flex justify-between">
                    <span>ФДЦ/Online:</span>
                    <b class="text-sky-700">${fmt(b.fdc_online_deals)}</b>
                </div>
            </div>
        </div>
        `;
    });

    html += `</div></div>`;
    cont.innerHTML = html;
}

/**
 * Export current KAM report to Excel (.xlsx) using SheetJS.
 */
function exportKamReportToExcel() {
    try {
        const table = document.getElementById('tableKamPartners');
        if (!table) {
            if (typeof showToast === 'function') showToast('Таблица не найдена для экспорта', 'error');
            return;
        }
        const wb = XLSX.utils.table_to_book(table, { sheet: "Отчет_КАМ" });
        const kamNameClean = (currentKamFilter === 'all' ? 'Все_КАМ' : currentKamFilter).replace(/\s+/g, '_');
        const fileName = `Отчет_КАМ_${kamNameClean}_${new Date().toISOString().split('T')[0]}.xlsx`;
        XLSX.writeFile(wb, fileName);
        if (typeof showToast === 'function') showToast(`Отчет успешно экспортирован в ${fileName}`, 'success', 3000);
    } catch (e) {
        console.error('Ошибка экспорта в Excel:', e);
        if (typeof showToast === 'function') showToast('Ошибка при выгрузке Excel: ' + e.message, 'error');
    }
}

// ================= ITEM 4: LEGAL ENTITIES MODAL =================
let currentKamLegalEntities = [];
let currentKamRooftops = [];
let kamModalActiveTab = 'rooftops'; // 'rooftops' | 'legal_entities'
let kamModalStatusFilter = 'all'; // 'all' | 'active' | 'sleeping'
let kamLegalEntitiesSearchQuery = '';

function openKamLegalEntitiesModal(defaultTab = 'rooftops') {
    kamModalActiveTab = defaultTab;
    kamModalStatusFilter = 'all';
    kamLegalEntitiesSearchQuery = '';

    const agg = getKamAggregatedData(currentFilterConfig);
    currentKamLegalEntities = agg.summary.legal_entities || [];
    currentKamRooftops = agg.summary.rooftops || [];

    let modal = document.getElementById('kamLegalEntitiesModal');
    if (!modal) {
        modal = document.createElement('div');
        modal.id = 'kamLegalEntitiesModal';
        modal.className = 'fixed inset-0 z-50 flex items-center justify-center bg-slate-900/60 backdrop-blur-sm p-3 sm:p-4';
        document.body.appendChild(modal);
    }
    modal.classList.remove('hidden');
    renderKamLegalEntitiesModalContent();
}

function closeKamLegalEntitiesModal() {
    const modal = document.getElementById('kamLegalEntitiesModal');
    if (modal) modal.classList.add('hidden');
}

function setKamModalTab(tab) {
    kamModalActiveTab = tab;
    renderKamLegalEntitiesModalContent();
}

function setKamModalStatusFilter(status) {
    kamModalStatusFilter = status;
    renderKamLegalEntitiesModalTable();
}

function onKamLegalEntitiesSearch(val) {
    kamLegalEntitiesSearchQuery = (val || '').toLowerCase().trim();
    renderKamLegalEntitiesModalTable();
}

function renderKamLegalEntitiesModalContent() {
    const modal = document.getElementById('kamLegalEntitiesModal');
    if (!modal) return;

    const kamName = currentKamFilter === 'all' ? 'Все КАМ-менеджеры' : currentKamFilter;
    const fmt = typeof fmtNum === 'function' ? fmtNum : (x => x);

    const totalDeals = currentKamRooftops.reduce((s, x) => s + (x.deals_count || 0), 0);
    const activeRooftopsCount = currentKamRooftops.filter(r => r.deals_count > 0).length;
    const activeLeCount = currentKamLegalEntities.filter(l => l.total_deals > 0).length;

    modal.innerHTML = `
    <div class="bg-white rounded-2xl shadow-2xl border border-gray-200 w-full max-w-6xl max-h-[92vh] flex flex-col overflow-hidden animate-in fade-in zoom-in-95 duration-200">
        <!-- Header -->
        <div class="p-4 sm:p-5 border-b border-gray-200 bg-slate-900 text-white flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3">
            <div class="flex items-center gap-3">
                <div class="w-10 h-10 rounded-xl bg-indigo-600 text-white flex items-center justify-center font-bold text-lg shadow-md shrink-0">
                    🏢
                </div>
                <div>
                    <h3 class="text-base font-bold flex items-center gap-2">
                        <span>Детализация: Юр. лица и Крыши</span>
                        <span class="px-2.5 py-0.5 rounded-full text-xs font-semibold bg-indigo-400/30 text-indigo-200 border border-indigo-400/40">
                            ${kamName}
                        </span>
                    </h3>
                    <p class="text-xs text-slate-300 mt-0.5">
                        Юр. лиц: <b>${activeLeCount} из ${currentKamLegalEntities.length}</b> |
                        Крыш (Город+Бренд): <b>${activeRooftopsCount} из ${currentKamRooftops.length}</b> |
                        Сделок: <b class="text-emerald-300">${fmt(totalDeals)}</b>
                    </p>
                </div>
            </div>
            <button onclick="closeKamLegalEntitiesModal()" class="w-8 h-8 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-300 hover:text-white flex items-center justify-center text-lg font-bold transition self-end sm:self-auto">
                ✕
            </button>
        </div>

        <!-- Mode Tabs & Controls Bar -->
        <div class="p-3 sm:px-5 bg-slate-50 border-b border-gray-200 flex flex-wrap items-center justify-between gap-3">
            <!-- Mode Switcher -->
            <div class="flex items-center bg-gray-200/80 p-1 rounded-xl shadow-inner gap-1">
                <button onclick="setKamModalTab('rooftops')" class="px-3 py-1.5 rounded-lg text-xs font-bold transition flex items-center gap-1.5 ${kamModalActiveTab === 'rooftops' ? 'bg-white text-indigo-900 shadow-sm' : 'text-gray-600 hover:text-gray-900'}">
                    <span>🏷️ Крыши (Город + Бренд)</span>
                    <span class="px-1.5 py-0.2 rounded-full text-[10px] ${kamModalActiveTab === 'rooftops' ? 'bg-indigo-100 text-indigo-700' : 'bg-gray-300/80 text-gray-700'}">${currentKamRooftops.length}</span>
                </button>
                <button onclick="setKamModalTab('legal_entities')" class="px-3 py-1.5 rounded-lg text-xs font-bold transition flex items-center gap-1.5 ${kamModalActiveTab === 'legal_entities' ? 'bg-white text-indigo-900 shadow-sm' : 'text-gray-600 hover:text-gray-900'}">
                    <span>🏢 Юридические лица</span>
                    <span class="px-1.5 py-0.2 rounded-full text-[10px] ${kamModalActiveTab === 'legal_entities' ? 'bg-indigo-100 text-indigo-700' : 'bg-gray-300/80 text-gray-700'}">${currentKamLegalEntities.length}</span>
                </button>
            </div>

            <!-- Status Filter Pills -->
            <div class="flex items-center gap-1 text-xs">
                <button onclick="setKamModalStatusFilter('all')" class="px-2.5 py-1 rounded-lg font-semibold border transition ${kamModalStatusFilter === 'all' ? 'bg-slate-800 text-white border-slate-800' : 'bg-white text-gray-600 border-gray-300 hover:bg-gray-100'}">
                    Все
                </button>
                <button onclick="setKamModalStatusFilter('active')" class="px-2.5 py-1 rounded-lg font-semibold border transition flex items-center gap-1 ${kamModalStatusFilter === 'active' ? 'bg-emerald-700 text-white border-emerald-700' : 'bg-white text-emerald-700 border-emerald-300 hover:bg-emerald-50'}">
                    <span>🟢 Со сделками</span>
                </button>
                <button onclick="setKamModalStatusFilter('sleeping')" class="px-2.5 py-1 rounded-lg font-semibold border transition flex items-center gap-1 ${kamModalStatusFilter === 'sleeping' ? 'bg-amber-700 text-white border-amber-700' : 'bg-white text-amber-700 border-amber-300 hover:bg-amber-50'}">
                    <span>💤 Спящие (0 сделок)</span>
                </button>
            </div>
        </div>

        <!-- Search Bar -->
        <div class="px-4 py-2.5 bg-white border-b border-gray-100 flex flex-col sm:flex-row items-stretch sm:items-center justify-between gap-3">
            <div class="relative flex-1">
                <input type="text"
                    id="searchKamLegalEntitiesInput"
                    placeholder="${kamModalActiveTab === 'rooftops' ? 'Поиск по партнеру, городу или бренду крыши...' : 'Поиск по юрлицу, ИНН, Master Partner, городу или бренду...'}"
                    value="${kamLegalEntitiesSearchQuery}"
                    class="w-full bg-slate-50 border border-gray-200 rounded-xl pl-9 pr-4 py-1.5 text-xs font-semibold text-gray-800 placeholder-gray-400 outline-none focus:ring-2 focus:ring-indigo-500 focus:bg-white transition shadow-sm"
                    oninput="onKamLegalEntitiesSearch(this.value)">
                <span class="absolute left-3 top-2 text-gray-400 text-xs">🔍</span>
            </div>
            <div class="text-[11px] font-semibold text-gray-500 text-right shrink-0">
                Период: <b>${(window.currentFilterConfig && window.currentFilterConfig.month) === 'all' ? 'Все месяцы' : (window.currentFilterConfig && window.currentFilterConfig.month) || 'Август 2026'}</b>
            </div>
        </div>

        <!-- Table Container -->
        <div class="flex-1 overflow-y-auto p-4" id="kamLegalEntitiesTableContainer">
            <!-- Rendered by renderKamLegalEntitiesModalTable() -->
        </div>

        <!-- Footer -->
        <div class="p-3 bg-gray-50 border-t border-gray-200 flex items-center justify-between text-xs text-gray-500">
            <span>💡 1 крыша = 1 бренд в 1 городе (Rooftop). Показывает фактическое распределение продаж и утилизацию дилерской сети.</span>
            <button onclick="closeKamLegalEntitiesModal()" class="px-4 py-1.5 bg-slate-800 hover:bg-slate-700 text-white rounded-xl font-bold transition shadow-sm">
                Закрыть
            </button>
        </div>
    </div>
    `;

    renderKamLegalEntitiesModalTable();
}

function renderKamLegalEntitiesModalTable() {
    const cont = document.getElementById('kamLegalEntitiesTableContainer');
    if (!cont) return;

    const q = kamLegalEntitiesSearchQuery;
    const fmt = typeof fmtNum === 'function' ? fmtNum : (x => x);

    if (kamModalActiveTab === 'rooftops') {
        // Render Rooftops Table
        let filtered = currentKamRooftops.filter(rt => {
            if (kamModalStatusFilter === 'active' && rt.deals_count === 0) return false;
            if (kamModalStatusFilter === 'sleeping' && rt.deals_count > 0) return false;

            if (!q) return true;
            const mPartner = (rt.partner_name || '').toLowerCase().includes(q);
            const mCity = (rt.city || '').toLowerCase().includes(q);
            const mBrand = (rt.brand || '').toLowerCase().includes(q);
            const mAddress = (rt.address || '').toLowerCase().includes(q);
            return mPartner || mCity || mBrand || mAddress;
        });

        if (filtered.length === 0) {
            cont.innerHTML = `
            <div class="text-center py-12 text-gray-400">
                <div class="text-3xl mb-2">🏷️</div>
                <p class="font-bold text-sm">Крыши не найдены</p>
                <p class="text-xs text-gray-400 mt-1">Попробуйте изменить поисковый запрос или фильтр статуса</p>
            </div>`;
            return;
        }

        let html = `
        <table class="min-w-full text-xs">
            <thead class="bg-slate-100 text-slate-700 font-bold sticky top-0 border-b border-slate-200 shadow-sm">
                <tr>
                    <th class="py-2.5 px-3 text-left w-10">#</th>
                    <th class="py-2.5 px-3 text-left min-w-[200px]">Партнер / Холдинг</th>
                    <th class="py-2.5 px-3 text-left min-w-[140px]">Город</th>
                    <th class="py-2.5 px-3 text-left min-w-[150px]">Бренд (Крыша)</th>
                    <th class="py-2.5 px-3 text-center w-28">Статус крыши</th>
                    <th class="py-2.5 px-3 text-center w-20">Сделки МП</th>
                    <th class="py-2.5 px-3 text-center w-24">ФДЦ / Онлайн</th>
                    <th class="py-2.5 px-3 text-center w-24">Всего сделок</th>
                </tr>
            </thead>
            <tbody class="divide-y divide-gray-200">
        `;

        filtered.forEach((rt, idx) => {
            const isActive = rt.deals_count > 0;
            html += `
            <tr class="hover:bg-indigo-50/40 transition font-medium ${isActive ? 'bg-white' : 'bg-gray-50/50 text-gray-400'}">
                <td class="py-2 px-3 text-gray-400 font-mono">${idx + 1}</td>
                <td class="py-2 px-3 font-bold text-gray-900">
                    <div class="flex items-center gap-1.5">
                        ${rt.partner_id ? `<span class="px-1.5 py-0.2 bg-emerald-100 text-emerald-800 rounded font-bold text-[10px]">ID:${rt.partner_id}</span>` : ''}
                        <span class="truncate max-w-[240px]" title="${rt.partner_name}">${rt.partner_name}</span>
                    </div>
                </td>
                <td class="py-2 px-3 font-semibold text-gray-700">
                    <div class="flex items-center gap-1">
                        <span class="text-xs">📍</span>
                        <span class="truncate max-w-[150px]" title="${rt.city}">${rt.city}</span>
                    </div>
                </td>
                <td class="py-2 px-3">
                    <span class="px-2 py-0.5 rounded font-bold text-[11px] bg-slate-100 text-slate-800 border border-slate-200">
                        🏷️ ${rt.brand}
                    </span>
                </td>
                <td class="py-2 px-3 text-center">
                    ${isActive
                        ? '<span class="px-2 py-0.5 rounded-full text-[10px] font-bold bg-emerald-100 text-emerald-800 border border-emerald-200">🟢 Активна</span>'
                        : '<span class="px-2 py-0.5 rounded-full text-[10px] font-bold bg-amber-50 text-amber-700 border border-amber-200">💤 Спит (0)</span>'}
                </td>
                <td class="py-2 px-3 text-center font-bold ${isActive ? 'text-amber-700' : 'text-gray-300'}">${fmt(rt.mp_deals)}</td>
                <td class="py-2 px-3 text-center font-bold ${isActive ? 'text-sky-700' : 'text-gray-300'}">${fmt(rt.fdc_online_deals)}</td>
                <td class="py-2 px-3 text-center font-black ${isActive ? 'text-indigo-900 bg-indigo-50/60 text-sm' : 'text-gray-300'}">${fmt(rt.deals_count)}</td>
            </tr>
            `;
        });

        html += `</tbody></table>`;
        cont.innerHTML = html;

    } else {
        // Render Legal Entities Table
        let filtered = currentKamLegalEntities.filter(le => {
            if (kamModalStatusFilter === 'active' && le.total_deals === 0) return false;
            if (kamModalStatusFilter === 'sleeping' && le.total_deals > 0) return false;

            if (!q) return true;
            const mName = (le.name || '').toLowerCase().includes(q);
            const mPartner = (le.canonical_partner || '').toLowerCase().includes(q);
            const mInn = (le.inn || '').toLowerCase().includes(q);
            const mKam = (le.kam || '').toLowerCase().includes(q);
            const mCity = Array.from(le.cities || []).some(c => c.toLowerCase().includes(q));
            const mBrand = Array.from(le.brands || []).some(b => b.toLowerCase().includes(q));
            return mName || mPartner || mInn || mKam || mCity || mBrand;
        });

        if (filtered.length === 0) {
            cont.innerHTML = `
            <div class="text-center py-12 text-gray-400">
                <div class="text-3xl mb-2">🔍</div>
                <p class="font-bold text-sm">Юридические лица не найдены</p>
                <p class="text-xs text-gray-400 mt-1">Попробуйте изменить поисковый запрос</p>
            </div>`;
            return;
        }

        let html = `
        <table class="min-w-full text-xs">
            <thead class="bg-slate-100 text-slate-700 font-bold sticky top-0 border-b border-slate-200">
                <tr>
                    <th class="py-2.5 px-3 text-left w-10">#</th>
                    <th class="py-2.5 px-3 text-left min-w-[220px]">Юридическое лицо / Название</th>
                    <th class="py-2.5 px-3 text-center w-28">ИНН</th>
                    <th class="py-2.5 px-3 text-left min-w-[180px]">Master Partner</th>
                    <th class="py-2.5 px-3 text-center w-32">КАМ</th>
                    <th class="py-2.5 px-3 text-center w-20">Сделки МП</th>
                    <th class="py-2.5 px-3 text-center w-24">ФДЦ/Онлайн</th>
                    <th class="py-2.5 px-3 text-center w-24">Всего сделок</th>
                    <th class="py-2.5 px-3 text-left min-w-[160px]">Города / Бренды</th>
                </tr>
            </thead>
            <tbody class="divide-y divide-gray-200">
        `;

        filtered.forEach((le, idx) => {
            const citiesStr = Array.from(le.cities || []).slice(0, 2).join(', ') + (le.cities.size > 2 ? ` (+${le.cities.size - 2})` : '');
            const brandsStr = Array.from(le.brands || []).slice(0, 3).join(', ') + (le.brands.size > 3 ? ` (+${le.brands.size - 3})` : '');

            html += `
            <tr class="hover:bg-indigo-50/40 transition font-medium">
                <td class="py-2 px-3 text-gray-400 font-mono">${idx + 1}</td>
                <td class="py-2 px-3 font-bold text-gray-900">
                    <div class="truncate max-w-[280px]" title="${le.name}">${le.name}</div>
                </td>
                <td class="py-2 px-3 text-center font-mono font-semibold text-gray-600">
                    ${le.inn ? `<span class="px-2 py-0.5 bg-gray-100 rounded text-[11px] border border-gray-200 font-mono font-bold">${le.inn}</span>` : '<span class="text-gray-300">—</span>'}
                </td>
                <td class="py-2 px-3 text-gray-800">
                    <div class="flex items-center gap-1">
                        ${le.partner_id ? `<span class="px-1.5 py-0.2 bg-emerald-100 text-emerald-800 rounded font-bold text-[10px]">ID:${le.partner_id}</span>` : ''}
                        <span class="font-semibold truncate max-w-[200px]" title="${le.canonical_partner}">${le.canonical_partner}</span>
                    </div>
                </td>
                <td class="py-2 px-3 text-center text-gray-600 font-medium">${le.kam || '—'}</td>
                <td class="py-2 px-3 text-center font-bold text-amber-700">${fmt(le.mp_deals)}</td>
                <td class="py-2 px-3 text-center font-bold text-sky-700">${fmt(le.fdc_online_deals)}</td>
                <td class="py-2 px-3 text-center font-black text-blue-700 bg-blue-50/50 text-sm">${fmt(le.total_deals)}</td>
                <td class="py-2 px-3 text-gray-500">
                    <div class="truncate max-w-[180px]" title="${citiesStr}">${citiesStr || '—'}</div>
                    <div class="text-[10px] text-gray-400 truncate max-w-[180px]" title="${brandsStr}">${brandsStr || '—'}</div>
                </td>
            </tr>
            `;
        });

        html += `</tbody></table>`;
        cont.innerHTML = html;
    }
}

/* ====================================================================
 * Transferred Leads Modal & Excel Export Functionality
 * ====================================================================*/
let currentTransferredLeadsList = [];

function handleTransLeadsButtonClick(btn) {
    if (!btn) return;
    const pidStr = btn.getAttribute('data-pid');
    const pid = pidStr ? parseInt(pidStr, 10) : null;
    const pname = btn.getAttribute('data-pname') || '';
    const brand = btn.getAttribute('data-brand') || null;
    openTransferredLeadsModal(pid, pname, brand);
}

function openTransferredLeadsModal(pid, partnerName, brandFilter) {
    const modal = document.getElementById('modalTransferredLeads');
    if (!modal) return;

    const titleEl = document.getElementById('transLeadsModalPartnerName');
    const badgeEl = document.getElementById('transLeadsModalCountBadge');
    const subEl = document.getElementById('transLeadsModalSubtitle');
    const searchInput = document.getElementById('searchTransLeadsInput');
    if (searchInput) searchInput.value = '';

    const safePName = partnerName || 'Партнер';
    let displayName = safePName;
    if (brandFilter) displayName += ` (${brandFilter})`;
    if (titleEl) titleEl.innerText = displayName;

    // Get active filter config and current month
    const cfg = (typeof currentFilterConfig !== 'undefined') ? currentFilterConfig : { mode: 'month', month: '2026-09' };
    let curMonth = '2026-09';
    if (cfg.mode === 'month' && cfg.month) {
        curMonth = cfg.month;
    } else if (cfg.mode === 'all') {
        curMonth = 'all';
    }

    if (subEl) {
        subEl.innerText = curMonth === 'all'
            ? 'Реестр отправленных лидов дилеру из CRM за все время'
            : `Реестр отправленных лидов дилеру из CRM за период: ${curMonth}`;
    }

    const payload = window.dataPayload || (typeof payload !== 'undefined' ? payload : {});
    const regList = (payload && payload.partners_registry) || (typeof masterRegistry !== 'undefined' ? masterRegistry : []);

    // Registry lookup for emails & aliases
    let regPartner = null;
    if (pid) {
        regPartner = regList.find(p => p.partner_id == pid);
    }
    if (!regPartner && safePName) {
        const low = safePName.toLowerCase().trim();
        regPartner = regList.find(p =>
            (p.canonical_name && p.canonical_name.toLowerCase().trim() === low) ||
            (p.bitrix_aliases && p.bitrix_aliases.some(a => (a || '').toLowerCase().trim() === low)) ||
            (p.bi_aliases && p.bi_aliases.some(a => (a || '').toLowerCase().trim() === low))
        );
    }

    // Build client-to-deal map for models
    const clientDealMap = {};
    if (payload.sys_db && Array.isArray(payload.sys_db)) {
        payload.sys_db.forEach(d => {
            if (d.ClientId) clientDealMap[String(d.ClientId).trim()] = d;
            if (d.LeadId) clientDealMap[String(d.LeadId).trim()] = d;
        });
    }

    // Filter leads from payload.sys_db_partners
    const allLeads = (payload && payload.sys_db_partners && Array.isArray(payload.sys_db_partners)) ? payload.sys_db_partners : [];
    const matchedLeads = [];

    const normPName = safePName.toLowerCase().trim();
    const normBrand = brandFilter ? normalizeBrandName(brandFilter) : null;
    const targetPid = pid ? parseInt(pid, 10) : (regPartner ? regPartner.partner_id : null);

    allLeads.forEach(r => {
        if (r.Type !== 'Лид') return;
        const rMonth = (r.Month || '').replace("'", "");

        // Month / date filter
        if (cfg.mode === 'month') {
            if (curMonth !== 'all' && rMonth !== curMonth) return;
        } else if (cfg.mode === 'custom') {
            const fTime = cfg.from ? new Date(cfg.from).getTime() : -Infinity;
            const tTime = cfg.to ? new Date(cfg.to).getTime() : Infinity;
            const d = typeof excelToJSDate === 'function' ? excelToJSDate(r.Date) : null;
            if (d) {
                const t = d.getTime();
                if (t < fTime || t > tTime) return;
            }
        }

        // Transferred leads are clean leads without prepay
        if (r.HasPrepay && r.HasPrepay !== 0) return;

        // Match partner
        let match = false;
        if (targetPid && r.PartnerId && parseInt(r.PartnerId, 10) === targetPid) match = true;
        else if (r.Partner && r.Partner.toLowerCase().trim() === normPName) match = true;
        else if (r.RawPartner && r.RawPartner.toLowerCase().includes(normPName)) match = true;
        else if (regPartner && r.PartnerId && parseInt(r.PartnerId, 10) === regPartner.partner_id) match = true;
        else if (normPName && r.Partner && normPName.includes(r.Partner.toLowerCase().trim())) match = true;

        if (!match && regPartner) {
            const rName = (r.Partner || r.RawPartner || '').toLowerCase().trim();
            if (rName) {
                if (regPartner.canonical_name && regPartner.canonical_name.toLowerCase().trim() === rName) match = true;
                else if (regPartner.bitrix_aliases && regPartner.bitrix_aliases.some(a => (a || '').toLowerCase().trim() === rName)) match = true;
                else if (regPartner.bi_aliases && regPartner.bi_aliases.some(a => (a || '').toLowerCase().trim() === rName)) match = true;
            }
        }

        if (!match) return;

        // Match brand if provided
        if (normBrand) {
            const b = normalizeBrandName(r.Brand);
            if (b !== normBrand) return;
        }

        // Resolve model from deals if not present in lead
        let model = r.Model || '';
        const deal = (r.ClientId && clientDealMap[String(r.ClientId).trim()]) || (r.LeadId && clientDealMap[String(r.LeadId).trim()]);
        if (deal && deal.Model) {
            model = deal.Model;
        }

        // Resolve recipient email from OEM data or pochta_aliases
        let recipientEmail = '';
        if (regPartner) {
            if (regPartner.oem_data && regPartner.oem_data.length > 0) {
                const leadBrand = normalizeBrandName(r.Brand);
                const matchingOem = regPartner.oem_data.find(o => normalizeBrandName(o.brand) === leadBrand && o.email) || regPartner.oem_data.find(o => o.email);
                if (matchingOem && matchingOem.email) {
                    recipientEmail = matchingOem.email;
                }
            }
            if (!recipientEmail && regPartner.pochta_aliases && regPartner.pochta_aliases.length > 0) {
                recipientEmail = regPartner.pochta_aliases.join(', ');
            }
        }

        matchedLeads.push({
            lead_id: r.LeadId || '',
            client_id: r.ClientId || '',
            date_serial: r.Date,
            brand: r.Brand || '—',
            model: model || '—',
            partner_name: r.Partner || safePName,
            recipient_email: recipientEmail || '—',
            has_prepay: r.HasPrepay || 0
        });
    });

    // Sort by date descending
    matchedLeads.sort((a, b) => (b.date_serial || 0) - (a.date_serial || 0));

    currentTransferredLeadsList = matchedLeads;

    if (badgeEl) badgeEl.innerText = `${matchedLeads.length} шт.`;

    renderTransferredLeadsModalTable(matchedLeads);

    modal.classList.remove('hidden');
    modal.classList.add('flex');
    modal.style.display = 'flex';
    if (typeof lucide !== 'undefined') lucide.createIcons();
}

function closeTransferredLeadsModal() {
    const modal = document.getElementById('modalTransferredLeads');
    if (modal) {
        modal.classList.add('hidden');
        modal.classList.remove('flex');
        modal.style.display = 'none';
    }
}

function renderTransferredLeadsModalTable(leads) {
    const container = document.getElementById('transLeadsTableContainer');
    const counterEl = document.getElementById('transLeadsRowsCounter');
    if (!container) return;

    if (counterEl) {
        counterEl.innerText = `Отображено: ${leads.length} из ${currentTransferredLeadsList.length}`;
    }

    if (leads.length === 0) {
        container.innerHTML = `
            <div class="text-center py-12 text-gray-400">
                <div class="text-3xl mb-2">📭</div>
                <p class="font-bold text-gray-700">Лиды не найдены</p>
                <p class="text-xs text-gray-400 mt-1">По данному партнеру отсутствуют переданные лиды за указанный период</p>
            </div>
        `;
        return;
    }

    let html = `
    <table class="min-w-full text-xs">
        <thead class="bg-slate-800 text-white font-bold sticky top-0 z-10">
            <tr>
                <th class="py-2.5 px-3 text-center w-12">№</th>
                <th class="py-2.5 px-3 text-left w-24">Дата</th>
                <th class="py-2.5 px-3 text-left w-36">ID Лида (CRM)</th>
                <th class="py-2.5 px-3 text-left w-32">Client ID</th>
                <th class="py-2.5 px-3 text-left w-32">Марка</th>
                <th class="py-2.5 px-3 text-left">Модель</th>
                <th class="py-2.5 px-3 text-left">Email получателя (ДЦ)</th>
                <th class="py-2.5 px-3 text-center w-28">Статус аванса</th>
            </tr>
        </thead>
        <tbody class="divide-y divide-gray-200">
    `;

    leads.forEach((l, idx) => {
        const rowBg = idx % 2 === 0 ? 'bg-white' : 'bg-slate-50/60';

        let dateStr = '—';
        if (l.date_serial && typeof excelToJSDate === 'function') {
            const d = excelToJSDate(l.date_serial);
            if (d) dateStr = d.toLocaleDateString('ru-RU');
        }

        const leadLink = l.lead_id
            ? `<a href="https://back.sberauto.com/crm/leads/${l.lead_id}" target="_blank" class="inline-flex items-center gap-1 font-bold text-blue-600 hover:text-blue-800 hover:underline">
                ${l.lead_id}
                <svg class="w-3 h-3" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6"></path><polyline points="15 3 21 3 21 9"></polyline><line x1="10" y1="14" x2="21" y2="3"></line></svg>
               </a>`
            : '<span class="text-gray-400">—</span>';

        const clientLink = l.client_id
            ? `<a href="https://back.sberauto.com/crm/clients/${l.client_id}" target="_blank" class="font-mono text-slate-700 hover:text-blue-600 font-semibold">
                ${l.client_id}
               </a>`
            : '<span class="text-gray-400">—</span>';

        const prepayBadge = l.has_prepay === 1
            ? `<span class="px-2 py-0.5 rounded-full text-[10px] font-bold bg-emerald-100 text-emerald-800 border border-emerald-200">Есть аванс</span>`
            : `<span class="px-2 py-0.5 rounded-full text-[10px] font-medium bg-gray-100 text-gray-600">Без аванса</span>`;

        html += `
        <tr class="${rowBg} hover:bg-blue-50/50 transition">
            <td class="py-2 px-3 text-center text-gray-400 font-medium">${idx + 1}</td>
            <td class="py-2 px-3 text-gray-700 whitespace-nowrap">${dateStr}</td>
            <td class="py-2 px-3 whitespace-nowrap">${leadLink}</td>
            <td class="py-2 px-3 whitespace-nowrap">${clientLink}</td>
            <td class="py-2 px-3 font-bold text-gray-900">${l.brand}</td>
            <td class="py-2 px-3 text-gray-700 font-medium">${l.model}</td>
            <td class="py-2 px-3 text-gray-600 font-mono text-[11px] truncate max-w-xs" title="${l.recipient_email}">${l.recipient_email}</td>
            <td class="py-2 px-3 text-center">${prepayBadge}</td>
        </tr>
        `;
    });

    html += `</tbody></table>`;
    container.innerHTML = html;
}

function filterTransferredLeadsModalTable(q) {
    const query = (q || '').toLowerCase().trim();
    if (!query) {
        renderTransferredLeadsModalTable(currentTransferredLeadsList);
        return;
    }
    const filtered = currentTransferredLeadsList.filter(l => {
        return (l.lead_id && l.lead_id.toLowerCase().includes(query)) ||
               (l.client_id && l.client_id.toLowerCase().includes(query)) ||
               (l.brand && l.brand.toLowerCase().includes(query)) ||
               (l.model && l.model.toLowerCase().includes(query)) ||
               (l.recipient_email && l.recipient_email.toLowerCase().includes(query));
    });
    renderTransferredLeadsModalTable(filtered);
}

function exportTransferredLeadsToExcel() {
    if (typeof XLSX === 'undefined') {
        alert("Библиотека экспорта в Excel еще загружается. Повторите попытку через секунду.");
        return;
    }
    if (!currentTransferredLeadsList || currentTransferredLeadsList.length === 0) {
        alert("Нет лидов для экспорта.");
        return;
    }

    const wsData = [
        ["№", "ID Лида", "Client ID", "Партнер", "Дата передачи", "Марка", "Модель", "Email получателя (ДЦ)", "Статус аванса", "Ссылка на CRM BackOffice"]
    ];

    currentTransferredLeadsList.forEach((l, idx) => {
        let dateStr = '—';
        if (l.date_serial && typeof excelToJSDate === 'function') {
            const d = excelToJSDate(l.date_serial);
            if (d) dateStr = d.toLocaleDateString('ru-RU');
        }
        const backofficeUrl = l.lead_id ? `https://back.sberauto.com/crm/leads/${l.lead_id}` : (l.client_id ? `https://back.sberauto.com/crm/clients/${l.client_id}` : '—');

        wsData.push([
            idx + 1,
            l.lead_id || '—',
            l.client_id || '—',
            l.partner_name || '—',
            dateStr,
            l.brand || '—',
            l.model || '—',
            l.recipient_email || '—',
            l.has_prepay === 1 ? 'Есть аванс' : 'Без аванса',
            backofficeUrl
        ]);
    });

    const ws = XLSX.utils.aoa_to_sheet(wsData);
    ws['!cols'] = [
        { wch: 6 },
        { wch: 14 },
        { wch: 16 },
        { wch: 28 },
        { wch: 14 },
        { wch: 16 },
        { wch: 20 },
        { wch: 35 },
        { wch: 15 },
        { wch: 45 }
    ];

    const wb = XLSX.utils.book_new();
    XLSX.utils.book_append_sheet(wb, ws, "Переданные_лиды");

    const pName = (currentTransferredLeadsList[0] && currentTransferredLeadsList[0].partner_name) || 'Партнер';
    const cleanName = pName.replace(/["*\\/?:<>|]/g, '').replace(/\s+/g, '_').slice(0, 30);
    const todayStr = new Date().toLocaleDateString('ru-RU').replace(/\./g, '_');
    const fileName = `Переданные_лиды_${cleanName}_${todayStr}.xlsx`;

    XLSX.writeFile(wb, fileName);
}


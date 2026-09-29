import json

with open('partners_registry.json', 'r', encoding='utf-8') as f:
    reg = json.load(f)

partners_by_id = {p['partner_id']: p for p in reg.get('partners', [])}

targets = [
    (1285, 'Вагнер Авто / Авторитэйл', 12),
    (1002, 'Аларм-Моторс ГК', 36),
    (632032, 'Премиум Авто ONLINE', 7),
    (1005, 'Восток Авто', 20),
    (1163, 'Автохолдинг Максимум', 41),
    (1083, 'ООО "НЕВААВТО', 16),
    (1017, 'Автопродикс', 56),
    (1063, 'Автополе', 37),
    (1192, 'ИАТ', 11),
    (1011, 'ГК Сигма', 9),
    (1280, 'Сократ (Моторленд СПб)', 8),
    (1032, 'ГК Форсаж', 11),
    (1001, 'Автостиль СПб и Великий Новгород', 4),
    (1025, 'Р-Моторс ЛАДА', 7),
    (1022, 'Прагматика', 8),
    (1021, 'Элан Моторс (Санкт Петербург)', 1),
    (1254, 'Автотим', 3),
    (1219, 'Элке Авто', 9),
    (1242, 'Рус-Авто Трейд', 1),
    (1031, 'ГК ДИНАМИКА', 14),
    (1027, 'Ай-Би-Эм', 1),
    (1245, 'Картель', 9),
    (1257, 'АлексМоторс', 1),
    (1068, 'Сармат', 7),
]

print(f"Total target partners: {len(targets)}, Sum of plans: {sum(t[2] for t in targets)}")
missing = []
for tid, tname, tplan in targets:
    p = partners_by_id.get(tid)
    if not p:
        missing.append((tid, tname))
    else:
        print(f"OK: ID {tid:6} -> {p.get('canonical_name')} | KAM: {p.get('kam')} | Plan: {tplan}")

if missing:
    print('MISSING:', missing)

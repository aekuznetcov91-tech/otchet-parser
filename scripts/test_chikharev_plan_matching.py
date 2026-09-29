import json
import sys
import re

if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

target_dealers = [
    ('БОРИСХОФ', 10, 'Москва и МО'),
    ('ООО "ДЕЛИВЕРИ КАР"', 1, 'Москва и МО'),
    ('ООО "ИЗМАЙЛОВО-СЕРВИС"', 10, 'Москва и МО'),
    ('ООО Автодин-Кама', 2, 'Москва и МО'),
    ('Тауэр Орехово', 6, 'Москва и МО'),
    ('ООО У Сервис', 20, 'Москва и МО'),
    ('Автодом и АСЦ', 45, 'Москва и МО'),
    ('ООО "МАРКАР ГРУПП" ONLINE', 60, 'Москва и МО'),
    ('ООО КВАЗАР', 30, 'Москва и МО'),
    ('КМ/ч', 1, 'Москва и МО'),
    ('ООО Кунцево АТ', 50, 'Москва и МО'),
    ('ООО Автопассаж', 2, 'Москва и МО'),
    ('Мейджер', 5, 'Москва и МО'),
    ('Эрси Автотрейд', 8, 'Москва и МО'),
    ('Фаворит', 7, 'Москва и МО'),
    ('Империя(независимость)', 15, 'Москва и МО'),
    ('Автопрестиж', 70, 'Москва и МО'),
    ('Автокласс', 3, 'ЦО'),
    ('Автоград', 1, 'ЦО'),
    ('Важная Персона Тверь', 10, 'ЦО'),
    ('ООО "ПАРУС" online', 2, 'ЦО'),
    ('Радар', 15, 'ЦО'),
    ('Анкар', 1, 'ЦО'),
    ('Гранд Техцентр Владимир JETOUR (Млада Авто)', 25, 'ЦО'),
    ('Автоцентр Лада', 2, 'ЦО'),
    ('Авто Премиум (Союз Т)', 10, 'ЦО'),
    ('Звезда Ярославии', 8, 'ЦО'),
    ('Автоимпорт', 5, 'ЦО'),
    ('Диалог', 76, 'Татарстан'),
    ('КАН АВТО', 10, 'Татарстан'),
    ('БАРС АВТО', 23, 'Татарстан'),
    ('Апельсин', 20, 'Татарстан'),
]

with open('partners_registry.json', 'r', encoding='utf-8') as f:
    reg_data = json.load(f)
partners = reg_data.get('partners', [])

with open('data.json', 'r', encoding='utf-8') as f:
    djson = json.load(f)
sep_deals = [r for r in djson.get('sys_db_partners', []) if r.get('Month') == '2026-09' and r.get('Type') == 'Сделка']
chikharev_deals = [r for r in sep_deals if 'чихарев' in (r.get('KAM') or '').lower()]

print(f"Total target dealers: {len(target_dealers)}, Total target plan: {sum(x[1] for x in target_dealers)}")
print(f"Total September deals under Chikharev: {len(chikharev_deals)}")

def clean_toks(s):
    if not s: return set()
    s = s.lower()
    for w in ['ооо', 'зао', 'ао', 'online', 'онлайн', '"', "'", '(', ')', '/', '\\', '-', '–']:
        s = s.replace(w, ' ')
    tokens = [t for t in s.split() if len(t) > 2 and t not in ('авто', 'плюс', 'групп', 'группа', 'сервис', 'центр', 'трейдинг', 'трейд', 'лтд', 'холдинг')]
    return set(tokens)

results = []
for d_name, plan, region in target_dealers:
    d_toks = clean_toks(d_name)
    best_partner = None
    scored_partners = []
    for p in partners:
        p_cname = p.get('canonical_name') or ''
        p_holding = p.get('holding') or ''
        p_kam = p.get('kam') or ''
        aliases = p.get('bitrix_aliases', []) + p.get('bi_aliases', [])
        
        # Check token overlap
        all_p_toks = clean_toks(p_cname) | clean_toks(p_holding)
        for a in aliases:
            all_p_toks |= clean_toks(a)
            
        overlap = d_toks & all_p_toks
        if overlap:
            score = len(overlap)
            if 'чихарев' in p_kam.lower():
                score += 5
            scored_partners.append((score, p))
            
    scored_partners.sort(key=lambda x: x[0], reverse=True)
    chosen = scored_partners[0][1] if scored_partners else None
    results.append({
        'target_name': d_name,
        'plan': plan,
        'region': region,
        'chosen': chosen,
        'top_candidates': [sp[1] for sp in scored_partners[:3]]
    })

print("\n=== MATCHING AUDIT ===")
matched_count = 0
for r in results:
    ch = r['chosen']
    if ch:
        matched_count += 1
        is_chik = 'чихарев' in (ch.get('kam') or '').lower()
        kam_name = ch.get('kam')
        tag = 'OK CHIKHAREV' if is_chik else f'OTHER KAM ({kam_name})'
        print(f"[{tag}] {r['target_name']:<45} (План: {r['plan']:>2}) -> ID {ch.get('partner_id')}: {ch.get('canonical_name')} | Holding: {ch.get('holding')}")
    else:
        print(f"[❌ НЕТ СОВПАДЕНИЯ] {r['target_name']:<45} (План: {r['plan']:>2})")

print("\n=== FINAL VERIFICATION OF ALL 33 MAPPINGS ===")
final_mappings = [
    ('1070', 'БорисХоф', 10),
    ('1099', 'ООО ДЕЛИВЕРИ КАР', 1),
    ('1059', 'CHERY Измайлово', 10),
    ('1042', 'Автодин', 2),
    ('1133', 'ООО ТАУЭР ЛТД', 6),
    ('1111', 'Geely У Сервис', 20),
    ('1154', 'ГК Автодом', 20),
    ('1130', 'ООО КАР АЦ (АСЦ)', 25),
    ('1120', 'ООО МАРКАР ГРУПП', 60),
    ('1052', 'КВАЗАР', 30),
    ('1095', 'КМ/Ч', 1),
    ('1091', 'ТЦ Кунцево', 50),
    ('1160', 'Автопассаж', 2),
    ('1044', 'ГК Major/Мэйджор', 5),
    ('1135', 'ЭрСи Автотрейд', 8),
    ('1227', 'Фаворит', 7),
    ('1261', 'Независимость', 15),
    ('1076', 'ГК Автопрестиж', 70),
    ('1102', 'Чери Центр Автокласс (М-Авто)', 3),
    ('1050', 'ООО АВТОГРАД-Н', 1),
    ('1258', 'Важная персона', 10),
    ('1117', 'ООО ПАРУС', 2),
    ('1041', 'Радар-Авто', 15),
    ('1090', 'Анкар Калуга', 1),
    ('1124', 'ООО МЛАДА - АВТО', 25),
    ('1126', 'ООО Центр Лада', 2),
    ('1040', 'Авто Премиум Тверь', 10),
    ('1046', 'ЗВЕЗДА ЯРОСЛАВИИ', 8),
    ('1087', 'ГК Автоимпорт', 5),
    ('1082', 'ГК Диалог Авто', 76),
    ('1201', 'Приоритет_ГК КАН Авто', 10),
    ('1233', 'Барс Авто', 23),
    ('1054', 'Апельсин-Челны', 20),
]

tot_plan = sum(m[2] for m in final_mappings)
print(f"Total entries: {len(final_mappings)}, Total target plan: {tot_plan}")

partners_by_id = {str(p.get('partner_id')): p for p in partners}
for pid, label, plan in final_mappings:
    p = partners_by_id.get(pid)
    if not p:
        print(f"❌ Missing ID {pid} ({label})")
    else:
        cname = p.get('canonical_name')
        kam = p.get('kam')
        print(f"✅ ID {pid:<4} | {cname:<30} | KAM: {kam:<17} | Plan: {plan:>2}")


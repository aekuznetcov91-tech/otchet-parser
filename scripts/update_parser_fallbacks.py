with open('scripts/parser_engine.py', 'r', encoding='utf-8') as f:
    text = f.read()

# 1. Update deals: add pid = 1076 for Автопрестиж Оренбург
s1 = """                    elif 'оренбург' in p_lower and 'эксперт' in p_lower:
                        cname = 'ГК Автопрестиж'
                        kam_partner = 'Алексей Чихарев'"""
r1 = """                    elif 'оренбург' in p_lower and 'эксперт' in p_lower:
                        pid = 1076
                        cname = 'ГК Автопрестиж'
                        kam_partner = 'Алексей Чихарев'"""
assert s1 in text, "s1 not found"
text = text.replace(s1, r1, 1)

# 2. Update deals: add pid = 1076 for Эксперт Оренбург
s2 = """                        elif any(k in p_lower or k in deal_city.lower() for k in ['оренбург']) or deal_inn in ('5638063829', '5638070618'):
                            cname = 'ГК Автопрестиж'
                            kam_partner = 'Алексей Чихарев'"""
r2 = """                        elif any(k in p_lower or k in deal_city.lower() for k in ['оренбург']) or deal_inn in ('5638063829', '5638070618'):
                            pid = 1076
                            cname = 'ГК Автопрестиж'
                            kam_partner = 'Алексей Чихарев'"""
assert s2 in text, "s2 not found"
text = text.replace(s2, r2, 1)

# 3. Update leads: holding fallback before not pid or pid == 1116
s3 = """            # Substring / Holding fallback if not matched or erroneously mapped:
            if 'рольф' in p_lower:
                pid, cname, kam = (1084, 'РОЛЬФ', 'Андрей Кузнецов')
            elif not pid or pid == 1116:"""
r3 = """            # Substring / Holding fallback if not matched or erroneously mapped:
            if 'рольф' in p_lower:
                pid, cname, kam = (1084, 'РОЛЬФ', 'Андрей Кузнецов')
            elif 'автопрестиж' in p_lower:
                pid, cname, kam = (1076, 'ГК Автопрестиж', 'Алексей Чихарев')
            elif 'прагматика' in p_lower:
                pid, cname, kam = (1022, 'Прагматика', 'Светлана Дариенко')
            elif 'боравто' in p_lower:
                pid, cname, kam = (1094, 'ГК Боравто', 'Валерия Солдатова')
            elif 'диалог' in p_lower and 'авто' in p_lower:
                pid, cname, kam = (1082, 'ГК Диалог Авто', 'Алексей Чихарев')
            elif 'дав-авто' in p_lower or 'дав авто' in p_lower:
                pid, cname, kam = (1184, 'Дав-Авто', 'Андрей Кузнецов')
            elif not pid or pid in (1116, 1045, 1198, 1127, 1193, 1205):"""
assert s3 in text, "s3 not found"
text = text.replace(s3, r3, 1)

# 4. Update leads: add pid = 1076 for Оренбург Автопрестиж
s4 = """                    elif any(k in p_lower or k in lead_city.lower() for k in ['оренбург']):
                        cname = 'ГК Автопрестиж'
                        kam = 'Алексей Чихарев'"""
r4 = """                    elif any(k in p_lower or k in lead_city.lower() for k in ['оренбург']):
                        pid = 1076
                        cname = 'ГК Автопрестиж'
                        kam = 'Алексей Чихарев'"""
assert s4 in text, "s4 not found"
text = text.replace(s4, r4, 1)

# 5. Update leads: major
s5 = """                elif any(k in p_lower for k in ['мэйджор', 'major']):
                    pid, cname, kam = (1078, 'ГК Major/Мэйджор', 'Алексей Чихарев')"""
r5 = """                elif any(k in p_lower for k in ['мэйджор', 'major']):
                    pid, cname, kam = (1044, 'ГК Major/Мэйджор', 'Алексей Чихарев')"""
if s5 in text:
    text = text.replace(s5, r5, 1)

with open('scripts/parser_engine.py', 'w', encoding='utf-8') as f:
    f.write(text)

print("Successfully updated parser_engine.py!")

import json

with open('partners_registry.json', 'r', encoding='utf-8') as f:
    reg = json.load(f)

partners = reg.get('partners', [])

print("=== 1. СИГМА ===")
for p in partners:
    cn = str(p.get('canonical_name', ''))
    pid = p.get('partner_id') or p.get('id')
    if 'сигма' in cn.lower() or pid in [1011, 1024, 1028]:
        print(f"ID {pid}: cn='{cn}', kam='{p.get('kam')}'")
        print(f"  bitrix: {p.get('bitrix_aliases')}")
        print(f"  bi: {p.get('bi_aliases')}")
        print(f"  pochta: {p.get('pochta_aliases')}")

print("\n=== 2. АВТО ПРЕМИУМ (Тверь / СПб) ===")
for p in partners:
    cn = str(p.get('canonical_name', ''))
    pid = p.get('partner_id') or p.get('id')
    if 'премиум' in cn.lower() or pid == 1040:
        print(f"ID {pid}: cn='{cn}', kam='{p.get('kam')}'")
        print(f"  bitrix: {p.get('bitrix_aliases')}")
        print(f"  bi: {p.get('bi_aliases')}")
        print(f"  pochta: {p.get('pochta_aliases')}")

print("\n=== 3. СБЕРАВТО / ID 1210 ===")
for p in partners:
    cn = str(p.get('canonical_name', ''))
    pid = p.get('partner_id') or p.get('id')
    if 'сбер' in cn.lower() or pid == 1210:
        print(f"ID {pid}: cn='{cn}', kam='{p.get('kam')}'")
        print(f"  bitrix: {p.get('bitrix_aliases')}")
        print(f"  bi: {p.get('bi_aliases')}")
        print(f"  pochta: {p.get('pochta_aliases')}")

print("\n=== 4. АВТОРИТЕТ ===")
for p in partners:
    cn = str(p.get('canonical_name', ''))
    pid = p.get('partner_id') or p.get('id')
    if 'авторитет' in cn.lower():
        print(f"ID {pid}: cn='{cn}', kam='{p.get('kam')}'")
        print(f"  bitrix: {p.get('bitrix_aliases')}")
        print(f"  bi: {p.get('bi_aliases')}")
        print(f"  pochta: {p.get('pochta_aliases')}")

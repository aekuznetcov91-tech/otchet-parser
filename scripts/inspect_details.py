import json

with open('partners_registry.json', 'r', encoding='utf-8') as f:
    reg = json.load(f)

partners = reg.get('partners', [])

with open('duplicates_analysis.txt', 'w', encoding='utf-8') as out:
    for p in partners:
        cn = p.get('canonical_name', '').strip()
        pid = p.get('partner_id') or p.get('id')
        if any(k in cn.lower() for k in ['автопрестиж', 'прагматик', 'fresh', 'арконт', 'башавтоком', 'диалог', 'интерпартнер', 'леон', 'лунаавто', 'нижегородец', 'оптима', 'твс', 'транстехсервис', 'ттс', 'темп авто', 'эксперт самара', 'major', 'мажор']):
            out.write(f"ID {pid}: cn='{cn}', kam='{p.get('kam')}'\n")
            out.write(f"    bitrix_aliases: {p.get('bitrix_aliases', [])}\n")
            out.write(f"    bi_aliases: {p.get('bi_aliases', [])}\n")
            out.write(f"    pochta_queues: {p.get('pochta_queues', [])}\n")

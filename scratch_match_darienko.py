import json, re

with open('scratch_darienko_dealers.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

with open('partners_registry.json', 'r', encoding='utf-8') as f:
    reg = json.load(f)

partners = reg.get('partners', [])

# Map partners by id, canonical_name, aliases
partner_by_id = {p['partner_id']: p for p in partners}

def normalize_text(t):
    if not t: return ""
    t = str(t).lower()
    t = re.sub(r'[\"\',()\\/\-_]', ' ', t)
    return ' '.join(t.split())

def match_dealer(dealer_name, region, brands):
    norm_d = normalize_text(dealer_name)
    
    # 1. Exact match canonical_name
    for p in partners:
        if normalize_text(p.get('canonical_name')) == norm_d:
            return p, 'exact_canonical'
            
    # 2. Check bitrix / bi aliases
    for p in partners:
        for a in (p.get('bitrix_aliases') or []) + (p.get('bi_aliases') or []) + (p.get('pochta_aliases') or []):
            if normalize_text(a) == norm_d:
                return p, 'exact_alias'
                
    # 3. Check OEM names
    for p in partners:
        for o in p.get('oem_data') or []:
            if normalize_text(o.get('name')) == norm_d:
                return p, 'exact_oem_name'
                
    # 4. Partial substring match with Darienko preference
    best_p = None
    best_score = 0
    d_tokens = set([w for w in norm_d.split() if len(w) >= 3 and w not in ['ооо', 'зао', 'пао', 'ао', 'онлайн', 'online', 'авто', 'плюс', 'дилер', 'центр', 'групп', 'моторс']])
    
    for p in partners:
        p_cname = normalize_text(p.get('canonical_name'))
        p_kam = p.get('kam') or ''
        is_darienko = 'дариенко' in p_kam.lower()
        
        all_aliases = [p_cname] + [normalize_text(a) for a in (p.get('bitrix_aliases') or []) + (p.get('bi_aliases') or [])]
        for o in p.get('oem_data') or []:
            if o.get('name'): all_aliases.append(normalize_text(o.get('name')))
            
        for a in all_aliases:
            if not a: continue
            a_tokens = set([w for w in a.split() if len(w) >= 3 and w not in ['ооо', 'зао', 'пао', 'ао', 'онлайн', 'online', 'авто', 'плюс', 'дилер', 'центр', 'групп', 'моторс']])
            common = d_tokens.intersection(a_tokens)
            if common:
                score = len(common) * 10
                if is_darienko: score += 15
                if a in norm_d or norm_d in a: score += 20
                if score > best_score:
                    best_score = score
                    best_p = p
                    
    if best_p and best_score >= 20:
        return best_p, f'fuzzy_{best_score}'
        
    return None, 'no_match'

results = []
for d in data['dealers']:
    d_name = d['dealer']
    region = d['region']
    brands = [it['brand'] for it in d['items']]
    p, method = match_dealer(d_name, region, brands)
    results.append({
        'excel_dealer': d_name,
        'region': region,
        'plan_raw': d['total_plan_raw'],
        'plan_round': d['total_plan_round'],
        'items': d['items'],
        'matched_id': p['partner_id'] if p else None,
        'matched_name': p['canonical_name'] if p else None,
        'matched_kam': p['kam'] if p else None,
        'match_method': method
    })

with open('scratch_matched_darienko.json', 'w', encoding='utf-8') as f:
    json.dump(results, f, ensure_ascii=False, indent=2)

matched_count = sum(1 for r in results if r['matched_id'] is not None)
print(f"Matched {matched_count} of {len(results)} dealers.")

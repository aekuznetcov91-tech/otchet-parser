import os, re, json, html, openpyxl
from collections import Counter, defaultdict

# 1. Load OEM directory from raw_data/OEM СберАвто финал (15).xlsx
wb = openpyxl.load_workbook('raw_data/OEM СберАвто финал (15).xlsx', data_only=True)

def normalize_brand(t_str):
    t = str(t_str or '').upper()
    t_clean = t.replace('О', 'O').replace('А', 'A').replace('Е', 'E').replace('С', 'C').replace('Т', 'T').replace('Р', 'P')
    
    # 1. Belgee vs Geely
    if 'BELGEE' in t_clean or 'BEELGEE' in t_clean or 'БЕЛДЖИ' in t:
        return 'Belgee'
    if 'GEELY' in t_clean or 'ДЖИЛИ' in t or 'COOLRAY' in t_clean or 'MONJARO' in t_clean or 'ATLAS' in t_clean or 'EMGRAND' in t_clean or 'PREFACE' in t_clean or 'OKAVANGO' in t_clean:
        return 'Geely'
        
    # 2. Chery & Tenet (combined)
    if 'CHERY' in t_clean or 'CHETY' in t_clean or 'ЧЕРИ' in t or 'TIGGO' in t_clean or 'ARRIZO' in t_clean or 'TENET' in t_clean or 'ТЕНЕТ' in t:
        return 'CHERY & TENET'
        
    # 3. Omoda & Jaecoo (combined)
    if 'OMODA' in t_clean or 'ОМОДА' in t or 'JAECOO' in t_clean or 'ДЖЕЙКУ' in t or 'JELAND' in t_clean or 'C5' in t_clean or 'S5' in t_clean or 'J7' in t_clean or 'J8' in t_clean:
        return 'OMODA & JAECOO'
        
    # 4. Lada
    if 'LADA' in t_clean or 'ЛАДА' in t or 'ВАЗ' in t or 'GRANTA' in t_clean or 'VESTA' in t_clean or 'NIVA' in t_clean or 'LARGUS' in t_clean or 'ISKRA' in t_clean:
        return 'LADA'
        
    # 5. Jetour
    if 'JETOUR' in t_clean or 'JATOUR' in t_clean or 'JETOR' in t_clean or 'ДЖЕТУР' in t or 'DASHING' in t_clean or 'X70' in t_clean or 'X90' in t_clean:
        return 'JETOUR'
        
    # 6. Haval
    if 'HAVAL' in t_clean or 'ХАВЕЙЛ' in t or 'JOLION' in t_clean or 'DARGO' in t_clean or 'F7' in t_clean or 'H3' in t_clean or 'H9' in t_clean or 'M6' in t_clean:
        return 'HAVAL'
        
    # 7. Changan
    if 'CHANGAN' in t_clean or 'ЧАНГАН' in t or 'ALSVIN' in t_clean or 'EADO' in t_clean or 'LAMORE' in t_clean or 'CS35' in t_clean or 'CS55' in t_clean or 'CS75' in t_clean or 'CS95' in t_clean or 'UNI-' in t_clean or 'HUNTER' in t_clean:
        return 'CHANGAN'
        
    # 8. Solaris
    if 'SOLARIS' in t_clean or 'СОЛЯРИС' in t or 'KRS' in t_clean or 'KRX' in t_clean or 'HC' in t_clean or 'HS' in t_clean:
        return 'SOLARIS'
        
    # 9. GAC
    if 'GAC' in t_clean or 'ГАК' in t or 'GS3' in t_clean or 'GS4' in t_clean or 'GS8' in t_clean or 'EMPOW' in t_clean or 'AION' in t_clean or 'HYPTEC' in t_clean:
        return 'GAC'
        
    # 10. Soueast
    if 'SOUEAST' in t_clean or 'СОУИСТ' in t or 'S06' in t_clean or 'S07' in t_clean or 'S09' in t_clean:
        return 'SOUEAST'
        
    # 11. Москвич
    if 'МОСКВИЧ' in t or 'MOSKVICH' in t_clean or 'М70' in t or 'М90' in t or 'M70' in t_clean or 'M90' in t_clean:
        return 'Москвич'
        
    # 12. Deepal
    if 'DEEPAL' in t_clean or 'ДИПАЛ' in t or 'G318' in t_clean:
        return 'DEEPAL'
        
    # 13. Jetta
    if 'JETTA' in t_clean or 'ДЖЕТТА' in t or 'VA3' in t_clean or 'VS5' in t_clean or 'VS7' in t_clean:
        return 'JETTA'
        
    # 14. Voyah
    if 'VOYAH' in t_clean or 'VOYA' in t_clean or 'ВОЙЯ' in t or 'FREE' in t_clean or 'DREAM' in t_clean:
        return 'VOYAH'
        
    # 15. Knewstar
    if 'KNEWSTAR' in t_clean:
        return 'KNEWSTAR'
        
    # 16. Xcite
    if 'XCITE' in t_clean or 'X-CROSS' in t_clean or 'XCROSS' in t_clean:
        return 'XCITE'
        
    # 17. Tank
    if 'TANK' in t_clean or 'ТАНК' in t:
        return 'TANK'
        
    # 18. Exeed
    if 'EXEED' in t_clean or 'ЭКСИД' in t:
        return 'EXEED'
        
    # Recognizable other brands
    for b in ['TOYOTA', 'NISSAN', 'HYUNDAI', 'KIA', 'RENAULT', 'PEUGEOT', 'LIFAN', 'HONGQI', 'EVOLUTE', 'FAW', 'JAC', 'BAIC', 'KAIYI', 'LIVAN', 'УАЗ', 'AUDI']:
        if b in t_clean or b in t:
            return b.title()

    if 'MINI' in t_clean: return 'MINI'
    if 'LAND' in t_clean: return 'Land Rover'

    return t_str.split()[0].title() if t_str.split() else 'Другие'

def clean_city(c_str):
    if not c_str: return ''
    c = c_str.lower().strip()
    c = re.sub(r'^(г\.|гор\.|город)\s*', '', c)
    return c.strip()

def clean_addr(a_str):
    if not a_str: return ''
    a = a_str.lower().strip()
    a = re.sub(r'\s+', ' ', a)
    # clean leading index/postal codes if present: 620050, ...
    a = re.sub(r'^\d{6},\s*', '', a)
    a = a.strip(' ,;.')
    return a

# Build address lookup database
oem_records = []

for sname in wb.sheetnames:
    ws = wb[sname]
    sheet_b = normalize_brand(sname)
    header_row = None
    for r in range(1, min(ws.max_row+1, 50)):
        if 'Город' in str(ws.cell(r, 1).value or '') and any('Адрес' in str(ws.cell(r, c).value or '') for c in range(1, 15)):
            header_row = r
            break
    if not header_row: continue
    
    hcols = {}
    for c in range(1, ws.max_column+1):
        v = str(ws.cell(header_row, c).value or '').strip().lower()
        if 'город' in v: hcols['city'] = c
        elif 'название в беке' in v: hcols['back_name'] = c
        elif 'адрес' in v: hcols['address'] = c
        elif 'название' in v and 'беке' not in v: hcols['name'] = c
        elif 'инн' in v: hcols['inn'] = c
        elif 'юл' in v: hcols['legal_entity'] = c
        
    for r in range(header_row+1, ws.max_row+1):
        city = str(ws.cell(r, hcols.get('city', 1)).value or '').strip()
        addr = str(ws.cell(r, hcols.get('address', 7)).value or '').strip()
        bname = str(ws.cell(r, hcols.get('back_name', 8)).value or '').strip() if 'back_name' in hcols else ''
        name = str(ws.cell(r, hcols.get('name', 3)).value or '').strip() if 'name' in hcols else ''
        le = str(ws.cell(r, hcols.get('legal_entity', 4)).value or '').strip() if 'legal_entity' in hcols else ''
        inn = str(ws.cell(r, hcols.get('inn', 5)).value or '').strip() if 'inn' in hcols else ''
        
        if not city and not addr and not name: continue
        oem_records.append({
            'brand': sheet_b,
            'city': clean_city(city),
            'address': clean_addr(addr),
            'raw_address': addr,
            'back_name': bname,
            'name': name,
            'legal_entity': le,
            'inn': inn
        })

# Also load data.json partners_registry
with open('data.json', 'r', encoding='utf-8') as f:
    data_json = json.load(f)

for p in data_json.get('partners_registry', []):
    cname = p.get('canonical_name', '')
    aliases = p.get('bitrix_aliases', [])
    for oem in p.get('oem_data', []):
        b = normalize_brand(oem.get('brand') or oem.get('sheet') or '')
        addr = clean_addr(oem.get('address') or '')
        city = clean_city(oem.get('city') or '')
        bname = (oem.get('back_name') or '').strip()
        name = (oem.get('name') or '').strip()
        le = (oem.get('legal_entity') or '').strip()
        inn = (oem.get('inn') or '').strip()
        if addr:
            oem_records.append({
                'brand': b,
                'city': city,
                'address': addr,
                'raw_address': oem.get('address'),
                'back_name': bname,
                'name': name or cname,
                'legal_entity': le,
                'inn': inn,
                'aliases': aliases
            })

print(f'Total address records in registry: {len(oem_records)}')

# Read deal export
deal_path = os.path.expanduser('~/Downloads/DEAL_20260922_1245eb64_6ab264526d153 (1).xls')
with open(deal_path, 'r', encoding='utf-8') as f:
    content = f.read()

tr_matches = re.findall(r'<tr>(.*?)</tr>', content, re.DOTALL)
header = [html.unescape(re.sub(r'<.*?>', '', c)).strip() for c in re.findall(r'<th.*?>(.*?)</th>', tr_matches[0], re.DOTALL)]
col_idx = {h: i for i, h in enumerate(header)}

id_col = col_idx['ID']
tovar_col = col_idx['Товар']
stage_col = col_idx['Стадия сделки']
date_col = col_idx['Предполагаемая дата закрытия']
company_col = col_idx['Компания: Название компании']
city_col = col_idx['Город. B2C']

aux_keywords = ("ВНЕСЕНИЕ АВАНСА", "КРЕДИТ", "КАСКО", "ОСАГО", "ГАП", "СТРАХОВ", "СЕРТИФИКАТ", "ДОП. ОБОРУДОВАНИЕ", "ДОПОЛНИТЕЛЬНОЕ ОБОРУДОВАНИЕ")

deals = {}
for tr in tr_matches[1:]:
    tds = [html.unescape(re.sub(r'<.*?>', '', c)).strip() for c in re.findall(r'<td.*?>(.*?)</td>', tr, re.DOTALL)]
    if not tds: continue
    tovar = tds[tovar_col].strip()
    if any(kw in tovar.upper() for kw in aux_keywords): continue
    if 'ЗАКРЫТО И РЕАЛИЗОВАН' not in tds[stage_col].upper(): continue
    
    did = tds[id_col]
    d_str = tds[date_col]
    m_match = re.search(r'(\d{2})\.(\d{2})\.(\d{4})', str(d_str))
    if not m_match: continue
    month = f'{m_match.group(3)}-{m_match.group(2)}'
    
    if did not in deals:
        deals[did] = {
            'id': did,
            'tovar': tovar,
            'brand': normalize_brand(tovar),
            'month': month,
            'company': tds[company_col].strip(),
            'city': clean_city(tds[city_col].strip())
        }

print(f'Total deduplicated sales deals: {len(deals)}')

# Matcher function for each deal
def match_address(d):
    brand = d['brand']
    comp = d['company'].lower().strip()
    comp_clean = re.sub(r'^(online|онлайн)\s*', '', comp, flags=re.IGNORECASE).strip()
    city = d['city']
    
    # Try to extract quoted legal entity: e.g. ООО "АВТОГЕРМЕС-ЗАПАД" -> автогермес-запад
    q_match = re.search(r'["«](.*?)["»]', comp)
    q_name = q_match.group(1).lower().strip() if q_match else ''
    
    # Candidates filtered by brand (or ANY brand)
    candidates = []
    
    for r in oem_records:
        r_b = r['brand']
        r_city = r['city']
        r_bn = (r['back_name'] or '').lower().strip()
        r_n = (r['name'] or '').lower().strip()
        r_le = (r['legal_entity'] or '').lower().strip()
        r_addr = r['address']
        
        # Check brand compatibility
        brand_match = (r_b == brand) or (r_b == 'ANY')
        
        # Score match
        score = 0
        if r_bn and (r_bn == comp or r_bn in comp or comp in r_bn):
            score += 10
        if q_name and (q_name in r_le or q_name in r_n or q_name in r_bn):
            score += 8
        if r_n and (r_n in comp or comp_clean in r_n or r_n in comp_clean) and len(r_n) > 3:
            score += 5
        if r_le and (r_le in comp or comp_clean in r_le) and len(r_le) > 3:
            score += 5
            
        for al in r.get('aliases', []):
            al_l = al.lower().strip()
            if al_l and (al_l == comp or al_l in comp or comp in al_l):
                score += 8
                break
                
        if score > 0:
            if brand_match:
                score += 5
            if city and r_city and (city == r_city or city in r_city or r_city in city):
                score += 10
            elif city and r_city and city != r_city:
                score -= 5
                
            candidates.append((score, r_addr, r))
            
    if candidates:
        candidates.sort(key=lambda x: x[0], reverse=True)
        best_score, best_addr, best_r = candidates[0]
        if best_score >= 10:
            return best_addr
            
    # Fallback: City + Partner
    fallback = f"г. {d['city'].title() if d['city'] else 'Не указан'}, {d['company']}"
    return clean_addr(fallback)

# Compute rooftop attribution
rooftop_per_deal = {}
for did, d in deals.items():
    addr = match_address(d)
    brand = d['brand']
    rt_key = (brand, addr)
    rooftop_per_deal[did] = {
        'deal_id': did,
        'month': d['month'],
        'brand': brand,
        'address': addr,
        'rooftop_key': f"{brand} | {addr}",
        'company': d['company'],
        'city': d['city']
    }

# Monthly aggregation
months = sorted(list(set(d['month'] for d in rooftop_per_deal.values() if d['month'].startswith('2026-'))))

monthly_summary = []
ytd_rooftops = set()

for m in months:
    m_deals = [d for d in rooftop_per_deal.values() if d['month'] == m]
    m_rooftops = set(d['rooftop_key'] for d in m_deals)
    
    ytd_rooftops.update(m_rooftops)
    
    # Brand breakdown
    brand_deals = Counter(d['brand'] for d in m_deals)
    brand_rts_map = defaultdict(set)
    for d in m_deals:
        brand_rts_map[d['brand']].add(d['address'])
    brand_rts = {b: len(addrs) for b, addrs in brand_rts_map.items()}
    
    monthly_summary.append({
        'month': m,
        'deals': len(m_deals),
        'rooftops': len(m_rooftops),
        'cumulative_ytd_rooftops': len(ytd_rooftops),
        'brand_rooftops': dict(sorted(brand_rts.items(), key=lambda x: x[1], reverse=True)),
        'brand_deals': dict(brand_deals.most_common())
    })

results = {
    'total_deals': len(deals),
    'total_unique_rooftops_ytd': len(ytd_rooftops),
    'monthly': monthly_summary
}

with open('final_rooftops_result.json', 'w', encoding='utf-8') as out:
    json.dump(results, out, ensure_ascii=False, indent=2)

print('Done computing final rooftops. Results saved to final_rooftops_result.json')

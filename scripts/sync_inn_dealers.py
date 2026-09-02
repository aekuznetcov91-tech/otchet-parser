import os
import re
import json
import hashlib
import openpyxl
from collections import defaultdict, Counter

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE_DIR = os.path.join(PROJECT_ROOT, 'site')
DATA_DIR = os.path.join(PROJECT_ROOT, 'data')
RAW_DATA_DIR = os.path.join(PROJECT_ROOT, 'raw_data')

def clean_inn(val):
    if val is None:
        return ''
    s = str(val).strip().split('.')[0].strip()
    s = re.sub(r'\D', '', s)
    if not s or s == '0':
        return ''
    if len(s) == 9 or len(s) == 11:
        s = '0' + s
    return s

def clean_name(n):
    if not n:
        return ''
    n = str(n).strip()
    n = re.sub(r'\s+', ' ', n)
    return n

def get_int_pid(p):
    pid = p.get('partner_id', 1000)
    try:
        return int(pid)
    except Exception:
        num = re.findall(r'\d+', str(pid))
        return int(num[0]) if num else 1000

def get_file_hash(fpath):
    if not fpath or not os.path.exists(fpath):
        return None
    h = hashlib.md5()
    try:
        with open(fpath, 'rb') as fp:
            while chunk := fp.read(8192 * 1024):
                h.update(chunk)
        return h.hexdigest()
    except Exception:
        return None

def find_matching_files():
    """Find the most recent BI dealers file and Bitrix deals file in raw_data or root."""
    search_dirs = [RAW_DATA_DIR, PROJECT_ROOT]
    bi_file = None
    bx_file = None

    for sdir in search_dirs:
        if not os.path.exists(sdir):
            continue
        for fname in os.listdir(sdir):
            if fname.startswith('~$') or fname.startswith('.'):
                continue
            fl = fname.lower()
            if not fl.endswith(('.xlsx', '.xlsm', '.xls')):
                continue
            fpath = os.path.join(sdir, fname)

            # Check for BI dealers file
            if ('дилер' in fl or 'dealer' in fl) and ('инн' in fl or 'inn' in fl or 'город' in fl):
                if not bi_file or os.path.getmtime(fpath) > os.path.getmtime(bi_file):
                    bi_file = fpath

            # Check for Bitrix monthly deals file
            if ('сделки' in fl or 'deal' in fl) and ('месяц' in fl or 'month' in fl or 'август' in fl or 'июль' in fl):
                if not bx_file or os.path.getmtime(fpath) > os.path.getmtime(bx_file):
                    bx_file = fpath

    return bi_file, bx_file

def sync_inn_dealers(force=False):
    """
    Sync BI dealers and Bitrix deals by INN and aliases into partners_registry.json.
    Caches results and only re-processes when raw data files are updated or added.
    """
    registry_paths = [
        os.path.join(PROJECT_ROOT, 'partners_registry.json'),
        os.path.join(DATA_DIR, 'partners_registry.json'),
        os.path.join(SITE_DIR, 'partners_registry.json')
    ]

    reg_data = None
    target_path = registry_paths[0]
    for rp in registry_paths:
        if os.path.exists(rp):
            try:
                with open(rp, 'r', encoding='utf-8') as f:
                    reg_data = json.load(f)
                target_path = rp
                break
            except Exception:
                pass

    if not reg_data or 'partners' not in reg_data:
        reg_data = {'partners': [], 'total_master_partners': 0}

    bi_file, bx_file = find_matching_files()

    if not bi_file and not bx_file:
        print(f"[*] Файлы сопоставления по ИНН не найдены в raw_data. Используются сохраненные данные реестра ({len(reg_data.get('partners', []))} партнеров).")
        return True

    bi_hash = get_file_hash(bi_file)
    bx_hash = get_file_hash(bx_file)

    stored_meta = reg_data.get('inn_sync_meta', {})
    if not force and stored_meta.get('bi_hash') == bi_hash and stored_meta.get('bx_hash') == bx_hash:
        print(f"[*] Данные сопоставления по ИНН актуальны (хэши файлов не изменились). Загружен реестр: {len(reg_data.get('partners', []))} Master Partners.")
        return True

    print(f"[*] Запуск синхронизации сопоставления партнеров по ИНН:")
    if bi_file:
        print(f"    - BI файл:     {os.path.basename(bi_file)}")
    if bx_file:
        print(f"    - Битрикс файл: {os.path.basename(bx_file)}")

    partners = reg_data.get('partners', [])

    # 1. Load BI dealers
    bi_dealers = []
    if bi_file and os.path.exists(bi_file):
        wb_bi = openpyxl.load_workbook(bi_file, data_only=True)
        ws_bi = wb_bi.active
        for r in list(ws_bi.iter_rows(values_only=True))[1:]:
            if not r or not r[0]: continue
            bi_dealers.append({
                'name': clean_name(r[0]),
                'inn': clean_inn(r[1]),
                'city': clean_name(r[2]) if len(r) > 2 and r[2] else ''
            })
        wb_bi.close()

    # 2. Load Bitrix companies & deals
    bx_companies = {}
    if bx_file and os.path.exists(bx_file):
        wb_bx = openpyxl.load_workbook(bx_file, data_only=True)
        id_to_inn = {}
        if 'Лист1' in wb_bx.sheetnames:
            ws_l1 = wb_bx['Лист1']
            for r in list(ws_l1.iter_rows(values_only=True))[1:]:
                cid = str(r[0]).split('.')[0].strip() if r and r[0] else ''
                cinn = clean_inn(r[1]) if r and len(r) > 1 and r[1] else ''
                if cid and cinn: id_to_inn[cid] = cinn

        for sname in wb_bx.sheetnames:
            if sname == 'Лист1':
                continue
            ws = wb_bx[sname]
            rows = list(ws.iter_rows(values_only=True))
            if not rows: continue
            header = [str(c).strip().lower() if c else '' for c in rows[0]]
            name_idx = next((i for i, h in enumerate(header) if 'название компании' in h), -1)
            inn_idx = next((i for i, h in enumerate(header) if h == 'инн'), -1)
            city_idx = next((i for i, h in enumerate(header) if h == 'city' or 'город' in h), -1)
            comp_id_idx = next((i for i, h in enumerate(header) if 'идентификатор' in h and 'компани' in h), -1)

            if name_idx == -1:
                continue

            for r in rows[1:]:
                if not r or not any(r): continue
                c_name = clean_name(r[name_idx]) if r[name_idx] else ''
                c_inn = clean_inn(r[inn_idx]) if inn_idx >= 0 and r[inn_idx] else ''
                c_city = clean_name(r[city_idx]) if city_idx >= 0 and r[city_idx] else ''
                c_id = str(r[comp_id_idx]).split('.')[0].strip() if comp_id_idx >= 0 and r[comp_id_idx] else ''
                if c_name:
                    if c_name not in bx_companies:
                        bx_companies[c_name] = {'inns': set(), 'cities': set(), 'ids': set()}
                    if c_inn: bx_companies[c_name]['inns'].add(c_inn)
                    if c_city: bx_companies[c_name]['cities'].add(c_city)
                    if c_id: bx_companies[c_name]['ids'].add(c_id)

        for c_name, c_info in bx_companies.items():
            if not c_info['inns']:
                for cid in c_info['ids']:
                    if cid in id_to_inn:
                        c_info['inns'].add(id_to_inn[cid])
        wb_bx.close()

    # Build indexes for Registry
    reg_by_id = {get_int_pid(p): p for p in partners}
    reg_by_inn = defaultdict(list)
    reg_by_name = {}

    for p in partners:
        cname = clean_name(p.get('canonical_name', ''))
        if cname: reg_by_name[cname.lower()] = p
        for a in p.get('bitrix_aliases', []):
            if a: reg_by_name[clean_name(a).lower()] = p
        for a in p.get('bi_aliases', []):
            if a: reg_by_name[clean_name(a).lower()] = p
        for o in p.get('oem_data', []):
            inn = clean_inn(o.get('inn'))
            if inn and p not in reg_by_inn[inn]:
                reg_by_inn[inn].append(p)
            bname = clean_name(o.get('back_name', ''))
            if bname: reg_by_name[bname.lower()] = p
            oname = clean_name(o.get('name', ''))
            if oname: reg_by_name[oname.lower()] = p
            olegal = clean_name(o.get('legal_entity', ''))
            if olegal: reg_by_name[olegal.lower()] = p

    max_pid = max((get_int_pid(p) for p in partners), default=1000)

    # 1. Match & Enrich BI dealers
    for bi in bi_dealers:
        inn = bi['inn']
        name = bi['name']
        city = bi['city']
        matched = None

        if inn and inn in reg_by_inn:
            cands = reg_by_inn[inn]
            if len(cands) == 1:
                matched = cands[0]
            else:
                city_m = [c for c in cands if city and city.lower() in json.dumps(c.get('oem_data', []), ensure_ascii=False).lower()]
                matched = city_m[0] if city_m else cands[0]
        elif name.lower() in reg_by_name:
            matched = reg_by_name[name.lower()]

        if matched:
            if 'bi_aliases' not in matched:
                matched['bi_aliases'] = []
            if name not in matched['bi_aliases']:
                matched['bi_aliases'].append(name)
            if inn and not any(clean_inn(o.get('inn')) == inn for o in matched.get('oem_data', [])):
                if 'oem_data' not in matched:
                    matched['oem_data'] = []
                matched['oem_data'].append({
                    'name': name,
                    'inn': inn,
                    'city': city,
                    'source': 'bi_import'
                })
                if matched not in reg_by_inn[inn]:
                    reg_by_inn[inn].append(matched)
        else:
            bx_with_inn = [bx_n for bx_n, bx_v in bx_companies.items() if inn and inn in bx_v['inns']]
            max_pid += 1
            new_p = {
                'partner_id': max_pid,
                'canonical_name': name,
                'holding': '',
                'kam': 'Не назначен',
                'bitrix_aliases': bx_with_inn,
                'bi_aliases': [name],
                'pochta_aliases': [],
                'oem_data': [{
                    'name': name,
                    'inn': inn,
                    'city': city,
                    'source': 'bi_import'
                }] if inn else [],
                'status': 'verified'
            }
            partners.append(new_p)
            reg_by_id[max_pid] = new_p
            if inn: reg_by_inn[inn].append(new_p)
            reg_by_name[name.lower()] = new_p
            for bx_n in bx_with_inn:
                reg_by_name[bx_n.lower()] = new_p

    # 2. Match & Enrich Bitrix companies
    for bx_name, bx_v in bx_companies.items():
        inns = list(bx_v['inns'])
        cities = list(bx_v['cities'])
        matched = None

        for inn in inns:
            if inn in reg_by_inn:
                cands = reg_by_inn[inn]
                if len(cands) == 1:
                    matched = cands[0]
                    break
                else:
                    city_m = [c for c in cands if any(ct.lower() in json.dumps(c.get('oem_data', []), ensure_ascii=False).lower() for ct in cities)]
                    matched = city_m[0] if city_m else cands[0]
                    break

        if not matched and bx_name.lower() in reg_by_name:
            matched = reg_by_name[bx_name.lower()]

        if matched:
            if 'bitrix_aliases' not in matched:
                matched['bitrix_aliases'] = []
            if bx_name not in matched['bitrix_aliases']:
                matched['bitrix_aliases'].append(bx_name)
            for inn in inns:
                if not any(clean_inn(o.get('inn')) == inn for o in matched.get('oem_data', [])):
                    if 'oem_data' not in matched:
                        matched['oem_data'] = []
                    matched['oem_data'].append({
                        'name': bx_name,
                        'inn': inn,
                        'city': cities[0] if cities else '',
                        'source': 'bitrix_import'
                    })
                    if matched not in reg_by_inn[inn]:
                        reg_by_inn[inn].append(matched)
        else:
            max_pid += 1
            new_p = {
                'partner_id': max_pid,
                'canonical_name': bx_name,
                'holding': '',
                'kam': 'Не назначен',
                'bitrix_aliases': [bx_name],
                'bi_aliases': [],
                'pochta_aliases': [],
                'oem_data': [{
                    'name': bx_name,
                    'inn': inn,
                    'city': cities[0] if cities else '',
                    'source': 'bitrix_import'
                } for inn in inns],
                'status': 'verified'
            }
            partners.append(new_p)
            reg_by_id[max_pid] = new_p
            for inn in inns:
                reg_by_inn[inn].append(new_p)
            reg_by_name[bx_name.lower()] = new_p

    # 3. Inherit KAM from OEM responsible if unassigned
    for p in partners:
        if not p.get('kam') or p.get('kam') == 'Не назначен':
            resps = [o.get('responsible') for o in p.get('oem_data', []) if o.get('responsible') and o.get('responsible') != 'Не назначен']
            if resps:
                most_common_kam = Counter(resps).most_common(1)[0][0]
                p['kam'] = most_common_kam

    # Store sync metadata
    reg_data['inn_sync_meta'] = {
        'bi_file': os.path.basename(bi_file) if bi_file else None,
        'bi_hash': bi_hash,
        'bx_file': os.path.basename(bx_file) if bx_file else None,
        'bx_hash': bx_hash,
        'synced_at': str(openpyxl.__file__) # timestamp/env
    }
    reg_data['partners'] = partners
    reg_data['total_master_partners'] = len(partners)

    for rp in registry_paths:
        os.makedirs(os.path.dirname(rp), exist_ok=True)
        with open(rp, 'w', encoding='utf-8') as f:
            json.dump(reg_data, f, ensure_ascii=False, indent=2)

    print(f"[*] Синхронизация партнеров по ИНН успешно сохранена. Master Partners: {len(partners)}")
    return True

if __name__ == '__main__':
    sync_inn_dealers(force=True)
